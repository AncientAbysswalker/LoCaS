# -*- coding: utf-8 -*-
"""This module defines custom dialog boxes called upon at various instances"""

import wx
# import wx.richtext as wxr
import os
import hashlib
import shutil
import datetime

import widget
import global_colors
import config
import fn_path


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


class BaseModifyField(wx.Dialog):
    """Base class for dialogs to edit a text field in the application."""

    def __init__(self, parent):
        """Constructor"""
        super().__init__(parent)

    def draw_layout(self):
        """Draw the dialog box details - common between subclasses"""

        # Editable box and outline box
        self.wgt_editbox = wx.TextCtrl(self, value=self.orig_field_text, style=wx.TE_MULTILINE)
        szr_editbox = wx.StaticBoxSizer(wx.StaticBox(self, label=self.header_text), orient=wx.VERTICAL)
        szr_editbox.Add(self.wgt_editbox, proportion=1, flag=wx.ALL | wx.EXPAND, border=5)

        # Dialog buttons with binds
        btn_commit = wx.Button(self, label='Commit')
        btn_commit.Bind(wx.EVT_BUTTON, self.evt_commit)
        bton_cancel = wx.Button(self, label='Cancel')
        bton_cancel.Bind(wx.EVT_BUTTON, self.evt_cancel)

        # Dialog button sizer
        szr_buttons = wx.BoxSizer(wx.HORIZONTAL)
        szr_buttons.Add(btn_commit)
        szr_buttons.Add(bton_cancel, flag=wx.LEFT, border=5)

        # Add everything to master sizer and set sizer for pane
        szr_master = wx.BoxSizer(wx.VERTICAL)
        szr_master.Add(szr_editbox, proportion=1, flag=wx.ALL | wx.EXPAND, border=5)
        szr_master.Add(szr_buttons, flag=wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM, border=10)
        self.SetSizer(szr_master)

        self.Bind(wx.EVT_CLOSE, self.evt_close)

    def evt_commit(self, event):
        """Execute when committing a change - move change to SQL

            Args:
                event: Click event object
        """
        pass

    def evt_cancel(self, event):
        """Execute when cancelling a change

            Args:
                event: Click event object
        """
        self.evt_close()

    def evt_close(self, *args):
        """Execute when closing the dialog

            Args:
                args[0]: Click event object
        """
        self.Destroy()


class ModifyField(BaseModifyField):
    """Opens a dialog to modify an image comment.

        Args:
            parent (ref): Reference to the parent wx.object
            root (ref): Reference to the root parts tab
            header_text (str): String to display in the dialog header
            edit_field (wx.obj): Reference to the wx.object we are editing
            sql_field (str): String name of the field in the SQL database to update

        Attributes:
            parent (ref): Reference to the parent wx.object
            root (ref): Reference to the root parts tab
            header_text (str): String to display in the dialog header
            edit_field (wx.obj): Reference to the wx.object we are editing
            sql_field (str): String name of the field in the SQL database to update
    """

    def __init__(self, parent, root, edit_field, sql_field, header_text=""):
        """Constructor"""
        super().__init__(parent)

        # Define Attributes
        self.parent = parent
        self.root = root
        self.header_text = header_text
        self.edit_field = edit_field
        self.sql_field = sql_field

        # Ensuring that the proper method is called to get the initial value from the root
        try:
            self.orig_field_text = self.edit_field.GetValue()
            self.rewrite_edit_field = self.edit_field.SetValue
        except AttributeError:
            self.orig_field_text = self.edit_field.GetLabel()
            self.rewrite_edit_field = self.edit_field.SetLabel

        # If there is no entry, then keep the text field of the dialog empty
        if self.orig_field_text == "No Entry":
            self.orig_field_text = ""

        # Fill out the dialog layout and set the size and title
        self.draw_layout()
        self.SetSize((500, 200))
        self.SetTitle(self.header_text)

    def evt_commit(self, event):
        """Execute when committing a change - move change to SQL

            Args:
                event: Click event object
        """

        # Read new value and rewrite original field in UI
        _rewrite_value = self.wgt_editbox.GetValue().strip()
        if _rewrite_value:
            self.rewrite_edit_field(_rewrite_value)
            self.edit_field.SetForegroundColour(global_colors.black)
        else:
            self.rewrite_edit_field("No Entry")
            self.edit_field.SetForegroundColour(global_colors.no_entry)

        # Connect to the database
        conn = config.sql_db.connect(config.cfg["db_location"])
        crsr = conn.cursor()

        # Modify the existing cell in the database for existing part number and desired column
        if _rewrite_value:
            crsr.execute("UPDATE Parts SET (%s)=(?) WHERE part_num=(?) AND part_rev=(?);" % self.sql_field,
                         (_rewrite_value, self.root.part_num, self.root.part_rev))
        else:
            crsr.execute("UPDATE Parts SET (%s)=NULL WHERE part_num=(?) AND part_rev=(?);" % self.sql_field,
                         (self.root.part_num, self.root.part_rev))

        conn.commit()
        crsr.close()
        conn.close()

        self.evt_close()


class ModifyComment(BaseModifyField):
    """Opens a dialog to modify an image comment.

        Args:
            parent (ref): Reference to the parent wx.object
            root (ref): Reference to the root parts tab
            edit_field (wx.obj): Reference to the wx.object we are editing
            image (str): String name of image including file extension

        Attributes:
            parent (ref): Reference to the parent wx.object
            root (ref): Reference to the root parts tab
            header_text (str): String to display in the dialog header
            edit_field (wx.obj): Reference to the wx.object we are editing
            image (str): String name of image including file extension
    """

    def __init__(self, parent, root, edit_field, image):
        """Constructor"""
        super().__init__(parent)

        # Define Attributes
        self.parent = parent
        self.root = root
        self.header_text = "Editing Image Comment"
        self.edit_field = edit_field
        self.image = image

        # Get the initial value from the root
        self.orig_field_text = self.edit_field.GetValue()

        # If there is no entry, then keep the text field of the dialog empty
        if self.orig_field_text == "There is no comment recorded":
            self.orig_field_text = ""

        # Fill out the dialog layout and set the size and title
        self.draw_layout()
        self.SetSize((500, 200))
        self.SetTitle(self.header_text)

    def evt_commit(self, event):
        """Execute when committing a change - move change to SQL"""

        # Read new value so we can rewrite the original field
        _rewrite_value = self.wgt_editbox.GetValue()

        # Connect to the database
        conn = config.sql_db.connect(config.cfg["db_location"])
        crsr = conn.cursor()

        # Check if the image comment should be considered void, and commit the change
        if _rewrite_value.strip():
            self.parent.comments[self.image] = _rewrite_value
            self.parent.comment_set_and_style()
            crsr.execute("UPDATE Images SET description=(?) WHERE part_num=(?) AND part_rev=(?) AND image=(?);",
                         (_rewrite_value, self.root.part_num, self.root.part_rev, self.image))
        else:
            self.parent.comments[self.image] = ""
            self.parent.comment_set_and_style()
            crsr.execute("UPDATE Images SET description=NULL WHERE part_num=(?) AND part_rev=(?) AND image=(?);",
                         (self.root.part_num, self.root.part_rev, self.image))

        conn.commit()
        crsr.close()
        conn.close()

        self.evt_close()


class BaseImage(wx.Dialog):
    """Base class for dialogs to edit the assemblies data for this part"""

    def __init__(self, parent):
        """Constructor"""
        super().__init__(parent)

        # Set the width for the dialog and it's children
        self.SetMinSize((800, -1))

    def draw_layout(self):
        """Draw the UI for the image dialog"""

        # Set up the editable field
        self.draw_field()

        # Create image and get original size
        tmp_img = wx.Image(self.image_path(), wx.BITMAP_TYPE_ANY)
        (width_orig, height_orig) = wx.Image(self.image_path(), wx.BITMAP_TYPE_ANY).GetSize()

        # Calculate expected dimensions
        height_new = min(height_orig, 250)
        width_new = (height_new / height_orig) * width_orig

        # Store a reference to the wx.obj that can be destroyed later
        self.pnl_image = wx.StaticBitmap(self, wx.ID_ANY, wx.Bitmap(tmp_img.Scale(width_new, height_new)))

        # Add everything to master sizer and set sizer for pane
        self.szr_master = wx.BoxSizer(wx.VERTICAL)
        self.szr_master.Add(self.pnl_image, border=5, flag=wx.CENTER)
        self.szr_master.Add(self.pnl_comment, border=5, flag=wx.ALL | wx.EXPAND)
        self.szr_master.Add(self.draw_buttons(), border=5, flag=wx.ALL | wx.EXPAND)
        self.SetSizer(self.szr_master)

    def draw_buttons(self):
        """Define what control buttons are available and their bindings"""
        pass

    def draw_field(self):
        """Define the editable field"""
        pass

    def image_refresh(self):
        """Refresh the image panel and ensure correct sizing of panel"""

        # Create image and get original size
        tmp_img = wx.Image(self.image_path(), wx.BITMAP_TYPE_ANY)
        (width_orig, height_orig) = tmp_img.GetSize()

        # Calculate expected dimensions
        height_new = min(height_orig, 250)
        width_new = (height_new / height_orig) * width_orig

        # Create new image and scale to above calculation
        tmp_bitmap = wx.StaticBitmap(self, wx.ID_ANY, wx.Bitmap(tmp_img.Scale(width_new, height_new)))

        # Replace image in sizer, destroy old image, then change reference to point at new image
        self.szr_master.Replace(self.pnl_image, tmp_bitmap, False)
        self.pnl_image.Destroy()
        self.pnl_image = tmp_bitmap

    def image_path(self):
        """Return the path of the current image"""
        return fn_path.concat_img(self.root.part_num, self.image_list[self.image_index])

    def evt_next_image(self, evt):
        """If image is not last image, switch to next image"""
        pass

    def evt_prev_image(self, evt):
        """If image is not first image, switch to previous image"""
        pass


class EditImage(BaseImage):
    """Opens a dialog to display images relating to part

        Args:
            parent (ref): Reference to the parent wx.object
            root (ref): Reference to the root parts tab
            image_index (int): Index of current image in image_list

        Attributes:
            parent (ref): Reference to the parent wx.object
            root (ref): Reference to the root parts tab
            image_list (list of str): List of string names of images including file extension
            image_index (int): Index of current image in image_list
            comments (dict): Dictionary mapping of image file names into comments
    """

    def __init__(self, parent, root, image_index):
        """Constructor"""
        super().__init__(parent)

        # Define Attributes
        self.parent = parent
        self.root = root
        self.image_list = parent.image_list
        self.image_index = image_index

        # Load comments for images from database
        conn = config.sql_db.connect(config.cfg["db_location"])
        crsr = conn.cursor()
        crsr.execute("SELECT image, description FROM Images WHERE part_num=(?) AND part_rev=(?);",
                     (self.root.part_num, self.root.part_rev))

        # Resolve data into dictionary mapping image file names into comments, then close connection to DB
        self.comments = {x: y for x, y in crsr.fetchall()}
        crsr.close()
        conn.close()

        # Draw the UI for the image dialog
        self.draw_layout()

        # Resize dialog - specifically for fitting bottom edge
        self.Fit()

    def draw_buttons(self):
        """Define what control buttons are available and their bindings"""

        # Previous Image Button
        btn_prev = wx.BitmapButton(self, bitmap=wx.Bitmap(fn_path.concat_gui('l_arr.png')))
        btn_prev.Bind(wx.EVT_BUTTON, self.evt_prev_image)
        btn_prev.Bind(wx.EVT_SET_FOCUS, self.evt_btn_no_focus)

        # Use as Mugshot Button
        btn_mugshot = wx.BitmapButton(self, bitmap=wx.Bitmap(fn_path.concat_gui('new_mug.png')))
        btn_mugshot.Bind(wx.EVT_BUTTON, self.evt_set_mugshot)
        btn_mugshot.Bind(wx.EVT_SET_FOCUS, self.evt_btn_no_focus)

        # Remove Image Button
        btn_remove = wx.BitmapButton(self, bitmap=wx.Bitmap(fn_path.concat_gui('rem_img.png')))
        btn_remove.Bind(wx.EVT_BUTTON, self.evt_remove_img)
        btn_remove.Bind(wx.EVT_SET_FOCUS, self.evt_btn_no_focus)

        # Next Image Button
        btn_next = wx.BitmapButton(self, bitmap=wx.Bitmap(fn_path.concat_gui('r_arr.png')))
        btn_next.Bind(wx.EVT_BUTTON, self.evt_next_image)
        btn_next.Bind(wx.EVT_SET_FOCUS, self.evt_btn_no_focus)

        # Control button sizer
        szr_buttons = wx.BoxSizer(wx.HORIZONTAL)
        szr_buttons.Add(btn_prev, border=5, flag=wx.ALL | wx.EXPAND)
        szr_buttons.Add(btn_mugshot, border=5, flag=wx.ALL | wx.EXPAND)
        szr_buttons.Add(btn_remove, border=5, flag=wx.ALL | wx.EXPAND)
        szr_buttons.Add(btn_next, border=5, flag=wx.ALL | wx.EXPAND)

        # Return the collection of buttons
        return szr_buttons

    def draw_field(self):
        """Define the editable field"""

        # Set image comment box
        self.pnl_comment = wx.TextCtrl(self, value="There is no comment recorded", size=(-1, 48),
                                       style=wx.TE_MULTILINE | wx.TE_WORDWRAP | wx.TE_READONLY | wx.BORDER_NONE)

        # If database entry is null, make text color gray. Otherwise change text. Set background color
        self.comment_set_and_style()
        self.pnl_comment.Bind(wx.EVT_SET_FOCUS, self.evt_ctrlbox_no_focus)
        self.pnl_comment.Bind(wx.EVT_LEFT_DCLICK, self.evt_comment_edit)

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

    def evt_ctrlbox_no_focus(self, event):
        """Set cursor to default and pass before default on-focus method

            Args:
                event: A focus event object
        """
        self.SetCursor(wx.Cursor(wx.CURSOR_ARROW))
        pass

    def evt_btn_no_focus(self, event):
        """Prevents focus from being called on the buttons

            Args:
                event: A focus event object
        """
        pass

    def evt_comment_edit(self, event):
        """Open dialog to revise image comment

            Args:
                event: A click event object
        """

        dialog = ModifyComment(self, self.root, event.GetEventObject(), self.image_list[self.image_index])
        dialog.ShowModal()
        dialog.Destroy()

    def evt_next_image(self, *args):
        """If image is not last image, switch to next image

            Args:
                args[0]: Null, or a click event object
        """

        if self.image_index < len(self.image_list) - 1:
            self.image_index += 1
            self.image_refresh()
            self.comment_set_and_style()

            # Refit dialog height and layout
            self.Fit()
            self.szr_master.RecalcSizes()

    def evt_refresh_image(self, *args):
        """Reload this same image index

            Args:
                args[0]: Null, or a click event object
        """

        if len(self.image_list) != 0:
            self.image_refresh()
            self.comment_set_and_style()

            # Refit dialog height and layout
            self.Fit()
            self.szr_master.RecalcSizes()

    def evt_prev_image(self, *args):
        """If image is not first image, switch to previous image

            Args:
                args[0]: Null, or a click event object
        """
        if self.image_index > 0:
            self.image_index -= 1
            self.image_refresh()
            self.comment_set_and_style()

            # Refit dialog height and layout
            self.Fit()
            self.szr_master.RecalcSizes()

    def evt_set_mugshot(self, *args):
        """Allows the user to change the mugshot for the part

            Args:
                args[0]: Null, or a click event object
        """

        # Show confirmation dialog if not hidden in config
        if not config.cfg["dlg_hide_change_mugshot"]:
            dlg = wx.RichMessageDialog(self,
                                       caption="Update Mugshot?",
                                       message="Are you sure you would like to change the mugshot for this part?",
                                       style=wx.OK | wx.CANCEL | wx.CANCEL_DEFAULT | wx.ICON_WARNING)
            dlg.ShowCheckBox("Don't show this notification again")

            # Cancel or continue as necessary
            if dlg.ShowModal() == wx.ID_OK:
                if dlg.IsCheckBoxChecked():
                    # Set config to hide this dialog next time
                    config.cfg["dlg_hide_change_mugshot"] = True
            else:
                return

        # Refresh Mugshot
        self.root.pnl_mugshot.refresh(self.image_list[self.image_index])

        # Connect to the database
        conn = config.sql_db.connect(config.cfg["db_location"])
        crsr = conn.cursor()

        # Modify the existing mugshot in the database for existing part number
        crsr.execute("UPDATE Parts SET mugshot=(?) WHERE part_num=(?) AND part_rev=(?);",
                     (self.image_list[self.image_index], self.root.part_num, self.root.part_rev))

        conn.commit()
        crsr.close()
        conn.close()

    def evt_remove_img(self, *args):
        """Removes an image from the image grid and potentially the mugshot

            Args:
                args[0]: Null, or a click event object
        """

        # Show confirmation dialog if not hidden in config
        if not config.cfg["dlg_hide_remove_image"]:
            dlg = wx.RichMessageDialog(self,
                                       caption="Remove parts image?",
                                       message="Are you sure you would like to remove this image?",
                                       style=wx.OK | wx.CANCEL | wx.CANCEL_DEFAULT | wx.ICON_WARNING)
            dlg.ShowCheckBox("Don't show this notification again")

            # Cancel or continue as necessary
            if dlg.ShowModal() == wx.ID_OK:
                if dlg.IsCheckBoxChecked():
                    # Set config to hide this dialog next time
                    config.cfg["dlg_hide_remove_image"] = True
            else:
                return

        # Connect to the database
        conn = config.sql_db.connect(config.cfg["db_location"])
        crsr = conn.cursor()

        # Refresh Mugshot if needed and update SQL
        if self.image_list[self.image_index] == self.root.mugshot:
            self.root.pnl_mugshot.refresh()

            crsr.execute("UPDATE Parts SET mugshot=NULL WHERE part_num=(?) AND part_rev=(?);",
                         (self.root.part_num, self.root.part_rev))

        # Remove image from database
        crsr.execute("DELETE FROM Images WHERE part_num=(?) AND part_rev=(?) AND image=(?);",
                     (self.root.part_num, self.root.part_rev, self.image_list[self.image_index],))

        # Remove image physically from defined storage area
        os.remove(fn_path.concat_img(self.root.part_num, self.image_list[self.image_index]))

        # Update image grid to remove destroyed image from grid
        _r, _c = self.parent.sizer_grid.GetRows(), self.parent.sizer_grid.GetCols()
        self.parent.img_object_list[self.image_index].Destroy()
        self.parent.img_object_list.pop(self.image_index)
        self.image_list.pop(self.image_index)

        # Kick back one image in this dialog since this one is no longer present. If this is the last image, close me
        if self.image_index != 0:
            self.evt_prev_image()
        elif len(self.image_list) == 0:
            self.Destroy()
        else:
            self.evt_refresh_image()

        # Update image grid layout
        self.parent.sizer_grid.Layout()

        conn.commit()
        crsr.close()
        conn.close()


class AddImage(BaseImage):
    """Opens a dialog to display images to be added to the database

        Args:
            parent (ref): Reference to the parent wx.object
            root (ref): Reference to the root parts tab
            image_list (list of str): List of string names of images including file extension
            image_index (int): Index of current image in image_list

        Attributes:
            parent (ref): Reference to the parent wx.object
            root (ref): Reference to the root parts tab
            image_list (list of str): List of string names of images including file extension
            image_index (int): Index of current image in image_list
    """

    def __init__(self, parent, root, image_list):
        """Constructor"""
        super().__init__(parent)

        self.parent = parent
        self.root = root
        self.image_list = image_list
        self.image_index = 0

        self.draw_layout()

        self.Show()

        self.Fit()
        self.check_image_valid()

    def draw_buttons(self):
        """Define what control buttons are available and their bindings"""

        # Submit Image Button
        self.btn_next = wx.Button(self, label='Submit Image')
        self.btn_next.Bind(wx.EVT_BUTTON, self.evt_next_image)

        # Control button sizer
        szr_controls = wx.BoxSizer(wx.HORIZONTAL)
        szr_controls.AddStretchSpacer(1)
        szr_controls.Add(self.btn_next, border=5, flag=wx.ALL | wx.ALIGN_CENTER)
        szr_controls.AddStretchSpacer(1)

        # Return the collection of buttons
        return szr_controls

    def draw_field(self):
        """Define the editable field"""

        # Define editable field and initial text
        self.pnl_comment = wx.TextCtrl(self, value="", size=(-1, 48),
                                       style=wx.TE_MULTILINE | wx.TE_WORDWRAP | wx.BORDER_NONE)

        # Set text background color
        self.pnl_comment.SetBackgroundColour(global_colors.edit_field)

    def evt_next_image(self, *args):
        """If image is not last image, switch to next image

            Args:
                args[0]: Null, or a click event object
        """

        if not self.image_in_db():
            # Hash current image data and commit to
            image_hash = self.hash_image()

            # Make directory if needed
            _path = fn_path.concat_img(self.root.part_num, image_hash)
            if not os.path.exists(os.path.dirname(_path)):
                os.makedirs(os.path.dirname(_path))

            # Copy file
            shutil.copy2(self.image_list[self.image_index],
                         fn_path.concat_img(self.root.part_num, image_hash))

            # Get text to add to database
            _commit_text = self.pnl_comment.GetValue()

            # Connect to the database
            conn = config.sql_db.connect(config.cfg["db_location"])
            crsr = conn.cursor()

            # Check if the image comment should be considered void, and commit the change
            if _commit_text.strip():
                crsr.execute("INSERT INTO Images (part_num, part_rev, image, description) VALUES ((?), (?), (?), (?));",
                             (self.root.part_num, self.root.part_rev, image_hash, _commit_text))
            else:
                crsr.execute("INSERT INTO Images (part_num, part_rev, image, description) VALUES ((?), (?), (?), NULL);",
                             (self.root.part_num, self.root.part_rev, image_hash))
            crsr.close()
            conn.commit()

            # Add image object to image grid, adding the bind
            _n = len(self.parent.images)
            _tmp = crop_square(wx.Image(fn_path.concat_img(self.root.part_num, image_hash)), widget.WidgetGallery.icon_size)
            _temp = wx.StaticBitmap(self.parent, bitmap=wx.Bitmap(_tmp))
            _temp.Bind(wx.EVT_LEFT_UP, self.parent.evt_image_click)
            self.parent.sizer_grid.Add(_temp, wx.EXPAND)
            self.image_list.append(image_hash)

            # Add image hash to list of images in sizer
            self.parent.img_object_list.append(_temp)

            # Need to actually update grid
            self.parent.Layout()

        # Load next image and reset comment to empty, or close the dialog if the image-to-add list is over
        if self.image_index < len(self.image_list) - 1:
            self.image_index += 1
            self.image_refresh()
            self.pnl_comment.SetValue("")

            self.szr_master.Layout()
            self.szr_master.RecalcSizes()
        else:
            self.Destroy()
            return

        # Check if the next entry is valid or not (and fit the dialog of course)
        self.Fit()
        self.check_image_valid()

    def image_in_db(self):
        """Checks if the image already exists in the database"""

        # Hash current image data
        image_hash = self.hash_image()

        # Connect to the database
        conn = config.sql_db.connect(config.cfg["db_location"])
        crsr = conn.cursor()

        # Check if the current image is already hashed into the database
        crsr.execute("SELECT EXISTS (SELECT 1 FROM Images WHERE part_num=(?) AND part_rev=(?) AND image=(?));",
                     (self.root.part_num, self.root.part_rev, image_hash))

        in_db = crsr.fetchone()[0]
        crsr.close()
        conn.close()

        # Return boolean for if the image already exists in the database
        return in_db

    def check_image_valid(self):
        """Throw error dialog if image is already in database, and pass over adding it"""

        if self.image_in_db():
            wx.MessageBox("This image is already added to this part. You may not have duplicate images.",
                          "Image cannot be added", wx.OK | wx.ICON_ERROR)
            self.evt_next_image()

    def hash_image(self):
        """Hash image data and digest into HEX"""

        hasher = hashlib.md5()
        with open(self.image_list[self.image_index], 'rb') as image:
            buffer = image.read()
            hasher.update(buffer)
        return hasher.hexdigest() + os.path.splitext(self.image_list[self.image_index])[1]


class BaseEditAssemblies(wx.Dialog):
    """Base class for dialogs to edit the assemblies data for this part

        Args:
            parent (ref): Reference to the parent wx.object
            root (ref): Reference to the root parts tab

        Attributes:
            parent (ref): Reference to the parent wx.object
            root (ref): Reference to the root parts tab
            remove_choices (list: str): List of choices to be shown in the dropdown box
            title (str): Title to be shown on the dialog window
    """

    def __init__(self, parent, root):
        """Constructor"""
        super().__init__(parent)

        self.parent = parent
        self.root = root

        # Variables to be overridden in load_data() method
        self.remove_choices = []
        self.title = ""

        self.load_data()

        # Add assembly section widgets, with bind
        self.wgt_txt_add_num = wx.TextCtrl(self, value="")
        self.wgt_txt_add_rev = wx.TextCtrl(self, size=(80, -1), value="")
        btn_add = wx.Button(self, size=(80, -1), label="Add Part")
        btn_add.Bind(wx.EVT_BUTTON, self.evt_add)

        # Add assembly section sizer
        szr_add = wx.StaticBoxSizer(wx.StaticBox(self, label="Add a Sub-Assembly"), orient=wx.HORIZONTAL)
        szr_add.Add(self.wgt_txt_add_num, proportion=1, flag=wx.ALL, border=5)
        szr_add.Add(self.wgt_txt_add_rev, flag=wx.ALL, border=5)
        szr_add.Add(btn_add, flag=wx.ALL, border=4)

        # Remove assembly section widgets, with bind
        self.wgt_drop_remove = wx.ComboBox(self, choices=self.remove_choices, style=wx.CB_READONLY)
        btn_remove = wx.Button(self, size=(80, -1), label="Remove Part")
        btn_remove.Bind(wx.EVT_BUTTON, self.evt_remove)

        # Remove assembly section sizer
        szr_remove = wx.StaticBoxSizer(wx.StaticBox(self, label="Remove a Sub-Assembly"), orient=wx.HORIZONTAL)
        szr_remove.Add(self.wgt_drop_remove, proportion=1, flag=wx.ALL, border=5)
        szr_remove.Add(btn_remove, flag=wx.ALL, border=4)

        # Done button with bind
        btn_done = wx.Button(self, label='Done')
        btn_done.Bind(wx.EVT_BUTTON, self.evt_done)

        # Add everything to master sizer and set sizer for pane
        szr_main = wx.BoxSizer(wx.VERTICAL)
        szr_main.Add(szr_add, flag=wx.ALL | wx.EXPAND, border=5)
        szr_main.Add(szr_remove, flag=wx.ALL | wx.EXPAND, border=5)
        szr_main.Add(btn_done, flag=wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM, border=5)

        # Set main sizer
        self.SetSizer(szr_main)

        # Set size and title
        self.SetSize((500, 220))
        self.SetTitle(self.title)

    def load_data(self):
        """Load data pertinent to variations of this dialog - overload method in derived classes"""

        pass

    def evt_add(self, event):
        """Add a part to the assembly list - overload method in derived classes

            Args:
                event: A button event object passed from the button click
        """

        pass

    def evt_remove(self, event):
        """Remove a part from the assembly list - overload method in derived classes

            Args:
                event: A button event object passed from the button click
        """

        pass

    def evt_done(self, event):
        """Close the dialog because we are done

            Args:
                event: A button event object passed from the button click
        """

        self.Destroy()


class EditSubAssemblies(BaseEditAssemblies):
    """Opens a dialog to edit the sub-assemblies data for this part

        Args:
            parent (ref): Reference to the parent wx.object
            root (ref): Reference to the root parts tab

        Attributes:
            parent (ref): Reference to the parent wx.object
            root (ref): Reference to the root parts tab
            remove_choices (list: str): List of choices to be shown in the dropdown box
            title (str): Title to be shown on the dialog window
    """

    def load_data(self):
        """Load specific dialog box details - unique between subclasses"""

        self.title = "Edit List of Sub-Assemblies"
        self.remove_choices = ["%s (%s r%s)" % (self.root.data_wgt_sub[i[0]][i[1]], i[0], i[1])
                               for i in self.root.helper_wgt_sub]

    def evt_add(self, event):
        """Add a part to the sub-assembly list

            Args:
                event: A button event object passed from the button click
        """

        # Get part number and rev to remove
        _num = self.wgt_txt_add_num.GetValue()
        _rev = self.wgt_txt_add_rev.GetValue()

        # Only execute if the two text boxes have been filled out
        if _num != "" and _rev != "":
            conn = config.sql_db.connect(config.cfg["db_location"])
            crsr = conn.cursor()

            # Check if the subassembly is already listed for this part
            crsr.execute("""SELECT EXISTS
                            (
                                SELECT 
                                    1 
                                FROM Children 
                                WHERE part_num=(?) 
                                    AND part_rev=(?) 
                                    AND child_num=(?) 
                                    AND child_rev=(?)
                            );""", (_num, _rev, self.root.part_num, self.root.part_rev))

            # If the sub-assembly is not yet in the DB, carry out the additions
            if not crsr.fetchone()[0]:
                # Add the part from the assembly list on the parts tab
                self.parent.wgt_sub_assm.Append("%s r%s" % (_num, _rev))

                # Insert the sub-assembly into the DB
                crsr.execute(
                    "INSERT INTO Children (part_num, part_rev, child_num, child_rev) VALUES ((?), (?), (?), (?));",
                    (_num, _rev, self.root.part_num, self.root.part_rev))
                conn.commit()

                # Get the name of the sub-assembly if it exists
                crsr.execute("SELECT name FROM Parts WHERE part_num=(?) AND part_rev=(?);", (_num, _rev))
                try:
                    _name = crsr.fetchone()[0]
                except:
                    _name = None

                crsr.close()
                conn.close()

                # Add the part to the data structures holding the data for the assembly widget
                self.root.helper_wgt_sub.append([_num, _rev])
                if _num not in self.root.data_wgt_sub:
                    self.root.data_wgt_sub[_num] = {_rev: _name}
                elif _rev not in self.root.data_wgt_sub[_num]:
                    self.root.data_wgt_sub[_num][_rev] = _name

                # Clear the dialog widgets of any text
                self.wgt_txt_add_num.SetLabel("")
                self.wgt_txt_add_rev.SetLabel("")

    def evt_remove(self, event):
        """Remove a part from the sub-assembly list

            Args:
                event: A button event object passed from the button click
        """

        # Get index of the selected part
        _index = self.wgt_drop_remove.GetSelection()

        # Only do anything if something is selected
        if _index != -1:
            # Get part number and rev to remove
            _num, _rev = self.root.helper_wgt_sub[_index]

            # Remove the part from the dialog dropdown list
            self.wgt_drop_remove.Delete(_index)

            # Remove the part from the assembly list on the parts tab
            self.parent.wgt_sub_assm.Delete(_index)

            # Remove the part from the SQL database
            conn = config.sql_db.connect(config.cfg["db_location"])
            crsr = conn.cursor()

            # Remove image from database
            crsr.execute("DELETE FROM Children WHERE part_num=(?) AND part_rev=(?) AND child_num=(?) AND child_rev=(?);",
                         (_num, _rev, self.root.part_num, self.root.part_rev))

            conn.commit()
            crsr.close()
            conn.close()

            # Remove the part from the data structures holding the data for the assembly widget
            del self.root.data_wgt_sub[_num][_rev]
            del self.root.helper_wgt_sub[int(_index)]


class EditSuperAssemblies(BaseEditAssemblies):
    """Opens a dialog to edit the super-assemblies data for this part

        Args:
            parent (ref): Reference to the parent wx.object
            root (ref): Reference to the root parts tab

        Attributes:
            parent (ref): Reference to the parent wx.object
            root (ref): Reference to the root parts tab
            remove_choices (list: str): List of choices to be shown in the dropdown box
            title (str): Title to be shown on the dialog window
    """

    def load_data(self):
        """Load specific dialog box details - unique between subclasses"""

        self.title = "Edit List of Super-Assemblies"
        self.remove_choices = ["%s (%s r%s)" % (self.root.data_wgt_super[i[0]][i[1]], i[0], i[1])
                               for i in self.root.helper_wgt_super]

    def evt_add(self, event):
        """Add a part to the super-assembly list

            Args:
                event: A button event object passed from the button click
        """

        # Get part number and rev to remove
        _num = self.wgt_txt_add_num.GetValue()
        _rev = self.wgt_txt_add_rev.GetValue()

        # Only execute if the two text boxes have been filled out
        if _num != "" and _rev != "":
            conn = config.sql_db.connect(config.cfg["db_location"])
            crsr = conn.cursor()

            # Check if the super-assembly is already listed for this part
            crsr.execute("""SELECT EXISTS 
                            (
                                SELECT 
                                    1 
                                FROM Children
                                WHERE part_num=(?) 
                                    AND part_rev=(?) 
                                    AND child_num=(?) 
                                    AND child_rev=(?)
                            );""", (self.root.part_num, self.root.part_rev, _num, _rev))

            # If the super-assembly is not yet in the DB, carry out the additions
            if not crsr.fetchone()[0]:
                # Add the part from the assembly list on the parts tab
                self.parent.wgt_super_assm.Append("%s r%s" % (_num, _rev))

                # Insert the sub-assembly into the DB
                crsr.execute(
                    "INSERT INTO Children (part_num, part_rev, child_num, child_rev) VALUES ((?), (?), (?), (?));",
                    (self.root.part_num, self.root.part_rev, _num, _rev))
                conn.commit()

                # Get the name of the sub-assembly if it exists
                crsr.execute("SELECT name FROM Parts WHERE part_num=(?) AND part_rev=(?);", (_num, _rev))
                try:
                    _name = crsr.fetchone()[0]
                except:
                    _name = None

                crsr.close()
                conn.close()

                # Add the part to the data structures holding the data for the assembly widget
                self.root.helper_wgt_super.append([_num, _rev])
                if _num not in self.root.data_wgt_super:
                    self.root.data_wgt_super[_num] = {_rev: _name}
                elif _rev not in self.root.data_wgt_super[_num]:
                    self.root.data_wgt_super[_num][_rev] = _name

                # Clear the dialog widgets of any text
                self.wgt_txt_add_num.SetLabel("")
                self.wgt_txt_add_rev.SetLabel("")

    def evt_remove(self, event):
        """Remove a part from the super-assembly list

            Args:
                event: A button event object passed from the button click
        """

        # Get index of the selected part
        _index = self.wgt_drop_remove.GetSelection()

        # Only do anything if something is selected
        if _index != -1:
            # Get part number and rev to remove
            _num, _rev = self.root.helper_wgt_super[_index]

            # Remove the part from the dialog dropdown list
            self.wgt_drop_remove.Delete(_index)

            # Remove the part from the assembly list on the parts tab
            self.parent.wgt_super_assm.Delete(_index)

            # Remove the part from the SQL database
            conn = config.sql_db.connect(config.cfg["db_location"])
            crsr = conn.cursor()

            # Remove image from database
            crsr.execute(
                "DELETE FROM Children WHERE part_num=(?) AND part_rev=(?) AND child_num=(?) AND child_rev=(?);",
                (self.root.part_num, self.root.part_rev, _num, _rev))

            conn.commit()
            crsr.close()
            conn.close()

            # Remove the part from the data structures holding the data for the assembly widget
            del self.root.data_wgt_super[_num][_rev]
            del self.root.helper_wgt_super[int(_index)]


class EditComponentType(wx.Dialog):
    """Opens a dialog to edit the component type for this part

        Args:
            parent (ref): Reference to the parent wx.object
            root (ref): Reference to the root parts tab
            old_type (str): The value of the part's "type" before editing

        Attributes:
            parent (ref): Reference to the parent wx.object
            root (ref): Reference to the root parts tab
            old_type (str): The value of the part's "type" before editing
    """

    def __init__(self, parent, root, old_type):
        """Constructor"""
        super().__init__(parent)

        self.parent = parent
        self.root = root

        # The value of the type value before editing
        self.old_type = old_type

        # Type selection dropdown, with bind and sizer
        self.wgt_drop_type = wx.ComboBox(self, choices=["Assembly", "Manufactured", "Purchased"], style=wx.CB_READONLY)
        szr_drop = wx.StaticBoxSizer(wx.StaticBox(self, label="Select the type for this part to fall under"), orient=wx.HORIZONTAL)
        szr_drop.Add(self.wgt_drop_type, proportion=1, flag=wx.ALL, border=5)

        # Set initial selection
        self.wgt_drop_type.SetValue(self.old_type)

        # Dialog buttons with binds
        btn_commit = wx.Button(self, label='Commit')
        btn_commit.Bind(wx.EVT_BUTTON, self.evt_commit)
        btn_cancel = wx.Button(self, label='Cancel')
        btn_cancel.Bind(wx.EVT_BUTTON, self.evt_cancel)

        # Dialog button sizer
        szr_buttons = wx.BoxSizer(wx.HORIZONTAL)
        szr_buttons.Add(btn_commit)
        szr_buttons.Add(btn_cancel, flag=wx.LEFT, border=5)

        # Add everything to master sizer and set sizer for pane
        szr_master = wx.BoxSizer(wx.VERTICAL)
        szr_master.Add(szr_drop, proportion=1, flag=wx.ALL | wx.EXPAND, border=5)
        szr_master.Add(szr_buttons, flag=wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM, border=10)
        self.SetSizer(szr_master)

        # Set size and title
        self.SetSize((500, 160))
        self.SetTitle("Change the 'type' for this component")

        self.Bind(wx.EVT_CLOSE, self.evt_close)

    def evt_commit(self, event):
        """Execute when committing a change to the part type

            Args:
                event: A button event object passed from the button click
        """

        # Only carry out the event if any item in the dropdown is selected
        if self.wgt_drop_type.GetSelection() != -1:
            # The newly selected type
            _new_type = self.wgt_drop_type.GetValue()

            # If the type has changed then commit the change before closing the dialog
            if self.old_type != _new_type:
                # Change the widget text to reflect the change
                self.root.wgt_txt_part_type.SetLabel(_new_type)

                # Connect to the database
                conn = config.sql_db.connect(config.cfg["db_location"])
                crsr = conn.cursor()

                # Modify the existing cell in the database for existing part number and desired column
                crsr.execute("UPDATE Parts SET part_type=(?) WHERE part_num=(?) AND part_rev=(?);",
                             (_new_type, self.root.part_num, self.root.part_rev))

                conn.commit()
                crsr.close()
                conn.close()

            self.evt_close()

    def evt_cancel(self, event):
        """Cancel the change and close the dialog

            Args:
                event: A button event object passed from the button click
        """

        self.evt_close()

    def evt_close(self, *args):
        """Close the dialog

            Args:
                args[0]: Null, or an event object passed from the calling event
        """

        self.Destroy()


class AddNote(wx.Dialog):
    """Opens a dialog to add a note for this part

        Args:
            parent (ref): Reference to the parent wx.object
            root (ref): Reference to the root parts tab

        Attributes:
            parent (ref): Reference to the parent wx.object
            root (ref): Reference to the root parts tab
    """

    def __init__(self, parent, root):
        """Constructor"""
        super().__init__(parent)

        self.parent = parent
        self.root = root

        # Type selection dropdown, with bind and sizer
        self.wgt_txt_note = wx.TextCtrl(self, style=wx.TE_MULTILINE)
        szr_note = wx.StaticBoxSizer(wx.StaticBox(self, label="Note text to add"), orient=wx.HORIZONTAL)
        szr_note.Add(self.wgt_txt_note, proportion=1, flag=wx.ALL | wx.EXPAND, border=5)

        # Dialog buttons with binds
        btn_commit = wx.Button(self, label='Commit')
        btn_commit.Bind(wx.EVT_BUTTON, self.evt_commit)
        btn_cancel = wx.Button(self, label='Cancel')
        btn_cancel.Bind(wx.EVT_BUTTON, self.evt_cancel)

        # Dialog button sizer
        szr_buttons = wx.BoxSizer(wx.HORIZONTAL)
        szr_buttons.Add(btn_commit)
        szr_buttons.Add(btn_cancel, flag=wx.LEFT, border=5)

        # Add everything to master sizer and set sizer for pane
        szr_master = wx.BoxSizer(wx.VERTICAL)
        szr_master.Add(szr_note, proportion=1, flag=wx.ALL | wx.EXPAND, border=5)
        szr_master.Add(szr_buttons, flag=wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM, border=10)
        self.SetSizer(szr_master)

        # Set size and title
        self.SetSize((500, 200))
        self.SetTitle("Add a new note")

        self.Bind(wx.EVT_CLOSE, self.evt_close)

    def evt_commit(self, event):
        """Execute when committing a new note to the part

            Args:
                event: A button event object passed from the button click
        """

        # Only carry out the event if the textbox contains text
        if self.wgt_txt_note.GetValue():
            # Add an entry to the notes widget
            self.parent.add_note(datetime.datetime.now().strftime("%Y-%m-%d"),
                                 self.root.parent.user,
                                 self.wgt_txt_note.GetValue())

            # Connect to the database
            conn = config.sql_db.connect(config.cfg["db_location"])
            crsr = conn.cursor()

            # Modify the existing cell in the database for existing part number and desired column
            crsr.execute("INSERT INTO Notes (part_num, part_rev, author, date, note) VALUES ((?), (?), (?), (?), (?));",
                         (self.root.part_num,
                          self.root.part_rev,
                          self.root.parent.user,
                          datetime.datetime.now(),
                          self.wgt_txt_note.GetValue()))

            conn.commit()
            crsr.close()
            conn.close()

            self.evt_close()

    def evt_cancel(self, event):
        """Cancel the change and close the dialog

            Args:
                event: A button event object passed from the button click
        """

        self.evt_close()

    def evt_close(self, *args):
        """Close the dialog

          Args:
              args[0]: Null, or an event object passed from the calling event
        """

        self.Destroy()
