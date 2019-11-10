# -*- coding: utf-8 -*-
"""This module contains functions for determining path to files for the other modules."""

import config
import os

import mode


def part_to_dir(part_num):
    """Convert a part number to a directory structure - TODO: Implement config variable to REGEX here

        Args:
            part_num (str): The part number to convert to a directory list

        Returns:
            (list: str): List of string names of folders, to be concatenated together using os.path.join()
    """

    dir1, temp = part_num.split('-')
    dir2 = temp[:2]
    dir3 = temp[2:]
    return [dir1, dir2, dir3]


def concat_img(part_num, file):
    """Convert a part number and image name into an expected path to that image in the image database

        Args:
            part_num (str): The part number to convert to a directory list
            file (str): Image filename

        Returns:
            (str): A string which represents the concatenated path the indicated image file
    """

    return os.path.join(config.cfg["img_archive"], *part_to_dir(part_num), file)


def concat_gui(file):
    """Convert a GUI image name into an expected path to that GUI image element

        Args:
            file (str): Image filename

        Returns:
            (str): A string which represents the concatenated path the indicated GUI image element
    """

    return os.path.join(mode.app_root, 'img', 'gui', file)