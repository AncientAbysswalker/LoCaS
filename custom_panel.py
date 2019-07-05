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
        self.parent = parent

        # Load list of images from database and store the image names with extensions
        conn = config.sql_db.connect(config.db_location)
        crsr = conn.cursor()
        crsr.execute("SELECT image FROM Images WHERE part_num=(?) AND part_rev=(?);",
                     (self.parent.part_number, self.parent.part_revision))
        self.image_list = [i[0] for i in crsr.fetchall()]
        conn.close()

        # Draw button first, as the first object drawn stays on top
        self.button_add_image = wx.BitmapButton(self,
                                                bitmap=wx.Bitmap(fn_path.concat_gui('plus.png')),
                                                size=(ImgGridPanel.btn_size,) * 2)
        self.button_add_image.Bind(wx.EVT_BUTTON, self.event_add_image)
        self.button_add_image.Bind(wx.EVT_SET_FOCUS, self.event_button_no_focus)


        # Create list of raw images
        self.images = [fn_path.concat_img(parent.part_number, img) for img in self.image_list]

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
        self.Bind(wx.EVT_SIZE, self.resize_grid)

    def resize_grid(self, *args):
        """Resize the image grid

        Retrieves width and height of the grid panel and adds/removes grid columns/rows to fit panel nicely.

        Args:
            self: A reference to the parent instance of ImgPanel.
            args[0]: A size object passed from the resize event.
        """

        (w, h) = self.GetClientSize()

        if self.ncols > 1 and w < self.ncols * ImgGridPanel.icon_size + (self.ncols + 1) * ImgGridPanel.icon_gap - self.hyster_low:
            self.ncols -= 1
            self.nrows = max(ceil(len(self.images) / self.ncols), ceil((h + ImgGridPanel.icon_gap) / (ImgGridPanel.icon_size + ImgGridPanel.icon_gap)))
            self.sizer_grid.SetCols(self.ncols)
            self.sizer_grid.SetRows(self.nrows)
        elif w > self.ncols * ImgGridPanel.icon_size + (self.ncols + 1) * ImgGridPanel.icon_gap + self.hyster_high:
            self.ncols += 1
            self.nrows = max(ceil(len(self.images) / self.ncols), ceil((h + ImgGridPanel.icon_gap) / (ImgGridPanel.icon_size + ImgGridPanel.icon_gap)))
            self.sizer_grid.SetCols(self.ncols)
            self.sizer_grid.SetRows(self.nrows)

        if self.nrows > 1 and h < self.nrows * ImgGridPanel.icon_size + (self.nrows + 1) * ImgGridPanel.icon_gap - self.hyster_low:
            self.nrows = max(ceil(len(self.images) / self.ncols), ceil((h + ImgGridPanel.icon_gap) / (ImgGridPanel.icon_size + ImgGridPanel.icon_gap)))
            self.sizer_grid.SetRows(self.nrows)
        elif h > self.nrows * ImgGridPanel.icon_size + (self.nrows + 1) * ImgGridPanel.icon_gap + self.hyster_high:
            self.nrows = max(ceil(len(self.images) / self.ncols), ceil((h + ImgGridPanel.icon_gap) / (ImgGridPanel.icon_size + ImgGridPanel.icon_gap)))
            self.sizer_grid.SetRows(self.nrows)

        # Move the button that adds more images
        self.button_add_image.SetPosition((w - ImgGridPanel.btn_size, h - ImgGridPanel.btn_size))

    def event_image_click(self, event):
        """Open image dialog"""
        # TODO REMOVE DUMMY TEXT
        print("freaking mongrels", self.purgelist.index(event.GetEventObject()))
        dialog = ImageDialog(self, self.parent.mugshot, self.parent.mugshot_panel, self.image_list, self.purgelist.index(event.GetEventObject()), self.parent.part_number, self.parent.part_revision)
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
        dialog = ImageAddDialog(self, selected_files, self.parent.part_number, self.parent.part_revision)
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

        # Set up sizer to contain header and scrolled notes
        self.panel_notes = NotesScrolled(self)

        self.panel_notes.Bind(wx.EVT_LEFT_UP, self.test_fulnote_click_trigger)

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
        print("pickles", column_widths)

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
        self.purgelist.append(wx.StaticText(self, label="", style=wx.ALIGN_CENTER)) # TODO: Line removal failure

        self.sizer_title.Add(self.purgelist[0])
        self.sizer_title.Add(self.purgelist[1])
        self.sizer_title.Add(self.purgelist[2], proportion=1)
        self.sizer_title.Add(self.purgelist[3])

        self.sizer_title.RecalcSizes()

    def test_fulnote_click_trigger(self, event):
        """Open note-editing dialog
        TODO LIN001-00: Implement note-editing event
        """

        print(event.GetEventObject().GetId())


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
        conn = config.sql_db.connect(config.db_location)
        crsr = conn.cursor()
        crsr.execute("SELECT date, author, note FROM Notes WHERE part_num=(?) AND part_rev=(?)",
                     (self.parent.parent.part_number, "0"))#self.parent.parent.part_revision))
        _tmp_list = crsr.fetchall()
        conn.close()

        # Sort and remove non-date information from the datetime string
        if _tmp_list:
            _tmp_list = [(a[0][:10],)+a[1:] for a in sorted(_tmp_list, key=lambda x: x[0])]

        # Add the notes to the grid
        # TODO LIN000-00: Unsure that this forced sizing will work cross-platform. Check and/or rewrite to generalize
        for i, note in enumerate(_tmp_list):
            _tmp_item = wx.StaticText(self, id=i, label=note[0], style=wx.EXPAND)
            self.sizer_grid.Add(_tmp_item, flag=wx.ALL | wx.EXPAND)
            _tmp_item.Bind(wx.EVT_LEFT_UP, self.event_note_click)
            _tmp_item = wx.StaticText(self, size=(40, -1), id=i, label=note[1], style=wx.EXPAND)
            self.sizer_grid.Add(_tmp_item, flag=wx.ALL | wx.EXPAND)
            _tmp_item.Bind(wx.EVT_LEFT_UP, self.event_note_click)
            _tmp_item = wx.StaticText(self, size=(50, -1), id=i, label=note[2], style=wx.ST_ELLIPSIZE_END)
            self.sizer_grid.Add(_tmp_item, flag=wx.ALL | wx.EXPAND)
            _tmp_item.Bind(wx.EVT_LEFT_UP, self.event_note_click)

    def add_note(self):
        pass

    def event_note_click(self, event):
        """Open note-editing dialog
        TODO LIN001-00: Implement note-editing event
        """

        print(event.GetEventObject().GetId())
        #dialog = ImageDialog(self.image_list, event.GetEventObject().GetId(), self.parent.part_number, self.parent.part_revision)
        #dialog.ShowModal()
        #dialog.Destroy()


class PartsTabPanel(wx.Panel):
    def __init__(self, pn, *args, **kwargs):
        """Constructor"""
        wx.Panel.__init__(self, size=(0, 0), *args, **kwargs)  # Needs size parameter to remove black-square
        self.SetDoubleBuffered(True)  # Remove slight strobing on tab switch
        self.SetCursor(wx.Cursor(wx.CURSOR_ARROW))  # Ensure that edit cursor does not show by default

        self.parent = args[0]
        self.part_number = pn
        self.part_revision = "0"
        self.part_type = "You Should NEVER See This Text!!"
        self.short_description = "You Should NEVER See This Text!!"
        self.long_description = "You Should NEVER See This Text!!" \
                                "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Pellentesque tempor, elit " \
                                "sed pulvinar feugiat, tortor tortor posuere neque, eget ultrices eros est laoreet " \
                                "velit. Aliquam erat volutpat. Donec mi libero, elementum eu augue eget, iaculis " \
                                "dignissim ex. Nullam tincidunt nisl felis, eu efficitur turpis sodales et. Fusce " \
                                "vestibulum lacus sit amet ullamcorper efficitur. Morbi ultrices commodo leo, " \
                                "ultricies posuere mi finibus id. Nulla convallis velit ante, sed egestas nulla " \
                                "dignissim ac. "
        self.suc_number = "BADBADBAD"
        self.suc_revision = "BAD"
        self.mugshot = None
        self.drawing = None

        self.load_data()

        # Top row of information
        self.part_number_text = wx.StaticText(self, label=self.part_number, style=wx.ALIGN_CENTER)
        self.text_rev_number = wx.StaticText(self, label="R" + self.part_revision, style=wx.ALIGN_CENTER)
        # self.part_type_text = wx.StaticText(self, size=(100, -1), label=self.part_type, style=wx.ALIGN_CENTER)
        #         # self.short_descrip_text = wx.StaticText(self, size=(-1, -1), label=self.short_description, style=wx.ST_ELLIPSIZE_END)
        self.part_type_text = self.style_null_entry(self.part_type,
                                                    wx.StaticText(self, size=(100, -1), style=wx.ALIGN_CENTER))
        self.short_descrip_text = self.style_null_entry(self.short_description,
                                                    wx.StaticText(self, size=(-1, -1), style=wx.ST_ELLIPSIZE_END))

        # Revision number buttons and bindings
        self.button_rev_next = wx.Button(self, size=(10, -1))
        self.button_rev_prev = wx.Button(self, size=(10, -1))
        self.button_rev_next.Bind(wx.EVT_BUTTON, self.event_rev_next)
        self.button_rev_prev.Bind(wx.EVT_BUTTON, self.event_rev_prev)

        # Sizer for top row of information
        self.sizer_partline = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer_partline.Add(self.part_number_text, border=5, flag=wx.ALL)
        self.sizer_partline.Add(self.button_rev_prev, flag=wx.ALL)
        self.sizer_partline.Add(self.text_rev_number, border=5, flag=wx.ALL)
        self.sizer_partline.Add(self.button_rev_next, flag=wx.ALL)
        self.sizer_partline.AddSpacer(5)
        self.sizer_partline.Add(wx.StaticLine(self, style=wx.LI_VERTICAL), flag=wx.EXPAND)
        self.sizer_partline.Add(self.part_type_text, border=5, flag=wx.ALL)
        self.sizer_partline.Add(wx.StaticLine(self, style=wx.LI_VERTICAL), flag=wx.EXPAND)
        self.sizer_partline.Add(self.short_descrip_text, proportion=1, border=5, flag=wx.ALL | wx.EXPAND)



        # EVENTUALLY SWAP OUT FOR ULTIMATELISTBOX?
        self.sub_assembly_list = wx.ListBox(self, size=(-1, -1), choices=SUBLIST)#, size=(-1, 200), style=wx.LB_SINGLE)
        self.sup_assembly_list = wx.ListBox(self, size=(-1, -1), choices=SUPLIST)#, size=(-1, 200), style=wx.LB_SINGLE)

        # Load data into dictionary for mouseover on listboxes - superassemblies
        # TODO: Add consideration for revision
        conn = config.sql_db.connect(config.db_location)
        crsr = conn.cursor()
        crsr.execute("SELECT part_num, part_rev, name FROM Parts WHERE (part_num, part_rev) IN"
                     "(SELECT child_num, child_rev FROM Children WHERE part_num=(?) AND part_rev=(?))",
                     (self.part_number, self.part_revision))
        self.parts_super = {x: y for x, _, y in crsr.fetchall()}
        conn.close()

        # Load data into dictionary for mouseover on listboxes - subassemblies
        # TODO: Add consideration for revision
        conn = config.sql_db.connect(config.db_location)
        crsr = conn.cursor()
        crsr.execute("SELECT part_num, part_rev, name FROM Parts WHERE (part_num, part_rev) IN"
                     "(SELECT part_num, part_rev FROM Children WHERE child_num=(?) AND child_rev=(?))",
                     (self.part_number, self.part_revision))
        self.parts_sub = {x: y for x, _, y in crsr.fetchall()}
        conn.close()

        self.long_descrip_text = self.style_null_entry(self.long_description,
                                                       wx.TextCtrl(self, -1, "", size=(-1, 35), style=wx.TE_MULTILINE |
                                                                                                      wx.TE_WORDWRAP |
                                                                                                      wx.TE_READONLY |
                                                                                                      wx.BORDER_NONE))

        self.sizer_long_descrip = wx.StaticBoxSizer(wx.StaticBox(self, label='Extended Description'), orient=wx.VERTICAL)
        self.sizer_long_descrip.Add(self.long_descrip_text, flag=wx.ALL | wx.EXPAND)
        self.long_descrip_text.Bind(wx.EVT_SET_FOCUS, self.onfocus)

        self.notes_panel = NotesPanel(self)

        self.sizer_notes = wx.StaticBoxSizer(wx.StaticBox(self, label='Notes'), orient=wx.VERTICAL)
        self.sizer_notes.Add(self.notes_panel, border=2, proportion=1, flag=wx.ALL | wx.EXPAND)
        self.sizer_notes.Add(wx.StaticLine(self, style=wx.LI_HORIZONTAL), flag=wx.EXPAND)


        self.icon_grid = ImgGridPanel(self)

        #Revision Binds
        self.revision_bind(self.short_descrip_text, 'Short Description', self.part_number)

        # Assembly list binds
        self.sub_assembly_list.Bind(wx.EVT_LISTBOX, self.opennewpart)
        self.sub_assembly_list.Bind(wx.EVT_MOTION, self.update_tooltip_sub)
        self.sup_assembly_list.Bind(wx.EVT_LISTBOX, self.opennewpart)
        self.sup_assembly_list.Bind(wx.EVT_MOTION, self.update_tooltip_super)

        self.mugshot_panel = MugshotPanel(self)

        # Master Sizer
        self.sizer_master = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer_master_horizontal = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer_master_horizontal2 = wx.BoxSizer(wx.HORIZONTAL)

        self.sizer_master_left = wx.BoxSizer(wx.VERTICAL)

        self.sizer_master_left.Add(self.sizer_partline, flag=wx.ALL | wx.EXPAND)
        self.sizer_master_left.Add(wx.StaticLine(self, style=wx.LI_HORIZONTAL), flag=wx.EXPAND)
        self.sizer_master_left.Add(wx.StaticLine(self, style=wx.LI_HORIZONTAL), flag=wx.EXPAND)
        self.sizer_master_left.AddSpacer(5)

        self.sizer_master_left.Add(self.sizer_long_descrip, flag=wx.ALL | wx.EXPAND)  # , border=15)
        self.sizer_master_left.Add(self.sizer_notes, proportion=1, flag=wx.ALL | wx.EXPAND)  # , border=15)
        self.sizer_master_left.Add(self.icon_grid, proportion=2, flag=wx.ALL | wx.EXPAND)
        #self.sizer_master_left.Add(self.listBox, proportion=1, flag=wx.ALL | wx.EXPAND)  # , border=15)


        # Assembly Sizers
        self.sizer_assembly_left = wx.BoxSizer(wx.VERTICAL)
        self.sizer_assembly_left.Add(wx.StaticText(self, label="Sub-Assemblies", style=wx.ALIGN_CENTER), border=5, flag=wx.ALL | wx.EXPAND)
        self.sizer_assembly_left.Add(self.sub_assembly_list, proportion=1, flag=wx.ALL | wx.EXPAND)
        self.sizer_assembly_right = wx.BoxSizer(wx.VERTICAL)
        self.sizer_assembly_right.Add(wx.StaticText(self, label="Super-Assemblies", style=wx.ALIGN_CENTER), border=5, flag=wx.ALL | wx.EXPAND)
        self.sizer_assembly_right.Add(self.sup_assembly_list, proportion=1, flag=wx.ALL | wx.EXPAND)
        self.sizer_assembly = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer_assembly.Add(self.sizer_assembly_left, proportion=1, flag=wx.ALL | wx.EXPAND)
        self.sizer_assembly.Add(self.sizer_assembly_right, proportion=1, flag=wx.ALL | wx.EXPAND)

        self.sizer_master.Add(self.sizer_master_left, proportion=1, flag=wx.ALL | wx.EXPAND)
        self.sizer_master.Add(wx.StaticLine(self, style=wx.LI_VERTICAL), flag=wx.EXPAND)

        self.sizer_master_right = wx.BoxSizer(wx.VERTICAL)
        self.sizer_master_right.Add(self.mugshot_panel, flag=wx.ALL | wx.EXPAND)
        self.sizer_master_right.Add(self.sizer_assembly, proportion=1, flag=wx.ALL | wx.EXPAND)
        self.sizer_master.Add(self.sizer_master_right, flag=wx.ALL | wx.EXPAND)

        self.SetSizer(self.sizer_master)


    def revision_bind(self, target, field, pn):
        target.Bind(wx.EVT_LEFT_DCLICK, lambda event: self.revision_dialogue(event, pn, field))


    def revision_dialogue(self, event, pn, field):
        dialog = ModifyPartsFieldDialog(self, event.GetEventObject(), self.part_number, self.part_revision, "name", "Editing {0} of part {1}".format(field, pn))
        dialog.ShowModal()
        dialog.Destroy()

    def load_data(self):
        """Load the part data from the database"""

        # Load part data from database
        conn = config.sql_db.connect(config.db_location)
        crsr = conn.cursor()
        crsr.execute("SELECT part_type, name, description, successor_num, successor_rev, mugshot, drawing "
                     "FROM Parts WHERE part_num=(?) AND part_rev=(?)",
                     (self.part_number, self.part_revision))
        _tmp_sql_data = crsr.fetchone()
        conn.close()

        if _tmp_sql_data:
            self.part_type, \
            self.short_description, \
            self.long_description, \
            self.suc_number, \
            self.suc_revision, \
            self.mugshot, \
            self.drawing \
                = _tmp_sql_data

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

    def opennewpart(self, event):
        index = event.GetSelection()
        self.parent.fuck(event.GetEventObject().GetString(index), wx.GetKeyState(wx.WXK_SHIFT))
        event.GetEventObject().SetSelection(wx.NOT_FOUND)

    def update_tooltip_super(self, event):
        """
        Update the tooltip to show part name
        """

        mouse_pos = self.sup_assembly_list.ScreenToClient(wx.GetMousePosition())
        item_index = self.sup_assembly_list.HitTest(mouse_pos)

        if item_index != -1:
            a = self.parts_super[self.sup_assembly_list.GetString(item_index)]
            if self.sup_assembly_list.GetToolTipText() != a:
                msg = a
                self.sup_assembly_list.SetToolTip(msg)
        else:
            self.sup_assembly_list.SetToolTip("")

        event.Skip()

    def update_tooltip_sub(self, event):
        """
        Update the tooltip to show part name
        """

        mouse_pos = self.sub_assembly_list.ScreenToClient(wx.GetMousePosition())
        item_index = self.sub_assembly_list.HitTest(mouse_pos)

        if item_index != -1:
            a = self.parts_sub[self.sub_assembly_list.GetString(item_index)]
            if self.sub_assembly_list.GetToolTipText() != a:
                msg = a
                self.sub_assembly_list.SetToolTip(msg)
        else:
            self.sub_assembly_list.SetToolTip("")

        event.Skip()

    def onfocus(self, event):
        """Set cursor to default and pass before default on-focus method"""
        self.SetCursor(wx.Cursor(wx.CURSOR_ARROW))
        pass

    def event_rev_next(self, event):
        """Toggle to next revision if possible"""
        return

        if True:
            self.part_revision += 1

            self.text_rev_number.SetLabel("R" + str(self.part_revision))

            self.sizer_partline.Layout()

            # Hook a refresh()

        event.Skip()

    def event_rev_prev(self, event):
        """Toggle to next revision if possible"""
        return

        if self.part_revision > 0:
            self.part_revision -= 1

            self.text_rev_number.SetLabel("R" + str(self.part_revision))

            self.sizer_partline.Layout()

            # Hook a refresh()

        event.Skip()


class MugshotPanel(wx.Panel):

    mug_size = 250
    btn_size = 35

    def __init__(self, parent, *args, **kwargs):
        """Constructor"""
        wx.Panel.__init__(self, parent, *args, **kwargs)

        self.parent = parent

        # Primary part image
        if self.parent.mugshot:
            image = wx.Image(fn_path.concat_img(self.parent.part_number, self.parent.mugshot), wx.BITMAP_TYPE_ANY)
        else:
            image = wx.Image(fn_path.concat_gui('missing_mugshot.png'), wx.BITMAP_TYPE_ANY)

        # Draw button first as first drawn stays on top
        self.button_dwg = wx.Button(self,
                                    size=(MugshotPanel.btn_size,) * 2,
                                    pos=(0, MugshotPanel.mug_size - MugshotPanel.btn_size))
        self.button_dwg.Bind(wx.EVT_BUTTON, self.event_drawing)
        self.button_dwg.Bind(wx.EVT_SET_FOCUS, self.event_button_no_focus)

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
            temp = fn_path.concat_img(self.parent.part_number, new_image)
        else:
            temp = fn_path.concat_gui('missing_mugshot.png')
        self.imageBitmap.SetBitmap(wx.Bitmap(crop_square(wx.Image(temp, wx.BITMAP_TYPE_ANY), MugshotPanel.mug_size)))


    def event_drawing(self, event):
        """Loads a dialog or opens a program (unsure) showing the production drawing of said part"""

        dialog = wx.RichMessageDialog(self,
                                   caption="This feature is not yet implemented",
                                   message="This feature will load a production drawing of the current part",
                                   style=wx.OK | wx.ICON_INFORMATION)
        dialog.ShowModal()
        dialog.Destroy()

    def event_button_no_focus(self, event):
        """Prevents focus from being called on the buttons"""
        pass


class InterfaceTabs(wx.Notebook):
    def __init__(self, *args, **kwargs):
        wx.Notebook.__init__(self, *args, **kwargs) #fnb.FlatNotebook
        self.SetDoubleBuffered(True) #Remove slight strobiong on tab switch

        self.panels = []
        for name in PANELS:
            panel = PartsTabPanel(name, self)
            self.panels.append(panel)
            self.AddPage(panel, name)

    def fuck(self, name, opt_stay=0):
        #PANELS.append("rrr")
        #print("sdgsrg")
        panel = PartsTabPanel(name, self)
        if name not in [pnl.part_number for pnl in self.panels]:
            self.panels.append(panel)
            self.AddPage(panel, name)
            if not opt_stay:
                self.SetSelection(self.GetPageCount() - 1)
        elif not opt_stay:
            self.SetSelection([pnl.part_number for pnl in self.panels].index(name))