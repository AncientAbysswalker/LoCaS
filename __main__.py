COLORS = ["red", "blue", "black", "yellow", "green"]
NUMBERS = ["{:<6}|{:>25}|{}".format('JA1','23-JAN-2019','moretext for my othershit'), "{:<6}|{:<25}|{}".format('J1','23-J019','moretext for my othershit'), '2', '3', '4']
PANELS = ["107-00107", "G39-00107", "777-00107"]
SUBLIST = ["999-00107", "G39-00107", "767-00107"]
SUPLIST = ["456-00107", "G39-06767", "776-04577"]
DATADIR = r'C:\Users\Ancient Abysswalker\PycharmProjects\LoCaS'

import random
import wx
import sys, os
import wx.lib.agw.flatnotebook as fnb
import wx.lib.agw.ultimatelistctrl as ulc
import wx.lib.scrolledpanel as scrolled
import glob
import config
from math import ceil, floor
from custom_dialog import *
from custom_pane import *
import copy
#from os import path, makedirs, rename

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
    def __init__(self, *args, **kwargs):
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
        first = wx.Menu()
        second = wx.Menu()
        first.Append(wx.NewId(), "New", "Creates A new file")
        buttonfish = first.Append(wx.NewId(), "ADID", "Yo")
        self.Bind(wx.EVT_MENU, self.onAdd, buttonfish)
        self.menubar.Append(first, "File")
        self.menubar.Append(second, "Edit")
        self.SetMenuBar(self.menubar)

        self.SetSizer(self.sizer_login)
        self.Show()

    def onAdd(self, event):
        del self.pane_login
        self.pane_login = MainPane(self)
        #self.panel.notebook.fuck("fuck")
        #PANELS.append("rrr")
        #print("sdgsrg")

if __name__ == '__main__':
    config.load_config()

    if getattr(sys, 'frozen', False):
        config.db_location = os.path.join(os.getcwd(), 'LoCaS.sqlite')
        print("fuckstick", config.db_location)
        config.img_archive = os.getcwd()
        print("fuckstick", config.img_archive)

    app = wx.App(False)
    win = InterfaceWindow(None, size=(1200, 600))
    app.MainLoop()