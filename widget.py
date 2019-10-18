# -*- coding: utf-8 -*-
"""This module contains widgets (composite panels) to be used in the application frame.

Attributes:
    module_level_variable1 (int): Module level variables may be documented in
        either the ``Attributes`` section of the module docstring, or in an
        inline docstring immediately following the variable.

        Either form is acceptable, but the two should not be mixed. Choose
        one convention to document module level variables and be consistent
        with it.
"""


# Import global colors
import global_colors

import wx
import glob
import os

import random
#import wx.lib.agw.flatnotebook as fnb
#import wx.lib.agw.ultimatelistctrl as ulc
import wx.lib.scrolledpanel as scrolled
from math import ceil, floor
from custom_dialog import *
import config
import fn_path
import datetime


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


class CompositeGallery(wx.Panel):
    """Custom widget that overlays an "add image" button on top of the WidgetGallery custom widget

            Class Variables:
                btn_size (int): Size of the "add image" button in the overlay

            Args:
                parent (ref): Reference to the parent wx.object

            Attributes:
                parent (ref): Reference to the parent wx.object
    """

    btn_size = 25

    def __init__(self, parent):
        """Constructor"""
        wx.Panel.__init__(self, parent)

        self.parent = parent

        # Button overlay and binding
        self.btn_add_image = wx.BitmapButton(self,
                                             bitmap=wx.Bitmap(fn_path.concat_gui('plus.png')),
                                             size=(CompositeGallery.btn_size,) * 2)

        # Image gallery subwidget
        self.pnl_gallery = WidgetGallery(self, self.parent)

        # Button overlay binding - Must be after subwidget to bind to
        self.btn_add_image.Bind(wx.EVT_BUTTON, self.pnl_gallery.evt_add_image)
        self.btn_add_image.Bind(wx.EVT_SET_FOCUS, self.evt_btn_no_focus)

        # Main sizer - do not add button so it floats
        szr_main = wx.BoxSizer(wx.VERTICAL)
        szr_main.Add(self.pnl_gallery, proportion=1, flag=wx.EXPAND)
        self.SetSizer(szr_main)

        # Bind button movement to resize
        self.Bind(wx.EVT_SIZE, self.evt_resize)

    def evt_resize(self, event):
        """Move the button overlay when resized

        Args:
            self: A reference to the parent wx.object instance
            event: A resize event object passed from the resize event
        """

        # Get width and height of the resize and subtract a tuple representing the scrollbar size
        (_w, _h) = event.GetSize() - (16, 0)

        # Move the button that adds more images
        self.btn_add_image.SetPosition((_w - CompositeGallery.btn_size, _h - CompositeGallery.btn_size))

        # Refresh Layout required for unknown reasons - otherwise odd scale behaviour on pnl_gallery
        self.Layout()

    def evt_btn_no_focus(self, event):
        """Prevents focus from being called on the buttons"""
        pass


class WidgetGallery(scrolled.ScrolledPanel):
    """Custom scrolled widget to contain a gallery of photos associated with the part of the parent tab

        Class Variables:
            icon_gap (int): Spacing between adjacent icons in sizer
            icon_size (int): Square size intended for the icon for each image

        Args:
            parent (ref): Reference to the parent wx.object
            root (ref): Reference to the root parts tab

        Attributes:
            parent (ref): Reference to the parent wx.object
            root (ref): Reference to the root parts tab

        TODO LIN000-04: Grey out and no select for new image text - extend to create general method for several dialogs
    """

    icon_gap = 5
    icon_size = 120

    def __init__(self, parent, root):
        """Constructor"""
        super().__init__(parent, style=wx.BORDER_SIMPLE)

        # Variables
        self.parent = parent
        self.root = root

        # Load list of images from database and store the image filenames with extensions
        conn = config.sql_db.connect(config.cfg["db_location"])
        crsr = conn.cursor()
        crsr.execute("SELECT image FROM Images WHERE part_num=(?) AND part_rev=(?);",
                     (self.root.part_num, self.root.part_rev))
        self.image_list = [i[0] for i in crsr.fetchall()]
        conn.close()

        # Create list of raw images
        self.images = [fn_path.concat_img(self.root.part_num, img) for img in self.image_list]

        # Create a grid sizer to contain image icons
        self.nrows, self.ncols = 1, len(self.images)
        self.purgelist = []
        self.sizer_grid = wx.GridSizer(rows=self.nrows + 1,
                                       cols=self.ncols,
                                       hgap=WidgetGallery.icon_gap,
                                       vgap=WidgetGallery.icon_gap)

        # Add cropped and scaled image icons to the grid sizer
        for r in range(self.nrows):
            for c in range(self.ncols):
                _n = self.ncols * r + c
                _tmp = crop_square(wx.Image(self.images[_n], wx.BITMAP_TYPE_ANY), WidgetGallery.icon_size)
                _temp = wx.StaticBitmap(self, id=_n, bitmap=wx.Bitmap(_tmp))
                _temp.Bind(wx.EVT_LEFT_UP, self.evt_image_click)
                self.purgelist.append(_temp)
                self.sizer_grid.Add(_temp, wx.EXPAND)

        # Main sizer
        szr_main = wx.BoxSizer(wx.VERTICAL)
        szr_main.Add(self.sizer_grid)
        self.SetSizer(szr_main)

        # Setup the scrolling style and function, wanting only vertical scroll to be available
        self.SetAutoLayout(1)
        self.SetupScrolling()
        self.ShowScrollbars(wx.SHOW_SB_NEVER, wx.SHOW_SB_ALWAYS)
        self.SetWindowStyle(wx.VSCROLL)

        # Bind button movement to resize
        self.Bind(wx.EVT_SIZE, self.evt_resize)

    def evt_resize(self, event):
        """Resize the image grid

        Retrieves width and height of the grid panel and adds/removes grid columns/rows to fit panel nicely.

        Args:
            self: A reference to the parent wx.object instance
            event: A resize event object passed from the resize event
        """

        # Get width and height of the resize
        (_w, _h) = event.GetSize()

        # Calculate the number of columns that fit in the scrolled panel, force a minimum of 1 columns
        _c = max((_w - WidgetGallery.icon_gap) // (WidgetGallery.icon_size + WidgetGallery.icon_gap), 1)

        # Redistribute rows and columns for the grid
        self.sizer_grid.SetCols(_c)
        self.sizer_grid.SetRows(ceil(len(self.image_list)/_c))

    def evt_image_click(self, event):
        """Call up the dialog for when an image is clicked

        Args:
            self: A reference to the parent wx.object instance
            event: The triggering click event object
        """

        # Load the "image clicked" dialog
        dialog = ImageDialog(self, self.root.mugshot, self.root.pnl_mugshot, self.image_list, self.purgelist.index(event.GetEventObject()), self.root.part_num, self.root.part_rev)
        dialog.ShowModal()
        dialog.Destroy()

    def evt_add_image(self, event):
        """Call up dialogs to add an image to the database

        Args:
            self: A reference to the parent wx.object instance
            event: The triggering event object - often click
        """

        # Open an explorer dialog to select images to import
        with wx.FileDialog(None, "Open",
                           wildcard="Images (*.png;*.jpg;*.bmp;*.gif)|*.png;*.jpg;*.jpeg;*.bmp;*.gif|"
                                    "PNG (*.png)|*.png|"
                                    "JPEG (*.jpg)|*.jpg;*.jpeg|"
                                    "BMP (*.bmp)|*.bmp|"
                                    "GIF (*.gif)|*.gif",
                           style=wx.FD_MULTIPLE | wx.FD_FILE_MUST_EXIST) as file_dialog:

            # Check if the user changed their mind about importing
            if file_dialog.ShowModal() == wx.ID_CANCEL:
                return

            # Make a list of chosen images to add to the database
            selected_files = file_dialog.GetPaths()

        # Proceed loading the file(s) chosen by the user to the "add image" dialog
        dialog = ImageAddDialog(self, selected_files, self.root.part_num, self.root.part_rev)
        dialog.ShowModal()
        dialog.Destroy()

    def evt_btn_no_focus(self, event):
        """Prevents focus from being called on the buttons"""
        pass
