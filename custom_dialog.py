# -*- coding: utf-8 -*-
"""This module defines custom dialog boxes called upon at various instances"""

import wx
# import wx.richtext as wxr
import glob
import os
import pickle
import json
import sqlite3
import hashlib
import shutil

DATADIR = r'C:\Users\Ancient Abysswalker\PycharmProjects\LoCaS'


def part_to_dir(pn):
    dir1, temp = pn.split('-')
    dir2 = temp[:2]
    dir3 = temp[2:]
    return [dir1, dir2, dir3]


class ModifyFieldDialog(wx.Dialog):
    """Opens a dialog to modify the intended property.

        Args:
            edit_field (ptr): Reference to the wx.object we are editing
            header_text (str, optional): String to display in the dialog header

        Attributes:
            edit_field (ptr): Reference to the wx.object we are editing
            header_text (str): String to display in the dialog header
            orig_field_text (str): Original text to display when editing
    """

    def __init__(self, parent, edit_field, header_text="", *args, **kw):
        """Constructor"""
        super(ModifyFieldDialog, self).__init__(None, *args, **kw)

        self.parent = parent

        self.header_text = header_text
        self.edit_field = edit_field
        self.orig_field_text = self.edit_field.GetLabel()

        self.init_dialog()
        self.SetSize((500, 160))
        self.SetTitle(self.header_text)

    def init_dialog(self):
        """Draw the dialog box details - common between subclasses"""

        # Editable box and outline box
        self.editbox = wx.TextCtrl(self, value=self.orig_field_text, style=wx.TE_MULTILINE)
        sizer_editbox = wx.StaticBoxSizer(wx.StaticBox(self, label=self.header_text), orient=wx.VERTICAL)
        sizer_editbox.Add(self.editbox, flag=wx.ALL | wx.EXPAND, border=5)

        # Dialog buttons with binds
        button_commit = wx.Button(self, label='Commit')
        button_commit.Bind(wx.EVT_BUTTON, self.event_commit)
        button_cancel = wx.Button(self, label='Cancel')
        button_cancel.Bind(wx.EVT_BUTTON, self.event_cancel)

        # Dialog button sizer
        sizer_buttons = wx.BoxSizer(wx.HORIZONTAL)
        sizer_buttons.Add(button_commit)
        sizer_buttons.Add(button_cancel, flag=wx.LEFT, border=5)

        # Add everything to master sizer and set sizer for pane
        sizer_master = wx.BoxSizer(wx.VERTICAL)
        sizer_master.Add(sizer_editbox, proportion=1, flag=wx.ALL|wx.EXPAND, border=5)
        sizer_master.Add(sizer_buttons, flag=wx.ALIGN_CENTER|wx.TOP|wx.BOTTOM, border=10)
        self.SetSizer(sizer_master)

        self.Bind(wx.EVT_CLOSE, self.event_close)

    def event_commit(self, event):
        """Execute when committing a change"""
        _rewrite_value = self.editbox.GetValue()
        _original_value = self.edit_field.GetLabel()
        self.edit_field.SetLabel(_rewrite_value)

        self.event_close()

    def event_cancel(self, event):
        """Execute when cancelling a change"""
        self.event_close()

    def event_close(self, *args):
        self.Destroy()


class ModifyImageCommentDialog(ModifyFieldDialog):
    """Opens a dialog to modify an image comment.

        Args:
            header_text (str): String to display in the dialog header
            edit_field (wx.obj): Reference to the wx.object we are editing
            comment_key (str): Key in the image:comment dict
            comment_path (str): Path of the image:comment dict file

        Attributes:
            header_text (str): String to display in the dialog header
            edit_field (wx.obj): Reference to the wx.object we are editing
            comment_key (str): Key in the image:comment dict
            comment_path (str): Path of the image:comment dict file
            orig_field_text (str): Original text to display when editing
    """

    def __init__(self, parent, edit_field, comment_key, comment_path, header_text="", *args, **kw):
        """Constructor"""
        super(ModifyFieldDialog, self).__init__(None, *args, **kw)

        self.parent = parent

        self.header_text = header_text
        self.edit_field = edit_field
        self.comment_key = comment_key
        self.comment_path = comment_path

        self.orig_field_text = self.edit_field.GetValue()
        if self.orig_field_text == "There is no comment recorded":
            self.orig_field_text = ""

        self.init_dialog()
        self.SetSize((500, 160))
        self.SetTitle(self.header_text)

    def event_commit(self, event):
        """Execute when committing a change"""

        _original_value = self.edit_field.GetLabel()
        _rewrite_value = self.editbox.GetValue()
        self.edit_field.SetValue(_rewrite_value)

        self.parent.comments[self.comment_key] = _rewrite_value

        with open(self.comment_path, 'w') as json_file:
            json.dump(['Image Comments', self.parent.comments], json_file, sort_keys=True, indent=4)

        # _temp = open(self.comment_path).read()
        # _check = _temp.find(self.comment_key + '<' + chr(00) + '>')
        # if _check != -1:  # Modify existing dict file
        #     _start = _check + len(self.comment_key) + 3
        #     _end = _temp.find(_original_value) + len(_original_value)
        #     _temp = _temp[:_start] + _rewrite_value + _temp[_end:]
        #
        #     with open(self.comment_path, 'w') as comment_file:
        #         comment_file.write(_temp)
        #
        #     #with open(self.comment_path, 'wb') as pickle_file:
        #     #    pickle.dump(,pickle_file)
        # else:  # Append to existing dict file
        #     _temp += '\n' + chr(00) + '\n' + self.comment_key + '<' + chr(00) + '>' + _rewrite_value
        #
        #     with open(self.comment_path, 'w') as comment_file:
        #         comment_file.write(_temp)

        self.Destroy()


class ImageDialog2(wx.Dialog):
    """Opens a dialog to display images relating to part

        Args:
            image_list (list of str): List of string paths of images
            image_index (int): Index of current image in image_list
            comment_path (str): Path of the image:comment dict file

        Attributes:
            image_list (list of str): List of string paths of images
            image_index (int): Index of current image in image_list
            comment_path (str): Path of the image:comment dict file
            comments (list of str): List of string comments for images
    """

    def __init__(self, image_hash, image_index, part_num, part_rev, *args, **kw):
        """Constructor"""
        super(ImageDialog, self).__init__(None, *args, **kw)

        self.image_hash = image_hash
        self.image_index = image_index
        self.comment_path = None
        self.part_num = part_num
        self.part_rev = part_rev

        self.load_data()

        self.init_dialog()
        self.SetSize((500, 500))

    def load_data(self):
        """Load data from sql database"""

        try:
            with open(self.comment_path, 'r') as json_file:
                self.comments = json.load(json_file)[1]
        except (FileNotFoundError, json.decoder.JSONDecodeError):
            self.comments = {}
            pass

        conn = sqlite3.connect(r"C:\Users\Ancient Abysswalker\sqlite_databases\LoCaS.sqlite")
        crsr = conn.cursor()
        print("SELECT image FROM Images WHERE part_num='" + self.parent.part_number +
              "' AND part_rev='" + self.parent.part_revision + "'")
        crsr.execute("SELECT image FROM Images WHERE part_num='" + self.parent.part_number +
                     "' AND part_rev='" + self.parent.part_revision + "'")
        print(crsr.fetchall())

    def init_dialog(self):
        """Draw the UI for the image dialog"""

        # Set up comment text
        self.comment_text = ""
        self.init_field()

        #Create and scale image
        temp_image = wx.Image(self.image_hash[self.image_index], wx.BITMAP_TYPE_ANY)
        height_orig = temp_image.GetHeight()
        height_new = min(height_orig, 250)
        width_new = (height_new / height_orig) * temp_image.GetWidth()
        self.imageBitmap = wx.StaticBitmap(self, wx.ID_ANY, wx.Bitmap(temp_image.Scale(width_new, height_new)))

        # Add everything to master sizer and set sizer for pane
        self.sizer_master = wx.BoxSizer(wx.VERTICAL)
        self.sizer_master.Add(self.imageBitmap, border=5, flag=wx.CENTER)
        self.sizer_master.Add(self.init_buttons(), border=5, flag=wx.ALL | wx.EXPAND)
        self.sizer_master.Add(self.comment_text, border=5, flag=wx.ALL | wx.EXPAND)
        self.SetSizer(self.sizer_master)

    def init_buttons(self):
        """Define what control buttons are available and their bindings"""

        # Control buttons
        button_prev = wx.BitmapButton(self, wx.ID_ANY,
                                      wx.Bitmap(r"C:\Users\Ancient Abysswalker\PycharmProjects\LoCaS\img\gui\l_arr.png",
                                                wx.BITMAP_TYPE_ANY), wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW)
        button_prev.Bind(wx.EVT_BUTTON, self.event_prev_image)
        button_next = wx.BitmapButton(self, wx.ID_ANY,
                                      wx.Bitmap(r"C:\Users\Ancient Abysswalker\PycharmProjects\LoCaS\img\gui\r_arr.png",
                                                wx.BITMAP_TYPE_ANY), wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW)
        button_next.Bind(wx.EVT_BUTTON, self.event_next_image)

        # Control button sizer
        sizer_controls = wx.BoxSizer(wx.HORIZONTAL)
        sizer_controls.Add(button_prev, border=5, flag=wx.ALL | wx.EXPAND)
        sizer_controls.Add(button_next, border=5, flag=wx.ALL | wx.EXPAND)

        return sizer_controls

    def init_field(self):
        """Define the editable field"""

        # Set image comment
        self.comment_text = wx.TextCtrl(self, value="There is no comment recorded", size=(-1, 35),
                                        style=wx.TE_MULTILINE | wx.TE_WORDWRAP | wx.TE_READONLY | wx.BORDER_NONE | wx.TE_NO_VSCROLL)
        self.comment_text.Bind(wx.EVT_SET_FOCUS, self.onfocus)

        self.comment_text.SetBackgroundColour((248, 248, 248))  # set text back color
        try:
            self.comment_text.SetValue(self.comments[os.path.split(self.image_hash[self.image_index])[1]])
        except KeyError:
            pass
        self.comment_text.Bind(wx.EVT_LEFT_DCLICK, self.event_comment_edit)

    def onfocus(self, event):
        """Set cursor to default and pass before default on-focus method"""
        self.SetCursor(wx.Cursor(wx.CURSOR_ARROW))
        pass

    def image_refresh(self):
        (width_orig, height_orig) = wx.Image(self.image_hash[self.image_index], wx.BITMAP_TYPE_ANY).GetSize()

        height_new = min(height_orig, 250)
        width_new = (height_new / height_orig) * width_orig

        self.imageBitmap.SetBitmap(wx.Bitmap(
            wx.Image(self.image_hash[self.image_index], wx.BITMAP_TYPE_ANY).Rescale((width_new), (height_new))))


class ImageDialog(wx.Dialog):
    """Opens a dialog to display images relating to part

        Args:
            image_list (list of str): List of string paths of images
            image_index (int): Index of current image in image_list
            comment_path (str): Path of the image:comment dict file

        Attributes:
            image_list (list of str): List of string paths of images
            image_index (int): Index of current image in image_list
            comment_path (str): Path of the image:comment dict file
            comments (list of str): List of string comments for images
    """

    def __init__(self, image_list, image_index, part_num, part_rev, *args, **kw):
        """Constructor"""
        super().__init__(None, *args, **kw)

        self.image_list = image_list
        self.image_index = image_index
        self.part_num = part_num
        self.part_rev = part_rev
        self.comments = {}

        self.load_data()

        self.init_dialog()
        self.SetSize((500, 500))

        self.Show()

    def load_data(self):
        """Load data from sql database"""

        conn = sqlite3.connect(r"C:\Users\Ancient Abysswalker\sqlite_databases\LoCaS.sqlite")
        crsr = conn.cursor()
        crsr.execute("SELECT image, description FROM Images WHERE part_num='" + self.part_num +
                     "' AND part_rev='" + self.part_rev + "'")
        self.comments = {x: y for x, y in crsr.fetchall()}

    def init_dialog(self):
        """Draw the UI for the image dialog"""

        # Set up comment text
        self.comment_text = ""
        self.init_field()

        #Create and scale image
        temp_image = wx.Image(os.path.join(DATADIR, 'img', *part_to_dir(self.part_num), self.image_list[self.image_index]), wx.BITMAP_TYPE_ANY)
        height_orig = temp_image.GetHeight()
        height_new = min(height_orig, 250)
        width_new = (height_new / height_orig) * temp_image.GetWidth()
        self.panel_image = wx.StaticBitmap(self, wx.ID_ANY, wx.Bitmap(temp_image.Scale(width_new, height_new)))

        # Add everything to master sizer and set sizer for pane
        self.sizer_master = wx.BoxSizer(wx.VERTICAL)
        self.sizer_master.Add(self.panel_image, border=5, flag=wx.CENTER)
        self.sizer_master.Add(self.init_buttons(), border=5, flag=wx.ALL | wx.EXPAND)
        self.sizer_master.Add(self.comment_text, border=5, flag=wx.ALL | wx.EXPAND)
        self.SetSizer(self.sizer_master)

    def init_buttons(self):
        """Define what control buttons are available and their bindings"""

        # Control buttons
        button_prev = wx.BitmapButton(self, wx.ID_ANY,
                                      wx.Bitmap(r"C:\Users\Ancient Abysswalker\PycharmProjects\LoCaS\img\gui\l_arr.png",
                                                wx.BITMAP_TYPE_ANY), wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW)
        button_prev.Bind(wx.EVT_BUTTON, self.event_prev_image)
        button_next = wx.BitmapButton(self, wx.ID_ANY,
                                      wx.Bitmap(r"C:\Users\Ancient Abysswalker\PycharmProjects\LoCaS\img\gui\r_arr.png",
                                                wx.BITMAP_TYPE_ANY), wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW)
        button_next.Bind(wx.EVT_BUTTON, self.event_next_image)

        # Control button sizer
        sizer_controls = wx.BoxSizer(wx.HORIZONTAL)
        sizer_controls.Add(button_prev, border=5, flag=wx.ALL | wx.EXPAND)
        sizer_controls.Add(button_next, border=5, flag=wx.ALL | wx.EXPAND)

        return sizer_controls

    def init_field(self):
        """Define the editable field"""

        # Set image comment
        self.comment_text = wx.TextCtrl(self, value="There is no comment recorded", size=(-1, 35),
                                        style=wx.TE_MULTILINE | wx.TE_WORDWRAP | wx.BORDER_NONE | wx.TE_NO_VSCROLL)

        self.comment_text.SetBackgroundColour((248, 248, 248))  # set text back color

    def image_refresh(self):
        """Refresh the image field and ensure correct sizing"""

        (width_orig, height_orig) = wx.Image(os.path.join(DATADIR, 'img', *part_to_dir(self.part_num), self.image_list[self.image_index]), wx.BITMAP_TYPE_ANY).GetSize()

        height_new = min(height_orig, 250)
        width_new = (height_new / height_orig) * width_orig

        self.panel_image.SetBitmap(wx.Bitmap(
            wx.Image(os.path.join(DATADIR, 'img', *part_to_dir(self.part_num), self.image_list[self.image_index]), wx.BITMAP_TYPE_ANY).Rescale(width_new, height_new))) #####

    def event_comment_edit(self, evt):
        """Open dialog to revise image comment"""

        dialog = ModifyImageCommentDialog(self, evt.GetEventObject(),
                                          os.path.split(self.image_list[self.image_index])[1],
                                          "", "Editing image comment")
        dialog.ShowModal()
        dialog.Destroy()
        self.sizer_master.RecalcSizes()
        evt.Skip()

    def event_next_image(self, evt):
        """If image is not last image, switch to next image"""

        if self.image_index < len(self.image_list) - 1:
            self.image_index += 1
            # self.imageBitmap.SetBitmap(wx.Bitmap(self.image_list[self.image_index], wx.BITMAP_TYPE_ANY))
            # (width_orig, height_orig) = wx.Image(self.image_list[self.image_index], wx.BITMAP_TYPE_ANY).GetSize()
            #
            # height_new = min(height_orig, 250)
            # width_new = (height_new / height_orig) * width_orig
            #
            # self.imageBitmap.SetBitmap(wx.Bitmap(wx.Image(self.image_list[self.image_index], wx.BITMAP_TYPE_ANY).Rescale((width_new), (height_new))))
            # #self.imageBitmap.SetSize(_tmp_width2)wx.Image(os.path.join(DATADIR, r'whitewitch2.jpg'), wx.BITMAP_TYPE_ANY)
            #

            self.image_refresh()
            try:
                self.comment_text.SetValue(self.comments[self.image_list[self.image_index]])
            except TypeError:
                self.comment_text.SetValue("There is no comment recorded")
                pass

            self.sizer_master.Layout()
            self.sizer_master.RecalcSizes()
        evt.Skip()

    def event_prev_image(self, evt):
        """If image is not first image, switch to previous image"""

        if self.image_index > 0:
            self.image_index -= 1
            #self.imageBitmap.SetBitmap(wx.Bitmap(self.image_list[self.image_index], wx.BITMAP_TYPE_ANY))

            self.image_refresh()
            ##REWRITE
            #self.imageBitmap.SetSize(10, 10)
            #self.img_toggle()
            try:
                self.comment_text.SetValue(self.comments[self.image_list[self.image_index]])
            except TypeError:
                self.comment_text.SetValue("There is no comment recorded")
                pass

            self.sizer_master.Layout()
            self.sizer_master.RecalcSizes()
        evt.Skip()

    def image_in_db(self):
        """Checks if the image already exists in the database"""

        # Hash current image data
        image_hash = self.hash_image()

        # Connect to the database
        conn = sqlite3.connect(r"C:\Users\Ancient Abysswalker\sqlite_databases\LoCaS.sqlite")
        crsr = conn.cursor()

        # Check if the current image is already hashed into the database
        crsr.execute("SELECT EXISTS (SELECT 1 FROM Images WHERE part_num='" + self.part_num + "' AND part_rev='"
                     + self.part_rev + "' AND image='" + image_hash + "');")

        in_db = crsr.fetchone()[0]
        crsr.close()
        conn.close()

        return in_db

    def check_image_valid(self):
        """Throw dialog if image is already in database, and pass over it"""

        if self.image_in_db():
            wx.MessageBox("This image is already added to this part. You may not have duplicate images.",
                          "Image cannot be added", wx.OK | wx.ICON_ERROR)
            self.event_next_image()

    def hash_image(self):
        """Hash image data and digest into HEX"""

        hasher = hashlib.md5()
        with open(self.image_list[self.image_index], 'rb') as image:
            buffer = image.read()
            hasher.update(buffer)
        return hasher.hexdigest() + os.path.splitext(self.image_list[self.image_index])[1]

    def onfocus(self, event):
        """Set cursor to default and pass before default on-focus method"""
        self.SetCursor(wx.Cursor(wx.CURSOR_ARROW))
        pass

    def init_field(self):
        """Define the editable field"""

        # Set image comment
        self.comment_text = wx.TextCtrl(self, value="There is no comment recorded", size=(-1, 35),
                                        style=wx.TE_MULTILINE | wx.TE_WORDWRAP | wx.TE_READONLY | wx.BORDER_NONE | wx.TE_NO_VSCROLL)
        self.comment_text.Bind(wx.EVT_SET_FOCUS, self.onfocus)

        self.comment_text.SetBackgroundColour((248, 248, 248))  # set text back color
        try:
            self.comment_text.SetValue(self.comments[self.image_list[self.image_index]])
        except TypeError:
            pass
        self.comment_text.Bind(wx.EVT_LEFT_DCLICK, self.event_comment_edit)


class ImageAddDialog(wx.Dialog):
    """Opens a dialog to display images relating to part

        Args:
            image_list (list of str): List of string paths of images
            image_index (int): Index of current image in image_list
            comment_path (str): Path of the image:comment dict file

        Attributes:
            image_list (list of str): List of string paths of images
            image_index (int): Index of current image in image_list
            comment_path (str): Path of the image:comment dict file
            comments (list of str): List of string comments for images
    """

    def __init__(self, image_list, part_num, part_rev, *args, **kw):
        """Constructor"""
        super().__init__(None, *args, **kw)

        self.image_list = image_list
        self.image_index = 0
        self.part_num = part_num
        self.part_rev = part_rev

        self.init_dialog()
        self.SetSize((500, 500))

        self.Show()

        self.check_image_valid()

    def init_dialog(self):
        """Draw the UI for the image dialog"""

        # Set up comment text
        self.init_field()

        # Create and scale image
        temp_image = wx.Image(self.image_list[self.image_index], wx.BITMAP_TYPE_ANY)
        height_orig = temp_image.GetHeight()
        height_new = min(height_orig, 250)
        width_new = (height_new / height_orig) * temp_image.GetWidth()
        self.panel_image = wx.StaticBitmap(self, wx.ID_ANY, wx.Bitmap(temp_image.Scale(width_new, height_new)))

        # Add everything to master sizer and set sizer for pane
        self.sizer_master = wx.BoxSizer(wx.VERTICAL)
        self.sizer_master.Add(self.panel_image, border=5, flag=wx.CENTER)
        self.sizer_master.Add(self.comment_text, border=5, flag=wx.ALL | wx.EXPAND)
        self.sizer_master.Add(self.init_buttons(), border=5, flag=wx.ALL | wx.EXPAND)
        self.SetSizer(self.sizer_master)

    def init_buttons(self):
        """Define what control buttons are available and their bindings"""

        # Submit Image Button
        self.button_next = wx.Button(self, label='Submit Image')
        self.button_next.Bind(wx.EVT_BUTTON, self.event_next_image)

        # Control button sizer
        sizer_controls = wx.BoxSizer(wx.HORIZONTAL)
        sizer_controls.Add(self.button_next, border=5, flag=wx.ALL | wx.EXPAND)

        return sizer_controls

    def init_field(self):
        """Define the editable field"""

        # Set image comment
        self.comment_text = wx.TextCtrl(self, value="There is no comment recorded", size=(-1, 35),
                                        style=wx.TE_MULTILINE | wx.TE_WORDWRAP | wx.BORDER_NONE | wx.TE_NO_VSCROLL)

        self.comment_text.SetBackgroundColour((248, 248, 248))  # set text back color

    def image_refresh(self):
        """Refresh the image field and ensure correct sizing"""

        (width_orig, height_orig) = wx.Image(self.image_list[self.image_index], wx.BITMAP_TYPE_ANY).GetSize()

        height_new = min(height_orig, 250)
        width_new = (height_new / height_orig) * width_orig

        self.panel_image.SetBitmap(wx.Bitmap(
            wx.Image(self.image_list[self.image_index], wx.BITMAP_TYPE_ANY).Rescale(width_new, height_new)))

    def event_next_image(self, *args):
        """If image is not last image, switch to next image"""

        if not self.image_in_db():
            # Hash current image data and commit to
            image_hash = self.hash_image()
            shutil.copy2(self.image_list[self.image_index],
                         os.path.join(DATADIR, "img", *part_to_dir(self.part_num), image_hash))

            query_insert = "INSERT INTO Images (part_num, part_rev, image) VALUES ('" + str(self.part_num) + "', '" + str(self.part_rev) + "', '" + image_hash + "');"
            print(query_insert)
            crsr.execute(query_insert)
            crsr.close()
            conn.commit()

        if self.image_index < len(self.image_list) - 1:
            self.image_index += 1
            self.image_refresh()
            self.comment_text.SetValue("There is no comment recorded")

            self.sizer_master.Layout()
            self.sizer_master.RecalcSizes()
        else:
            self.Destroy()
            return

        self.check_image_valid()

    def image_in_db(self):
        """Checks if the image already exists in the database"""

        # Hash current image data
        image_hash = self.hash_image()

        # Connect to the database
        conn = sqlite3.connect(r"C:\Users\Ancient Abysswalker\sqlite_databases\LoCaS.sqlite")
        crsr = conn.cursor()

        # Check if the current image is already hashed into the database
        crsr.execute("SELECT EXISTS (SELECT 1 FROM Images WHERE part_num='" + self.part_num + "' AND part_rev='"
                     + self.part_rev + "' AND image='" + image_hash + "');")

        in_db = crsr.fetchone()[0]
        crsr.close()
        conn.close()

        return in_db

    def check_image_valid(self):
        """Throw dialog if image is already in database, and pass over it"""

        if self.image_in_db():
            wx.MessageBox("This image is already added to this part. You may not have duplicate images.",
                          "Image cannot be added", wx.OK | wx.ICON_ERROR)
            self.event_next_image()

    def hash_image(self):
        """Hash image data and digest into HEX"""

        hasher = hashlib.md5()
        with open(self.image_list[self.image_index], 'rb') as image:
            buffer = image.read()
            hasher.update(buffer)
        return hasher.hexdigest() + os.path.splitext(self.image_list[self.image_index])[1]