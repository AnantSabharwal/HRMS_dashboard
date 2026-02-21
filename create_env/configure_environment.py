import logging
import os.path

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(name)s %(message)s')
logger = logging.getLogger(__name__)


def log_env_variable_creation(var):
    logger.info("Environment variable {} created for {}".format(os.environ[var], var))


def configure_environment(depth=2):
    depth_path = ""
    for level in range(0, depth):
        depth_path += r"../"

        source_path = os.path.abspath(depth_path + "../")
        bin_path = os.path.abspath(depth_path + "Bin")
        install_path = os.path.abspath(depth_path + "Installers")
        zipped_path = os.path.abspath(depth_path + "Zipped")

        src_env_var_name = "SRC_DIR"
        bin_env_var_name = "BIN_DIR"
        installer_env_var_name = "INSTALL_DIR"
        zipped_env_var_name = "ZIPPED_DIR"

        os.environ[src_env_var_name] = source_path
        os.environ[bin_env_var_name] = bin_path
        os.environ[installer_env_var_name] = install_path
        os.environ[zipped_env_var_name] = zipped_path

        log_env_variable_creation(src_env_var_name)
        log_env_variable_creation(bin_env_var_name)
        log_env_variable_creation(installer_env_var_name)
        log_env_variable_creation(zipped_env_var_name)

        if not os.path.exists(bin_path):
            os.makedirs(bin_path)

        if not os.path.exists(install_path):
            os.makedirs(install_path)

        if not os.path.exists(zipped_path):
            os.makedirs(zipped_path)
