# -*- coding: utf-8 -*-
"""This module defines login widgets and their associated login behaviours"""

import wx
import hashlib
import datetime


class LoginDebug(wx.Panel):
    """Debug login panel class. Automatically passes login check to following (landing) page

        Args:
            parent (ptr): Reference to the wx.object this panel belongs to
            sizer_landing (ptr): Reference to the sizer (of the parent) the landing pane belongs to
            pane_landing (ptr): Reference to the landing pane
            bound_text (str, optional): String to display in the login panel bounding box
            user_last (str, optional): String to initially display within the "user" textbox
            pass_last (str, optional): String to initially display within the "passkey" textbox
            user_text (str, optional): String to display preceding the "user" textbox
            pass_text (str, optional): String to display preceding the "passkey" textbox

        Attributes:
            parent (ptr): Reference to the wx.object this panel belongs to
            szr_landing (ptr): Reference to the sizer (of the parent) the landing pane belongs to
            pane_landing (ptr): Reference to the landing pane
            wgt_txt_login_user (ptr): Reference to the "user" textbox
            wgt_txt_login_pass (ptr): Reference to the "passkey" textbox
    """

    def __init__(self, parent, szr_landing, pane_landing, bound_text="Please enter registry info",
                 user_last="", pass_last="", user_text="Username:", pass_text="Password:"):
        """Constructor"""
        wx.Panel.__init__(self, parent)

        # Variable Definition
        self.parent = parent
        self.szr_landing = szr_landing
        self.pane_landing = pane_landing
        self.invalid_text = None
        self.invalid_count = 0

        # Login Widget Objects
        btn_submit = wx.Button(self, size=(75, 25), label="SUBMIT")
        self.Bind(wx.EVT_BUTTON, self.evt_login, btn_submit)
        self.wgt_txt_login_user = wx.TextCtrl(self, value=user_last, size=(400, 20))
        self.wgt_txt_login_pass = wx.TextCtrl(self, value=pass_last, size=(400, 20))

        # Login Widget Sizers
        self.temp_space = 10  # To make modifying spacing easier
        self.szr_login_inner = wx.BoxSizer(wx.VERTICAL)
        self.szr_login_inner.AddSpacer(self.temp_space)
        self.szr_login_inner.Add(wx.StaticText(self, label=user_text), flag=wx.EXPAND)
        self.szr_login_inner.Add(self.wgt_txt_login_user, flag=wx.EXPAND)
        self.szr_login_inner.AddSpacer(self.temp_space)
        self.szr_login_inner.Add(wx.StaticText(self, label=pass_text), flag=wx.EXPAND)
        self.szr_login_inner.Add(self.wgt_txt_login_pass, flag=wx.EXPAND)
        self.szr_login_inner.AddSpacer(self.temp_space)
        self.szr_login_inner.Add(btn_submit, flag=wx.CENTER)
        self.szr_login_inner.AddSpacer(self.temp_space)

        # Login Widget Box Sizer
        szr_login = wx.StaticBoxSizer(wx.StaticBox(self, label=bound_text), orient=wx.HORIZONTAL)
        szr_login.AddSpacer(self.temp_space)
        szr_login.Add(self.szr_login_inner, flag=wx.EXPAND)
        szr_login.AddSpacer(self.temp_space)

        # Set main sizer
        self.SetSizer(szr_login)

    def evt_login(self, event):
        """Execute when attempting to login - Always hides login pane and shows landing pane

            Args:
                event: A button click event
        """

        # Hide current pane, show PaneMain, then reset the active sizer and call Layout()
        self.parent.Hide()
        self.pane_landing.Show()
        self.parent.parent.SetSizer(self.szr_landing)
        self.parent.parent.Layout()


class LoginCrypto(LoginDebug):
    """Crypto login panel class. Uses cryptographic hashing to determine if a valid passkey is entered.

            Args:
                parent (ptr): Reference to the wx.object this panel belongs to
                sizer_landing (ptr): Reference to the sizer (of the parent) the landing pane belongs to
                pane_landing (ptr): Reference to the landing pane
                bound_text (str, optional): String to display in the login panel bounding box
                user_text (str, optional): String to display preceding the "user" textbox
                pass_text (str, optional): String to display preceding the "passkey" textbox
                user_last (str, optional): String to initially display within the "user" textbox
                pass_last (str, optional): String to initially display within the "passkey" textbox

            Attributes:
                parent (ptr): Reference to the wx.object this panel belongs to
                sizer_landing (ptr): Reference to the sizer (of the parent) the landing pane belongs to
                pane_landing (ptr): Reference to the landing pane
                login_user (ptr): Reference to the "user" textbox
                login_pass (ptr): Reference to the "passkey" textbox
    """

    def evt_login(self, event):
        """Execute when attempting to login - Hide login pane and show landing pane if cryptographically correct

            Args:
                event: A button click event
        """
        if self.pair_correct(self.wgt_txt_login_user.GetValue(), self.wgt_txt_login_pass.GetValue()):
            self.parent.Hide()
            self.pane_landing.Show()
            self.parent.parent.SetSizer(self.szr_landing)
            self.parent.parent.Layout()
        else:
            if self.invalid_text == None:
                self.invalid_text = wx.StaticText(self, size=(60, -1), label="INVALID USER/PASSKEY PAIR", style=wx.ALIGN_CENTER)
                self.invalid_text.SetBackgroundColour('red')
                self.szr_login_inner.Add(self.invalid_text, flag=wx.EXPAND)
                self.szr_login_inner.AddSpacer(self.temp_space)
                self.Fit()
            else:
                self.invalid_text.SetLabel("C'mon, I said it's not a bloody valid passkey")
                self.invalid_count += 1
                self.Layout()

    def pair_correct(self, _u, _p):
        """Cryptographically check if user:passkey pair is valid based on year

        Args:
            _u (str): String "username"
            _p (str): String "passkey"

        Returns:
            True if valid pair, False otherwise.
        """

        _d = str(datetime.datetime.now().year)
        return hashlib.sha3_256((_d[:2] + _u + _d[2:] + "Rakuyo").encode('utf-8')).hexdigest() == _p
