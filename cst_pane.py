# -*- coding: utf-8 -*-
"""This module defines panes - master panels that act as direct children of the progenitor frame"""

import wx

import login
import tabs
import fn_path


class MainPane(wx.Panel):
    """Master pane that contains the tabbed data panels

            Args:
                parent (ptr): Reference to the wx.object this panel belongs to

            Attributes:
                parent (ptr): Reference to the wx.object this panel belongs to
    """

    def __init__(self, parent, *args, **kwargs):
        """Constructor"""
        wx.Panel.__init__(self, parent, *args, **kwargs)

        self.parent = parent

        # Widgets
        #wgt_txt_searchbar = wx.StaticText(self, label="Search Part Numbers:")
        self.wgt_searchbar = wx.TextCtrl(self, value="", size=(250, 25), style=wx.TE_PROCESS_ENTER)
        btn_search = wx.BitmapButton(self, bitmap=wx.Bitmap(fn_path.concat_gui('search2.png')), size=(25, 25))
        btn_search.Bind(wx.EVT_BUTTON, self.event_search)
        btn_search.Bind(wx.EVT_SET_FOCUS, self.event_button_no_focus)
        self.wgt_notebook = tabs.InterfaceTabs(self)

        # Searchbar Bind
        self.wgt_searchbar.Bind(wx.EVT_TEXT_ENTER, self.event_search)
        btn_search.Bind(wx.EVT_BUTTON, self.event_search)
        btn_search.Bind(wx.EVT_SET_FOCUS, self.event_button_no_focus)

        # Bar Sizer
        szr_bar = wx.BoxSizer(wx.HORIZONTAL)
        szr_bar.AddSpacer(5)
        #szr_bar.Add(wgt_txt_searchbar, flag=wx.EXPAND)
        #szr_bar.AddSpacer(2)
        szr_bar.Add(self.wgt_searchbar)
        szr_bar.AddSpacer(2)
        szr_bar.Add(btn_search)

        # Main Sizer
        self.szr_main = wx.BoxSizer(wx.VERTICAL)
        self.szr_main.Add(szr_bar, flag=wx.EXPAND)
        self.szr_main.AddSpacer(1)
        self.szr_main.Add(wx.StaticLine(self, style=wx.LI_HORIZONTAL), flag=wx.EXPAND)
        self.szr_main.Add(self.wgt_notebook, proportion=1, flag=wx.EXPAND)

        self.SetSizer(self.szr_main)

    def event_button_no_focus(self, event):
        """Prevents focus from being called on the buttons"""
        pass

    def event_search(self, *args):
        """Search for a part number"""
        self.wgt_notebook.open_parts_tab(self.wgt_searchbar.GetValue())
        self.wgt_searchbar.SetValue("")


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
