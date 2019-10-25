# -*- coding: utf-8 -*-
"""This module contains widgets (composite panels) to be used in the main application frame."""


import wx
import wx.lib.scrolledpanel as scrolled
from math import ceil

import custom_dialog
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

        # Bind layout recalculation to scrolling
        self.Bind(wx.EVT_SCROLLWIN, self.evt_scroll)

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

    def evt_scroll(self, event):
        """Adds forced recalculation of layout on scroll - as default repainting of frames does not work here

        Args:
            event: Scroll event
        """

        wx.CallAfter(self.Layout)
        event.Skip()


class CompositeNotes(wx.Panel):
    """Custom widget that overlays an "add note" button on top of the WidgetNotes custom widget as well as
    governs the column header behavior

        Class Variables:
            btn_size (int): Size of the "add image" button in the overlay
            col_min (list: int): List of minimum column widths for the column headers

        Args:
            parent (ref): Reference to the parent wx.object
            root (ref): Reference to the root parts tab

        Attributes:
            parent (ref): Reference to the parent wx.object
            root (ref): Reference to the root parts tab
    """

    btn_size = 25
    col_min = [25, 40, -1]

    def __init__(self, parent, root):
        """Constructor"""
        wx.Panel.__init__(self, parent)

        self.parent = parent
        self.root = root

        # List of text objects in the header
        self.header_list = []

        # Draw button first, as the first object drawn stays on top
        self.btn_add_note = wx.BitmapButton(self,
                                            bitmap=wx.Bitmap(fn_path.concat_gui('plus.png')),
                                            size=(CompositeNotes.btn_size,) * 2)

        # Set up sizer to contain header and scrolled notes
        self.pnl_notes = NotesScrolled(self, self.root)

        # Button overlay binding - Must be after subwidget to bind to
        self.btn_add_note.Bind(wx.EVT_BUTTON, self.pnl_notes.evt_add_note)
        self.btn_add_note.Bind(wx.EVT_SET_FOCUS, self.evt_button_no_focus)

        # Binding for clicking between notes text
        self.pnl_notes.Bind(wx.EVT_LEFT_UP, self.evt_edit_note)

        # Main Sizer
        self.szr_title = wx.BoxSizer(wx.HORIZONTAL)
        self.szr_main = wx.BoxSizer(wx.VERTICAL)
        self.szr_main.Add(self.szr_title, flag=wx.ALL | wx.EXPAND)
        self.szr_main.Add(self.pnl_notes, proportion=1, flag=wx.ALL | wx.EXPAND)

        self.header_list.append(
            wx.StaticText(self,
                          label="Date", style=wx.ALIGN_LEFT))
        self.header_list.append(
            wx.StaticText(self,
                          label="Author", style=wx.ALIGN_LEFT))
        self.header_list.append(wx.StaticText(self, label="Note", style=wx.ALIGN_LEFT))
        # self.header_list.append(wx.StaticText(self, label="", style=wx.ALIGN_CENTER))  # TODO: Line removal failure

        self.szr_title.Add(self.header_list[0])
        self.szr_title.Add(self.header_list[1])
        self.szr_title.Add(self.header_list[2], proportion=1)
        #self.szr_title.Add(self.header_list[3])

        # Refresh headers, repopulating self.sizer_title
        self.refresh_headers()

        # Set sizer and resize
        self.SetSizer(self.szr_main)
        self.Layout()

        # Bind button movement to resize
        self.Bind(wx.EVT_SIZE, self.evt_resize)

    def refresh_headers(self):
        """Refresh the column headers to reflect the column widths in the lower scrolled sizer"""

        # Append three 0s in case the notes list is empty. Only the first 3 entries are observed
        column_widths = [*self.pnl_notes.szr_grid.GetColWidths(), 0, 0, 0][:3]

        # Change the size of the first two column headers
        self.header_list[0].SetMinSize((max(column_widths[0], CompositeNotes.col_min[0]) + NotesScrolled.col_gap, -1))
        self.header_list[1].SetMinSize((max(column_widths[1], CompositeNotes.col_min[1]) + NotesScrolled.col_gap, -1))

        # Ensure headers resize properly
        self.Layout()

    def evt_edit_note(self, event):
        """Determine where in the scrolled panel was clicked and pass that to the method handling the dialog

        Args:
            self: A reference to the parent wx.object instance
            event: A resize event object passed from the click event
        """

        # Mouse positions within the overall panel, corrected for scroll. The math signage is odd, but works out
        pos_panel = self.pnl_notes.ScreenToClient(wx.GetMousePosition())[1]
        pos_scroll = -self.pnl_notes.CalcScrolledPosition(0, 0)[1]

        # Call method from the panel itself to handle dialog popup
        self.pnl_notes.edit_notes((pos_panel + pos_scroll) // 20)

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

    def evt_button_no_focus(self, event):
        """Prevents focus from being called on the buttons"""
        pass


class NotesScrolled(scrolled.ScrolledPanel):
    """Custom scrolled widget to contain notes associated with the part of the parent tab

        Class Variables:
            row_gap (int): Vertical spacing between rows in grid
            col_gap (int): Horizontal spacing between columns in grid

        Args:
            parent (ref): Reference to the parent wx.object
            root (ref): Reference to the root parts tab

        Attributes:
            parent (ref): Reference to the parent wx.object
            root (ref): Reference to the root parts tab
    """

    row_gap = 5
    col_gap = 15

    def __init__(self, parent, root):
        """Constructor"""
        super().__init__(parent, style=wx.ALL | wx.VSCROLL)

        self.parent = parent
        self.root = root

        # List of current notes items in widget; each entry is a list of three wx.objects
        self.notes_list = []

        # Sizer to hold notes entries - Also set as main sizer
        self.szr_grid = wx.FlexGridSizer(3, NotesScrolled.row_gap, NotesScrolled.col_gap)
        self.szr_grid.AddGrowableCol(2)
        self.szr_grid.SetFlexibleDirection(wx.HORIZONTAL)
        self.szr_grid.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_NONE)
        self.SetSizer(self.szr_grid)

        # Load notes into the provided grid sizer
        self.load_notes()

        # Setup the scrolling style and function, wanting only vertical scroll to be available
        self.SetupScrolling()
        self.ShowScrollbars(wx.SHOW_SB_NEVER, wx.SHOW_SB_ALWAYS)
        self.SetWindowStyle(wx.VSCROLL)

        # Not clear as to why this is needed, but without it the scrollbar is missing in some circumstances
        self.SetScrollbars(*(1,) * 4)

        # Bind layout recalculation to scrolling
        self.Bind(wx.EVT_SCROLLWIN, self.evt_scroll)

    def load_notes(self):
        """Open SQL database and load notes from table"""

        # Load notes from database
        conn = config.sql_db.connect(config.cfg["db_location"])
        crsr = conn.cursor()
        crsr.execute("SELECT date, author, note FROM Notes WHERE part_num=(?) AND part_rev=(?)",
                     (self.root.part_num, self.root.part_rev))
        _tmp_list = crsr.fetchall()
        conn.close()

        # Sort and remove non-date information from the datetime string
        if _tmp_list:
            _tmp_list = [(a[0][:10],)+a[1:] for a in sorted(_tmp_list, key=lambda x: x[0])]

        # Add the notes to the grid
        for i, note in enumerate(_tmp_list):
            _tmp_item = [wx.StaticText(self, id=i, label=note[0], style=wx.EXPAND),
                         wx.StaticText(self, size=(40, -1), id=i, label=note[1], style=wx.EXPAND),
                         wx.StaticText(self, size=(50, -1), id=i, label=note[2], style=wx.ST_ELLIPSIZE_END)]

            # Binding for the items in the notes widget
            for item in _tmp_item:
                item.Bind(wx.EVT_LEFT_UP, self.evt_edit_notes_trigger)
                self.szr_grid.Add(item, flag=wx.ALL | wx.EXPAND)

            self.notes_list.append(_tmp_item)

    def evt_add_note(self, event):
        _tmp_item = [wx.StaticText(self, id=7, label="FRY", style=wx.EXPAND),
                     wx.StaticText(self, size=(40, -1), id=7, label="PORK", style=wx.EXPAND),
                     wx.StaticText(self, size=(50, -1), id=7, label="NOTE", style=wx.ST_ELLIPSIZE_END)]

        # Binding for the items in the notes widget
        for item in _tmp_item:
            item.Bind(wx.EVT_LEFT_UP, self.evt_edit_notes_trigger)
            self.szr_grid.Add(item, flag=wx.ALL | wx.EXPAND)

        self.notes_list.append(_tmp_item)

        # Refresh both layouts so the scrollbar resets
        self.Layout()
        self.parent.Layout()

    def evt_edit_notes_trigger(self, event):
        """Determine which entry in the scrolled panel was clicked and pass that to the method handling the dialog

        Args:
            event: Click event that triggered this function
        """

        self.edit_notes(event.GetEventObject().GetId())

    def edit_notes(self, my_index):
        """Method to edit an existing note, based on the provided index in the list

        Args:
            my_index (int): Index for the notes entry you want to edit
        """

        print(self.notes_list[my_index][0].GetLabel(), self.notes_list[my_index][1].GetLabel(), self.notes_list[my_index][2].GetLabel())
        #dialog = ImageDialog(self.image_list, event.GetEventObject().GetId(), self.parent.part_num, self.parent.part_rev)
        #dialog.ShowModal()
        #dialog.Destroy()

    def evt_scroll(self, event):
        """Adds forced recalculation of layout on scroll - as default repainting of frames does not work here

        Args:
            event: Scroll event
        """

        wx.CallAfter(self.Layout)
        event.Skip()


class CompositeMugshot(wx.Panel):

    mug_size = 250
    btn_size = 40

    def __init__(self, parent, root):
        """Constructor"""
        wx.Panel.__init__(self, parent)

        self.parent = parent
        self.root = root

        # Primary part image
        if self.parent.mugshot:
            image = wx.Image(fn_path.concat_img(self.parent.part_num, self.parent.mugshot), wx.BITMAP_TYPE_ANY)
        else:
            image = wx.Image(fn_path.concat_gui('missing_mugshot.png'), wx.BITMAP_TYPE_ANY)

        # Draw button first as first drawn stays on top
        self.button_dwg = wx.BitmapButton(self,
                                          bitmap=wx.Bitmap(fn_path.concat_gui('schematic.png')),
                                          size=(CompositeMugshot.btn_size,) * 2,
                                          pos=(0, CompositeMugshot.mug_size - CompositeMugshot.btn_size))
        self.button_dwg.Bind(wx.EVT_SET_FOCUS, self.event_button_no_focus)
        self.button_dwg.Bind(wx.EVT_BUTTON, self.event_drawing)

        self.imageBitmap = wx.StaticBitmap(self, wx.ID_ANY, wx.Bitmap(crop_square(image, CompositeMugshot.mug_size)))

        self.sizer_main = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer_main.Add(self.imageBitmap, flag=wx.ALL)
        # self.button_dwg2 = wx.Button(self, size=(500, 500), pos=(50, 0))
        #self.button_dwg = wx.Button(self, size=(50, 50), pos=(50, 0))
        #self.sizer_main.Add(self.button_dwg, flag=wx.ALL)
        #self.button_dwg2 = wx.Button(self, size=(500, 500), pos=(50, 0))

        self.SetSizer(self.sizer_main)
        self.Layout()
        self.Fit()

    def refresh(self, new_image=None):
        if new_image:
            temp = fn_path.concat_img(self.parent.part_num, new_image)
        else:
            temp = fn_path.concat_gui('missing_mugshot.png')
        self.imageBitmap.SetBitmap(wx.Bitmap(crop_square(wx.Image(temp, wx.BITMAP_TYPE_ANY), CompositeMugshot.mug_size)))

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


class CompositeAssemblies(wx.Panel):

    def __init__(self, parent, root):
        """Constructor"""
        wx.Panel.__init__(self, parent)

        self.parent = parent
        self.root = root

        # Lists containing sub and super assembly info
        self.wgt_sub_assm = wx.ListBox(self, choices=[i[0] for i in self.root.helper_wgt_sub], size=(CompositeMugshot.mug_size//2, -1))  # , size=(-1, 200), style=wx.LB_SINGLE)
        self.wgt_super_assm = wx.ListBox(self, choices=[i[0] for i in self.root.helper_wgt_super], size=(CompositeMugshot.mug_size//2, -1))  # , size=(-1, 200), style=wx.LB_SINGLE)

        # Assembly list binds
        self.wgt_sub_assm.Bind(wx.EVT_LISTBOX, self.event_click_assm_lists)
        self.wgt_sub_assm.Bind(wx.EVT_MOTION, self.update_tooltip_sub)
        self.wgt_super_assm.Bind(wx.EVT_LISTBOX, self.event_click_assm_lists)
        self.wgt_super_assm.Bind(wx.EVT_MOTION, self.update_tooltip_super)

        # Assembly List Sizers
        self.szr_sub_assm = wx.BoxSizer(wx.VERTICAL)
        self.szr_sub_assm.Add(wx.StaticText(self, label="Sub-Assemblies", style=wx.ALIGN_CENTER), border=5,
                              flag=wx.ALL | wx.EXPAND)
        self.szr_sub_assm.Add(self.wgt_sub_assm, proportion=1, flag=wx.ALL | wx.EXPAND)
        self.szr_super_assm = wx.BoxSizer(wx.VERTICAL)
        self.szr_super_assm.Add(wx.StaticText(self, label="Super-Assemblies", style=wx.ALIGN_CENTER), border=5,
                                flag=wx.ALL | wx.EXPAND)
        self.szr_super_assm.Add(self.wgt_super_assm, proportion=1, flag=wx.ALL | wx.EXPAND)
        self.sizer_main = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer_main.Add(self.szr_sub_assm, proportion=1, flag=wx.ALL | wx.EXPAND)
        self.sizer_main.Add(self.szr_super_assm, proportion=1, flag=wx.ALL | wx.EXPAND)

        # # Primary part image
        # if self.parent.mugshot:
        #     image = wx.Image(fn_path.concat_img(self.parent.part_num, self.parent.mugshot), wx.BITMAP_TYPE_ANY)
        # else:
        #     image = wx.Image(fn_path.concat_gui('missing_mugshot.png'), wx.BITMAP_TYPE_ANY)
        #
        # # Draw button first as first drawn stays on top
        # self.button_dwg = wx.BitmapButton(self,
        #                                   bitmap=wx.Bitmap(fn_path.concat_gui('schematic.png')),
        #                                   size=(CompositeMugshot.btn_size,) * 2,
        #                                   pos=(0, CompositeMugshot.mug_size - CompositeMugshot.btn_size))
        # self.button_dwg.Bind(wx.EVT_SET_FOCUS, self.event_button_no_focus)
        # self.button_dwg.Bind(wx.EVT_BUTTON, self.event_drawing)
        #
        # self.imageBitmap = wx.StaticBitmap(self, wx.ID_ANY, wx.Bitmap(crop_square(image, CompositeMugshot.mug_size)))
        #
        # self.sizer_main = wx.BoxSizer(wx.HORIZONTAL)
        # self.sizer_main.Add(self.imageBitmap, flag=wx.ALL)
        # # self.button_dwg2 = wx.Button(self, size=(500, 500), pos=(50, 0))
        # #self.button_dwg = wx.Button(self, size=(50, 50), pos=(50, 0))
        # #self.sizer_main.Add(self.button_dwg, flag=wx.ALL)
        # #self.button_dwg2 = wx.Button(self, size=(500, 500), pos=(50, 0))

        self.SetSizer(self.sizer_main)
        self.Layout()

    def refresh(self, new_image=None):
        if new_image:
            temp = fn_path.concat_img(self.parent.part_num, new_image)
        else:
            temp = fn_path.concat_gui('missing_mugshot.png')
        self.imageBitmap.SetBitmap(wx.Bitmap(crop_square(wx.Image(temp, wx.BITMAP_TYPE_ANY), CompositeMugshot.mug_size)))

    def event_click_assm_lists(self, event):
        index = event.GetSelection()
        self.root.parent.open_parts_tab(event.GetEventObject().GetString(index), wx.GetKeyState(wx.WXK_SHIFT))
        event.GetEventObject().SetSelection(wx.NOT_FOUND)

    def update_tooltip_super(self, event):
        """
        Update the tooltip to show part name
        """

        mouse_pos = self.wgt_super_assm.ScreenToClient(wx.GetMousePosition())
        item_index = self.wgt_super_assm.HitTest(mouse_pos)

        if item_index != -1:
            num, rev = self.root.helper_wgt_super[item_index]
            new_msg = self.root.data_wgt_super[num][rev]
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
            num, rev = self.root.helper_wgt_sub[item_index]
            new_msg = self.root.data_wgt_sub[num][rev]
            if self.wgt_sub_assm.GetToolTipText() != new_msg:
                self.wgt_sub_assm.SetToolTip(new_msg)
        else:
            self.wgt_sub_assm.SetToolTip("")

        event.Skip()


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