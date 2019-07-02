# -*- coding: utf-8 -*-
"""This module defines panes - master panels that act as direct children of the progenitor frame"""

import wx
import login
import custom_panel


class MainPane(wx.Panel):
    """Master pane that deals with login behaviour for the application.

            Args:
                parent (ptr): Reference to the wx.object this panel belongs to

            Attributes:
                parent (ptr): Reference to the wx.object this panel belongs to
    """

    def __init__(self, parent, *args, **kwargs):
        """Constructor"""
        wx.Panel.__init__(self, parent, *args, **kwargs)

        self.parent = parent
        #self.textextext = wx.StaticText(self, size=(60, -1), label="WORDSFSBNGJGBNG", style = wx.ALIGN_CENTER)
        self.notebook = custom_panel.InterfaceTabs(self)

        # Main Sizer
        self.sizer_main = wx.BoxSizer(wx.VERTICAL)
        #self.sizer_main.Add(self.textextext, flag=wx.EXPAND)
        self.sizer_main.Add(self.notebook, proportion=1, flag=wx.EXPAND)

        self.SetSizer(self.sizer_main)


class LoginPane(wx.Panel):
    """Master pane that deals with login behaviour for the application.

            Args:
                parent (ptr): Reference to the wx.object this panel belongs to
                sizer_landing (ptr): Reference to the sizer (of the parent) the landing pane belongs to
                pane_landing (ptr): Reference to the landing pane

            Attributes:
                parent (ptr): Reference to the wx.object this panel belongs to
    """

    def __init__(self, parent, sizer_landing, pane_landing, *args, **kwargs):
        """Constructor"""
        wx.Panel.__init__(self, parent, *args, **kwargs)

        self.SetDoubleBuffered(True)  # Remove slight strobing on failed login

        self.parent = parent
        login_panel = login.LoginDebug(self, sizer_landing, pane_landing)

        # Main Sizer
        sizer_main = wx.BoxSizer(wx.VERTICAL)
        sizer_main.AddStretchSpacer()
        sizer_main.Add(login_panel, flag=wx.CENTER)
        sizer_main.AddStretchSpacer()

        self.SetSizer(sizer_main)
