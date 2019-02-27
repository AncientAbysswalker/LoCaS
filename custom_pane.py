# -*- coding: utf-8 -*-
"""This module contains custom dialog boxes to work with the main code base.

Attributes:
    module_level_variable1 (int): Module level variables may be documented in
        either the ``Attributes`` section of the module docstring, or in an
        inline docstring immediately following the variable.

        Either form is acceptable, but the two should not be mixed. Choose
        one convention to document module level variables and be consistent
        with it.
"""

COLORS = ["red", "blue", "black", "yellow", "green"]
NUMBERS = ["{:<6}|{:>25}|{}".format('JA1','23-JAN-2019','moretext for my othershit'), "{:<6}|{:<25}|{}".format('J1','23-J019','moretext for my othershit'), '2', '3', '4']
PANELS = ["107-00107", "G39-00107", "777-00107"]
SUBLIST = ["999-00107", "G39-00107", "767-00107"]
SUPLIST = ["456-00107", "G39-06767", "776-04577"]
DATADIR = r'C:\Users\Ancient Abysswalker\PycharmProjects\LoCaS'

import wx
from custom_panel import *
import login


class InterfacePanel(wx.Panel):
    """Opens a dialog to modify the intended property.

            Args:
                edit_field (ptr): Reference to the wx.object we are editing
                header_text (str, optional): String to display in the dialog header

            Attributes:
                edit_field (ptr): Reference to the wx.object we are editing
                header_text (str): String to display in the dialog header
                orig_field_text (str): Original text to display when editing
    """
    def __init__(self, *args, **kwargs):
        """Constructor"""
        wx.Panel.__init__(self, *args, **kwargs)

        self.textextext = wx.StaticText(self, size=(60, -1), label="WORDSFSBNGJGBNG", style = wx.ALIGN_CENTER)
        self.notebook = InterfaceTabs(self)
#        self.button = wx.Button(self, label="Something else here? Maybe!")

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.textextext, flag=wx.EXPAND)
        self.sizer.Add(self.notebook, proportion=1, flag=wx.EXPAND)
#        self.sizer.Add(self.button, proportion=0)
        self.SetSizer(self.sizer)


class LoginPane(wx.Panel):
    """Opens a dialog to modify the intended property.

            Args:
                edit_field (ptr): Reference to the wx.object we are editing
                header_text (str, optional): String to display in the dialog header

            Attributes:
                edit_field (ptr): Reference to the wx.object we are editing
                header_text (str): String to display in the dialog header
                orig_field_text (str): Original text to display when editing
    """
    def __init__(self, parent, sizer_landing, pane_landing, *args, **kwargs):
        """Constructor"""
        wx.Panel.__init__(self, parent, *args, **kwargs)
        self.SetDoubleBuffered(True)  # Remove slight strobing on failed login

        self.parent = parent

        login_panel = login.LoginCrypto(self, sizer_landing, pane_landing)

        # Main Sizer
        sizer_main = wx.BoxSizer(wx.VERTICAL)
        sizer_main.AddStretchSpacer()
        sizer_main.Add(login_panel, flag=wx.CENTER)
        sizer_main.AddStretchSpacer()

        self.SetSizer(sizer_main)
