# -*- coding: utf-8 -*-
"""Main Interface Window and Application Launch"""

import sys

from dialog import *
from cst_pane import *

# Temporary bootstrap for 'current directory' files
if getattr(sys, 'frozen', False):
    app_root = sys._MEIPASS
    fn_path.frozen = True
    fn_path.app_root = app_root
else:
    app_root = os.path.dirname(os.path.abspath(__file__))
    fn_path.frozen = False
config.app_root = app_root


class InterfaceWindow(wx.Frame):
    """Base class for dialogs to display images relating to part. This class should not be called externally."""

    def __init__(self, *args, **kwargs):
        """Constructor"""
        wx.Frame.__init__(self, *args, **kwargs)

        self.sizer_login = wx.BoxSizer(wx.VERTICAL)
        self.sizer_parts = wx.BoxSizer(wx.VERTICAL)

        self.pane_parts = MainPane(self)
        self.pane_parts.Hide()
        self.sizer_parts.Add(self.pane_parts, proportion=1, flag=wx.EXPAND)

        self.pane_login = LoginPane(self, self.sizer_parts, self.pane_parts)

        self.sizer_login.Add(self.pane_login, proportion=1, flag=wx.EXPAND)

        self.status = self.CreateStatusBar() #???Bottom bar

        self.menubar = wx.MenuBar()
        menu_file = wx.Menu()
        menu_edit = wx.Menu()
        menu_help = wx.Menu()
        menu_file.Append(wx.NewId(), "New", "Creates A new file")
        buttonfish = menu_file.Append(wx.NewId(), "ADID", "Yo")
        self.Bind(wx.EVT_MENU, self.onAdd, buttonfish)
        self.menubar.Append(menu_file, "File")
        self.menubar.Append(menu_edit, "Edit")
        self.menubar.Append(menu_help, "Help")
        self.SetMenuBar(self.menubar)

        self.SetMinSize((700, 500))
        self.SetSizer(self.sizer_login)
        self.Show()

    def onAdd(self, event):
        del self.pane_login
        self.pane_login = MainPane(self)
        #self.panel.notebook.fuck("fuck")
        #PANELS.append("rrr")
        #print("sdgsrg")


if __name__ == '__main__':
    """Launch the application."""

    build = "1.0.0"
    app = wx.App(False)
    config.load_config(app)

    if getattr(sys, 'frozen', False):
        config.cfg["db_location"] = os.path.join(os.getcwd(), 'LoCaS.sqlite')
        config.cfg["img_archive"] = os.getcwd()

    #app = wx.App(False)
    win = InterfaceWindow(None, size=(1200, 600))
    win.SetTitle("LoCaS - Build " + build)
    app.MainLoop()
