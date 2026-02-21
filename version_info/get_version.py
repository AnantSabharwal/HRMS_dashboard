import os
import platform
import sys

from configparser import ConfigParser


def read_config_file(filepath):
    parser = ConfigParser()
    parser.read(filepath)
    config = {}
    config.clear()
    for section_name in parser.sections():
        config[section_name] = {}
        for name, value in parser.items(section_name):
            config[section_name][name] = value
    return config


def get_version():
    version = read_config_file(os.path.join(os.path.dirname(os.path.realpath(__file__)), "version.ini"))
    VERSION = version["VersionInfo"]["version"]
    SUB_VERSION = version["VersionInfo"]["sub_version"]
    application_name = "Company Name Report Master"
    architecture_info = platform.architecture()
    architecture_bits = architecture_info[0].replace("bit", "") if architecture_info else "Unknown"
    application_version = "{}.{}.{}({})".format(VERSION, sys.version_info.major, SUB_VERSION, architecture_bits)
    return application_name, application_version
