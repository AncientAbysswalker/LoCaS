#asgnkljaenrhasedlhnmsrthjsaftgjmsfyks
COLORS = ["red", "blue", "black", "yellow", "green"]
NUMBERS = ["{:<6}|{:>25}|{}".format('JA1','23-JAN-2019','moretext for my othershit'), "{:<6}|{:<25}|{}".format('J1','23-J019','moretext for my othershit'), '2', '3', '4']
PANELS = ["107-00107", "G39-00107", "777-00107"]
SUBLIST = ["999-00107", "G39-00107", "767-00107"]
SUPLIST = ["456-00107", "G39-06767", "776-04577"]
DATADIR = r'C:\Users\Ancient Abysswalker\PycharmProjects\LoCaS'

import random
import wx
import sys, os
import wx.lib.agw.flatnotebook as fnb
import wx.lib.agw.ultimatelistctrl as ulc
import wx.lib.scrolledpanel as scrolled
import glob
from math import ceil, floor
from custom_dialog import *
import copy
#from os import path, makedirs, rename

def crop_box(image):
    if image.Height > image.Width:
        min_edge = image.Width
        posx = 0
        posy = (image.Width - image.Height) / 2
    else:
        min_edge = image.Height
        posx = (image.Height - image.Width) / 2
        posy = 0

    image.Resize(size=(min_edge, min_edge), pos=(posx, posy))
    return image

def part_to_dir(pn):
    dir1, temp = pn.split('-')
    dir2 = temp[:2]
    dir3 = temp[2:]
    return [dir1, dir2, dir3]


class ImgGridPanel(scrolled.ScrolledPanel):
    """Summary of class here.

    Longer class information....
    Longer class information....

    Attributes:
        likes_spam: A boolean indicating if we like SPAM or not.
        eggs: An integer count of the eggs we have laid.
    """


    def __init__(self, parent):
        """Inits ImgGridPanel with reference to parent panel or frame."""
        super(ImgGridPanel, self).__init__(parent, style = wx.BORDER_SIMPLE)

        #Variables
        self.icon_size=100
        self.hyster_low=5
        self.hyster_high=self.icon_size-self.hyster_low
        self.icon_gap = 5
        self.parent=parent

        #Load list of images
        self.images = [x for x in glob.glob(os.path.join(DATADIR, 'img', *part_to_dir(parent.part_number), '*'))
                       for y in ['.png', '.jpg', '.gif'] if y in x]

        #Load dict of image comments
        self.comments = {}
        try:
            with open(os.path.join(DATADIR, 'img', *part_to_dir(parent.part_number), 'comments.txt')) as comfile:
                _entries = comfile.read().split('\n' + chr(00) + '\n')
                for entry in _entries:
                    _name, _comment = entry.split('<' + chr(00) + '>')
                    self.comments[_name] = _comment
        except FileNotFoundError:
            pass


        self.nrows, self.ncols = 1, len(self.images)
        self.sizer_grid = wx.GridSizer(rows=self.nrows, cols=self.ncols, hgap=self.icon_gap, vgap=self.icon_gap)


        # Add images to the grid.
        for r in range(self.nrows):
            for c in range(self.ncols):
                _n = self.ncols * r + c
                _tmp = wx.Image(self.images[_n], wx.BITMAP_TYPE_ANY).Rescale(self.icon_size, self.icon_size)
                _temp = wx.StaticBitmap(self, id=_n, bitmap=wx.BitmapFromImage(_tmp))
                _temp.Bind(wx.EVT_LEFT_UP, self.image_click_event)
                self.sizer_grid.Add(_temp, wx.EXPAND) #THROUGH ID??

        # for r in range(self.nrows):
        #     c=1#for c in range(self.ncols):
        #     _n = self.ncols * r + c
        #     _tmp = wx.Image(self.imgs[_n], wx.BITMAP_TYPE_ANY).Rescale(self.icon_size, self.icon_size)
        #     _temp2 = wx.StaticBitmap(self, wx.ID_ANY, wx.BitmapFromImage(_tmp))
        #     _temp2.Bind(wx.EVT_LEFT_UP, lambda event: self.image_click_event(event, self.imgs, _n))
        #     self.sizer_grid.Add(_temp2, wx.EXPAND)

        # self.grid.Fit(self)

        self.SetSizer(self.sizer_grid)


        #self.imgSizer = wx.BoxSizer(wx.VERTICAL)
        #for each in imagelist:
        #    self.imgSizer.Add(each, 1, flag=wx.ALL | wx.EXPAND, border=10)
        #self.SetSizer(self.imgSizer)

        self.SetAutoLayout(1)
        self.SetupScrolling()
        #self.Bind(wx.EVT_PAINT, self.OnPaint)
        #self.bitmap.Bind(wx.EVT_MOTION, self.OnMove)
        #self.bitmap.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)
        #self.bitmap.Bind(wx.EVT_LEFT_UP, self.OnLeftUp)
        self.IsRectReady = False
        self.newRectPara=[0,0,0,0]

        self.Bind(wx.EVT_SIZE, self.resize_grid)


    def resize_grid(self, size):
        """Resize the image grid

        Retrieves width and height of the grid panel and adds/removes grid columns/rows to fit panel nicely.

        Args:
            self: A reference to the parent instance of ImgPanel.
            size: A size object passed from the resize event.
        """

        (w, h) = self.GetSize()

        if self.ncols > 1 and w < self.ncols * self.icon_size + (self.ncols + 1) * self.icon_gap - self.hyster_low:
            self.ncols -= 1
            self.nrows = max(ceil(len(self.images) / self.ncols), ceil((h + self.icon_gap) / (self.icon_size + self.icon_gap)))
            self.sizer_grid.SetCols(self.ncols)
            self.sizer_grid.SetRows(self.nrows)
        elif w > self.ncols * self.icon_size + (self.ncols + 1) * self.icon_gap + self.hyster_high:
            self.ncols += 1
            self.nrows = max(ceil(len(self.images) / self.ncols), ceil((h + self.icon_gap) / (self.icon_size + self.icon_gap)))
            self.sizer_grid.SetCols(self.ncols)
            self.sizer_grid.SetRows(self.nrows)

        if self.nrows > 1 and h < self.nrows * self.icon_size + (self.nrows + 1) * self.icon_gap - self.hyster_low:
            self.nrows = max(ceil(len(self.images) / self.ncols), ceil((h + self.icon_gap) / (self.icon_size + self.icon_gap)))
            self.sizer_grid.SetRows(self.nrows)
        elif h > self.nrows * self.icon_size + (self.nrows + 1) * self.icon_gap + self.hyster_high:
            self.nrows = max(ceil(len(self.images) / self.ncols), ceil((h + self.icon_gap) / (self.icon_size + self.icon_gap)))
            self.sizer_grid.SetRows(self.nrows)

    def image_click_event(self, event):
        dialog = ImageDialog(self.images, event.GetEventObject().GetId(), os.path.join(DATADIR, "img", *part_to_dir(self.parent.part_number), self.parent.part_number + ".cmt"))
        dialog.ShowModal()
        dialog.Destroy()


class PartsTabPanel(wx.Panel):
    def __init__(self, pn, *args, **kwargs):
        """Constructor"""

        self.parent=args[0]
        self.part_number = pn
        self.part_type = "Finished Product"
        self.short_description = "These are a short descrip for a part!"
        self.long_description = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Pellentesque tempor, elit " \
                                "sed pulvinar feugiat, tortor tortor posuere neque, eget ultrices eros est laoreet " \
                                "velit. Aliquam erat volutpat. Donec mi libero, elementum eu augue eget, iaculis " \
                                "dignissim ex. Nullam tincidunt nisl felis, eu efficitur turpis sodales et. Fusce " \
                                "vestibulum lacus sit amet ullamcorper efficitur. Morbi ultrices commodo leo, " \
                                "ultricies posuere mi finibus id. Nulla convallis velit ante, sed egestas nulla " \
                                "dignissim ac. "

        wx.Panel.__init__(self, size=(0,0), *args, **kwargs) #Needs size parameter to not black-square strobe the user
        #self.SetBackgroundColour(random.choice(COLORS))

        self.SetDoubleBuffered(True)  # Remove slight strobiong on tab switch


        #Text Widgets
        self.part_number_text = wx.StaticText(self, size = (60, -1), label = self.part_number, style = wx.ALIGN_CENTER)
        self.part_type_text = wx.StaticText(self, size = (100, -1), label = self.part_type, style = wx.ALIGN_CENTER)
        self.short_descrip_text = wx.StaticText(self, size = (-1, -1), label = self.short_description, style = wx.ST_ELLIPSIZE_END)


        ## EVENTUALLY SWAP OUT FOR ULTIMATELISTBOX
        self.sub_assembly_list = wx.ListBox(self, size=(-1, -1), choices=SUBLIST)#, size=(-1, 200), style=wx.LB_SINGLE)


        #self.sub_assembly_list = wx.ListCtrl(self, size=(-1, -1))
        #self.sub_assembly_list.InsertColumn(0,'Sub-Assemblies')
        #temp=0
        #for sub in SUBLIST:
        #    index = self.sub_assembly_list.InsertItem(temp, sub)
            #self.list.SetStringItem(index, 1, i[1])
            #self.list.SetStringItem(index, 2, i[2])
         #   temp+=1

        self.sup_assembly_list = wx.ListBox(self, size=(-1, -1), choices=SUPLIST)#, size=(-1, 200), style=wx.LB_SINGLE)
        #self.sup_assembly_list = wx.ListCtrl(self, size=(-1, -1), style=wx.LC_REPORT | wx.BORDER_SUNKEN)  # , size=(-1, 200), style=wx.LB_SINGLE)
        #self.sup_assembly_list.InsertColumn(0, 'Super-Assemblies', width=125)
        #self.sup_assembly_list.InsertItem(0,'Supelies')
        #self.sup_assembly_list.InsertItem(1, 'Supelies')

        self.long_descrip_text = wx.TextCtrl(self, -1, self.long_description, size=(-1, 35), style=wx.TE_MULTILINE | wx.TE_WORDWRAP | wx.TE_READONLY | wx.BORDER_NONE)
        self.sizer_long_descrip = wx.StaticBoxSizer(wx.StaticBox(self, label='Extended Description'), orient=wx.VERTICAL)
        self.sizer_long_descrip.Add(self.long_descrip_text, flag=wx.ALL | wx.EXPAND)

        self.notes_header = wx.StaticText(self, -1, "{:<6}{:<25}{}".format("PM","DATE","NOTE"))
        self.notes_list = wx.ListBox(self, size=(-1, -1), choices=NUMBERS, style=wx.LB_SINGLE | wx.BORDER_NONE)

        self.sizer_notes = wx.StaticBoxSizer(wx.StaticBox(self, label='Notes'), orient=wx.VERTICAL)
        self.sizer_notes.Add(self.notes_header, border=2, flag=wx.ALL | wx.EXPAND)
        self.sizer_notes.Add(wx.StaticLine(self, style=wx.LI_HORIZONTAL), flag=wx.EXPAND)
        self.sizer_notes.Add(self.notes_list, flag=wx.ALL | wx.EXPAND)

        self.temptemptemp = ImgGridPanel(self)#ListCtrl(self, size=(-1,100), style=wx.LC_ICON | wx.BORDER_SUNKEN)
        #self.temptemptemp.InsertColumn(0, 'Subject')
        #self.temptemptemp = wx.TextCtrl(self, -1, self.long_description, size=(-1, -1),
        #                                style=wx.TE_MULTILINE | wx.TE_WORDWRAP | wx.TE_READONLY)

        #Revision Binds
        self.revision_bind(self.short_descrip_text, 'Short Description', self.part_number)

        self.sub_assembly_list.Bind(wx.EVT_LISTBOX, self.opennewpart)
        self.sub_assembly_list.Bind(wx.EVT_MOTION, self.updateTooltip)
        self.sup_assembly_list.Bind(wx.EVT_LISTBOX, self.opennewpart)
        self.sup_assembly_list.Bind(wx.EVT_MOTION, self.updateTooltip)


        #LEGACY BIND FOR FIDELITY -- self.shortdescriptext.Bind(wx.EVT_LEFT_DCLICK,
        #                           lambda event: self.revision_dialogue(event, self.part_number, self.shortdescriptext))


        image = wx.Image(os.path.join(DATADIR, r'whitewitch2.jpg'), wx.BITMAP_TYPE_ANY)
        imageBitmap = wx.StaticBitmap(self, wx.ID_ANY, wx.Bitmap(crop_box(image).Rescale(250, 250)))
        #print(self.shortdescriptext.label)



        #wx.Button(self, size=(200, -1), label="Something else here? Maybe!")

        self.sizer_master = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer_master_horizontal = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer_master_horizontal2 = wx.BoxSizer(wx.HORIZONTAL)
        #blep=wx.StaticText(self, label="Sub-Assemblies", style=wx.ALIGN_CENTER)
        #blep.SetBackgroundColour("purple")
        #self.sizer_master.Add(blep, proportion=1, border=5, flag=wx.ALL | wx.EXPAND)

        self.sizer_master_left = wx.BoxSizer(wx.VERTICAL)
        #self.test = wx.StaticBox(self, -1, "textbitches", flag=wx.Font(8))
        self.sizer_partline = wx.BoxSizer(wx.HORIZONTAL)
        #self.partnumtext.SetBackgroundColour("purple")
        self.sizer_partline.Add(self.part_number_text, border=5, flag=wx.ALL)
        self.sizer_partline.Add(wx.StaticLine(self, style=wx.LI_VERTICAL), flag=wx.EXPAND)
        self.sizer_partline.Add(self.part_type_text, border=5, flag=wx.ALL)
        self.sizer_partline.Add(wx.StaticLine(self, style=wx.LI_VERTICAL), flag=wx.EXPAND)
        self.sizer_partline.Add(self.short_descrip_text, proportion=1, border=5, flag=wx.ALL | wx.EXPAND)

        self.sizer_master_left.Add(self.sizer_partline, flag=wx.ALL | wx.EXPAND)
        self.sizer_master_left.Add(wx.StaticLine(self, style=wx.LI_HORIZONTAL), flag=wx.EXPAND)
        self.sizer_master_left.Add(wx.StaticLine(self, style=wx.LI_HORIZONTAL), flag=wx.EXPAND)
        self.sizer_master_left.AddSpacer(5)

        self.sizer_master_left.Add(self.sizer_long_descrip, flag=wx.ALL | wx.EXPAND)  # , border=15)
        self.sizer_master_left.Add(self.sizer_notes, proportion=1, flag=wx.ALL | wx.EXPAND)  # , border=15)
        self.sizer_master_left.Add(self.temptemptemp, proportion=2, flag=wx.ALL | wx.EXPAND)
        #self.sizer_master_left.Add(self.listBox, proportion=1, flag=wx.ALL | wx.EXPAND)  # , border=15)


        #Assembly Sizers
        self.sizer_assembly_left = wx.BoxSizer(wx.VERTICAL)
        self.sizer_assembly_left.Add(wx.StaticText(self, label="Children", style=wx.ALIGN_CENTER), border=5, flag=wx.ALL | wx.EXPAND)
        self.sizer_assembly_left.Add(self.sub_assembly_list, proportion=1, flag=wx.ALL | wx.EXPAND)

        self.sizer_assembly_right = wx.BoxSizer(wx.VERTICAL)
        self.sizer_assembly_right.Add(wx.StaticText(self, label="Parents", style=wx.ALIGN_CENTER), border=5, flag=wx.ALL | wx.EXPAND)
        self.sizer_assembly_right.Add(self.sup_assembly_list, proportion=1, flag=wx.ALL | wx.EXPAND)

        self.sizer_assembly = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer_assembly.Add(self.sizer_assembly_left, proportion=1, flag=wx.ALL | wx.EXPAND)
        self.sizer_assembly.Add(self.sizer_assembly_right, proportion=1, flag=wx.ALL | wx.EXPAND)

        self.sizer_master.Add(self.sizer_master_left, proportion=1, flag=wx.ALL | wx.EXPAND)
        self.sizer_master.Add(wx.StaticLine(self, style=wx.LI_VERTICAL), flag=wx.EXPAND)

        self.sizer_master_right = wx.BoxSizer(wx.VERTICAL)
        self.sizer_master_right.Add(imageBitmap, flag=wx.ALL | wx.EXPAND)
        self.sizer_master_right.Add(self.sizer_assembly, proportion=1, flag=wx.ALL | wx.EXPAND)
        self.sizer_master.Add(self.sizer_master_right, flag=wx.ALL | wx.EXPAND)

        self.SetSizer(self.sizer_master)


    def revision_bind(self, target, field, pn):
        target.Bind(wx.EVT_LEFT_DCLICK, lambda event: self.revision_dialogue(event, pn, field))


    def revision_dialogue(self, event, pn, field):
        dialog=ModifyFieldDialog(event.GetEventObject(), "Editing {0} of part {1}".format(field, pn))
        dialog.ShowModal()
        dialog.Destroy()
        #wx.MessageBox('Pythonspot wxWidgets demo', 'Editing __ of part ' + 'stringhere', wx.OK | wx.ICON_INFORMATION)
        #event.GetEventObject().SetLabel("TEREREE")

    def opennewpart(self, event):
        index = event.GetSelection()
        self.parent.fuck(event.GetEventObject().GetString(index), wx.GetKeyState(wx.WXK_SHIFT))
        event.GetEventObject().SetSelection(wx.NOT_FOUND)
        #self.text.SetValue(self.MESSAGE_FIELD_TYPES['1'][index])

    def updateTooltip(self, event):
        """
        Update the tooltip!
        """

        pos = wx.GetMousePosition()
        mouse_pos = self.sub_assembly_list.ScreenToClient(pos)
        item_index = self.sub_assembly_list.HitTest(mouse_pos)




        if item_index != -1:
            a = "%s is a good book!" % self.sub_assembly_list.GetString(item_index)
            if self.sub_assembly_list.GetToolTipText() != a:
                msg = a
                self.sub_assembly_list.SetToolTip(msg)
        else:
            self.sub_assembly_list.SetToolTip("")

        event.Skip()


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



class InterfacePanel(wx.Panel):
    def __init__(self, *args, **kwargs):
        wx.Panel.__init__(self, *args, **kwargs)

        self.notebook = InterfaceTabs(self)#, wx.EXPAND)#size=(400, -1))
#        self.button = wx.Button(self, label="Something else here? Maybe!")

        self.sizer = wx.BoxSizer()
        self.sizer.Add(self.notebook, proportion=1, flag=wx.EXPAND)
#        self.sizer.Add(self.button, proportion=0)
        self.SetSizer(self.sizer)


class InterfaceWindow(wx.Frame):
    def __init__(self, *args, **kwargs):
        wx.Frame.__init__(self, *args, **kwargs)
        self.panel = InterfacePanel(self)

        self.status = self.CreateStatusBar() #???Bottom bar

        self.menubar = wx.MenuBar()
        first=wx.Menu()
        second=wx.Menu()
        first.Append(wx.NewId(), "New", "Creates A new file")
        buttonfish=first.Append(wx.NewId(), "ADID", "Yo")
        self.Bind(wx.EVT_MENU, self.onAdd, buttonfish)
        self.menubar.Append(first, "File")
        self.menubar.Append(second, "Edit")
        self.SetMenuBar(self.menubar)

        self.Show()

    def onAdd(self, event):
        self.panel.notebook.fuck("fuck")
        #PANELS.append("rrr")
        #print("sdgsrg")


app = wx.App(False)
win = InterfaceWindow(None, size=(1200, 600))
win.SetIcon(wx.Icon('CH.png'))
app.MainLoop()