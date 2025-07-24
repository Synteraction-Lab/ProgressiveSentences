# coding=utf-8

import glob
import json
import logging
import os

import pandas as pd
from pathlib import Path

_CREDENTIAL_DIRECTORY = "credential"


def append_data(file_name, data):
    os.makedirs(os.path.dirname(file_name), exist_ok=True)

    try:
        with open(file_name, "a") as file:
            file.write(data)
        return True
    except Exception:
        logging.exception("Failed to write to %s", file_name)
        return False


def is_yaml_file(file_name):
    return file_name.endswith(".yaml")


def is_file_exists(file_name):
    return os.path.isfile(file_name)


def create_directory(directory):
    try:
        os.makedirs(directory, exist_ok=True)
        return True
    except Exception:
        logging.exception("Failed to create directory: %s", directory)
        return False


# return lines
def read_file(file_name):
    with open(file_name) as f:
        return f.readlines()


def read_json_file(file_name):
    with open(file_name) as f:
        return json.load(f)


def write_data(file_name, data):
    try:
        with open(file_name, "wb") as file:
            file.write(data)
        return True
    except Exception as e:
        logging.exception("Failed to write to %s", file_name)
        return False


# extension: extension with . (e.g. .csv)
def read_file_names(directory, extension, prefix=None):
    all_files_with_extension = [
        file for file in glob.glob(f'{directory}/*{extension}')]
    all_files_with_extension.sort()
    # logging.debug(all_files_with_extension)

    if prefix:
        return [file for file in all_files_with_extension if Path(file).stem.startswith(prefix)]
    else:
        return all_files_with_extension


def get_project_root():
    current_dir = os.path.dirname(os.path.abspath(__file__))

    while not os.path.isfile(os.path.join(current_dir, 'main.py')):
        current_dir = os.path.dirname(current_dir)

    return current_dir


def get_credential_file_path(credential_file_name):
    """
    return the path of the credential file (which is stored in the `credential` folder)
    """
    return os.path.join(get_project_root(), _CREDENTIAL_DIRECTORY, credential_file_name)


def get_audio_file_path(directory, file_name):
    if directory is None:
        return os.path.join(get_project_root(), file_name)

    create_directory(directory)
    return os.path.join(get_project_root(), directory, file_name)


def read_csv(file):
    # Reading the CSV file using pandas
    data = pd.read_csv(file)

    return data


def load_first_column_from_csv(file):
    data = read_csv(file)

    # Extracting the first column
    first_column = data.iloc[:, 0].tolist()

    return first_column


def load_first_second_colum_from_csv(file):
    data = read_csv(file)

    # Extracting the first and second columns
    first_column = data.iloc[:, 0].tolist()
    second_column = data.iloc[:, 1].tolist()

    return first_column, second_column


def write_rows_to_csv(file, data, column_names):
    # Creating a DataFrame from the provided data
    df = pd.DataFrame(data, columns=column_names)

    # Writing the DataFrame to a CSV file
    df.to_csv(file, index=False)


def write_data_to_csv(file, data_with_columns):
    # Creating a DataFrame from the provided data
    df = pd.DataFrame(data_with_columns)

    # Writing the DataFrame to a CSV file
    df.to_csv(file, index=False)


def get_files_with_extension(folder_path, extension):
    """
    Get all files in the specified folder with the given extension.
    """
    files_in_folder = []
    for file_name in os.listdir(folder_path):
        if file_name.endswith(extension):
            files_in_folder.append(file_name)
    return files_in_folder


def compare_files(folder_files, file_list):
    """
    Compare files in the folder with the given list.
    """
    folder_files_set = set(folder_files)
    file_list_set = set(file_list)

    # Files in the folder but not in the list
    extra_in_folder = folder_files_set - file_list_set

    # Files in the list but not in the folder
    missing_in_folder = file_list_set - folder_files_set

    return extra_in_folder, missing_in_folder
