#!/usr/bin/env python
# PyVision License
#
# Copyright (c) 2006-2008 David S. Bolme, Sayantan Sarkar, Ananya Mukherjee
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# 1. Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution.
#
# 3. Neither name of copyright holders nor the names of its contributors
# may be used to endorse or promote products derived from this software
# without specific prior written permission.
#
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# ``AS IS'' AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL THE REGENTS OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
# PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import wx
import os
import os.path
import csv
import random
'''
This program is a simple gui for selecting landmarks for a
set of images.
The program takes a file with image locations as an argument.
It loads each image in that directory into a list frame.
It displays the image in the frame.
The image is clicked on to select the landmark coordinates.
landmark coordinates are saved to a file.
'''

#GUI references: http://wiki.wxpython.org/Getting%20Started

IMAGE_FORMATS=[".JPG",".PNG",".PPM",".PGM",".GIF",".TIF",".TIFF",]

class EyePickerFrame(wx.Frame):

    def __init__(self,parent,id,name,image_key,n_points=None,randomize=False,scale=1.0, landmarkNames = '', startpoint = 0):
        wx.Frame.__init__(self,parent,id,name)

        # ---------------- Basic Data -------------------
        self.image_key = image_key
        self.n_points = n_points
        self.image_names = []
        self.current_image = None
        self.image_name = None
        self.scale = scale
        self.landmarkNames = landmarkNames
        self.imageOrientation = {}
        with open(image_key, 'r') as content_file:
            content = content_file.read()

        for name in content.split('\n')[startpoint:]:
            for format in IMAGE_FORMATS:
                if name.upper().endswith(format):
                    self.image_names.append(name)

        if randomize:
            random.shuffle(self.image_names)
        self.filename = None
        self.coords = {}

        # ------------- Other Components ----------------
        self.CreateStatusBar()

        # ------------------- Menu ----------------------

        filemenu= wx.Menu()
        id_about = wx.NewId()
        id_help = wx.NewId()
        id_open = wx.NewId()
        id_save = wx.NewId()
        id_save_as = wx.NewId()
        id_exit  = wx.NewId()
        # File Menu
        filemenu.Append(wx.ID_ABOUT, wx.EmptyString)
        filemenu.Append(wx.ID_HELP, wx.EmptyString)
        filemenu.AppendSeparator()
        filemenu.Append(wx.ID_OPEN, wx.EmptyString)
        filemenu.Append(wx.ID_SAVE, wx.EmptyString)
        filemenu.Append(wx.ID_SAVEAS, wx.EmptyString)
        filemenu.AppendSeparator()
        filemenu.Append(wx.ID_EXIT,wx.EmptyString)
        # Creating the menubar.
        menuBar = wx.MenuBar()
        menuBar.Append(filemenu,"&File") # Adding the "filemenu" to the MenuBar
        self.SetMenuBar(menuBar)  # Adding the MenuBar to the Frame content.

        # ----------------- Image List ------------------
        self.list=wx.ListBox(self,wx.NewId(),style=wx.LC_REPORT|wx.SUNKEN_BORDER,choices=[str(i+startpoint) + ' ' + self.image_names[i] for i in range(0,len(self.image_names))])
        #self.list=wx.ListBox(self,wx.NewId(),style=wx.LC_REPORT|wx.SUNKEN_BORDER,choices=self.image_names)
        self.list.Show(True)

        # --------------- Image Display -----------------
        self.static_bitmap = wx.StaticBitmap(self,wx.NewId(), bitmap=wx.EmptyBitmap(300, 300))
        self.static_bitmap.SetCursor(wx.CROSS_CURSOR)

        # --------------- Comments/Prompts -----------------
        self.static_text = wx.StaticText(self, 2, 'Click on an image in the left pane')
        #wxStaticText(panel, -1, "Size:", wxDLG_PNT(panel, wxPoint(4, 4)),  wxDefaultSize)

        # --------------- Window Layout -----------------
        box = wx.BoxSizer(wx.HORIZONTAL)
        box.Add(self.list, 1, wx.EXPAND)
        box.Add(self.static_bitmap, 3, wx.EXPAND)
        box.Add(self.static_text,2, wx.EXPAND)

        self.SetAutoLayout(True)
        self.SetSizer(box)
        self.Layout()

        # -------------- Event Handleing ----------------
        #wx.EVT_LISTBOX(self, self.list.GetId(), self.onSelect)
        self.list.Bind(wx.EVT_KEY_UP, self.onSelect)
        wx.EVT_SIZE(self.static_bitmap, self.onBitmapResize)
        wx.EVT_LEFT_DOWN(self.static_bitmap, self.onClick)
        wx.EVT_LEFT_UP(self.static_bitmap, self.onRelease)
        wx.EVT_MOTION(self.static_bitmap, self.onMotion)
        wx.EVT_RIGHT_DOWN(self.static_bitmap, self.onRightClick)
        wx.EVT_RIGHT_UP(self.static_bitmap, self.onRightRelease)
        wx.EVT_MIDDLE_DOWN(self.static_bitmap, self.onMidClick)
        wx.EVT_MIDDLE_UP(self.static_bitmap, self.onMidRelease)
        wx.EVT_LEFT_DCLICK(self.static_bitmap, self.onLeftDoubleClick)
        wx.EVT_KEY_DOWN(self, self.onKeyDown)
##        self.static_bitmap.Bind(wx.EVT_CHAR_HOOK, self.onKeyDown)
##        panel = wx.Panel(self, wx.ID_ANY)
##        btn = wx.Button(panel, label="OK")
##        btn.Bind(wx.EVT_KEY_DOWN, self.onKeyDown)

        self.moving = None

        wx.EVT_MENU(self,wx.ID_OPEN,self.onOpen)
        wx.EVT_MENU(self,wx.ID_SAVE,self.onSave)
        wx.EVT_MENU(self,wx.ID_SAVEAS,self.onSaveAs)

        wx.EVT_MENU(self,wx.ID_ABOUT,self.onAbout)
        wx.EVT_MENU(self,wx.ID_HELP,self.onHelp)
        #wx.EVT_MENU(self,wx.ID_EXIT,self.onExit)

        wx.EVT_CLOSE(self,self.onClose)


    def openCSVFile(self,path):
        reader = csv.reader(open(path, "rb"))
        first = True
        eyes = False
        coords = {}
        for row in reader:
            filename = row[0]
            row = row[1:]

            if len(row)%2 != 0:
                print "Error Loading File"
                raise TypeError("Odd number of values in this row")

            points = []
            for i in range(0,len(row),2):
                point = (float(row[i]),float(row[i+1]))
                points.append(point)

            coords[filename] = points
        print "CSV File Data: ", coords
        self.coords = coords


    def save(self,path):
        ''' Save the coords to a csv file. '''
        writer = csv.writer(open(path,'wb'))

        keys = self.coords.keys()
        keys.sort()
        for key in keys:
            row = [key]
            for point in self.coords[key]:
                row.append(point[0])
                row.append(point[1])
            row.append(self.imageOrientation[key])
            writer.writerow(row)


    def onSelect(self,event):
        keypressed = event.GetKeyCode()
        #print keypressed

        if keypressed == wx.WXK_LEFT or keypressed == wx.WXK_RIGHT or keypressed == wx.WXK_UP or keypressed == wx.WXK_DOWN:

            if self.image_name:
                if self.n_points != None and len(self.coords[self.image_name]) != self.n_points:
                    print "ERROR: incorrect number of points."

            s = event.GetEventObject().GetSelection()
            #print s

            self.image_name = self.image_names[s]

            if not self.coords.has_key(self.image_name):
                self.coords[self.image_name] = []

            filename = os.path.join(self.image_key,self.image_name)
            self.current_image = wx.Image(filename)
            self.first_click = True
            self.DisplayImage()
            self.static_text.SetLabel(landmark_names.split(',')[0])
            self.imageOrientation[self.image_name] = 1
            print 'Orientation = top (default)'

        if keypressed == ord('W') :
            self.imageOrientation[self.image_name] = 1
            print 'Orientation = top (default)'
        if keypressed == ord('A') :
            self.imageOrientation[self.image_name] = 2
            print 'Orientation = left'
        if keypressed == ord('S') :
            self.imageOrientation[self.image_name] = 3
            print 'Orientation = right'
        if keypressed == ord('Z') :
            self.imageOrientation[self.image_name] = 4
            print 'Orientation = bottom'


    def onBitmapResize(self,event):
        w = event.GetSize().GetWidth()
        h = event.GetSize().GetHeight()
        self.static_bitmap.SetSize(event.GetSize())
        self.DisplayImage()


    def DisplayImage(self):
        if self.current_image:
            tw = self.static_bitmap.GetSize().GetWidth()
            th = self.static_bitmap.GetSize().GetHeight()
            sw = self.current_image.GetSize().GetWidth()
            sh = self.current_image.GetSize().GetHeight()

            #self.scale = min(tw/float(sw),th/float(sh))

            tw = int(sw*self.scale)
            th = int(sh*self.scale)

            im = self.current_image.Copy()
            im.Rescale(tw,th)
            bm = im.ConvertToBitmap()
            bmdc = wx.MemoryDC(bm)
            bmdc.SetBrush(wx.TRANSPARENT_BRUSH)
            bmdc.SetPen(wx.RED_PEN)
            bmdc.SetTextForeground(wx.RED)

            i = 1
            for point in self.coords[self.image_name]:
                if point[0] >= 0 and point[1] >= 0:
                    bmdc.DrawCircle(self.scale*point[0], self.scale*point[1], 5)
                    w,h = bmdc.GetTextExtent(str(i))
                    bmdc.DrawText(str(i),self.scale*point[0]-w/2, self.scale*point[1]+5)
                i += 1

            del bmdc
            self.static_bitmap.SetBitmap(bm)


    # ------------- Event Handlers ---------------
    def onClick(self,event):
        x = event.GetX()/self.scale
        y = event.GetY()/self.scale

        if not self.image_name: return

        # Adjust a point
        for i in range(len(self.coords[self.image_name])):
            px,py = self.coords[self.image_name][i]
            if abs(px - x) < 4 and abs(py - y) < 4:
                self.coords[self.image_name][i] = (x,y,)
                self.moving = i
                self.DisplayImage()
                return

        # Allow the user to enter new points if the image was just loaded.
        if self.first_click:
            self.coords[self.image_name] = []
            self.first_click = False

        if len(self.coords[self.image_name]) < self.n_points or self.n_points == None:
            self.coords[self.image_name].append((x,y,))
            self.moving = len(self.coords[self.image_name]) - 1
            self.DisplayImage()


    def onMotion(self,event):
        x = event.GetX()/self.scale
        y = event.GetY()/self.scale

        if self.moving != None:
            self.coords[self.image_name][self.moving] = (x,y,)
            self.DisplayImage()


    def onRelease(self,event):
        x = event.GetX()/self.scale
        y = event.GetY()/self.scale
        if self.moving != None and len(self.coords[self.image_name]) < self.n_points:
            self.coords[self.image_name][self.moving] = (x,y,)
            self.DisplayImage()
        self.moving = None
        self.static_text.SetLabel(landmark_names.split(',')[len(self.coords[self.image_name])] if len(self.coords[self.image_name]) < self.n_points else 'done')


    def onRightClick(self,event):
        if self.first_click:
            self.coords[self.image_name] = []
            self.first_click = False


    def onRightRelease(self,event):
        if len(self.coords[self.image_name]) < self.n_points:
            self.coords[self.image_name].append((-1,-1,))
            self.DisplayImage()
        self.static_text.SetLabel(landmark_names.split(',')[len(self.coords[self.image_name])] if len(self.coords[self.image_name]) < self.n_points else 'done')
        print 'right release: point ignored'


    def onMidClick(self,event):
        pass

    def onMidRelease(self,event):
        self.coords[self.image_name] = []
        self.first_click = True
        self.DisplayImage()
        self.static_text.SetLabel(landmark_names.split(',')[0])
        print('resetting')

    def onLeftDoubleClick(self, event):
        self.coords[self.image_name] = [(-1,-1)]*self.n_points
        self.static_text.SetLabel('done')
        self.DisplayImage()

    def onKeyDown(self, event):
        pass


    def onAbout(self,event):
        dlg = wx.MessageDialog(self,message="For more information visit:\nhttps://github.com/ssarkar2/faceMarker",style = wx.OK )
        result = dlg.ShowModal()


    def onHelp(self, event):
        dlg = wx.MessageDialog(self, '''Instructions:\n Starting off\n 1. In the first dialog, enter the location of the key file\n 2. In the second enter starting point in the key file 3. In the third enter the (max) number of landmarks that will be marked for each image\n 4. In the fourth enter names of the landmarks separated by \',\' \n 5. In the fifth enter the scaling factor \n\n Operations\n 1. select landmarks with single left click. The right pane shows a prompt which landmark to select now.\n 2. Right click anywhere on the image to ignore/skip a landmark (useful for partial faces where some landmarks are not visible)\n 3. The GUI will allow you to only mark \'max\' number of landmarks\n 4. Use up/down or left/right buttons to go to the next image, or click on the image in the image selector pane on the left \n 5. Use double click to indicate no face. Then move on to the next pic. \n 6. Use middle click to make all landmarks in current pic disappear. You can also go to another pic and come back and start again\n 7. Default orientation is top. press 2 for left (head is to the left, chin to the right on the screen), 3 for right and 4 for bottom (that is face is upside down)
        \n Other features \n 1. Save the landmarks as a csv file.\n 2. use \'open\' to load a csv that contains landmarks and view them superimposed on the images ''', style=wx.OK)
        result = dlg.ShowModal()
        dlg.Destroy()


    def onOpen(self,event):
        print "Open"
        fd = wx.FileDialog(self,style=wx.FD_OPEN)
        fd.ShowModal()
        self.filename = fd.GetPath()
        print "On Open...",self.filename
        self.openCSVFile(self.filename)


    def onSave(self,event):
        if self.filename == None:
            # In this case perform a "Save As"
            self.onSaveAs(event)
        else:
            self.save(self.filename)


    def onSaveAs(self,event):
        fd = wx.FileDialog(self,message="Save the coordinates as...",style=wx.FD_SAVE,
                           wildcard="Comma separated value (*.csv)|*.csv")
        fd.ShowModal()
        self.filename = fd.GetPath()
        self.save(self.filename)


    def onClose(self,event):
        dlg = wx.MessageDialog(self,message="Would you like to save the coordinates before exiting?",style = wx.YES_NO | wx.YES_DEFAULT)
        result = dlg.ShowModal()
        if result == wx.ID_YES:
            print "Saving..."
            self.onSave(event)
        else:
            print "Discarding changes..."

        # Pass this on to the default handler.
        event.Skip()


def ask(parent=None, message='', default_value=''):
    dlg = wx.TextEntryDialog(parent, message, defaultValue=default_value, style=wx.OK)
    dlg.ShowModal()
    result = dlg.GetValue()
    dlg.Destroy()
    return result

if __name__ == '__main__':
    app = wx.App(False)

    image_key = ask(message = 'Please select a file that contains images locations.', default_value = 'C:\Sayantan\project\sem4\\faceannotate\\keyfile.txt')
    print "Image Dir",image_key

    start = ask(message = 'Please enter start point in the file', default_value = '0')
    print "Start point",start

    num_points = int(ask(message = 'Please enter number of landmark points', default_value = '7'))
    print "Number of points",num_points

    landmark_names = ask(message = 'Please enter names of landmark points', default_value = 'top left, bottom right, left eye, right eye, nose, left mouth tip, right mouth tip')
    print "Landmarks",landmark_names

    scale = float(ask(message = 'Please enter scale factor (for displaying image)', default_value = '0.5'))
    print "Scale",scale

    frame = EyePickerFrame(None, wx.ID_ANY, "Landmark Annotation",image_key,n_points=num_points,randomize=False,scale=scale, landmarkNames = landmark_names, startpoint = int(start))
    frame.Show(True)
    app.MainLoop()
