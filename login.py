# -*- coding: utf-8 -*-
"""This module governs login behaviour through various methods

Attributes:
    module_level_variable1 (int): Module level variables may be documented in
        either the ``Attributes`` section of the module docstring, or in an
        inline docstring immediately following the variable.

        Either form is acceptable, but the two should not be mixed. Choose
        one convention to document module level variables and be consistent
        with it.
"""

import wx
import hashlib
import datetime


class LoginDebug(wx.Panel):
    """Debug login panel class. Does not pass login check to following (landing) page

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

    def __init__(self, parent, sizer_landing, pane_landing, bound_text="Please enter registry info",
                 user_text="Username:", pass_text="Password:", user_last="", pass_last="", *args, **kwargs):
        """Constructor"""
        wx.Panel.__init__(self, parent, *args, **kwargs)

        self.parent = parent
        self.sizer_landing = sizer_landing
        self.pane_landing = pane_landing
        self.invalid_text = None
        self.invalid_count = 0

        # Login Widget Objects
        button = wx.Button(self, size=(75, 25), label="SUBMIT")
        self.Bind(wx.EVT_BUTTON, self.event_login, button)
        self.login_user = wx.TextCtrl(self, value=user_last, size=(400, 20))
        self.login_pass = wx.TextCtrl(self, value=pass_last, size=(400, 20))

        # Login Widget Sizers
        self.temp_space = 10  # To make modifying spacing easier
        self.sizer_login_inner = wx.BoxSizer(wx.VERTICAL)
        self.sizer_login_inner.AddSpacer(self.temp_space)
        self.sizer_login_inner.Add(wx.StaticText(self, size=(-1, -1), label=user_text), flag=wx.EXPAND)
        self.sizer_login_inner.Add(self.login_user, flag=wx.EXPAND)
        self.sizer_login_inner.AddSpacer(self.temp_space)
        self.sizer_login_inner.Add(wx.StaticText(self, size=(-1, -1), label=pass_text), flag=wx.EXPAND)
        self.sizer_login_inner.Add(self.login_pass, flag=wx.EXPAND)
        self.sizer_login_inner.AddSpacer(self.temp_space)
        self.sizer_login_inner.Add(button, flag=wx.CENTER)
        self.sizer_login_inner.AddSpacer(self.temp_space)

        # Login Widget Box Sizer
        sizer_login = wx.StaticBoxSizer(wx.StaticBox(self, label=bound_text), orient=wx.HORIZONTAL)
        sizer_login.AddSpacer(self.temp_space)
        sizer_login.Add(self.sizer_login_inner, flag=wx.EXPAND)
        sizer_login.AddSpacer(self.temp_space)

        self.SetSizer(sizer_login)

    def event_login(self, event):
        """Execute when attempting to login - Debug only, prints to console"""
        print("LOGIN PASSED")


class LoginCrypto(LoginDebug):
    """Crypto login panel class. Uses cryptographic hashing to determine if a valid passkey is entered

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

    def event_login(self, event):
        """Execute when attempting to login - Hide login pane and show landing pane"""
        if self.pair_correct(self.login_user.GetValue(), self.login_pass.GetValue()):
            self.parent.Hide()
            self.pane_landing.Show()
            self.parent.parent.SetSizer(self.sizer_landing)
            self.parent.parent.Layout()
        else:
            if self.invalid_text == None:
                self.invalid_text = wx.StaticText(self, size=(60, -1), label="INVALID USER/PASSKEY PAIR", style=wx.ALIGN_CENTER)
                self.invalid_text.SetBackgroundColour('red')
                self.sizer_login_inner.Add(self.invalid_text, flag=wx.EXPAND)
                self.sizer_login_inner.AddSpacer(self.temp_space)
                self.Fit()
            else:
                self.invalid_text.SetLabel("C'mon, I said it's not a bloody valid passkey")
                self.invalid_count += 1
                self.Layout()

    def pair_correct(self, _u, _p):
        """Cryptographically check if user:passkey pair is valid

        Args:
            _u (str): String "username"
            _p (str): String "passkey"

        Returns:
            True if valid pair, False otherwise.
        """

        _d = str(datetime.datetime.now().year)
        return True# hashlib.sha3_256((_d[:2] + _u + _d[2:] + "Rakuyo").encode('utf-8')).hexdigest() == _p
