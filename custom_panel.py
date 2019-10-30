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
import custom_dialog


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


class PartsTabPanel(wx.Panel):
    def __init__(self, parent, part_num, part_rev, *args, **kwargs):
        """Constructor"""
        wx.Panel.__init__(self, parent, size=(0, 0), *args, **kwargs)  # Needs size parameter to remove black-square
        self.SetDoubleBuffered(True)  # Remove slight strobing on tab switch
        self.SetCursor(wx.Cursor(wx.CURSOR_ARROW))  # Ensure that edit cursor does not show by default

        print("leadss")

        # Variable initialization
        self.parent = parent
        self.part_num = part_num
        self.part_rev = part_rev
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
        # self.wgt_sub_assm = wx.ListBox(self, size=(MugshotPanel.mug_size/2, -1), choices=[i[0] for i in self.helper_wgt_sub])#, size=(-1, 200), style=wx.LB_SINGLE)
        # self.wgt_super_assm = wx.ListBox(self, size=(MugshotPanel.mug_size/2, -1), choices=[i[0] for i in self.helper_wgt_super])#, size=(-1, 200), style=wx.LB_SINGLE)


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
        self.wgt_txt_part_type.Bind(wx.EVT_LEFT_DCLICK, self.edit_type)

        # Assembly list binds
        # self.wgt_sub_assm.Bind(wx.EVT_LISTBOX, self.event_click_assm_lists)
        # self.wgt_sub_assm.Bind(wx.EVT_MOTION, self.update_tooltip_sub)
        # self.wgt_super_assm.Bind(wx.EVT_LISTBOX, self.event_click_assm_lists)
        # self.wgt_super_assm.Bind(wx.EVT_MOTION, self.update_tooltip_super)

        self.pnl_mugshot = widget.CompositeMugshot(self, self)

        # Assembly List Sizers
        # self.szr_sub_assm = wx.BoxSizer(wx.VERTICAL)
        # self.szr_sub_assm.Add(wx.StaticText(self, label="Sub-Assemblies", style=wx.ALIGN_CENTER), border=5, flag=wx.ALL | wx.EXPAND)
        # # self.szr_sub_assm.Add(self.wgt_sub_assm, proportion=1, flag=wx.ALL | wx.EXPAND)
        # self.szr_super_assm = wx.BoxSizer(wx.VERTICAL)
        # self.szr_super_assm.Add(wx.StaticText(self, label="Super-Assemblies", style=wx.ALIGN_CENTER), border=5, flag=wx.ALL | wx.EXPAND)
        # self.szr_super_assm.Add(self.wgt_super_assm, proportion=1, flag=wx.ALL | wx.EXPAND)
        # self.szr_assm = wx.BoxSizer(wx.HORIZONTAL)
        # self.szr_assm.Add(self.szr_sub_assm, proportion=1, flag=wx.ALL | wx.EXPAND)
        # self.szr_assm.Add(self.szr_super_assm, proportion=1, flag=wx.ALL | wx.EXPAND)

        self.szr_assm = widget.CompositeAssemblies(self, self)

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
        self.szr_master_right.Add(self.pnl_mugshot, flag=wx.ALL)
        self.szr_master_right.Add(self.szr_assm, proportion=1, flag=wx.ALL | wx.EXPAND)

        # Master Sizer
        self.szr_master = wx.BoxSizer(wx.HORIZONTAL)
        self.szr_master.Add(self.szr_master_left, proportion=1, flag=wx.ALL | wx.EXPAND)
        self.szr_master.Add(wx.StaticLine(self, style=wx.LI_VERTICAL), flag=wx.EXPAND)
        self.szr_master.Add(self.szr_master_right, flag=wx.ALL | wx.EXPAND)

        # Set Sizer
        self.SetSizer(self.szr_master)

    def edit_type(self, event):
        _dlg = custom_dialog.EditComponentType(self, self, self.wgt_txt_part_type.GetLabel())
        _dlg.ShowModal()
        _dlg.Destroy()

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

        # Populate Sub Assembly list
        conn = config.sql_db.connect(config.cfg["db_location"])
        crsr = conn.cursor()
        crsr.execute("SELECT part_num, part_rev FROM Children WHERE child_num=(?) AND child_rev=(?)",
                     (self.part_num, self.part_rev))
        _sub_all = crsr.fetchall()

        crsr.execute("SELECT part_num, part_rev, name FROM Parts WHERE (part_num, part_rev) IN"
                      "(SELECT part_num, part_rev FROM Children WHERE child_num=(?) AND child_rev=(?))",
                      (self.part_num, self.part_rev))
        _sub_named = crsr.fetchall()

        # Items that have names
        for _num, _rev, _name in _sub_named:
            self.helper_wgt_sub.append([_num, _rev])

            if _num not in self.data_wgt_sub:
                self.data_wgt_sub[_num] = {_rev: _name}
            elif _rev not in self.data_wgt_sub[_num]:
                self.data_wgt_sub[_num][_rev] = _name

        # Items that have no names
        for _num, _rev in set(_sub_all)-set(x[:2] for x in _sub_named):
            self.helper_wgt_sub.append([_num, _rev])

            if _num not in self.data_wgt_sub:
                self.data_wgt_sub[_num] = {_rev: None}
            elif _rev not in self.data_wgt_sub[_num]:
                self.data_wgt_sub[_num][_rev] = None

        # Populate Super Assembly list
        crsr.execute("SELECT child_num, child_rev FROM Children WHERE part_num=(?) AND part_rev=(?)",
                     (self.part_num, self.part_rev))
        _super_all = crsr.fetchall()

        crsr.execute("SELECT part_num, part_rev, name FROM Parts WHERE (part_num, part_rev) IN"
                     "(SELECT child_num, child_rev FROM Children WHERE part_num=(?) AND part_rev=(?))",
                     (self.part_num, self.part_rev))
        _super_named = crsr.fetchall()

        # Items that have names
        for _num, _rev, _name in _super_named:
            self.helper_wgt_super.append([_num, _rev])

            if _num not in self.data_wgt_super:
                self.data_wgt_super[_num] = {_rev: _name}
            elif _rev not in self.data_wgt_super[_num]:
                self.data_wgt_super[_num][_rev] = _name

        # Items that have no names
        for _num, _rev in set(_super_all) - set(x[:2] for x in _super_named):
            self.helper_wgt_super.append([_num, _rev])

            if _num not in self.data_wgt_super:
                self.data_wgt_super[_num] = {_rev: None}
            elif _rev not in self.data_wgt_super[_num]:
                self.data_wgt_super[_num][_rev] = None

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
        for part_num in PANELS:
            panel = PartsTabPanel(self, part_num, "0")
            self.panels.append(panel)
            self.AddPage(panel, part_num)

    def open_parts_tab(self, part_num, part_rev="0", opt_stay=False):
        """Open a new tab using the provided part number

            Args:
                part_num (string): The part number to open as a new tab
                part_rev (string): The part revision to open as a new tab
                opt_stay (bool): If true, do not change to newly opened tab
        """

        conn = config.sql_db.connect(config.cfg["db_location"])
        crsr = conn.cursor()
        crsr.execute("SELECT EXISTS (SELECT 1 FROM Parts WHERE part_num=(?) AND part_rev=(?))", (part_num, part_rev))
        _check = crsr.fetchone()[0]
        conn.close()

        if _check:
            panel = PartsTabPanel(self, part_num, part_rev)
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
                                                  "Do you want to add %s r%s to the database?" % (part_num, part_rev),
                                        style=wx.YES_NO | wx.NO_DEFAULT | wx.ICON_WARNING)
            if _dlg.ShowModal() == wx.ID_YES:

                conn = config.sql_db.connect(config.cfg["db_location"])
                crsr = conn.cursor()
                crsr.execute("INSERT INTO Parts (part_num, part_rev) VALUES ((?), (?));",
                             (part_num, part_rev))
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
