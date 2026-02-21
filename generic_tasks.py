import os.path
import sys


from zipfile import ZipFile


def prepare_zip(application_name):
    exe_file_path = os.path.join(os.environ["INSTALL_DIR"], "ReportAutomation",
                                 "{}.exe".format(application_name))
    version_file = os.path.abspath(r"version_info/version.ini")
    zipped = os.path.join(os.environ["ZIPPED_DIR"], "ReportAutomation.zip")
    with ZipFile(zipped, "w") as zip_object:
        zip_object.write(exe_file_path, os.path.basename(exe_file_path))
        # zip_object.write(version_file, os.path.basename(version_file))

    if os.path.exists(zipped):
        print("Zip file created")
        return zipped
    else:
        print("Zip file not created")
        return None


def query_yes_no(question, default="yes"):
    """Ask a yes/no question via raw_input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
            It must be "yes" (the default), "no" or None (meaning
            an answer is required of the user).

    The "answer" return value is True for "yes" or False for "no".
    """
    valid = {"yes": True, "y": True, "ye": True, "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = input().lower()
        if default is not None and choice == "":
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' " "(or 'y' or 'n').\n")
