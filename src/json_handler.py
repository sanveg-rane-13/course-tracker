"""
Module to handle json read and write
Author:
    Sanveg Rane
"""
import json
import logging as logger


def read_json(file_path):
    """
    Read json object from the file
    Args:
        file_path: Path of the json file, eg. path-to-file/file-name.json

    Returns:
        Json object retrieved from the file
    """
    with open(file_path, mode="r", encoding="UTF-8") as json_file:
        data = json.load(json_file)

    return data


def write_json(data, file_path):
    """
    Write an object of dict type to a file
    Args:
        data: Dict object to be saved to a file
        file_path: Location of the file eg. Drive:/loc_to_file/file_name
    """
    with open(file_path, mode="w", encoding="UTF-8") as json_file:
        json.dump(data, json_file)
        logger.debug("Success writing data to: {}".format(file_path))
