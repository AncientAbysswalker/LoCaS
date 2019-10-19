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

import custom_dialog
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
            root (ref): Reference to the root parts tab

        Attributes:
            parent (ref): Reference to the parent wx.object
            root (ref): Reference to the root parts tab
    """

    btn_size = 25

    def __init__(self, parent, root):
        """Constructor"""
        wx.Panel.__init__(self, parent)

        self.parent = parent
        self.root = root

        # Button overlay and binding
        self.btn_add_image = wx.BitmapButton(self,
                                             bitmap=wx.Bitmap(fn_path.concat_gui('plus.png')),
                                             size=(CompositeGallery.btn_size,) * 2)

        # Image gallery subwidget
        self.pnl_gallery = WidgetGallery(self, self.root)

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
        dialog = custom_dialog.ImageDialog(self, self.root.mugshot, self.root.pnl_mugshot, self.image_list, self.purgelist.index(event.GetEventObject()), self.root.part_num, self.root.part_rev)
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
        dialog = custom_dialog.ImageAddDialog(self, selected_files, self.root.part_num, self.root.part_rev)
        dialog.ShowModal()
        dialog.Destroy()

    def evt_btn_no_focus(self, event):
        """Prevents focus from being called on the buttons"""
        pass


class CompositeNotes(wx.Panel):
    """Custom panel that contains and scales column headers according to a child scrolled grid panel

        Class Variables:
            btn_size (int): Size of the "add image" button in the overlay
            row_gap (int): Vertical spacing between rows in grid
            col_gap (int): Horizontal spacing between columns in grid

        Args:
            parent (ref): Reference to the parent wx.object
            root (ref): Reference to the root parts tab

        Attributes:
            parent (ref): Reference to the parent wx.object
            root (ref): Reference to the root parts tab
    """

    btn_size = 25
    row_gap = 5
    col_gap = 15

    def __init__(self, parent, root):
        """Constructor"""
        wx.Panel.__init__(self, parent)

        self.parent = parent
        self.root = root

        self.purgelist = []

        # Draw button first, as the first object drawn stays on top
        self.btn_add_note = wx.BitmapButton(self,
                                            bitmap=wx.Bitmap(fn_path.concat_gui('plus.png')),
                                            size=(CompositeNotes.btn_size,) * 2)

        # Set up sizer to contain header and scrolled notes
        self.pnl_notes = NotesScrolled(self, self.root)

        # Button overlay binding - Must be after subwidget to bind to
        self.btn_add_note.Bind(wx.EVT_BUTTON, self.pnl_notes.event_add_note)
        self.btn_add_note.Bind(wx.EVT_SET_FOCUS, self.event_button_no_focus)

        # Binding for clicking between notes text
        self.pnl_notes.Bind(wx.EVT_LEFT_UP, self.event_edit_notes_trigger)

        # Main Sizer
        self.szr_title = wx.BoxSizer(wx.HORIZONTAL)
        self.szr_main = wx.BoxSizer(wx.VERTICAL)
        self.szr_main.Add(self.szr_title, flag=wx.ALL | wx.EXPAND)
        self.szr_main.Add(self.pnl_notes, proportion=1, flag=wx.ALL | wx.EXPAND)

        # Refresh headers, repopulating self.sizer_title
        self.refresh_headers()

        # Set sizer and resize
        self.SetSizer(self.szr_main)
        self.Layout()

        # Bind button movement to resize
        self.Bind(wx.EVT_SIZE, self.evt_resize)

    def refresh_headers(self):
        """Refresh the column headers to reflect the column widths in the lower scrolled sizer"""

        column_widths = self.pnl_notes.sizer_grid.GetColWidths()
        column_widths.append(0)
        column_widths.append(0)
        column_widths.append(0)

        for purge in self.purgelist:
            purge.Destroy()
        self.purgelist = []

        while not self.szr_title.IsEmpty():
            self.szr_title.Remove(0)

        # TODO LIN000-00: Once again check generalization for spacing
        self.purgelist.append(
            wx.StaticText(self, size=(max(column_widths[0], 25) + CompositeNotes.col_gap, -1),
                          label="Date", style=wx.ALIGN_LEFT))
        self.purgelist.append(
            wx.StaticText(self, size=(max(column_widths[1], 40) + CompositeNotes.col_gap, -1),
                          label="Author", style=wx.ALIGN_LEFT))
        self.purgelist.append(wx.StaticText(self, label="Note", style=wx.ALIGN_LEFT))
        self.purgelist.append(wx.StaticText(self, label="", style=wx.ALIGN_CENTER))  # TODO: Line removal failure

        self.szr_title.Add(self.purgelist[0])
        self.szr_title.Add(self.purgelist[1])
        self.szr_title.Add(self.purgelist[2], proportion=1)
        self.szr_title.Add(self.purgelist[3])

        self.szr_title.RecalcSizes()

    def event_edit_notes_trigger(self, event):
        """Determine where in the scrolled panel was clicked and pass that to the method handling the dialog"""

        # Mouse positions within the overall panel, corrected for scroll. The math signage is odd, but works out
        pos_panel = self.pnl_notes.ScreenToClient(wx.GetMousePosition())[1]
        pos_scroll = -self.pnl_notes.CalcScrolledPosition(0, 0)[1]

        # Call method from the panel itself to handle dialog popup
        self.pnl_notes.edit_notes((pos_panel + pos_scroll) // 20)

    def event_add_note(self, event):
        """Call up dialogs to add a note to the database"""
        pass

    def evt_resize(self, event):
        """Move the button overlay when resized

        Args:
            self: A reference to the parent wx.object instance
            event: A resize event object passed from the resize event
        """

        # Get width and height of the resize and subtract a tuple representing the scrollbar size
        (_w, _h) = event.GetSize() - (16, 0)

        # Move the button that adds more images
        self.btn_add_note.SetPosition((_w - CompositeNotes.btn_size, _h - CompositeNotes.btn_size))

        # Refresh Layout required for unknown reasons - otherwise odd scale behaviour on pnl_gallery
        self.Layout()

    def event_button_no_focus(self, event):
        """Prevents focus from being called on the buttons"""
        pass


class NotesScrolled(scrolled.ScrolledPanel):
    """Scrolled panel containing a grid of notes data.

    This class is generally the child of NotesPanel, which contains the headers outside the scroll

    Attributes:
        likes_spam: A boolean indicating if we like SPAM or not.
        eggs: An integer count of the eggs we have laid.
    """

    def __init__(self, parent, root):
        """Constructor"""
        super().__init__(parent, style=wx.ALL | wx.VSCROLL)#, style=wx.BORDER_SIMPLE)

        self.parent = parent
        self.sizer_grid = wx.FlexGridSizer(3, CompositeNotes.row_gap, CompositeNotes.col_gap)
        self.sizer_grid.AddGrowableCol(2)
        self.sizer_grid.SetFlexibleDirection(wx.HORIZONTAL)
        self.sizer_grid.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_NONE)
        self.notes_list = []

        # TODO LIN000-00: Keep for the moment, in case hiding headers is the key to generalizing spacing
        # self.sizer_grid.Add(wx.StaticText(self, label="Date"))
        # self.sizer_grid.Add(wx.StaticText(self, label="Author"))
        # self.sizer_grid.Add(wx.StaticText(self, label="Note"))

        self.SetSizer(self.sizer_grid)
        self.Layout()
        self.min_widths = self.sizer_grid.GetColWidths()
        print(self.min_widths)

        # for header_item in self.sizer_grid.GetChildren():
        #     header_item.Show(False)

        self.load_notes()

        # Setup the scrolling style and function, wanting only vertical scroll to be available
        self.SetupScrolling()
        self.ShowScrollbars(wx.SHOW_SB_NEVER, wx.SHOW_SB_ALWAYS)
        self.SetWindowStyle(wx.VSCROLL)


    def load_notes(self):
        """Open SQL database and load notes from table"""

        # Load notes from database
        conn = config.sql_db.connect(config.cfg["db_location"])
        crsr = conn.cursor()
        crsr.execute("SELECT date, author, note FROM Notes WHERE part_num=(?) AND part_rev=(?)",
                     (self.parent.parent.part_num, "0"))#self.parent.parent.part_rev))
        _tmp_list = crsr.fetchall()
        conn.close()

        # Sort and remove non-date information from the datetime string
        if _tmp_list:
            _tmp_list = [(a[0][:10],)+a[1:] for a in sorted(_tmp_list, key=lambda x: x[0])]

        # Add the notes to the grid
        # TODO LIN000-00: Unsure that this forced sizing will work cross-platform. Check and/or rewrite to generalize
        for i, note in enumerate(_tmp_list):
            _tmp_item = []
            _tmp_item.append(wx.StaticText(self, id=i, label=note[0], style=wx.EXPAND))
            _tmp_item.append(wx.StaticText(self, size=(40, -1), id=i, label=note[1], style=wx.EXPAND))
            _tmp_item.append(wx.StaticText(self, size=(50, -1), id=i, label=note[2], style=wx.ST_ELLIPSIZE_END))

            for item in _tmp_item:
                item.Bind(wx.EVT_LEFT_UP, self.event_edit_notes_trigger)
                self.sizer_grid.Add(item, flag=wx.ALL | wx.EXPAND)

            self.notes_list.append(_tmp_item)

            # _tmp_item = wx.StaticText(self, id=i, label=note[0], style=wx.EXPAND)
            # self.sizer_grid.Add(_tmp_item, flag=wx.ALL | wx.EXPAND)
            # _tmp_item.Bind(wx.EVT_LEFT_UP, self.event_note_click)
            # _tmp_item = wx.StaticText(self, size=(40, -1), id=i, label=note[1], style=wx.EXPAND)
            # self.sizer_grid.Add(_tmp_item, flag=wx.ALL | wx.EXPAND)
            # _tmp_item.Bind(wx.EVT_LEFT_UP, self.event_note_click)
            # _tmp_item = wx.StaticText(self, size=(50, -1), id=i, label=note[2], style=wx.ST_ELLIPSIZE_END)
            # self.sizer_grid.Add(_tmp_item, flag=wx.ALL | wx.EXPAND)
            # _tmp_item.Bind(wx.EVT_LEFT_UP, self.event_note_click)

    def event_add_note(self):
        pass

    def event_edit_notes_trigger(self, event):
        """Determine which entry in the scrolled panel was clicked and pass that to the method handling the dialog"""

        self.edit_notes(event.GetEventObject().GetId())

    def edit_notes(self, my_index):
        """Open note-editing dialog
        TODO Implement note-editing
        """

        print(self.notes_list[my_index][0].GetLabel(), self.notes_list[my_index][1].GetLabel(), self.notes_list[my_index][2].GetLabel())
        #dialog = ImageDialog(self.image_list, event.GetEventObject().GetId(), self.parent.part_num, self.parent.part_rev)
        #dialog.ShowModal()
        #dialog.Destroy()