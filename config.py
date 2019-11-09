# -*- coding: utf-8 -*-
"""This module defines and imports configuration variables

        Attributes:
            sql_db (module): A link to the python module for the chosen SQL type, for interoperability


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
cfg = {}
opt = {}
sql_db = None
sql_supported = [
                'SQLite'
                # 'PostgreSQL'
                # 'MySQL'
                ]
cfg_app_import = [
                 'directory_split',
                 'db_location',
                 'img_archive',
                 'sql_type'
                 ]
cfg_user_import = [
                  'dlg_hide_change_mugshot',
                  'dlg_hide_remove_image'
                  ]


def load_config(application):
    """Read a yaml file into config dictionary"""

    # Read user YAML file into config.opt dictionary, and automatically create if absent (all false)
    try:
        with open(os.path.join(app_root, 'demo' + '_config.yaml'), 'r', encoding='utf8') as stream:
            _loaded = yaml.safe_load(stream)

            # Load in variables intended for import if available
            _keys = list(_loaded.keys())
            globals()['opt'] = {x: _loaded[x] for x in set(cfg_user_import).intersection(_keys)}

            # If any user variables are missing
            if len(set(cfg_user_import).difference(_keys)) != 0:
                for undefined in set(cfg_user_import).difference(_keys):
                    globals()['opt'][undefined] = False
                with open(os.path.join(app_root, 'testuser' + '_config.yaml'), 'w', encoding='utf8') as stream:
                    yaml.dump(globals()['opt'], stream, default_flow_style=False)
    # If all user variables or the file are missing
    except (AttributeError, FileNotFoundError):
        globals()['opt'] = {x: False for x in cfg_user_import}
        with open(os.path.join(app_root, 'testuser' + '_config.yaml'), 'w', encoding='utf8') as stream:
            yaml.dump(globals()['opt'], stream, default_flow_style=False)

    # Read application YAML file into config.cfg dictionary, and prompt to create if absent
    try:
        with open(os.path.join(app_root, 'app_config.yaml'), 'r', encoding='utf8') as stream:
            _loaded = yaml.safe_load(stream)

            # Load in variables intended for import if available
            _keys = list(_loaded.keys())
            _missing_config = list(set(cfg_app_import).difference(_keys))
            globals()['cfg'] = {x: _loaded[x] for x in set(cfg_app_import).intersection(_keys)}

    except (AttributeError, FileNotFoundError):
        dlg = wx.RichMessageDialog(None,
                                   caption="Missing Config File",
                                   message="The config file is missing or empty. Please generate one now, or cancel if "
                                           "you want to locate the file",
                                   style=wx.OK | wx.CANCEL | wx.ICON_WARNING)
        if dlg.ShowModal() == wx.ID_OK:
            call_config_dialog()
            _missing_config = []
        else:
            exit()

    if len(_missing_config) != 0:  # AND IS VALID
        dlg = wx.RichMessageDialog(None,
                                   caption="Missing Config Values",
                                   message="Some variables are missing from the config file. Please update them now.",
                                   style=wx.OK | wx.ICON_WARNING)
        dlg.ShowModal()
        call_config_dialog()

    # Special handling for sql type
    if 'sql_type' not in globals()['cfg']:
        dlg = DialogConfigSQL()
        dlg.ShowModal()

    if globals()['cfg']['sql_type'] == "SQLite":  # SQLite
        import sqlite3
        globals()['sql_db'] = sqlite3
    elif globals()['cfg']['sql_type'] == "PostgreSQL":  # PostgreSQL
        import psycopg2
        globals()['sql_db'] = psycopg2
    else:
        raise Exception("An invalid SQL database management system provided: " + globals()['cfg']['sql_type'])


    # Special handling for missing required variables

    # Special handling for missing optional variables


def call_config_dialog():
    dlg = DialogConfigSQL()
    dlg.ShowModal()


class DialogConfigSQL(wx.Dialog):
    """Opens a dialog showing a dropdown of SQL types.

        Args:
            <>

        Attributes:
            <>
    """

    def __init__(self, *args, **kw):
        """Constructor"""
        super().__init__(None, *args, **kw)

        # Window variables
        self.init_dialog()
        self.SetSize((500, 270))
        self.SetTitle("Choose SQL Database Type")

    def init_dialog(self):
        """Draw the dialog box"""

        # SQL Selection
        wgt_txt_sql = wx.StaticText(self, label="SQL Database Location and Type")
        self.wgt_dropdown_sql = wx.ComboBox(self,
                                            value=self.config_ternary('sql_type'),
                                            choices=globals()['sql_supported'],
                                            style=wx.CB_READONLY)
        self.wgt_entry_sql = wx.TextCtrl(self, value=self.config_ternary('db_location'))

        # Image Database
        wgt_txt_image = wx.StaticText(self, label="Image Database Location")
        self.wgt_entry_image = wx.TextCtrl(self, value=self.config_ternary('img_archive'))

        # Part Number RegEx
        wgt_txt_regex = wx.StaticText(self, label="Part Number Regular Expression (Not yet functional)")
        self.wgt_entry_regex = wx.TextCtrl(self, value=self.config_ternary('directory_split'))

        # Buttons
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
        sizer_master.Add(wgt_txt_sql, flag=wx.ALL | wx.EXPAND, border=2)
        sizer_master.Add(self.wgt_dropdown_sql, flag=wx.ALL, border=2)
        sizer_master.Add(self.wgt_entry_sql, flag=wx.ALL | wx.EXPAND, border=2)
        sizer_master.AddSpacer(8)
        sizer_master.Add(wgt_txt_image, flag=wx.ALL | wx.EXPAND, border=2)
        sizer_master.Add(self.wgt_entry_image, flag=wx.ALL | wx.EXPAND, border=2)
        sizer_master.AddSpacer(8)
        sizer_master.Add(wgt_txt_regex, flag=wx.ALL | wx.EXPAND, border=2)
        sizer_master.Add(self.wgt_entry_regex, flag=wx.ALL | wx.EXPAND, border=2)
        sizer_master.Add(szr_buttons, flag=wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM, border=10)
        self.SetSizer(sizer_master)

        self.Bind(wx.EVT_CLOSE, self.event_close)

    @staticmethod
    def config_ternary(variable):
        """Common ternary for updating text field"""
        return globals()['cfg'][variable] if (variable in globals()['cfg']) else ''

    def event_commit(self, event):
        """Execute when committing the config variables - write configs to yaml"""

        # SQL type check
        _sql_type_enum = self.wgt_dropdown_sql.GetSelection()
        if _sql_type_enum != -1:
            globals()['cfg']['sql_type'] = globals()['sql_supported'][_sql_type_enum]
        else:
            return

        # SQL database location
        if globals()['cfg']['sql_type'] == 'SQLite':
            _sql_db = self.wgt_entry_sql.GetValue()
            print(os.path.splitext(_sql_db)[-1])
            if os.path.splitext(_sql_db)[-1] == '.sqlite' and os.path.isfile(_sql_db):
                globals()['cfg']['db_location'] = _sql_db
            else:
                return
        elif globals()['cfg']['sql_type'] == 'PostgreSQL':
            # Postgres check
            return
        else:
            return

        # Image database location
        _img_db = self.wgt_entry_image.GetValue()
        if os.path.isdir(_img_db):
            globals()['cfg']['img_archive'] = _img_db
        else:
            return

        # RegEx
        globals()['cfg']['directory_split'] = self.wgt_entry_regex.GetValue()

        with open(os.path.join(app_root, 'app_config.yaml'), 'w', encoding='utf8') as stream:
            yaml.dump(globals()['cfg'], stream, default_flow_style=False)

        self.Destroy()

    def event_cancel(self, event):
        """Execute when cancelling a change"""
        self.event_close()

    def event_close(self, *args):
        """Execute when closing the dialog"""
        self.a.Destroy()

