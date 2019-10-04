# -*- coding: utf-8 -*-
"""This module defines and imports configuration variables

        Attributes:
            directory_split (str): Used for RegEx on part numbers. Currently unused
            db_location (str): Path to SQL database file or server
            img_archive (str): Location of image database (storage)
            sql_type (str): Type of SQL database being used
            dlg_hide_change_mugshot (bool): Should the dialog warning mugshot change show?
            dlg_hide_remove_image (bool): Should the dialog warning image deletion show?
"""

import yaml
import os
import wx

# Defining & Initializing config variables
cfg = None
sql_db = None
sql_supported = [
                "SQLite",
                "PostgreSQL"
                ]
cfg_import = [
            "directory_split",
            "db_location",
            "img_archive",
            "sql_type",
            "dlg_hide_change_mugshot",
            "dlg_hide_remove_image"

            ]


def load_config(application):
    """Read a yaml file into config dictionary"""

    # Read YAML file into config.cfg dictionary, and prompt to create if absent
    try:
        with open(os.path.join(app_root, 'app_config.yaml'), 'r', encoding='utf8') as stream:
            _loaded = yaml.safe_load(stream)

            # Load in variables intended for import if available
            _keys = list(_loaded.keys())
            globals()['cfg'] = {x: _loaded[x] for x in set(cfg_import).intersection(_keys)}

    except FileNotFoundError:
        print("File not found - generate new config file? Or find file and move to home?")


    _missing_config = list(set(cfg_import).difference(_keys))
    print("missing", _missing_config)

    if len(_missing_config) != 0 or 'sql_type' not in globals()['cfg']:
        print("FUCK")

    # Special handling for sql type
    if 'sql_type' not in globals()['cfg']:
        dlg = DialogConfigSQL(application)
        dlg.ShowModal()

    if globals()['cfg']['sql_type'] == "sqlite3":  # SQLite
        import sqlite3
        globals()['sql_db'] = sqlite3
    elif globals()['cfg']['sql_type'] == "psycopg2":  # PostgreSQL
        import psycopg2
        globals()['sql_db'] = psycopg2
    else:
        raise Exception("An invalid SQL database management system provided: " + globals()['cfg']['sql_type'])


    # Special handling for missing required variables

    # Special handling for missing optional variables


class DialogConfigSQL(wx.Dialog):
    """Opens a dialog showing a dropdown of SQL types.

        Args:
            <>

        Attributes:
            <>
    """

    def __init__(self, application, *args, **kw):
        """Constructor"""
        super().__init__(None, *args, **kw)

        self.a = application
        self.init_dialog()
        self.SetSize((500, 160))
        self.SetTitle("Choose SQL Database Type")

    def init_dialog(self):
        """Draw the dialog box"""

        # Editable box and outline box
        wgt_txt_explain = wx.StaticText(self, label="Please select the type of SQL database you intend to use to "
                                                    "store the part assembly data.\n"
                                                    "This will affect how the data is loaded.")
        self.wgt_dropdown_sql = wx.ComboBox(self, value="", choices=globals()['sql_supported'], style=wx.CB_READONLY)

        # Dialog buttons with binds
        btn_commit = wx.Button(self, label='Commit')
        btn_commit.Bind(wx.EVT_BUTTON, self.event_commit)
        btn_cancel = wx.Button(self, label='Cancel')
        btn_cancel.Bind(wx.EVT_BUTTON, self.event_cancel)

        # Dialog button sizer
        szr_buttons = wx.BoxSizer(wx.HORIZONTAL)
        szr_buttons.Add(btn_commit)
        szr_buttons.Add(btn_cancel, flag=wx.LEFT, border=5)

        # Add everything to master sizer and set sizer for pane
        sizer_master = wx.BoxSizer(wx.VERTICAL)
        sizer_master.Add(wgt_txt_explain, flag=wx.ALL | wx.EXPAND, border=5)
        sizer_master.Add(self.wgt_dropdown_sql, flag=wx.ALL | wx.LEFT, border=5)
        sizer_master.Add(szr_buttons, flag=wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM, border=10)
        self.SetSizer(sizer_master)

        self.Bind(wx.EVT_CLOSE, self.event_close)

    def event_commit(self, event):
        """Execute when committing a change - move change to SQL"""

        if self.wgt_dropdown_sql.GetSelection() != -1:
            globals()['cfg']['sql_type'] = globals()['sql_supported'][self.wgt_dropdown_sql.GetSelection()]

    def event_cancel(self, event):
        """Execute when cancelling a change"""
        self.event_close()

    def event_close(self, *args):
        """Execute when closing the dialog"""
        self.a.Destroy()

