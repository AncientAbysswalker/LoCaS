# -*- coding: utf-8 -*-
"""This module contains functions for determining path to files for the other modules."""

import config
import os

import mode

def part_to_dir(pn):
    dir1, temp = pn.split('-')
    dir2 = temp[:2]
    dir3 = temp[2:]
    return [dir1, dir2, dir3]


def concat_img(part, file):
    return os.path.join(config.cfg["img_archive"], 'img', *part_to_dir(part), file)


def concat_gui(file):
    if not mode.frozen:
        return os.path.join(config.cfg["img_archive"], 'img', 'gui', file)
    else:
        return os.path.join(mode.app_root, 'img', 'gui', file)