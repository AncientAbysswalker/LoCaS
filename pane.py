# -*- coding: utf-8 -*-
"""This module defines panes - master panels that act as direct children of the progenitor frame"""

import wx

import login
import tab
import fn_path


class PaneMain(wx.Panel):
    """Master pane that contains the normal operational widgets for the application

        Class Variables:
            bar_size (int): Size (height) of the top ribbon with the searchbar

        Args:
            parent (ptr): Reference to the wx.object this panel belongs to

        Attributes:
            parent (ptr): Reference to the wx.object this panel belongs to
    """

    bar_size = 25

    def __init__(self, parent):
        """Constructor"""
        wx.Panel.__init__(self, parent)
        self.SetDoubleBuffered(True)  # Remove odd effects at main switch to this pane after login

        self.parent = parent

        # Search bar and bind
        self.wgt_searchbar = wx.TextCtrl(self,
                                         size=(PaneMain.bar_size*10, PaneMain.bar_size),
                                         style=wx.TE_PROCESS_ENTER)
        self.wgt_searchbar.Bind(wx.EVT_TEXT_ENTER, self.evt_search)

        # Search bar button and bind
        btn_search = wx.BitmapButton(self,
                                     bitmap=wx.Bitmap(fn_path.concat_gui('search.png')),
                                     size=(PaneMain.bar_size, ) * 2)
        btn_search.Bind(wx.EVT_BUTTON, self.evt_search)
        btn_search.Bind(wx.EVT_SET_FOCUS, self.evt_button_no_focus)

        # Notebook widget
        self.wgt_notebook = tab.Notebook(self)

        # Top bar sizer
        szr_bar = wx.BoxSizer(wx.HORIZONTAL)
        szr_bar.AddSpacer(3)
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

    def evt_button_no_focus(self, event):
        """Prevents focus from being called on the buttons

            Args:
                event: A focus event
        """
        pass

    def evt_search(self, *args):
        """Search for a part number and call open_parts_tab before emptying the searchbar

            Args:
                args[0]: Either None or a button click event
        """

        # Ensure there is something in the search bar before searching
        if self.wgt_searchbar.GetValue().strip():
            self.wgt_notebook.open_parts_tab(self.wgt_searchbar.GetValue())

        # Empty the searchbar
        self.wgt_searchbar.SetValue("")


class PaneLogin(wx.Panel):
    """Master pane that deals with login behaviour for the application.

        Args:
            parent (ptr): Reference to the wx.object this panel belongs to
            sizer_landing (ptr): Reference to the sizer (of the parent) the landing pane belongs to
            pane_landing (ptr): Reference to the landing pane

        Attributes:
            parent (ptr): Reference to the wx.object this panel belongs to
    """

    def __init__(self, parent, sizer_landing, pane_landing):
        """Constructor"""
        wx.Panel.__init__(self, parent)
        self.SetDoubleBuffered(True)  # Remove slight strobing on failed login

        self.parent = parent

        # Widget that controls user login auth - currently set to debug (no auth) for testing and dev
        login_panel = login.LoginDebug(self, sizer_landing, pane_landing)

        # Main Sizer
        sizer_main = wx.BoxSizer(wx.VERTICAL)
        sizer_main.AddStretchSpacer()
        sizer_main.Add(login_panel, flag=wx.CENTER)
        sizer_main.AddStretchSpacer()

        # Set main sizer
        self.SetSizer(sizer_main)
