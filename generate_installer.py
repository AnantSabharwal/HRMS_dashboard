import mimetypes
import subprocess
import sys
import logging

logging.getLogger("Generate installer")


def main():
    logging.info("Starting installer creation")
    mimetypes.init()
    cmd = ['iscc', '/F', 'inno_setup.iss']
    logging.info("Running inno setup")
    cmd_lines = subprocess.Popen(cmd, shell=True, universal_newlines=True, stdout=subprocess.PIPE,
                                 stderr=subprocess.STDOUT)

    for line in cmd_lines.stdout:
        sys.stdout.write(line)
        sys.stdout.flush()
    cmd_lines.wait()
