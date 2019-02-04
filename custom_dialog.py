# -*- coding: utf-8 -*-
"""This module contains custom dialog boxes for the main code base.

Attributes:
    module_level_variable1 (int): Module level variables may be documented in
        either the ``Attributes`` section of the module docstring, or in an
        inline docstring immediately following the variable.

        Either form is acceptable, but the two should not be mixed. Choose
        one convention to document module level variables and be consistent
        with it.

Todo:
    * Complete implementation of ImageDialog, along with hook for image index

"""

import wx
import glob


class ModifyFieldDialog(wx.Dialog):
    """Opens a dialog to modify the intended property.

        T

        Attributes:
            part_number: A boolean indicating if we like SPAM or not.
            field_name: An integer count of the eggs we have laid.
            edit_field
        """

    def __init__(self, part_number, field_name, edit_field, *args, **kw):
        super(ModifyFieldDialog, self).__init__(*args, **kw)

        self.part_number = part_number
        self.field_name = field_name
        self.edit_field = edit_field

        self.InitUI()
        self.SetSize((500, 160)) #NEEDS FINESSE FOR TYPE OF PASS!
        self.SetTitle('Editing {0} of part {1}'.format(self.field_name, self.part_number))


    def InitUI(self):

        pnl = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)

        sb = wx.StaticBox(pnl, label='Editing {0} of part {1}'.format(self.field_name, self.part_number))
        sbs = wx.StaticBoxSizer(sb, orient=wx.VERTICAL)

        self.importanttextbox=wx.TextCtrl(pnl, value = self.edit_field.GetLabel())

        sbs.Add(self.importanttextbox, flag=wx.ALL | wx.EXPAND, border=5)

        pnl.SetSizer(sbs)

        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        ok_button = wx.Button(self, label='Commit')
        close_button = wx.Button(self, label='Cancel')
        hbox2.Add(ok_button)
        hbox2.Add(close_button, flag=wx.LEFT, border=5)

        vbox.Add(pnl, proportion=1,
            flag=wx.ALL|wx.EXPAND, border=5)
        vbox.Add(hbox2, flag=wx.ALIGN_CENTER|wx.TOP|wx.BOTTOM, border=10)

        self.SetSizer(vbox)

        ok_button.Bind(wx.EVT_BUTTON, self.OnCommit)
        close_button.Bind(wx.EVT_BUTTON, self.OnCancel)
        #ok_button.Bind(wx.EVT_BUTTON, lambda event: self.OnClose(event))

    def OnCommit(self, e):
        self.edit_field.SetLabel(self.importanttextbox.GetValue())
        self.Destroy()

    def OnCancel(self, e):
        self.Destroy()


class ImageDialog(wx.Dialog):
    """Opens a dialog to modify the intended property.

        T

        Attributes:
            part_number: A boolean indicating if we like SPAM or not.
            field_name: An integer count of the eggs we have laid.
            edit_field
        """

    def __init__(self, image, *args, **kw):
        super(ImageDialog, self).__init__(*args, **kw)

        #self.image = event.GetEventObject()
        print(image)

        self.InitUI(image)
        self.SetSize((500, 160))
        #self.SetTitle('Editing {0} of part {1}'.format(self.field_name, self.part_number))


    def InitUI(self, image):

        pnl = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)

        _tmp_image = wx.Image(image, wx.BITMAP_TYPE_ANY)
        _tmp_height = _tmp_image.GetHeight()

        _tmp_height2 = min(_tmp_image.GetHeight(), 250)
        _tmp_width2 = (_tmp_height2 / _tmp_height2) * _tmp_image.GetWidth()

        imageBitmap = wx.StaticBitmap(self, wx.ID_ANY, wx.Bitmap(_tmp_image.Scale(_tmp_width2, _tmp_height2)))

        vbox.Add(imageBitmap, border=5, flag=wx.ALL)
        #
        # sb = wx.StaticBox(pnl, label='Editing {0} of part {1}'.format(self.field_name, self.part_number))
        # sbs = wx.StaticBoxSizer(sb, orient=wx.VERTICAL)
        #
        # self.importanttextbox=wx.TextCtrl(pnl, value = self.edit_field.GetLabel())
        #
        # sbs.Add(self.importanttextbox, flag=wx.ALL | wx.EXPAND, border=5)
        #
        # pnl.SetSizer(sbs)
        #
        # hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        # ok_button = wx.Button(self, label='Commit')
        # close_button = wx.Button(self, label='Cancel')
        # hbox2.Add(ok_button)
        # hbox2.Add(close_button, flag=wx.LEFT, border=5)
        #
        # vbox.Add(pnl, proportion=1,
        #     flag=wx.ALL|wx.EXPAND, border=5)
        # vbox.Add(hbox2, flag=wx.ALIGN_CENTER|wx.TOP|wx.BOTTOM, border=10)
        #
        # self.SetSizer(vbox)
        #
        # ok_button.Bind(wx.EVT_BUTTON, self.OnCommit)
        # close_button.Bind(wx.EVT_BUTTON, self.OnCancel)
        #ok_button.Bind(wx.EVT_BUTTON, lambda event: self.OnClose(event))

    def OnCommit(self, e):
        self.edit_field.SetLabel(self.importanttextbox.GetValue())
        self.Destroy()

    def OnCancel(self, e):
        self.Destroy()