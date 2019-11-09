# -*- coding: utf-8 -*-
"""This module contains the main Notebook class and all Tab classes that the notebook can display"""

import wx

import widget
import dialog

import config
import global_colors

# Hard-coded for demo, but will be changed later to be a user-based option
PANELS = [("107-00107", "0")]


class Notebook(wx.Notebook):
    """Notebook class that contains various Tab-type classes within itself

            Args:
                parent (ref): Reference to the parent wx.object

            Attributes:
                user (str): The logged-in user. Currently hard-coded to "demo"
                parent (ref): Reference to the parent wx.object
    """

    def __init__(self, parent):
        wx.Notebook.__init__(self, parent)
        self.SetDoubleBuffered(True)  # Remove slight strobing on tab switch

        self.user = "demo"
        self.parent = parent

        # Define the open panels and load any that should be opened on start
        self.open_tabs = []
        for part_to_open in PANELS:
            self.open_parts_tab(*part_to_open)

    def open_parts_tab(self, part_num, part_rev="0", opt_stay=False):
        """Open a new tab using the provided part number and revision

            Args:
                part_num (string): The part number to open as a new tab
                part_rev (string): The part revision to open as a new tab - default revision 0
                opt_stay (bool): If true, do not change to newly opened tab - default change tabs
        """

        # Open the database to quickly check if the part and revision exists
        conn = config.sql_db.connect(config.cfg["db_location"])
        crsr = conn.cursor()
        crsr.execute("SELECT EXISTS (SELECT 1 FROM Parts WHERE part_num=(?) AND part_rev=(?))", (part_num, part_rev))
        _check = crsr.fetchone()[0]
        conn.close()

        # Check if the part and revision exists; if not inquire if you would like to add one
        if _check:
            # If there is not yet a tab for this part number then create one, otherwise redirect to the existing
            if part_num not in [tab.part_num for tab in self.open_tabs]:
                new_tab = TabPartInfo(self, part_num, part_rev)
                self.open_tabs.append(new_tab)
                self.AddPage(new_tab, part_num)

                # Handles whether to stay on current tab or move to newly opened tab
                if not opt_stay:
                    self.SetSelection(self.GetPageCount() - 1)
            elif not opt_stay:
                self.SetSelection([pnl.part_num for pnl in self.open_tabs].index(part_num))
        else:
            _dlg = wx.RichMessageDialog(self,
                                        caption="Part Not In System",
                                        message="This part is not currently added to the system.\n"
                                                  "Do you want to add %s r%s to the database?" % (part_num, part_rev),
                                        style=wx.YES_NO | wx.NO_DEFAULT | wx.ICON_WARNING)

            # If the user selects that they want to add the part, then add the part
            if _dlg.ShowModal() == wx.ID_YES:

                conn = config.sql_db.connect(config.cfg["db_location"])
                crsr = conn.cursor()
                crsr.execute("INSERT INTO Parts (part_num, part_rev) VALUES ((?), (?));",
                             (part_num, part_rev))
                crsr.close()
                conn.commit()

                # If there is not yet a tab for this part number then create one, otherwise redirect to the existing
                if part_num not in [tab.part_num for tab in self.open_tabs]:
                    new_tab = TabPartInfo(self, part_num, part_rev)
                    self.open_tabs.append(new_tab)
                    self.AddPage(new_tab, part_num)

                    # Handles whether to stay on current tab or move to newly opened tab
                    if not opt_stay:
                        self.SetSelection(self.GetPageCount() - 1)
                elif not opt_stay:
                    self.SetSelection([pnl.part_num for pnl in self.open_tabs].index(part_num))
            _dlg.Destroy()


class TabPartInfo(wx.Panel):
    """Tab class that displays info relating to parts. It is important to note that classes that have a "root" attribute
        are referring to this or other Tab-level classes

        Args:
            parent (ref): Reference to the parent wx.object
            part_num (str): The part number that the tab loads the relevant information for
            part_rev (str): The revision number that the tab loads the relevant information for

        Attributes:
            parent (ref): Reference to the parent wx.object
            part_num (str): The part number that the tab loads the relevant information for
            part_rev (str): The revision number that the tab loads the relevant information for
    """

    def __init__(self, parent, part_num, part_rev):
        """Constructor"""
        wx.Panel.__init__(self, parent, size=(0, 0))  # Needs size parameter to remove black-square
        self.SetDoubleBuffered(True)  # Remove slight strobing on tab switch
        self.SetCursor(wx.Cursor(wx.CURSOR_ARROW))  # Ensure that edit cursor does not show by default

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

        # Top row of informational text widgets, and binds
        self.wgt_txt_part_num = wx.StaticText(self, label=self.part_num, style=wx.ALIGN_CENTER)
        self.wgt_txt_part_rev = wx.StaticText(self, label="r" + self.part_rev, style=wx.ALIGN_CENTER)
        self.wgt_txt_part_type = self.style_null_entry(self.part_type,
                                                       wx.StaticText(self,
                                                                     size=(100, -1),
                                                                     style=wx.ALIGN_CENTER))
        self.wgt_txt_description_short = self.style_null_entry(self.short_description,
                                                               wx.StaticText(self,
                                                                             style=wx.ST_ELLIPSIZE_END))
        self.revision_bind(self.wgt_txt_description_short, "Short Description", "name")
        self.wgt_txt_part_type.Bind(wx.EVT_LEFT_DCLICK, self.evt_edit_type)

        # Revision number buttons and bindings
        self.wgt_btn_rev_next = wx.Button(self, size=(10, -1))
        self.wgt_btn_rev_prev = wx.Button(self, size=(10, -1))
        self.wgt_btn_rev_next.Bind(wx.EVT_BUTTON, self.event_rev_next)
        self.wgt_btn_rev_prev.Bind(wx.EVT_BUTTON, self.event_rev_prev)

        # Sizer for top row of information, including revision buttons
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

        # Long description widget, sizer, and bind
        self.wgt_txt_description_long = self.style_null_entry(self.long_description,
                                                              wx.TextCtrl(self,
                                                                          size=(-1, 35),
                                                                          style=wx.TE_MULTILINE |
                                                                                wx.TE_WORDWRAP |
                                                                                wx.TE_READONLY |
                                                                                wx.BORDER_NONE))
        self.szr_long_descrip = wx.StaticBoxSizer(wx.StaticBox(self, label="Extended Description"), orient=wx.VERTICAL)
        self.szr_long_descrip.Add(self.wgt_txt_description_long, flag=wx.ALL | wx.EXPAND)
        self.wgt_txt_description_long.Bind(wx.EVT_SET_FOCUS, self.evt_onfocus)
        self.revision_bind(self.wgt_txt_description_long, "Long Description", "description")

        # Notes widget and sizer
        self.wgt_notes = widget.CompositeNotes(self, self)
        self.szr_notes = wx.StaticBoxSizer(wx.StaticBox(self, label='Notes'), orient=wx.VERTICAL)
        self.szr_notes.Add(self.wgt_notes, proportion=1, flag=wx.ALL | wx.EXPAND)

        # Gallery widget and sizer
        self.wgt_gallery = widget.CompositeGallery(self, self)
        self.szr_gallery = wx.StaticBoxSizer(wx.StaticBox(self, label='Image Gallery'), orient=wx.VERTICAL)
        self.szr_gallery.Add(self.wgt_gallery, proportion=1, flag=wx.ALL | wx.EXPAND)

        # Mugshot widget
        self.wgt_mugshot = widget.CompositeMugshot(self, self)

        # Assemblies info widget
        self.wgt_assm = widget.CompositeAssemblies(self, self)

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
        self.szr_master_right.Add(self.wgt_mugshot, flag=wx.ALL)
        self.szr_master_right.Add(self.wgt_assm, proportion=1, flag=wx.ALL | wx.EXPAND)

        # Master Sizer
        self.szr_master = wx.BoxSizer(wx.HORIZONTAL)
        self.szr_master.Add(self.szr_master_left, proportion=1, flag=wx.ALL | wx.EXPAND)
        self.szr_master.Add(wx.StaticLine(self, style=wx.LI_VERTICAL), flag=wx.EXPAND)
        self.szr_master.Add(self.szr_master_right, flag=wx.ALL | wx.EXPAND)

        # Set Sizer
        self.SetSizer(self.szr_master)

    def evt_edit_type(self, event):
        """Open a dialog to edit the parts type

            Args:
                event: A double-click event
        """

        _dlg = dialog.EditComponentType(self, self, self.wgt_txt_part_type.GetLabel())
        _dlg.ShowModal()
        if _dlg: _dlg.Destroy()

    def revision_bind(self, target, field_name, sql_field):
        """Bind a double click along with a string parameter to a given widget

            Args:
                target: A double-click event
                field_name (str): The name of the field to populate into the dialog for editing
                sql_field (str): The sql field to update
        """

        target.Bind(wx.EVT_LEFT_DCLICK, lambda event: self.evt_revision_dialogue(event, field_name, sql_field))

    def evt_revision_dialogue(self, event, field_name, sql_field):
        """Open a dialog to edit a parts field, provided a field name and a double-click event on the widget

            Args:
                event: A double-click event
                field_name (str): The name of the field to populate into the dialog for editing
                sql_field (str): The sql field to update
        """

        _dlg = dialog.ModifyField(self, self, event.GetEventObject(), sql_field,
                                  "Editing {0} of part {1} r{2}".format(field_name, self.part_num, self.part_rev))
        _dlg.ShowModal()
        if _dlg: _dlg.Destroy()

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

        # Dictionary of dictionaries. part_num: part_rev: short_description
        self.helper_wgt_super = []
        self.helper_wgt_sub = []

        # List of 2-entry lists, in order with widgets. Each entry of form [part_num, part_rev]
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
        """Style a text entry based on its SQL counterpart being NULL

            Args:
                conditional (str): The string being used in the field
                entry_field (ptr): Reference to the wx field being styled
        """

        # Determine if SetValue or SetLabel is required to change text
        try:
            _ = entry_field.GetValue()
            edit_field = entry_field.SetValue
        except AttributeError:
            edit_field = entry_field.SetLabel

        # Set the color and text according to if string passed is NULL
        if conditional:
            edit_field(conditional)
        else:
            edit_field("No Entry")
            entry_field.SetForegroundColour(global_colors.no_entry)

        return entry_field

    def evt_onfocus(self, event):
        """Set cursor to default instead of the 'I' type of cursor

            Args:
                event: A focus event from the bound widget receiving focus
        """

        self.SetCursor(wx.Cursor(wx.CURSOR_ARROW))

    def event_rev_next(self, event):
        """Toggle to next revision if possible

            Args:
                event: A click event
        """

        # TODO: Implement revision control in-tab
        return

        if True:
            self.part_rev += 1

            self.text_rev_number.SetLabel("R" + str(self.part_rev))

            self.sizer_partline.Layout()

            # Hook a refresh()

        event.Skip()

    def event_rev_prev(self, event):
        """Toggle to next revision if possible

            Args:
                event: A click event
        """

        # TODO: Implement revision control in-tab
        return

        if self.part_rev > 0:
            self.part_rev -= 1

            self.text_rev_number.SetLabel("R" + str(self.part_rev))

            self.sizer_partline.Layout()

            # Hook a refresh()

        event.Skip()
