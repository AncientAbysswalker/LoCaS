COLORS = ["red", "blue", "black", "yellow", "green"]
NUMBERS = ['0', '1', '2', '3', '4']
PANELS = ["107-00107", "G39-00107", "777-00107"]
SUBLIST = ["999-00107", "G39-00107", "767-00107"]
SUPLIST = ["456-00107", "G39-06767", "776-04577"]

import random
import wx
import sys
import wx.lib.agw.flatnotebook as fnb
import wx.lib.agw.ultimatelistctrl as ulc

class ModifyFieldDialog(wx.Dialog):

    def __init__(self, part_number, field_name, edit_field, *args, **kw):
        super(ModifyFieldDialog, self).__init__(*args, **kw)

        self.part_number = part_number
        self.field_name = field_name
        self.edit_field = edit_field

        self.InitUI()
        self.SetSize((500, 160)) #NEEDS FINESSE FOR TYPE OF PASS
        self.SetTitle('Editing {0} of part {1}'.format(self.field_name, self.part_number))


    def InitUI(self):

        pnl = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)

        sb = wx.StaticBox(pnl, label='Editing {0} of part {1}'.format(self.field_name, self.part_number))
        sbs = wx.StaticBoxSizer(sb, orient=wx.VERTICAL)

        self.importanttextbox=wx.TextCtrl(pnl, value = self.edit_field.GetLabel())

        sbs.Add(self.importanttextbox, flag=wx.ALL | wx.EXPAND, border=5)

        pnl.SetSizer(sbs)

        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        okButton = wx.Button(self, label='Commit')
        closeButton = wx.Button(self, label='Cancel')
        hbox2.Add(okButton)
        hbox2.Add(closeButton, flag=wx.LEFT, border=5)

        vbox.Add(pnl, proportion=1,
            flag=wx.ALL|wx.EXPAND, border=5)
        vbox.Add(hbox2, flag=wx.ALIGN_CENTER|wx.TOP|wx.BOTTOM, border=10)

        self.SetSizer(vbox)

        okButton.Bind(wx.EVT_BUTTON, self.OnCommit)
        closeButton.Bind(wx.EVT_BUTTON, self.OnCancel)
        #okButton.Bind(wx.EVT_BUTTON, lambda event: self.OnClose(event))

    def OnCommit(self, e):
        self.edit_field.SetLabel(self.importanttextbox.GetValue())
        self.Destroy()

    def OnCancel(self, e):
        self.Destroy()

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

        #Text Widgets
        self.part_number_text = wx.StaticText(self, size = (60, -1), label = self.part_number, style = wx.ALIGN_CENTER)
        self.part_type_text = wx.StaticText(self, size = (100, -1), label = self.part_type, style = wx.ALIGN_CENTER)
        self.short_descrip_text = wx.StaticText(self, size = (-1, -1), label = self.short_description, style = wx.ST_ELLIPSIZE_END)

        self.listBox = wx.ListBox(self, size=(-1, 200), choices=NUMBERS, style=wx.LB_SINGLE)


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

        self.long_descrip_text = wx.TextCtrl(self, -1, self.long_description, style=wx.TE_MULTILINE | wx.TE_WORDWRAP | wx.TE_READONLY)

        #Revision Binds
        self.revision_bind(self.short_descrip_text, 'Short Description', self.part_number)

        self.sub_assembly_list.Bind(wx.EVT_LISTBOX, self.opennewpart)
        self.sup_assembly_list.Bind(wx.EVT_LISTBOX, self.opennewpart)


        #LEGACY BIND FOR FIDELITY -- self.shortdescriptext.Bind(wx.EVT_LEFT_DCLICK,
        #                           lambda event: self.revision_dialogue(event, self.part_number, self.shortdescriptext))


        image = wx.Image('T:\Dark Storage\Software\Fantasy Grounds II\data\portraits\whitewitch.jpg', wx.BITMAP_TYPE_ANY)
        imageBitmap = wx.StaticBitmap(self, wx.ID_ANY, wx.Bitmap(image.Rescale(250,250)))
        #print(self.shortdescriptext.label)



        #wx.Button(self, size=(200, -1), label="Something else here? Maybe!")

        self.sizer_one = wx.BoxSizer()
        self.sizer_two = wx.BoxSizer(wx.VERTICAL)
        #self.test = wx.StaticBox(self, -1, "textbitches", flag=wx.Font(8))
        self.partline = wx.BoxSizer(wx.HORIZONTAL)
        #self.partnumtext.SetBackgroundColour("purple")
        self.partline.Add(self.part_number_text, border=5, flag=wx.ALL)
        self.partline.Add(wx.StaticLine(self, style=wx.LI_VERTICAL), flag=wx.EXPAND)
        self.partline.Add(self.part_type_text, border=5, flag=wx.ALL)
        self.partline.Add(wx.StaticLine(self, style=wx.LI_VERTICAL), flag=wx.EXPAND)
        self.partline.Add(self.short_descrip_text, proportion=1, border=5, flag=wx.ALL | wx.EXPAND)

        self.sizer_two.Add(self.partline, flag=wx.ALL | wx.EXPAND)
        self.sizer_two.Add(wx.StaticLine(self, style=wx.LI_HORIZONTAL), flag=wx.EXPAND)
        self.sizer_two.Add(wx.StaticLine(self, style=wx.LI_HORIZONTAL), flag=wx.EXPAND)
        self.sizer_two.AddSpacer(5)


        self.sizer_two.Add(self.long_descrip_text, proportion=1, flag=wx.ALL | wx.EXPAND)  # , border=15)
        self.sizer_two.Add(self.listBox, proportion=1, flag=wx.ALL | wx.EXPAND)  # , border=15)


        self.assembly_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.assembly_sizer.Add(self.sub_assembly_list, proportion=1, flag=wx.ALL | wx.EXPAND)
        self.assembly_sizer.Add(self.sup_assembly_list, proportion=1, flag=wx.ALL | wx.EXPAND)

        self.sizer_one.Add(self.sizer_two, proportion=1, flag=wx.ALL | wx.EXPAND)
        self.sizer_one.Add(wx.StaticLine(self, style=wx.LI_VERTICAL), flag=wx.EXPAND)

        self.rightcolumnsizer = wx.BoxSizer(wx.VERTICAL)
        self.rightcolumnsizer.Add(imageBitmap, flag=wx.ALL | wx.EXPAND)
        self.rightcolumnsizer.Add(self.assembly_sizer, proportion=1, flag=wx.ALL | wx.EXPAND)
        self.sizer_one.Add(self.rightcolumnsizer, flag=wx.ALL | wx.EXPAND)

        self.SetSizer(self.sizer_one)


    def revision_bind(self, target, field, pn):
        target.Bind(wx.EVT_LEFT_DCLICK, lambda event: self.revision_dialogue(event, pn, field))


    def revision_dialogue(self, event, pn, field):
        dialog=ModifyFieldDialog(pn, field, event.GetEventObject(), None)#, title='mytitle')
        dialog.ShowModal()
        dialog.Destroy()
        #wx.MessageBox('Pythonspot wxWidgets demo', 'Editing __ of part ' + 'stringhere', wx.OK | wx.ICON_INFORMATION)
        #event.GetEventObject().SetLabel("TEREREE")

    def opennewpart(self, event):
        index = event.GetSelection()
        self.parent.fuck(event.GetEventObject().GetString(index), wx.GetKeyState(wx.WXK_SHIFT))
        event.GetEventObject().SetSelection(wx.NOT_FOUND)
        #self.text.SetValue(self.MESSAGE_FIELD_TYPES['1'][index])


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
        self.sizer.Add(self.notebook, wx.EXPAND)
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