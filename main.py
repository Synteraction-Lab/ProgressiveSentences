import logging
import uvicorn
import sys
import os
import subprocess
import platform
import threading
from datetime import datetime
from utilities.git_utility import get_git_branch
from backend.backend import app


def start_logger():
    today = datetime.today()
    today_string = today.strftime('%Y%m%d')

    logging.basicConfig(
        filename=f'system-{today_string}.log',
        filemode='a',
        format='%(asctime)s - %(levelname)s - %(message)s',
        level=logging.DEBUG
    )
    _logger = logging.getLogger()
    _logger.info("Starting backend server: %s" % get_git_branch())
    return _logger


def run_backend(logger):
    try:
        logger.info("Running backend server...")
        uvicorn.run(app, host="0.0.0.0", port=8000)
    except Exception as e:
        logger.error(f"Exception occurred while running the backend server: {str(e)}")


def run_frontend(logger):
    original_dir = os.getcwd()
    try:
        frontend_dir = os.path.abspath(os.path.join(original_dir, 'frontend'))
        os.chdir(frontend_dir)

        npm_command = 'npm'
        if platform.system() == 'Windows':
            npm_command = 'npm.cmd'

        logger.info("Running frontend server...")
        subprocess.run([npm_command, 'run', 'dev'], check=True)
    except Exception as e:
        logger.error(f"Exception occurred while running the frontend server: {str(e)}")
    finally:
        os.chdir(original_dir)


if __name__ == "__main__":
    logger = start_logger()

    backend_thread = threading.Thread(target=run_backend, args=(logger,), daemon=True)
    frontend_thread = threading.Thread(target=run_frontend, args=(logger,), daemon=True)

    backend_thread.start()
    frontend_thread.start()

    backend_thread.join()
    frontend_thread.join()
