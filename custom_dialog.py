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
import os


class ModifyFieldDialog(wx.Dialog):
    """Opens a dialog to modify the intended property.

        Attributes:
            header_text: String to display in the dialog header
            edit_field: Reference to the wx.object we are editing
            self.orig_field_text: Original text to display when editing
    """

    def __init__(self, edit_field, header_text="", *args, **kw):
        """Initializes ModifyFieldDialog with given arguments"""
        super(ModifyFieldDialog, self).__init__(None, *args, **kw)

        self.header_text = header_text
        self.edit_field = edit_field
        self.orig_field_text = self.edit_field.GetLabel()

        self.InitUI()
        self.SetSize((500, 160)) #NEEDS FINESSE FOR TYPE OF PASS!
        self.SetTitle(self.header_text)


    def InitUI(self):
        """Draw the UI for the modification dialog"""
        pnl = wx.Panel(self)
        sizer_vertical = wx.BoxSizer(wx.VERTICAL)

        sb = wx.StaticBox(pnl, label=self.header_text)
        sbs = wx.StaticBoxSizer(sb, orient=wx.VERTICAL)

        self.importanttextbox = wx.TextCtrl(pnl, value=self.orig_field_text)

        sbs.Add(self.importanttextbox, flag=wx.ALL | wx.EXPAND, border=5)

        pnl.SetSizer(sbs)

        sizer_buttons = wx.BoxSizer(wx.HORIZONTAL)
        ok_button = wx.Button(self, label='Commit')
        close_button = wx.Button(self, label='Cancel')
        sizer_buttons.Add(ok_button)
        sizer_buttons.Add(close_button, flag=wx.LEFT, border=5)

        sizer_vertical.Add(pnl, proportion=1,
            flag=wx.ALL|wx.EXPAND, border=5)
        sizer_vertical.Add(sizer_buttons, flag=wx.ALIGN_CENTER|wx.TOP|wx.BOTTOM, border=10)

        self.SetSizer(sizer_vertical)

        ok_button.Bind(wx.EVT_BUTTON, self.OnCommit)
        close_button.Bind(wx.EVT_BUTTON, self.OnCancel)
        #LAMBDA BINDING ok_button.Bind(wx.EVT_BUTTON, lambda event: self.OnClose(event))

    def OnCommit(self, e):
        """Execute when committing a change"""
        _rewrite_value = self.importanttextbox.GetValue()
        _original_value = self.edit_field.GetLabel()
        self.edit_field.SetLabel(_rewrite_value)

        self.Destroy()

    def OnCancel(self, e):
        """Execute when cancelling a change"""
        self.Destroy()


class ModifyImageCommentDialog(ModifyFieldDialog):
    """Opens a dialog to modify an image comment.

        Attributes:
            header_text: String to display in the dialog header
            edit_field: Reference to the wx.object we are editing
            comment_key: Key in the image:comment dict
            comment_path: Path of the image:comment dict file
            self.orig_field_text: Original text to display when editing
    """

    def __init__(self, edit_field, comment_key, comment_path, header_text="", *args, **kw):
        """Initializes ModifyFieldDialog with given arguments"""
        super(ModifyFieldDialog, self).__init__(None, *args, **kw)

        self.header_text = header_text
        self.edit_field = edit_field
        self.comment_key = comment_key
        self.comment_path = comment_path

        self.orig_field_text = self.edit_field.GetLabel()
        if self.orig_field_text == "There is no comment recorded":
            self.orig_field_text = ""

        self.InitUI()
        self.SetSize((500, 160)) #NEEDS FINESSE FOR TYPE OF PASS!
        self.SetTitle(self.header_text)

    def OnCommit(self, e):
        """Execute when committing a change"""
        _original_value = self.edit_field.GetLabel()
        _rewrite_value = self.importanttextbox.GetValue()
        self.edit_field.SetLabel(_rewrite_value)

        _temp = open(self.comment_path).read()
        _check = _temp.find(self.comment_key + '<' + chr(00) + '>')
        if _check != -1:
            _start = _check + len(self.comment_key) + 3
            _end = _temp.find(_original_value) + len(_original_value)
            _temp = _temp[:_start] + _rewrite_value + _temp[_end:]

            with  open(self.comment_path, 'w') as comfile:
                comfile.write(_temp)
        else:
            _temp += '\n' + chr(00) + '\n' + self.comment_key + '<' + chr(00) + '>' + _rewrite_value

            with  open(self.comment_path, 'w') as comfile:
                comfile.write(_temp)

        self.Destroy()


class ImageDialog(wx.Dialog):
    """Opens a dialog to show a selected image

        Attributes:
            part_number: A boolean indicating if we like SPAM or not.
            field_name: An integer count of the eggs we have laid.
            edit_field
    """

    def __init__(self, imagelist, index, compath, *args, **kw):
        super(ImageDialog, self).__init__(None, *args, **kw)

        self.SetSize((500, 400))
        self.imagelist = imagelist
        self.index = index
        self.compath = compath
        self.comments = {}
        try:
            with open(self.compath) as comfile:
                _entries = comfile.read().split('\n' + chr(00) + '\n')
                for entry in _entries:
                    _name, _comment = entry.split('<' + chr(00) + '>')
                    self.comments[_name] = _comment
        except FileNotFoundError:
            pass

        print(self.comments)

        self.InitUI()

    def InitUI(self):
        pnl = wx.Panel(self)

        #Set image comment
        self.comment_text = wx.StaticText(self, size=(60, 60), label="There is no comment recorded", style=wx.ALIGN_CENTER)
        try:
            self.comment_text.SetLabel(self.comments[os.path.split(self.imagelist[self.index])[1]])
        except KeyError:
            pass

        self.sizer_main = wx.BoxSizer(wx.VERTICAL)
        sizer_controls = wx.BoxSizer(wx.HORIZONTAL)

        _tmp_image = wx.Image(self.imagelist[self.index], wx.BITMAP_TYPE_ANY)
        _tmp_height = _tmp_image.GetHeight()


        _tmp_height2 = min(_tmp_image.GetHeight(), 250)
        _tmp_width2 = (_tmp_height2 / _tmp_height) * _tmp_image.GetWidth()

        self.imageBitmap = wx.StaticBitmap(self, wx.ID_ANY, wx.Bitmap(_tmp_image.Scale(_tmp_width2, _tmp_height2)))

        prev_button = wx.BitmapButton(self, wx.ID_ANY, wx.Bitmap(r"C:\Users\Ancient Abysswalker\PycharmProjects\LoCaS\img\gui\l_arr.png", wx.BITMAP_TYPE_ANY), wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW)
        next_button = wx.BitmapButton(self, wx.ID_ANY, wx.Bitmap(r"C:\Users\Ancient Abysswalker\PycharmProjects\LoCaS\img\gui\r_arr.png", wx.BITMAP_TYPE_ANY), wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW)

        sizer_controls.Add(prev_button, border=5, flag=wx.ALL | wx.EXPAND)
        sizer_controls.Add(next_button, border=5, flag=wx.ALL | wx.EXPAND)


        self.sizer_main.Add(self.imageBitmap, border=5, flag=wx.CENTER)
        self.sizer_main.Add(sizer_controls, border=5, flag=wx.ALL | wx.EXPAND)
        self.sizer_main.Add(self.comment_text, proportion=1, border=5, flag=wx.ALL | wx.EXPAND)

        self.SetSizer(self.sizer_main)

        prev_button.Bind(wx.EVT_LEFT_UP, self.prev_image)
        next_button.Bind(wx.EVT_LEFT_UP, self.next_image)
        self.comment_text.Bind(wx.EVT_LEFT_DCLICK, lambda event: self.event_revision(event, ""))

    def OnCommit(self, e):
        self.edit_field.SetLabel(self.importanttextbox.GetValue())
        self.Destroy()

    def OnCancel(self, e):
        self.Destroy()

    def next_image(self, evt):
        if self.index < len(self.imagelist) - 1:
            self.index += 1
            self.imageBitmap.SetBitmap(wx.Bitmap(self.imagelist[self.index], wx.BITMAP_TYPE_ANY))

            ##KHJSBDGUKJNSA
            self.imageBitmap.SetSize(100-10*self.index, 100-10*self.index)

            try:
                self.comment_text.SetLabel(self.comments[os.path.split(self.imagelist[self.index])[1]])
            except KeyError:
                self.comment_text.SetLabel("There is no comment recorded")
                pass

            self.sizer_main.RecalcSizes()
        evt.Skip()

    def prev_image(self, evt):
        if self.index > 0:
            self.index -= 1
            self.imageBitmap.SetBitmap(wx.Bitmap(self.imagelist[self.index], wx.BITMAP_TYPE_ANY))

            ##KHJSBDGUKJNSA
            self.imageBitmap.SetSize(10, 10)

            try:
                self.comment_text.SetLabel(self.comments[os.path.split(self.imagelist[self.index])[1]])
            except KeyError:
                self.comment_text.SetLabel("There is no comment recorded")
                pass

            self.sizer_main.RecalcSizes()
        evt.Skip()

    def event_revision(self, evt, field):
        dialog=ModifyImageCommentDialog(evt.GetEventObject(), os.path.split(self.imagelist[self.index])[1], self.compath, "Editing image comment")
        dialog.ShowModal()
        dialog.Destroy()
        self.sizer_main.RecalcSizes()
        evt.Skip()