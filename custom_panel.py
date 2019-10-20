# -*- coding: utf-8 -*-
"""This module contains custom dialog boxes to work with the main code base.

Attributes:
    module_level_variable1 (int): Module level variables may be documented in
        either the ``Attributes`` section of the module docstring, or in an
        inline docstring immediately following the variable.

        Either form is acceptable, but the two should not be mixed. Choose
        one convention to document module level variables and be consistent
        with it.
"""

COLORS = ["red", "blue", "black", "yellow", "green"]
NUMBERS = ["{:<6}|{:>25}|{}".format('JA1','23-JAN-2019', 'moretext for my othershit'), "{:<6}|{:<25}|{}".format('J1','23-J019','moretext for my othershit'), '2', '3', '4']
PANELS = ["107-00107"]#, "G39-00107", "777-00107"]
SUPLIST = ["999-00107", "G39-00107", "767-00107"]
SUBLIST = ["456-00107", "G39-06767", "776-04577"]
DATADIR = r'C:\Users\Ancient Abysswalker\PycharmProjects\LoCaS'

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

import widget


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


class ImgGridPanelWrapper(wx.Panel):

    btn_size = 25

    def __init__(self, parent, *args, **kwargs):
        """Constructor"""
        wx.Panel.__init__(self, parent, *args, **kwargs)

        self.parent = parent
        self.btn_add_image = wx.BitmapButton(self,
                                             bitmap=wx.Bitmap(fn_path.concat_gui('plus.png')),
                                             size=(ImgGridPanelWrapper.btn_size,) * 2)

        self.pnl_image_grid = ImgGridPanel(self)

        self.btn_add_image.Bind(wx.EVT_BUTTON, self.pnl_image_grid.event_add_image)
        self.btn_add_image.Bind(wx.EVT_SET_FOCUS, self.event_button_no_focus)

        #self.pnl_image_grid = ImgGridPanel()

        self.sizer_main = wx.BoxSizer(wx.VERTICAL)
        self.sizer_main.Add(self.pnl_image_grid, proportion=1, flag=wx.EXPAND)

        self.SetSizer(self.sizer_main)
        self.Layout()

        self.Bind(wx.EVT_SIZE, self.event_resize)

    def event_resize(self, *args):
        """Resize the image grid

        Retrieves width and height of the grid panel and adds/removes grid columns/rows to fit panel nicely.

        Args:
            self: A reference to the parent instance of ImgPanel.
            args[0]: A size object passed from the resize event.
        """
        # Get width and height of are inside scrolled panel; calculate number of columns that fit
        (_w, _h) = self.GetClientSize() - (16, 0)
        #_c = (_w - ImgGridPanel.icon_gap) // (ImgGridPanel.icon_size + ImgGridPanel.icon_gap)

        # Move the button that adds more images
        self.btn_add_image.SetPosition((_w - ImgGridPanelWrapper.btn_size, _h - ImgGridPanelWrapper.btn_size))

        self.Layout()

    def event_button_no_focus(self, event):
        """Prevents focus from being called on the buttons"""
        pass


class ImgGridPanel(scrolled.ScrolledPanel):
    """Custom scrolled grid panel that displays the photos associated with the part of the parent tab

        Class Variables:
            icon_gap (int): Spacing between adjacent icons in sizer
            icon_size (int): Square size intended for the icon for each image

        Args:
            parent (ref): Reference to the parent panel

        Attributes:
            parent (ref): Reference to the parent panel
            hyster_low (int): Keep for now
            hyster_high (int): Keep for now

        TODO LIN000-01: Normalize image grid behaviour on resize
        TODO LIN000-02: Fix initial row/col behaviour of grid
        TODO LIN000-03: Update image grid after adding image
        TODO LIN000-04: Grey out and no select for new image text - extend to create general method for several dialogs
    """

    icon_gap = 5
    icon_size = 120
    mug_size = 250
    btn_size = 35

    def __init__(self, parent):
        """Constructor"""
        super().__init__(parent, style=wx.BORDER_SIMPLE)

        # Variables
        self.hyster_low = 5
        self.hyster_high = ImgGridPanel.icon_size - self.hyster_low
        self.parent = parent.parent

        # Load list of images from database and store the image names with extensions
        conn = config.sql_db.connect(config.cfg["db_location"])
        crsr = conn.cursor()
        crsr.execute("SELECT image FROM Images WHERE part_num=(?) AND part_rev=(?);",
                     (self.parent.part_num, self.parent.part_rev))
        self.image_list = [i[0] for i in crsr.fetchall()]
        conn.close()

        # Draw button first, as the first object drawn stays on top
        # self.button_add_image = wx.BitmapButton(self,
        #                                         bitmap=wx.Bitmap(fn_path.concat_gui('plus.png')),
        #                                         size=(ImgGridPanel.btn_size,) * 2)
        # self.button_add_image.Bind(wx.EVT_BUTTON, self.event_add_image)
        # self.button_add_image.Bind(wx.EVT_SET_FOCUS, self.event_button_no_focus)

        # Create list of raw images
        self.images = [fn_path.concat_img(self.parent.part_num, img) for img in self.image_list]

        # Create a grid sizer to contain image icons
        self.nrows, self.ncols = 1, len(self.images)
        self.purgelist = []
        self.sizer_grid = wx.GridSizer(rows=self.nrows + 1,
                                       cols=self.ncols,
                                       hgap=ImgGridPanel.icon_gap,
                                       vgap=ImgGridPanel.icon_gap)

        # Add image icons to the grid
        for r in range(self.nrows):
            for c in range(self.ncols):
                _n = self.ncols * r + c
                _tmp = crop_square(wx.Image(self.images[_n], wx.BITMAP_TYPE_ANY), ImgGridPanel.icon_size)
                _temp = wx.StaticBitmap(self, id=_n, bitmap=wx.Bitmap(_tmp))
                _temp.Bind(wx.EVT_LEFT_UP, self.event_image_click)
                self.purgelist.append(_temp)
                self.sizer_grid.Add(_temp, wx.EXPAND)

        print(self.sizer_grid.GetChildren())

        # # Add a button to the grid to add further images
        # _tmp = wx.Image(fn_path.concat_gui("plus.png"), wx.BITMAP_TYPE_ANY).Rescale(*(ImgGridPanel.icon_size,) * 2)
        # _temp0 = wx.StaticBitmap(self, bitmap=wx.Bitmap(_tmp))
        # _temp0.Bind(wx.EVT_LEFT_UP, self.event_add_image)
        # self.sizer_grid.Add(_temp0, wx.EXPAND)

        sizer_stick = wx.BoxSizer(wx.VERTICAL)
        sizer_stick.Add(self.sizer_grid)
        self.SetSizer(sizer_stick)

        # Setup the scrolling style and function, wanting only vertical scroll to be available
        # self.SetAutoLayout(1)
        self.SetupScrolling()
        self.ShowScrollbars(wx.SHOW_SB_NEVER, wx.SHOW_SB_ALWAYS)
        self.SetWindowStyle(wx.VSCROLL)

        # Bind an event to any resizing of the grid
        #

        self.Bind(wx.EVT_SIZE, self.event_resize)
        #self.Bind(wx.EVT_MOTION, self.event_resize)

    def event_resize(self, *args):
        """Resize the image grid

        Retrieves width and height of the grid panel and adds/removes grid columns/rows to fit panel nicely.

        Args:
            self: A reference to the parent instance of ImgPanel.
            args[0]: A size object passed from the resize event.
        """
        # Get width and height of are inside scrolled panel; calculate number of columns that fit
        (_w, _h) = self.GetClientSize()
        _c = (_w - ImgGridPanel.icon_gap) // (ImgGridPanel.icon_size + ImgGridPanel.icon_gap)

        # Redistribute rows and columns for the grid
        #self.sizer_grid.SetCols(_c)
        #self.sizer_grid.SetRows(ceil(len(self.image_list)/_c))

        # Move the button that adds more images
        #self.button_add_image.SetPosition((_w - ImgGridPanel.btn_size, _h - ImgGridPanel.btn_size - self.CalcScrolledPosition(0, 0)[1]/2))
        pass

    def event_image_click(self, event):
        """Open image dialog"""
        # TODO REMOVE DUMMY TEXT
        print("Opening Image Index ", self.purgelist.index(event.GetEventObject()))
        dialog = ImageDialog(self, self.parent.mugshot, self.parent.pnl_mugshot, self.image_list, self.purgelist.index(event.GetEventObject()), self.parent.part_num, self.parent.part_rev)
        dialog.ShowModal()
        dialog.Destroy()

    def event_add_image(self, event):
        """Call up dialogs to add an image and its comment to the database"""
        with wx.FileDialog(None, "Open", "", "",
                           "Images (*.bmp;*.gif;*.png;*.jpg)|*.png;*.gif;*.bmp;*.jpg;*.jpeg",
                           wx.FD_MULTIPLE | wx.FD_FILE_MUST_EXIST) as file_dialog:

            if file_dialog.ShowModal() == wx.ID_CANCEL:
                return  # The user changed their mind

            selected_files = file_dialog.GetPaths()

        # Proceed loading the file chosen by the user
        dialog = ImageAddDialog(self, selected_files, self.parent.part_num, self.parent.part_rev)
        dialog.ShowModal()
        dialog.Destroy()

    def event_button_no_focus(self, event):
        """Prevents focus from being called on the buttons"""
        pass


class NotesPanel(wx.Panel):
    """Custom panel that contains and scales column headers according to a child scrolled grid panel

        Class Variables:
            vspace (int): Vertical spacing between rows in grid
            hspace (int): Horizontal spacing between columns in grid

        Args:
            parent (ref): Reference to the parent, generally

        Attributes:
            purgelist (list: wx.object): List of header objects to be purged on resize
            icon_gap (int): Distance between adjacent icons
            hyster_low (int): Keep for now
            hyster_high (int): Keep for now
    """

    vspace = 5
    hspace = 15

    def __init__(self, parent, *args, **kwargs):
        """Constructor"""
        wx.Panel.__init__(self, parent, *args, **kwargs)

        self.parent = parent
        self.purgelist = []

        # Draw button first, as the first object drawn stays on top
        self.button_add_note = wx.BitmapButton(self,
                                               bitmap=wx.Bitmap(fn_path.concat_gui('plus3.png')),
                                               size=(17,) * 2)
        self.button_add_note.Bind(wx.EVT_BUTTON, self.event_add_note)
        self.button_add_note.Bind(wx.EVT_SET_FOCUS, self.event_button_no_focus)

        # Set up sizer to contain header and scrolled notes
        self.panel_notes = NotesScrolled(self)

        self.panel_notes.Bind(wx.EVT_LEFT_UP, self.event_edit_notes_trigger)

        self.sizer_title = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer_main = wx.BoxSizer(wx.VERTICAL)
        self.sizer_main.Add(self.sizer_title, flag=wx.ALL | wx.EXPAND)
        self.sizer_main.Add(self.panel_notes, proportion=1, flag=wx.ALL | wx.EXPAND)

        # Refresh headers, repopulating self.sizer_title
        self.refresh_headers()

        self.SetSizer(self.sizer_main)
        self.Layout()

    def refresh_headers(self):
        """Refresh the column headers to reflect the column widths in the lower scrolled sizer"""

        column_widths = self.panel_notes.sizer_grid.GetColWidths()
        column_widths.append(0)
        column_widths.append(0)
        column_widths.append(0)

        for purge in self.purgelist:
            purge.Destroy()
        self.purgelist = []

        while not self.sizer_title.IsEmpty():
            self.sizer_title.Remove(0)

        # TODO LIN000-00: Once again check generalization for spacing
        self.purgelist.append(
            wx.StaticText(self, size=(max(column_widths[0], 25) + NotesPanel.hspace, -1),
                          label="Date", style=wx.ALIGN_LEFT))
        self.purgelist.append(
            wx.StaticText(self, size=(max(column_widths[1], 40) + NotesPanel.hspace, -1),
                          label="Author", style=wx.ALIGN_LEFT))
        self.purgelist.append(wx.StaticText(self, label="Note", style=wx.ALIGN_LEFT))
        self.purgelist.append(wx.StaticText(self, label="", style=wx.ALIGN_CENTER))  # TODO: Line removal failure

        self.sizer_title.Add(self.purgelist[0])
        self.sizer_title.Add(self.purgelist[1])
        self.sizer_title.Add(self.purgelist[2], proportion=1)
        self.sizer_title.Add(self.purgelist[3])

        self.sizer_title.RecalcSizes()

    def event_edit_notes_trigger(self, event):
        """Determine where in the scrolled panel was clicked and pass that to the method handling the dialog"""

        # Mouse positions within the overall panel, corrected for scroll. The math signage is odd, but works out
        pos_panel = self.panel_notes.ScreenToClient(wx.GetMousePosition())[1]
        pos_scroll = -self.panel_notes.CalcScrolledPosition(0, 0)[1]

        # Call method from the panel itself to handle dialog popup
        self.panel_notes.edit_notes((pos_panel + pos_scroll) // 20)

    def event_add_note(self, event):
        """Call up dialogs to add a note to the database"""
        pass

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

    def __init__(self, parent, *args, **kwargs):
        """Constructor"""
        super().__init__(parent, *args, **kwargs, style=wx.ALL | wx.VSCROLL)#, style=wx.BORDER_SIMPLE)

        self.parent = parent
        self.sizer_grid = wx.FlexGridSizer(3, NotesPanel.vspace, NotesPanel.hspace)
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

        # Bind an event to any resizing of the panel
        self.Bind(wx.EVT_SIZE, self.event_resize)
        self.Bind(wx.EVT_SCROLL, self.event_resize)

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

    def add_note(self):
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

    def event_resize(self, *args):
        """Resize the image grid

        Retrieves width and height of the grid panel and adds/removes grid columns/rows to fit panel nicely.

        Args:
            self: A reference to the parent instance of ImgPanel.
            args[0]: A size object passed from the resize event.
        """

        # Get width and height of are inside scrolled panel; taking into account the notes header
        (_w, _h) = (self.GetClientSize()[0], self.parent.GetClientSize()[1])

        # Move the button that adds more images
        self.parent.button_add_note.SetPosition((_w - 17, _h - 17))#(_w - ImgGridPanel.btn_size, _h - ImgGridPanel.btn_size))
        self.Refresh()
        self.Layout()
        # # Mouse positions within the overall panel, corrected for scroll. The math signage is odd, but works out
        # pos_panel = self.panel_notes.ScreenToClient(wx.GetMousePosition())[1]
        # pos_scroll = -self.panel_notes.CalcScrolledPosition(0, 0)[1]
        #
        # # Call method from the panel itself to handle dialog popup
        # self.panel_notes.edit_notes((pos_panel + pos_scroll) // 20)


class PartsTabPanel(wx.Panel):
    def __init__(self, pn, *args, **kwargs):
        """Constructor"""
        wx.Panel.__init__(self, size=(0, 0), *args, **kwargs)  # Needs size parameter to remove black-square
        self.SetDoubleBuffered(True)  # Remove slight strobing on tab switch
        self.SetCursor(wx.Cursor(wx.CURSOR_ARROW))  # Ensure that edit cursor does not show by default

        # Variable initialization
        self.parent = args[0]
        self.part_num = pn
        self.part_rev = "0"
        self.part_type = "You Should NEVER See This Text!!"
        self.short_description = "You Should NEVER See This Text!!"
        self.long_description = "You Should NEVER See This Text!!" \
                                "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Pellentesque tempor, elit " \
                                "sed pulvinar feugiat, tortor tortor posuere neque, eget ultrices eros est laoreet " \
                                "velit. Aliquam erat volutpat. Donec mi libero, elementum eu augue eget, iaculis " \
                                "dignissim ex. Nullam tincidunt nisl felis, eu efficitur turpis sodales et. Fusce " \
                                "vestibulum lacus sit amet ullamcorper efficitur. Morbi ultrices commodo leo, " \
                                "ultricies posuere mi finibus id. Nulla convallis velit ante, sed egestas nulla " \
                                "dignissim ac."
        self.suc_number = "BADBADBAD"
        self.suc_revision = "BAD"
        self.mugshot = None
        self.drawing = None
        self.sub_data_list = []
        self.super_data_list = []

        # Method to load data
        self.load_data()

        # Top row of information
        self.wgt_txt_part_num = wx.StaticText(self, label=self.part_num, style=wx.ALIGN_CENTER)
        self.wgt_txt_part_rev = wx.StaticText(self, label="R" + self.part_rev, style=wx.ALIGN_CENTER)
        self.wgt_txt_part_type = self.style_null_entry(self.part_type,
                                                       wx.StaticText(self,
                                                                     size=(100, -1),
                                                                     style=wx.ALIGN_CENTER))
        self.wgt_txt_description_short = self.style_null_entry(self.short_description,
                                                               wx.StaticText(self,
                                                                             size=(-1, -1),
                                                                             style=wx.ST_ELLIPSIZE_END))
        self.wgt_txt_description_long = self.style_null_entry(self.long_description,
                                                              wx.TextCtrl(self,
                                                                          size=(-1, 35),
                                                                          style=wx.TE_MULTILINE |
                                                                                wx.TE_WORDWRAP |
                                                                                wx.TE_READONLY |
                                                                                wx.BORDER_NONE))

        # Revision number buttons and bindings
        self.wgt_btn_rev_next = wx.Button(self, size=(10, -1))
        self.wgt_btn_rev_prev = wx.Button(self, size=(10, -1))
        self.wgt_btn_rev_next.Bind(wx.EVT_BUTTON, self.event_rev_next)
        self.wgt_btn_rev_prev.Bind(wx.EVT_BUTTON, self.event_rev_prev)

        # Sizer for top row of information
        self.szr_infoline = wx.BoxSizer(wx.HORIZONTAL)
        self.szr_infoline.Add(self.wgt_txt_part_num, border=5, flag=wx.ALL)
        self.szr_infoline.Add(self.wgt_btn_rev_prev, flag=wx.ALL)
        self.szr_infoline.Add(self.wgt_txt_part_rev, border=5, flag=wx.ALL)
        self.szr_infoline.Add(self.wgt_btn_rev_next, flag=wx.ALL)
        self.szr_infoline.AddSpacer(5)
        self.szr_infoline.Add(wx.StaticLine(self, style=wx.LI_VERTICAL), flag=wx.EXPAND)
        self.szr_infoline.Add(self.wgt_txt_part_type, border=5, flag=wx.ALL)
        self.szr_infoline.Add(wx.StaticLine(self, style=wx.LI_VERTICAL), flag=wx.EXPAND)
        self.szr_infoline.Add(self.wgt_txt_description_short, proportion=1, border=5, flag=wx.ALL | wx.EXPAND)


        # Lists containing sub and super assembly info
        self.wgt_sub_assm = wx.ListBox(self, size=(-1, -1), choices=[i[0] for i in self.helper_wgt_sub])#, size=(-1, 200), style=wx.LB_SINGLE)
        self.wgt_super_assm = wx.ListBox(self, size=(-1, -1), choices=[i[0] for i in self.helper_wgt_super])#, size=(-1, 200), style=wx.LB_SINGLE)


        self.szr_long_descrip = wx.StaticBoxSizer(wx.StaticBox(self, label='Extended Description'), orient=wx.VERTICAL)
        self.szr_long_descrip.Add(self.wgt_txt_description_long, flag=wx.ALL | wx.EXPAND)
        self.wgt_txt_description_long.Bind(wx.EVT_SET_FOCUS, self.onfocus)

        # Notes Panel
        self.pnl_notes = widget.CompositeNotes(self, self)
        self.szr_notes = wx.StaticBoxSizer(wx.StaticBox(self, label='Notes'), orient=wx.VERTICAL)
        self.szr_notes.Add(self.pnl_notes, proportion=1, flag=wx.ALL | wx.EXPAND)

        self.pnl_icon_grid = widget.CompositeGallery(self, self)
        self.szr_gallery = wx.StaticBoxSizer(wx.StaticBox(self, label='Image Gallery'), orient=wx.VERTICAL)
        self.szr_gallery.Add(self.pnl_icon_grid, proportion=1, flag=wx.ALL | wx.EXPAND)

        # Revision Binds
        self.revision_bind(self.wgt_txt_description_short, 'Short Description', self.part_num)  # Short Description Revision

        # Assembly list binds
        self.wgt_sub_assm.Bind(wx.EVT_LISTBOX, self.event_click_assm_lists)
        self.wgt_sub_assm.Bind(wx.EVT_MOTION, self.update_tooltip_sub)
        self.wgt_super_assm.Bind(wx.EVT_LISTBOX, self.event_click_assm_lists)
        self.wgt_super_assm.Bind(wx.EVT_MOTION, self.update_tooltip_super)

        self.pnl_mugshot = MugshotPanel(self)

        # Assembly List Sizers
        self.szr_sub_assm = wx.BoxSizer(wx.VERTICAL)
        self.szr_sub_assm.Add(wx.StaticText(self, label="Sub-Assemblies", style=wx.ALIGN_CENTER), border=5, flag=wx.ALL | wx.EXPAND)
        self.szr_sub_assm.Add(self.wgt_sub_assm, proportion=1, flag=wx.ALL | wx.EXPAND)
        self.szr_super_assm = wx.BoxSizer(wx.VERTICAL)
        self.szr_super_assm.Add(wx.StaticText(self, label="Super-Assemblies", style=wx.ALIGN_CENTER), border=5, flag=wx.ALL | wx.EXPAND)
        self.szr_super_assm.Add(self.wgt_super_assm, proportion=1, flag=wx.ALL | wx.EXPAND)
        self.szr_assm = wx.BoxSizer(wx.HORIZONTAL)
        self.szr_assm.Add(self.szr_sub_assm, proportion=1, flag=wx.ALL | wx.EXPAND)
        self.szr_assm.Add(self.szr_super_assm, proportion=1, flag=wx.ALL | wx.EXPAND)

        # Left Master Sizer
        self.szr_master_left = wx.BoxSizer(wx.VERTICAL)
        self.szr_master_left.Add(self.szr_infoline, flag=wx.ALL | wx.EXPAND)
        self.szr_master_left.Add(wx.StaticLine(self, style=wx.LI_HORIZONTAL), flag=wx.EXPAND)
        self.szr_master_left.Add(wx.StaticLine(self, style=wx.LI_HORIZONTAL), flag=wx.EXPAND)
        self.szr_master_left.AddSpacer(5)
        self.szr_master_left.Add(self.szr_long_descrip, flag=wx.ALL | wx.EXPAND)  # , border=15)
        self.szr_master_left.Add(self.szr_notes, proportion=1, flag=wx.ALL | wx.EXPAND)  # , border=15)
        self.szr_master_left.Add(self.szr_gallery, proportion=2, flag=wx.ALL | wx.EXPAND)

        # Right Master Sizer
        self.szr_master_right = wx.BoxSizer(wx.VERTICAL)
        self.szr_master_right.Add(self.pnl_mugshot, flag=wx.ALL | wx.EXPAND)
        self.szr_master_right.Add(self.szr_assm, proportion=1, flag=wx.ALL | wx.EXPAND)

        # Master Sizer
        self.szr_master = wx.BoxSizer(wx.HORIZONTAL)
        self.szr_master.Add(self.szr_master_left, proportion=1, flag=wx.ALL | wx.EXPAND)
        self.szr_master.Add(wx.StaticLine(self, style=wx.LI_VERTICAL), flag=wx.EXPAND)
        self.szr_master.Add(self.szr_master_right, flag=wx.ALL | wx.EXPAND)

        # Set Sizer
        self.SetSizer(self.szr_master)

    def revision_bind(self, target, field, pn):
        target.Bind(wx.EVT_LEFT_DCLICK, lambda event: self.revision_dialogue(event, pn, field))

    def revision_dialogue(self, event, pn, field):
        dialog = ModifyPartsFieldDialog(self, event.GetEventObject(), self.part_num, self.part_rev, "name", "Editing {0} of part {1}".format(field, pn))
        dialog.ShowModal()
        dialog.Destroy()

    def load_data(self):
        """Load the part data from the database"""

        # Load part data from database
        conn = config.sql_db.connect(config.cfg["db_location"])
        crsr = conn.cursor()
        crsr.execute("SELECT part_type, name, description, successor_num, successor_rev, mugshot, drawing "
                     "FROM Parts WHERE part_num=(?) AND part_rev=(?)",
                     (self.part_num, self.part_rev))

        # Load main data
        _tmp_sql_data = crsr.fetchone()
        if _tmp_sql_data:
            self.part_type, \
            self.short_description, \
            self.long_description, \
            self.suc_number, \
            self.suc_revision, \
            self.mugshot, \
            self.drawing \
                = _tmp_sql_data

        self.helper_wgt_super = []
        self.helper_wgt_sub = []
        self.data_wgt_super = {}
        self.data_wgt_sub = {}

        # populate Sub and Super Assembly lists
        conn = config.sql_db.connect(config.cfg["db_location"])
        crsr = conn.cursor()
        crsr.execute("SELECT part_num, part_rev, name FROM Parts WHERE (part_num, part_rev) IN"
                     "(SELECT part_num, part_rev FROM Children WHERE child_num=(?) AND child_rev=(?))",
                     (self.part_num, self.part_rev))

        for num, rev, name in crsr.fetchall():

            self.helper_wgt_sub.append([num, rev])

            if num not in self.data_wgt_sub:
                self.data_wgt_sub[num] = {rev: name}
            elif rev not in self.data_wgt_sub[num]:
                self.data_wgt_sub[num][rev] = name

        crsr.execute("SELECT part_num, part_rev, name FROM Parts WHERE (part_num, part_rev) IN"
                     "(SELECT child_num, child_rev FROM Children WHERE part_num=(?) AND part_rev=(?))",
                     (self.part_num, self.part_rev))

        for num, rev, name in crsr.fetchall():

            self.helper_wgt_super.append([num, rev])

            if num not in self.data_wgt_super:
                self.data_wgt_super[num] = {rev: name}
            elif rev not in self.data_wgt_super[num]:
                self.data_wgt_super[num][rev] = name

        conn.close()

    def style_null_entry(self, conditional, entry_field):
        """Style a text entry based on its SQL counterpart being NULL"""

        # Determine if SetValue or SetLabel is required to change text
        try:
            _ = entry_field.GetValue()
            edit_field = entry_field.SetValue
        except AttributeError:
            edit_field = entry_field.SetLabel

        # Set the color and text according to if NULL
        if conditional:
            edit_field(conditional)
        else:
            edit_field("No Entry")
            entry_field.SetForegroundColour(global_colors.no_entry)

        return entry_field

    def event_click_assm_lists(self, event):
        index = event.GetSelection()
        self.parent.open_parts_tab(event.GetEventObject().GetString(index), wx.GetKeyState(wx.WXK_SHIFT))
        event.GetEventObject().SetSelection(wx.NOT_FOUND)

    def update_tooltip_super(self, event):
        """
        Update the tooltip to show part name
        """

        mouse_pos = self.wgt_super_assm.ScreenToClient(wx.GetMousePosition())
        item_index = self.wgt_super_assm.HitTest(mouse_pos)

        if item_index != -1:
            num, rev = self.helper_wgt_super[item_index]
            new_msg = self.data_wgt_super[num][rev]
            if self.wgt_super_assm.GetToolTipText() != new_msg:
                self.wgt_super_assm.SetToolTip(new_msg)
        else:
            self.wgt_super_assm.SetToolTip("")

        event.Skip()

    def update_tooltip_sub(self, event):
        """
        Update the tooltip to show part name
        """

        mouse_pos = self.wgt_sub_assm.ScreenToClient(wx.GetMousePosition())
        item_index = self.wgt_sub_assm.HitTest(mouse_pos)

        if item_index != -1:
            num, rev = self.helper_wgt_sub[item_index]
            new_msg = self.data_wgt_sub[num][rev]
            if self.wgt_sub_assm.GetToolTipText() != new_msg:
                self.wgt_sub_assm.SetToolTip(new_msg)
        else:
            self.wgt_sub_assm.SetToolTip("")

        event.Skip()

    def onfocus(self, event):
        """Set cursor to default and pass before default on-focus method"""
        self.SetCursor(wx.Cursor(wx.CURSOR_ARROW))
        pass

    def event_rev_next(self, event):
        """Toggle to next revision if possible"""
        return

        if True:
            self.part_rev += 1

            self.text_rev_number.SetLabel("R" + str(self.part_rev))

            self.sizer_partline.Layout()

            # Hook a refresh()

        event.Skip()

    def event_rev_prev(self, event):
        """Toggle to next revision if possible"""
        return

        if self.part_rev > 0:
            self.part_rev -= 1

            self.text_rev_number.SetLabel("R" + str(self.part_rev))

            self.sizer_partline.Layout()

            # Hook a refresh()

        event.Skip()


class MugshotPanel(wx.Panel):

    mug_size = 250
    btn_size = 40

    def __init__(self, parent, *args, **kwargs):
        """Constructor"""
        wx.Panel.__init__(self, parent, *args, **kwargs)

        self.parent = parent

        # Primary part image
        if self.parent.mugshot:
            image = wx.Image(fn_path.concat_img(self.parent.part_num, self.parent.mugshot), wx.BITMAP_TYPE_ANY)
        else:
            image = wx.Image(fn_path.concat_gui('missing_mugshot.png'), wx.BITMAP_TYPE_ANY)

        # Draw button first as first drawn stays on top
        self.button_dwg = wx.BitmapButton(self,
                                          bitmap=wx.Bitmap(fn_path.concat_gui('schematic.png')),
                                          size=(MugshotPanel.btn_size,) * 2,
                                          pos=(0, MugshotPanel.mug_size - MugshotPanel.btn_size))
        self.button_dwg.Bind(wx.EVT_SET_FOCUS, self.event_button_no_focus)
        self.button_dwg.Bind(wx.EVT_BUTTON, self.event_drawing)

        self.imageBitmap = wx.StaticBitmap(self, wx.ID_ANY, wx.Bitmap(crop_square(image, MugshotPanel.mug_size)))

        self.sizer_main = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer_main.Add(self.imageBitmap, flag=wx.ALL)
        # self.button_dwg2 = wx.Button(self, size=(500, 500), pos=(50, 0))
        #self.button_dwg = wx.Button(self, size=(50, 50), pos=(50, 0))
        #self.sizer_main.Add(self.button_dwg, flag=wx.ALL)
        #self.button_dwg2 = wx.Button(self, size=(500, 500), pos=(50, 0))

        self.SetSizer(self.sizer_main)
        self.Layout()

    def refresh(self, new_image=None):
        if new_image:
            temp = fn_path.concat_img(self.parent.part_num, new_image)
        else:
            temp = fn_path.concat_gui('missing_mugshot.png')
        self.imageBitmap.SetBitmap(wx.Bitmap(crop_square(wx.Image(temp, wx.BITMAP_TYPE_ANY), MugshotPanel.mug_size)))

    def event_drawing(self, event):
        """Loads a dialog or opens a program (unsure) showing the production drawing of said part"""

        _dlg = wx.RichMessageDialog(self,
                                   caption="This feature is not yet implemented",
                                   message="This feature will load a production drawing of the current part",
                                   style=wx.OK | wx.ICON_INFORMATION)
        _dlg.ShowModal()
        _dlg.Destroy()

    def event_button_no_focus(self, event):
        """Prevents focus from being called on the buttons"""
        pass


class InterfaceTabs(wx.Notebook):
    def __init__(self, *args, **kwargs):
        wx.Notebook.__init__(self, *args, **kwargs)
        self.SetDoubleBuffered(True)  # Remove slight strobing on tab switch

        self.panels = []
        for name in PANELS:
            panel = PartsTabPanel(name, self)
            self.panels.append(panel)
            self.AddPage(panel, name)

    def open_parts_tab(self, part_num, opt_stay=False):
        """Open a new tab using the provided part number

            Args:
                part_num (string): The part number to open as a new tab
                opt_stay (bool): If true, do not change to newly opened tab
        """

        conn = config.sql_db.connect(config.cfg["db_location"])
        crsr = conn.cursor()
        crsr.execute("SELECT EXISTS (SELECT 1 FROM Parts WHERE part_num=(?))", (part_num,))
        _check = crsr.fetchone()[0]
        conn.close()

        if _check:
            panel = PartsTabPanel(part_num, self)
            if part_num not in [pnl.part_num for pnl in self.panels]:
                self.panels.append(panel)
                self.AddPage(panel, part_num)
                if not opt_stay:
                    self.SetSelection(self.GetPageCount() - 1)
            elif not opt_stay:
                self.SetSelection([pnl.part_num for pnl in self.panels].index(part_num))
        else:
            _dlg = wx.RichMessageDialog(self,
                                        caption="Part Not In System",
                                        message="This part is not currently added to the system.\n"
                                                  "Do you want to add %s to the database?" % (part_num,),
                                        style=wx.YES_NO | wx.NO_DEFAULT | wx.ICON_WARNING)
            if _dlg.ShowModal() == wx.ID_YES:

                conn = config.sql_db.connect(config.cfg["db_location"])
                crsr = conn.cursor()
                crsr.execute("INSERT INTO Parts (part_num, part_rev) VALUES ((?), (?));",
                             (part_num, "0"))
                crsr.close()
                conn.commit()

                panel = PartsTabPanel(part_num, self)
                if part_num not in [pnl.part_num for pnl in self.panels]:
                    self.panels.append(panel)
                    self.AddPage(panel, part_num)
                    if not opt_stay:
                        self.SetSelection(self.GetPageCount() - 1)
                elif not opt_stay:
                    self.SetSelection([pnl.part_num for pnl in self.panels].index(part_num))
            _dlg.Destroy()
