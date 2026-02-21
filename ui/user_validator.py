# this is a temporary file till we decide how to deal with user authentication
import sys
from subprocess import check_output


def user_authorized():
    if sys.version_info[0] == 3:
        email = check_output("whoami /upn", shell=True, text=True)
    else:
        email = check_output("whoami /upn", shell=True)
    domain = email.split("@")[1]
    if domain.__contains__("Company Name.com"):
        return True
    else:
        return False
