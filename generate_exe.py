import os
import subprocess
import sys
from glob import glob
from pathlib import Path
import certifi
from create_env.configure_environment import configure_environment
from version_info.get_version import get_version

app_name = "ReportAutomation"
version = "1.0"


def find(name, path):
    for root, dirs, files in os.walk(path):
        if name in dirs:
            return os.path.join(root, name)


def main(venv_path, application_name, application_version):
    dir_name = os.path.dirname(os.path.realpath(__file__))
    icon = os.path.join(dir_name, "ui", "icons", "Logo.ico")
    name = application_name + application_version
    data1 = "{};ui/icons/".format(os.path.join(dir_name, 'ui', 'icons'))
    data2 = "{};employee_mapping_sheet/".format(dir_name, 'employee_mapping_sheet')

    paths = os.path.join(os.path.dirname(dir_name), venv_path, "lib", "site-packages")
    spec_path = os.environ['BIN_DIR']
    dist_path = os.environ['BIN_DIR']
    pyinstaller_path = os.path.join(venv_path, "Scripts", "pyinstaller.exe")
    if not os.path.exists(pyinstaller_path):
        print("Please install pyinstaller")
    cmd = [pyinstaller_path,
           "main.py",
           "--onefile",
           "--paths", paths,
           "--log-level", "DEBUG",
           "--name", name,
           "--add-data", data1,
           "--add-data", data2,
           "--specpath", spec_path,
           "--distpath", dist_path,
           "--icon", icon,
           "--clean"]
    print(cmd)
    run_cmd(cmd)


def run_cmd(cmd):
    proc = subprocess.Popen(cmd, shell=True, universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    for line in proc.stdout:
        sys.stdout.write(line)
        sys.stdout.flush()
    proc.wait()
    return proc.returncode


if __name__ == "__main__":
    configure_environment(depth=1)
    python_path = sys.executable
    venv_path = str(Path(python_path).parents[1])
    application_name, application_version = get_version()
    main(venv_path, application_name, application_version)
    #main(venv_path, "".join(application_name)+".exe")
