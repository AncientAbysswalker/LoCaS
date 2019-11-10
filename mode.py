# -*- coding: utf-8 -*-
"""Controls only two variables, handling the development vs build state of the application. This is set at the time of
build, and can reference either to this local folder, or to the temporary folder when files are bundled to the .exe

    Attributes:
        frozen (bool): Whether the application should run in dev or build mode. True indicates build mode
        mode.app_root (int, int, int): Path to the application files
"""

import os
import sys

# Read the state of whether the app is frozen for build and what the mode.app_root is
def set_mode(is_frozen):
    print(is_frozen)
    globals()['app_root'] = sys._MEIPASS if is_frozen else os.path.dirname(os.path.abspath(__file__))
    globals()['frozen'] = is_frozen