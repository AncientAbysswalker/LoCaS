# -*- coding: utf-8 -*-
"""This module contains functions for determining path to files for the other modules."""

import config
import os

def part_to_dir(pn):
    dir1, temp = pn.split('-')
    dir2 = temp[:2]
    dir3 = temp[2:]
    return [dir1, dir2, dir3]


def concat_img(part, file):
    return os.path.join(config.img_archive, 'img', *part_to_dir(part), file)


def concat_gui(file):
    return os.path.join(config.img_archive, 'img', 'gui', file)