# -*- coding: utf-8 -*-
"""This module defines custom dialog boxes called upon at various instances"""

import wx
# import wx.richtext as wxr
import os
import sqlite3
import hashlib
import shutil

import global_colors
import config
import fn_path


DATADIR = r'C:\Users\Ancient Abysswalker\PycharmProjects\LoCaS'
UNSELECTEDGRAY = (148, 148, 148)


def crop_square(image, rescale=None):
    """Crop an image to a square and resize if desired

        Args:
            image (wx.Image): The wx.Image object to crop and scale
            rescale (int): Square size to scale the image to. None if not desired
    """

    # Determine direction to cut and cut
    if image.Height > image.Width:
        min_edge = image.Width
        posx = 0
        posy = int((image.Height - image.Width) / 2)
    else:
        min_edge = image.Height
        posx = int((image.Width - image.Height) / 2)
        posy = 0

    # Determine if scaling is desired and scale. Return square image
    if rescale:
        return image.GetSubImage(wx.Rect(posx, posy, min_edge, min_edge)).Rescale(*(rescale,) * 2)
    else:
        return image.GetSubImage(wx.Rect(posx, posy, min_edge, min_edge))




def part_to_dir(pn):
    dir1, temp = pn.split('-')
    dir2 = temp[:2]
    dir3 = temp[2:]
    return [dir1, dir2, dir3]


class ModifyFieldDialogBase(wx.Dialog):
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

    def __init__(self, *args, **kw):
        """Constructor"""
        super().__init__(*args, **kw)

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
        sizer_master.Add(sizer_editbox, proportion=1, flag=wx.ALL | wx.EXPAND, border=5)
        sizer_master.Add(sizer_buttons, flag=wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM, border=10)
        self.SetSizer(sizer_master)

        self.Bind(wx.EVT_CLOSE, self.event_close)

    def event_commit(self, event):
        """Execute when committing a change - move change to SQL"""
        pass

    def event_cancel(self, event):
        """Execute when cancelling a change"""
        self.event_close()

    def event_close(self, *args):
        """Execute when closing the dialog"""
        self.Destroy()


class ModifyPartsFieldDialog(ModifyFieldDialogBase):
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

    def __init__(self, parent, edit_field, part_num, part_rev, sql_field, header_text="", *args, **kw):
        """Constructor"""
        super().__init__(None, *args, **kw)

        self.parent = parent

        self.header_text = header_text
        self.edit_field = edit_field
        self.part_num = part_num
        self.part_rev = part_rev
        self.sql_field = sql_field

        try:
            self.orig_field_text = self.edit_field.GetLabel()
            self.rewrite_edit_field = self.edit_field.SetLabel
        except AttributeError:
            self.orig_field_text = self.edit_field.GetValue()
            self.rewrite_edit_field = self.edit_field.SetValue

        if self.orig_field_text == "There is no comment recorded":
            self.orig_field_text = ""

        self.init_dialog()
        self.SetSize((500, 160))
        self.SetTitle(self.header_text)

    def event_commit(self, event):
        """Execute when committing a change - move change to SQL"""

        # Read new value and rewrite original field in UI
        _rewrite_value = self.editbox.GetValue()
        self.rewrite_edit_field(_rewrite_value)

        # Connect to the database
        conn = config.sql_db.connect(config.db_location)
        crsr = conn.cursor()

        # Modify the existing cell in the database for existing part number and desired column
        crsr.execute("UPDATE Parts SET (%s)=(?) WHERE part_num=(?) AND part_rev=(?);" % self.sql_field,
                     (_rewrite_value, self.part_num, self.part_rev))

        conn.commit()
        crsr.close()
        conn.close()

        self.event_close()


class ModifyImageCommentDialog(ModifyFieldDialogBase):
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

    def __init__(self, parent, edit_field, part_num, part_rev, image, header_text="", *args, **kw):
        """Constructor"""
        super().__init__(None, *args, **kw)

        self.parent = parent

        self.header_text = header_text
        self.edit_field = edit_field
        self.part_num = part_num
        self.part_rev = part_rev
        self.image = image

        self.orig_field_text = self.edit_field.GetValue()

        if self.orig_field_text == "There is no comment recorded":
            self.orig_field_text = ""

        self.init_dialog()
        self.SetSize((500, 160))
        self.SetTitle(self.header_text)

    def event_commit(self, event):
        """Execute when committing a change - move change to SQL"""

        _rewrite_value = self.editbox.GetValue()

        # Connect to the database
        conn = config.sql_db.connect(config.db_location)
        crsr = conn.cursor()

        # Check if the image comment should be considered void, and commit the change
        if _rewrite_value.strip():
            self.parent.comments[self.image] = _rewrite_value
            self.parent.comment_set_and_style()
            crsr.execute("UPDATE Images SET description=(?) WHERE part_num=(?) AND part_rev=(?) AND image=(?);",
                         (_rewrite_value, self.part_num, self.part_rev, self.image))
        else:
            self.parent.comments[self.image] = ""
            self.parent.comment_set_and_style()
            crsr.execute("UPDATE Images SET description=NULL WHERE part_num=(?) AND part_rev=(?) AND image=(?);",
                         (self.part_num, self.part_rev, self.image))

        conn.commit()
        crsr.close()
        conn.close()

        # _rewrite_value = self.editbox.GetValue()
        # _original_value = self.edit_field.GetLabel()
        # self.edit_field.SetLabel(_rewrite_value)

        self.event_close()


class ImageDialogBase(wx.Dialog):
    """Base class for dialogs to display images relating to part. This class should not be called externally."""

    def __init__(self, *args, **kw):
        """Constructor"""
        super().__init__(*args, **kw)

        self.SetSize((800, 800))

    def init_dialog(self):
        """Draw the UI for the image dialog"""

        # Set up comment text
        self.init_field()

        # Create and scale image
        img_temp = wx.Image(self.image_path(), wx.BITMAP_TYPE_ANY)
        height_orig = img_temp.GetHeight()
        height_new = min(height_orig, 250)
        width_new = (height_new / height_orig) * img_temp.GetWidth()
        print(height_new, width_new)
        self.pnl_image = wx.StaticBitmap(self, wx.ID_ANY, wx.Bitmap(img_temp.Scale(width_new, height_new)))

        # Add everything to master sizer and set sizer for pane
        self.sizer_master = wx.BoxSizer(wx.VERTICAL)
        self.sizer_master.Add(self.pnl_image, border=5, flag=wx.CENTER)
        self.sizer_master.Add(self.pnl_comment, border=5, flag=wx.ALL | wx.EXPAND)
        self.sizer_master.Add(self.init_buttons(), border=5, flag=wx.ALL | wx.EXPAND)
        self.SetSizer(self.sizer_master)

    def init_buttons(self):
        """Define what control buttons are available and their bindings"""
        pass

    def init_field(self):
        """Define the editable field"""
        pass

    def image_refresh(self):
        """Refresh the image panel and ensure correct sizing of panel"""

        # Get original size
        (width_orig, height_orig) = wx.Image(self.image_path(), wx.BITMAP_TYPE_ANY).GetSize()

        # Calculate expected dimensions
        height_new = min(height_orig, 250)
        width_new = (height_new / height_orig) * width_orig

        # Set new image and scale to above calculation
        self.pnl_image.SetBitmap(wx.Bitmap(
            wx.Image(self.image_path(), wx.BITMAP_TYPE_ANY).Rescale(width_new, height_new)))

    def image_path(self):
        return os.path.join(DATADIR, 'img', *part_to_dir(self.part_num), self.image_list[self.image_index])

    def event_next_image(self, evt):
        """If image is not last image, switch to next image"""
        pass

    def event_prev_image(self, evt):
        """If image is not first image, switch to previous image"""
        pass


class ImageDialog(ImageDialogBase):
    """Opens a dialog to display images relating to part

        Args:
            image_list (list of str): List of images file names including file extensions
            image_index (int): Index of current image in image_list
            part_num (str): String representation of part number
            part_rev (str): String representation of part revision

        Attributes:
            image_list (list of str): List of string names of images including file extension
            image_index (int): Index of current image in image_list
            part_num (str): String representation of part number
            part_rev (str): String representation of part revision
            comments (dict of str: str): Dictionary mapping image file names into comments
    """

    def __init__(self, parent, mugshot_file, mugshot_panel, image_list, image_index, part_num, part_rev, *args, **kw):
        """Constructor"""
        super().__init__(None, *args, **kw)

        # Define Attributes
        self.parent = parent
        self.mugshot_file = mugshot_file
        self.mugshot_panel = mugshot_panel
        self.image_list = image_list
        self.image_index = image_index
        self.part_num = part_num
        self.part_rev = part_rev

        # Load comments for images from database
        self.comments = {}
        self.load_data()

        # Draw the UI for the image dialog
        self.init_dialog()

        self.Show()

    def load_data(self):
        """Load data from the SQL database"""

        conn = config.sql_db.connect(config.db_location)
        crsr = conn.cursor()
        crsr.execute("SELECT image, description FROM Images WHERE part_num=(?) AND part_rev=(?);",
                     (self.part_num, self.part_rev))

        # Resolve data into dictionary mapping image file names into comments
        self.comments = {x: y for x, y in crsr.fetchall()}

        crsr.close()
        conn.close()

    def init_buttons(self):
        """Define what control buttons are available and their bindings"""

        # Control buttons and their binds
        button_prev = wx.BitmapButton(self, bitmap=wx.Bitmap(fn_path.concat_gui('l_arr.png')))
        button_prev.Bind(wx.EVT_BUTTON, self.event_prev_image)
        button_prev.Bind(wx.EVT_SET_FOCUS, self.event_button_no_focus)
        button_mugshot = wx.BitmapButton(self, bitmap=wx.Bitmap(fn_path.concat_gui('new_mug.png')))
        button_mugshot.Bind(wx.EVT_BUTTON, self.event_set_mugshot)
        button_mugshot.Bind(wx.EVT_SET_FOCUS, self.event_button_no_focus)
        button_remove = wx.BitmapButton(self, bitmap=wx.Bitmap(fn_path.concat_gui('rem_img.png')))
        button_remove.Bind(wx.EVT_BUTTON, self.event_remove_img)
        button_remove.Bind(wx.EVT_SET_FOCUS, self.event_button_no_focus)
        button_next = wx.BitmapButton(self, bitmap=wx.Bitmap(fn_path.concat_gui('r_arr.png')))
        button_next.Bind(wx.EVT_BUTTON, self.event_next_image)
        button_next.Bind(wx.EVT_SET_FOCUS, self.event_button_no_focus)

        # Control button sizer
        sizer_controls = wx.BoxSizer(wx.HORIZONTAL)
        sizer_controls.Add(button_prev, border=5, flag=wx.ALL | wx.EXPAND)
        sizer_controls.Add(button_mugshot, border=5, flag=wx.ALL | wx.EXPAND)
        sizer_controls.Add(button_remove, border=5, flag=wx.ALL | wx.EXPAND)
        sizer_controls.Add(button_next, border=5, flag=wx.ALL | wx.EXPAND)

        return sizer_controls

    def init_field(self):
        """Define the editable field"""

        # Set image comment
        self.pnl_comment = wx.TextCtrl(self, value="There is no comment recorded", size=(-1, 35),
                                       style=wx.TE_MULTILINE | wx.TE_WORDWRAP | wx.TE_READONLY | wx.BORDER_NONE | wx.TE_NO_VSCROLL)

        # If database entry is null, make text color gray. Otherwise change text. Set background color
        self.comment_set_and_style()
        self.pnl_comment.Bind(wx.EVT_SET_FOCUS, self.event_ctrlbox_no_focus)
        self.pnl_comment.Bind(wx.EVT_LEFT_DCLICK, self.event_comment_edit)

    def event_ctrlbox_no_focus(self, event):
        """Set cursor to default and pass before default on-focus method"""
        self.SetCursor(wx.Cursor(wx.CURSOR_ARROW))
        pass

    def event_button_no_focus(self, event):
        """Prevents focus from being called on the buttons"""
        pass

    def image_in_db(self):
        """Checks if the image already exists in the database"""

        # Hash current image data
        image_hash = self.hash_image()

        # Connect to the database
        conn = config.sql_db.connect(config.db_location)
        crsr = conn.cursor()

        # Check if the current image is already hashed into the database
        crsr.execute("SELECT EXISTS (SELECT 1 FROM Images WHERE part_num=(?) AND part_rev=(?) AND image=(?));",
                     (self.part_num, self.part_rev, image_hash))
        in_db = crsr.fetchone()[0]

        crsr.close()
        conn.close()

        return in_db

    def check_image_valid(self):
        """Throw a warning dialog if image is already in database, and pass over current image"""

        if self.image_in_db():
            wx.MessageBox("This image is already added to this part. You may not have duplicate images.",
                          "Image cannot be added.", wx.OK | wx.ICON_ERROR)
            self.event_next_image()

    def hash_image(self):
        """Hash image data and digest into HEX"""

        hasher = hashlib.md5()
        with open(self.image_list[self.image_index], 'rb') as image:
            buffer = image.read()
            hasher.update(buffer)
        return hasher.hexdigest() + os.path.splitext(self.image_list[self.image_index])[1]

    def event_comment_edit(self, event):
        """Open dialog to revise image comment"""

        dialog = ModifyImageCommentDialog(self, event.GetEventObject(), self.part_num, self.part_rev,
                                          self.image_list[self.image_index], "Editing image comment")
        dialog.ShowModal()
        dialog.Destroy()
        self.sizer_master.RecalcSizes()

    def event_next_image(self, *args):
        """If image is not last image, switch to next image"""

        if self.image_index < len(self.image_list) - 1:
            self.image_index += 1
            self.image_refresh()
            self.comment_set_and_style()

            self.sizer_master.Layout()
            self.sizer_master.RecalcSizes()

    def event_refresh_image(self, *args):
        """Reload this same image index"""

        if len(self.image_list) != 0:
            self.image_refresh()
            self.comment_set_and_style()

            self.sizer_master.Layout()
            self.sizer_master.RecalcSizes()

    def event_prev_image(self, *args):
        """If image is not first image, switch to previous image"""
        if self.image_index > 0:
            self.image_index -= 1
            self.image_refresh()
            self.comment_set_and_style()

            self.sizer_master.Layout()
            self.sizer_master.RecalcSizes()

    def event_set_mugshot(self, *args):
        """Allows the user to change the mugshot for the part"""

        # Show confirmation dialog if not hidden in config
        if not config.dlg_hide_change_mugshot:
            dlg = wx.RichMessageDialog(self,
                                       caption = "Update Mugshot?",
                                       message = "Are you sure you would like to change the mugshot for this part?",
                                       style=wx.OK | wx.CANCEL | wx.CANCEL_DEFAULT | wx.ICON_WARNING)
            dlg.ShowCheckBox("Don't show this notification again")

            # Cancel or continue as necessary
            if dlg.ShowModal() == wx.ID_OK:
                if dlg.IsCheckBoxChecked():
                    # Set config to hide this dialog next time
                    config.dlg_hide_change_mugshot = True
            else:
                return

        # Refresh Mugshot
        self.mugshot_panel.refresh(self.image_list[self.image_index])

        # Connect to the database
        conn = config.sql_db.connect(config.db_location)
        crsr = conn.cursor()

        # Modify the existing cell in the database for existing part number and desired column
        crsr.execute("UPDATE Parts SET mugshot=(?) WHERE part_num=(?) AND part_rev=(?);",
                     (self.image_list[self.image_index], self.part_num, self.part_rev))

        conn.commit()
        crsr.close()
        conn.close()

    def event_remove_img(self, *args):
        """Removes an image from the image grid and """

        # Show confirmation dialog if not hidden in config
        if not config.dlg_hide_remove_image:
            dlg = wx.RichMessageDialog(self,
                                       caption="Remove parts image?",
                                       message="Are you sure you would like to remove this image?",
                                       style=wx.OK | wx.CANCEL | wx.CANCEL_DEFAULT | wx.ICON_WARNING)
            dlg.ShowCheckBox("Don't show this notification again")

            # Cancel or continue as necessary
            if dlg.ShowModal() == wx.ID_OK:
                if dlg.IsCheckBoxChecked():
                    # Set config to hide this dialog next time
                    config.dlg_hide_remove_image = True
            else:
                return

        # Connect to the database
        conn = config.sql_db.connect(config.db_location)
        crsr = conn.cursor()

        # Refresh Mugshot if needed and update SQL
        if self.image_list[self.image_index] == self.mugshot_file:
            self.mugshot_panel.refresh()

            crsr.execute("UPDATE Parts SET mugshot=NULL WHERE part_num=(?) AND part_rev=(?);",
                         (self.part_num, self.part_rev))

        # Remove image from database
        crsr.execute("DELETE FROM Images WHERE image=(?);",
                     (self.image_list[self.image_index],))

        _r, _c = self.parent.sizer_grid.GetRows(), self.parent.sizer_grid.GetCols()
        #self.sizer.Detach(itm.GetWindow())
        #_item = self.parent.sizer_grid.     FindItemAtPosition((self.image_index // _r, self.image_index % _r))
        #self.parent.sizer_grid.Detach(self.parent.sizer_grid.GetItem(self.image_index), wx.EXPAND)
        self.parent.purgelist[self.image_index].Destroy()
        self.parent.purgelist.pop(self.image_index)
        self.parent.image_list.pop(self.image_index)

        # Kick back one image since this one is no longer present
        if self.image_index != 0:
            self.event_prev_image()
        elif len(self.image_list) == 0:
            self.Destroy()
        else:
            self.event_refresh_image()

        # Update image grid layout
        self.parent.sizer_grid.Layout()

        conn.commit()
        crsr.close()
        conn.close()



        #self.mugshot.refresh(self.image_list[self.image_index])

        # Connect to the database
        # conn = config.sql_db.connect(config.db_location)
        # crsr = conn.cursor()
        #
        # # Modify the existing cell in the database for existing part number and desired column
        # crsr.execute("UPDATE Parts SET mugshot=(?) WHERE part_num=(?) AND part_rev=(?);",
        #              (self.image_list[self.image_index], self.part_num, self.part_rev))
        #
        # conn.commit()
        # crsr.close()
        # conn.close()

    def comment_set_and_style(self):
        """Check if the comment is null and style accordingly if NULL"""
        try:
            if not self.comments[self.image_list[self.image_index]]:
                raise TypeError
            self.pnl_comment.SetValue(self.comments[self.image_list[self.image_index]])
            self.pnl_comment.SetForegroundColour(global_colors.black)
        except TypeError:
            self.pnl_comment.SetValue("There is no comment recorded")
            self.pnl_comment.SetForegroundColour(global_colors.no_entry)


class ImageAddDialog(ImageDialogBase):
    """Opens a dialog to display images to be added to the database

        Args:
            image_list (list of str): List of images file names including file extensions
            part_num (str): String representation of part number
            part_rev (str): String representation of part revision

        Attributes:
            image_list (list of str): List of string names of images including file extension
            image_index (int): Index of current image in image_list, starting 0 and counting up
            part_num (str): String representation of part number
            part_rev (str): String representation of part revision
            comments (dict of str: str): Dictionary mapping image file names into comments
    """

    def __init__(self, parent, image_list, part_num, part_rev, *args, **kw):
        """Constructor"""
        super().__init__(parent, *args, **kw)

        self.parent = parent
        self.image_list = image_list
        self.image_index = 0
        self.part_num = part_num
        self.part_rev = part_rev

        self.init_dialog()

        self.Show()

        self.check_image_valid()

    def init_buttons(self):
        """Define what control buttons are available and their bindings"""

        # Submit Image Button
        self.button_next = wx.Button(self, label='Submit Image')
        self.button_next.Bind(wx.EVT_BUTTON, self.event_next_image)

        # Control button sizer
        sizer_controls = wx.BoxSizer(wx.HORIZONTAL)
        sizer_controls.AddStretchSpacer(1)
        sizer_controls.Add(self.button_next, border=5, flag=wx.ALL | wx.ALIGN_CENTER)
        sizer_controls.AddStretchSpacer(1)

        return sizer_controls

    def init_field(self):
        """Define the editable field"""
        # TODO: Generalize with function
        # Set image comment
        self.pnl_comment = wx.TextCtrl(self, value="There is no comment recorded", size=(-1, 35),
                                       style=wx.TE_MULTILINE | wx.TE_WORDWRAP | wx.BORDER_NONE | wx.TE_NO_VSCROLL)

        self.pnl_comment.SetBackgroundColour(global_colors.edit_field)  # set text back color

    def event_next_image(self, *args):
        """If image is not last image, switch to next image"""

        if not self.image_in_db():
            # Hash current image data and commit to
            image_hash = self.hash_image()

            # Make directory if needed
            _path = fn_path.concat_img(self.part_num, image_hash)
            if not os.path.exists(os.path.dirname(_path)):
                os.makedirs(os.path.dirname(_path))

            # Copy file
            shutil.copy2(self.image_list[self.image_index],
                         fn_path.concat_img(self.part_num, image_hash))

            # Sterilize input to ensure blank input instead of 'no comment' text
            if self.pnl_comment.GetValue() == "There is no comment recorded":
                _commit_text = ""
            else:
                _commit_text = self.pnl_comment.GetValue()

            # Connect to the database
            conn = config.sql_db.connect(config.db_location)
            crsr = conn.cursor()

            # Check if the image comment should be considered void, and commit the change
            if _commit_text.strip():
                crsr.execute("INSERT INTO Images (part_num, part_rev, image, description) VALUES ((?), (?), (?), (?));",
                            (self.part_num, self.part_rev, image_hash, _commit_text))
            else:
                crsr.execute("INSERT INTO Images (part_num, part_rev, image, description) VALUES ((?), (?), (?), NULL);",
                             (self.part_num, self.part_rev, image_hash))
            crsr.close()
            conn.commit()

            # TODO: Fix row/col is smaller array than width
            _n = len(self.parent.images)
            _tmp = crop_square(wx.Image(fn_path.concat_img(self.part_num, image_hash), wx.BITMAP_TYPE_ANY), 120)  # TODO: ImgGridPanel.icon_size)
            _temp = wx.StaticBitmap(self.parent, id=_n, bitmap=wx.Bitmap(_tmp))
            _temp.Bind(wx.EVT_LEFT_UP, self.parent.event_image_click)
            self.parent.sizer_grid.Add(_temp, wx.EXPAND)
            self.parent.image_list.append(image_hash)

            # Add image hash to list of images in sizer
            self.parent.purgelist.append(_temp)

            # Needed to actually update grid
            self.parent.Layout()

        if self.image_index < len(self.image_list) - 1:
            self.image_index += 1
            self.image_refresh()
            self.pnl_comment.SetValue("There is no comment recorded")

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
        conn = config.sql_db.connect(config.db_location)
        crsr = conn.cursor()

        # Check if the current image is already hashed into the database
        crsr.execute("SELECT EXISTS (SELECT 1 FROM Images WHERE part_num=(?) AND part_rev=(?) AND image=(?));",
                     (self.part_num, self.part_rev, image_hash))

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



