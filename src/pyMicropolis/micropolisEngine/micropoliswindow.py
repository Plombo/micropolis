# micropoliswindow.py
#
# Micropolis, Unix Version.  This game was released for the Unix platform
# in or about 1990 and has been modified for inclusion in the One Laptop
# Per Child program.  Copyright (C) 1989 - 2007 Electronic Arts Inc.  If
# you need assistance with this program, you may contact:
#   http://wiki.laptop.org/go/Micropolis  or email  micropolis@laptop.org.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at
# your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.  You should have received a
# copy of the GNU General Public License along with this program.  If
# not, see <http://www.gnu.org/licenses/>.
#
#             ADDITIONAL TERMS per GNU GPL Section 7
#
# No trademark or publicity rights are granted.  This license does NOT
# give you any right, title or interest in the trademark SimCity or any
# other Electronic Arts trademark.  You may not distribute any
# modification of this program using the trademark SimCity or claim any
# affliation or association with Electronic Arts Inc. or its employees.
#
# Any propagation or conveyance of this program must include this
# copyright notice and these terms.
#
# If you convey this program (or any modifications of it) and assume
# contractual liability for the program to recipients of it, you agree
# to indemnify Electronic Arts for any liability that those contractual
# assumptions impose on Electronic Arts.
#
# You may not misrepresent the origins of this program; modified
# versions of the program must be marked as such and not identified as
# the original program.
#
# This disclaimer supplements the one included in the General Public
# License.  TO THE FULLEST EXTENT PERMISSIBLE UNDER APPLICABLE LAW, THIS
# PROGRAM IS PROVIDED TO YOU "AS IS," WITH ALL FAULTS, WITHOUT WARRANTY
# OF ANY KIND, AND YOUR USE IS AT YOUR SOLE RISK.  THE ENTIRE RISK OF
# SATISFACTORY QUALITY AND PERFORMANCE RESIDES WITH YOU.  ELECTRONIC ARTS
# DISCLAIMS ANY AND ALL EXPRESS, IMPLIED OR STATUTORY WARRANTIES,
# INCLUDING IMPLIED WARRANTIES OF MERCHANTABILITY, SATISFACTORY QUALITY,
# FITNESS FOR A PARTICULAR PURPOSE, NONINFRINGEMENT OF THIRD PARTY
# RIGHTS, AND WARRANTIES (IF ANY) ARISING FROM A COURSE OF DEALING,
# USAGE, OR TRADE PRACTICE.  ELECTRONIC ARTS DOES NOT WARRANT AGAINST
# INTERFERENCE WITH YOUR ENJOYMENT OF THE PROGRAM; THAT THE PROGRAM WILL
# MEET YOUR REQUIREMENTS; THAT OPERATION OF THE PROGRAM WILL BE
# UNINTERRUPTED OR ERROR-FREE, OR THAT THE PROGRAM WILL BE COMPATIBLE
# WITH THIRD PARTY SOFTWARE OR THAT ANY ERRORS IN THE PROGRAM WILL BE
# CORRECTED.  NO ORAL OR WRITTEN ADVICE PROVIDED BY ELECTRONIC ARTS OR
# ANY AUTHORIZED REPRESENTATIVE SHALL CREATE A WARRANTY.  SOME
# JURISDICTIONS DO NOT ALLOW THE EXCLUSION OF OR LIMITATIONS ON IMPLIED
# WARRANTIES OR THE LIMITATIONS ON THE APPLICABLE STATUTORY RIGHTS OF A
# CONSUMER, SO SOME OR ALL OF THE ABOVE EXCLUSIONS AND LIMITATIONS MAY
# NOT APPLY TO YOU.


########################################################################
# Micropolis Window
# Don Hopkins


########################################################################
# Import stuff


import sys
import os
import time
import gtk
import gobject
import cairo
import pango
import math
import thread
import random
import array


########################################################################
# Import our modules


import micropolisengine
import micropolisnotebook
import micropolisstartpanel
import micropolisgaugeview
import micropolisnoticepanel
import micropolismessagespanel
import micropolisdrawingarea
import micropolisevaluationpanel
import micropolishistorypanel
import micropolisbudgetpanel
import micropolismappanel
import micropolisdisasterspanel
import micropoliscontrolpanel


########################################################################
# MicropolisPanedWindow

class MicropolisPanedWindow(gtk.Window):


    def __init__(
        self,
        engine=None,
        **args):

        gtk.Window.__init__(self, **args)
        
        self.builder = gtk.Builder()
        self.builder.add_from_file('interface.ui')

        self.connect('destroy', gtk.main_quit)
        self.connect('realize', self.handleRealize)
        self.connect('size-allocate', self.handleResize)

        self.set_title("Open Source Micropolis on Python / GTK / Cairo / Pango")

        self.firstResize = True

        self.engine = engine

        engine.expressInterest(
            self,
            ('gameMode',))
        
        # Make the menu bar.
        
        menuBar = self.builder.get_object('menuBar')
        self.menuBar = menuBar

        # Make the big map view.

        editMapView = micropolisdrawingarea.EditableMicropolisDrawingArea(
                engine=self.engine)
        self.editMapView = editMapView

        # Make the navigation map view.

        navigationMapView = micropolisdrawingarea.NavigationMicropolisDrawingArea(
                engine=self.engine)
        self.navigationMapView = navigationMapView
        navigationMapView.set_size_request(
            micropolisengine.WORLD_W,
            micropolisengine.WORLD_H)

        # Make the gauge view.

        gaugeView = micropolisgaugeview.MicropolisGaugeView(engine=self.engine)
        self.gaugeView = gaugeView

        # Make the vbox for the gauge and navigation map views.

        vbox1 = gtk.VBox(False, 0)
        self.vbox1 = vbox1

        # Make the notebooks.

        modeNotebook = gtk.Notebook()
        self.modeNotebook = modeNotebook
        modeNotebook.set_group_id(0)
        modeNotebook.set_show_tabs(False)

        startPanel = micropolisstartpanel.MicropolisStartPanel(
            engine=engine,
            target=self)
        self.startPanel = startPanel

        notebook1 = micropolisnotebook.MicropolisNotebook(target=self)
        self.notebook1 = notebook1

        notebook2 = micropolisnotebook.MicropolisNotebook(target=self)
        self.notebook2 = notebook2

        notebook3 = micropolisnotebook.MicropolisNotebook(target=self)
        self.notebook3 = notebook3

        # Make the panels in the notebooks.

        noticePanel = micropolisnoticepanel.MicropolisNoticePanel(
            engine=engine,
            centerOnTileHandler=self.centerOnTileHandler)
        self.noticePanel = noticePanel
        notebook1.addLabelTab('Notice', noticePanel)

        # @fixme Try to fix the problem of the view's rect being huge on the mini map.
        noticePanel.resize_children()

        messagesPanel = micropolismessagespanel.MicropolisMessagesPanel(
            engine=engine)
        self.messagesPanel = messagesPanel
        notebook1.addLabelTab('Messages', messagesPanel)

        evaluationPanel = micropolisevaluationpanel.MicropolisEvaluationPanel(
            engine=engine)
        self.evaluationPanel = evaluationPanel
        notebook1.addLabelTab('Evaluation', evaluationPanel)

        historyPanel = micropolishistorypanel.MicropolisHistoryPanel(
            engine=engine)
        self.historyPanel = historyPanel
        notebook1.addLabelTab('History', historyPanel)

        budgetPanel = micropolisbudgetpanel.MicropolisBudgetPanel(
            engine=engine)
        self.budgetPanel = budgetPanel
        notebook1.addLabelTab('Budget', budgetPanel)

        mapPanel = micropolismappanel.MicropolisMapPanel(
            engine=engine,
            mapViews=[self.navigationMapView, self.editMapView,])
        self.mapPanel = mapPanel
        notebook1.addLabelTab('Map', mapPanel)

        disastersPanel = micropolisdisasterspanel.MicropolisDisastersPanel(
            engine=engine)
        self.disastersPanel = disastersPanel
        notebook1.addLabelTab('Disasters', disastersPanel)

        controlPanel = micropoliscontrolpanel.MicropolisControlPanel(
            engine=engine,
            target=self)
        self.controlPanel = controlPanel
        notebook1.addLabelTab('Control', controlPanel)

        # Panes

        vpaned1 = gtk.VPaned()
        self.vpaned1 = vpaned1

        vpaned2 = gtk.VPaned()
        self.vpaned2 = vpaned2

        hpaned1 = gtk.HPaned()
        self.hpaned1 = hpaned1

        hpaned2 = gtk.HPaned()
        self.hpaned2 = hpaned2

        # Pack the views into the panes.

        vbox1.pack_start(gaugeView, False, False, 0)
        vbox1.pack_start(navigationMapView, True, True, 0)

        hpaned1.pack1(vbox1, resize=False, shrink=False)
        hpaned1.pack2(notebook1, resize=False, shrink=False)

        hpaned2.pack1(notebook2, resize=False, shrink=False)
        hpaned2.pack2(notebook3, resize=False, shrink=False)

        vpaned1.pack1(hpaned1, resize=False, shrink=False)
        vpaned1.pack2(vpaned2, resize=False, shrink=False)

        vpaned2.pack1(editMapView, resize=False, shrink=False)
        vpaned2.pack2(hpaned2, resize=False, shrink=False)

        modeNotebook.append_page(startPanel)

        modeNotebook.append_page(vpaned1)
        
        # Create a top level vbox for the menu bar and top level mode notebook.
        
        mainVbox = gtk.VBox(False, 0)
        self.mainVbox = mainVbox
        mainVbox.pack_start(menuBar, False, True, 0)
        mainVbox.pack_start(modeNotebook, True, True, 0)

        # Put the top level vbox in this window.

        self.add(mainVbox)
        
        # Set the menu callbacks.
        
        self.setCallbacks()

        # Load a city file.

        self.startGame()


    def update(self, name, *args):

        if name == 'gameMode':

            engine = self.engine
            gameMode = engine.gameMode

            navigationMapView = self.navigationMapView
            editMapView = self.editMapView
            modeNotebook = self.modeNotebook

            if gameMode == 'start':

                navigationMapView.disengage()
                editMapView.disengage()
                engine.pause()
                modeNotebook.set_current_page(0)

            elif gameMode == 'play':

                navigationMapView.engage()
                editMapView.engage()
                navigationMapView.updateView()
                editMapView.updateView()
                engine.resume()
                modeNotebook.set_current_page(1)
    
    def setCallbacks(self):
        print "SET CALLBACKS: micropoliswindow"
        
        builder = self.builder
        
        loadCityItem = builder.get_object('loadCityItem')
        loadCityItem.connect('activate', self.loadCityDialog)
        
        saveCityItem = builder.get_object('saveCityItem')
        saveCityItem.connect('activate', self.saveCityDialog)
        
        saveCityItem = builder.get_object('saveCityAsItem')
        saveCityItem.connect('activate', self.saveCityAsDialog)

    def startGame(self):

        print "==== STARTGAME"

        engine = self.engine

        if False:
            cityFileName = 'cities/haight.cty'
            #cityFileName = 'cities/yokohama.cty'
            print "Loading city file:", cityFileName
            engine.loadFile(cityFileName)
        else:
            self.generateCity()

        # Initialize the simulator engine.

        engine.setSpeed(2)
        engine.setCityTax(9)
        engine.setEnableDisasters(False)

        self.startMode()


    def startScenario(self, id):
        print "STARTSCENARIO", id
        engine = self.engine
        engine.loadMetaScenario(id)


    def loadCityDialog(self, button=None, data=None):
        print "LOAD CITY DIALOG"

        dialog = gtk.FileChooserDialog(
            title='Select a city to load.',
            action=gtk.FILE_CHOOSER_ACTION_OPEN,
            buttons=(
                gtk.STOCK_CANCEL,
                gtk.RESPONSE_CANCEL,
                gtk.STOCK_OPEN,
                gtk.RESPONSE_OK,
            ))
        
        xmlFilter = gtk.FileFilter()
        xmlFilter.set_name("Micropolis Cities (*.xml)")
        xmlFilter.add_pattern("*.xml")
        dialog.add_filter(xmlFilter)
        
        ctyFilter = gtk.FileFilter()
        ctyFilter.set_name("SimCity Cities (*.cty)")
        ctyFilter.add_pattern("*.cty")
        ctyFilter.add_pattern("*.CTY")
        dialog.add_filter(ctyFilter)
        
        allFilter = gtk.FileFilter()
        allFilter.set_name("All Cities (*.xml, *.cty)")
        allFilter.add_pattern("*.xml")
        allFilter.add_pattern("*.cty")
        allFilter.add_pattern("*.CTY")
        dialog.add_filter(allFilter)
        dialog.set_filter(allFilter)

        citiesFolder = 'cities'
        dialog.set_current_folder(citiesFolder)

        response = dialog.run()
        if response == gtk.RESPONSE_OK:
            fileName = dialog.get_filename()
            filterName = dialog.get_filter().get_name()
            print "FILENAME", fileName
            print "FILE TYPE", filterName
            result = False
            if fileName.endswith('.xml'):
                try:
                    self.engine.loadMetaCity(fileName)
                    result = True
                except IOError, e:
                    print "FAILED TO LOAD META CITY", fileName
                    print str(e)
                    result = False
            elif fileName.lower().endswith('.cty'):
                try:
                    self.engine.loadPlainCity(fileName)
                    result = True
                except IOError, e:
                    print 'FAILED TO LOAD CITY', fileName
                    print str(e)
                    result = False
            else:
                print "ERROR: file '%s' is not a CTY or XML file"
                result = False
            print "RESULT", result
        elif response == gtk.RESPONSE_CANCEL:
            print 'Closed, no files selected'
        dialog.destroy()


    def generateCity(self):
        print "GENERATECITY"
        self.engine.generateNewMetaCity()


    def playCity(self):
        print "PLAYCITY"
        self.engine.setSpeed(2)
        self.engine.setPasses(1)
        self.engine.resume()
        self.playMode()


    def startMode(self):
        print "STARTMODE"
        self.engine.setGameMode('start')


    def playMode(self):
        print "PLAYMODE"
        self.engine.setGameMode('play')


    def aboutDialog(self):
        print "ABOUT DIALOG"

        def handleEmail(dialog, link, data):
            print "HANDLE EMAIL", dialog, link, data

        def handleUrl(dialog, link, data):
            print "HANDLE EMAIL", dialog, link, data

        engine = self.engine
        dialog = gtk.AboutDialog()
        dialog.set_name('Micropolis')
        dialog.set_version(engine.getMicropolisVersion())
        dialog.set_copyright('Copyright (C) 2009, 2011')
        dialog.set_comments('Developed by the EduVerse project; forked by Bryan Cain')
        dialog.set_license('GPLv3')
        #dialog.set_wrap_license(???)
        dialog.set_website('http://github.com/Plombo')
        dialog.set_website_label('Forked Micropolis repository')
        dialog.set_authors(('Will Wright', 'Fred Haslam', 'Don Hopkins', 'Bryan Cain', '[AUTHORS...]',))
        dialog.set_documenters(('[DOCUMENTERS...]',))
        dialog.set_artists(('[ARTISTS...]',))
        dialog.set_translator_credits('[TRANSLATORS...]')
        #dialog.set_logo(pixbuf)
        dialog.set_program_name('Micropolis')
        #dialog.set_email_hook(handleEmail, None)
        #dialog.set_url_hook(handleUrl, None)
        response = dialog.run()
        dialog.destroy()


    def saveCityDialog(self, button=None, data=None):
        # @todo "Save city..." dialog.
        print "SAVE CITY DIALOG"
        

    def saveCityAsDialog(self, button=None, data=None):
        print "SAVE CITY AS DIALOG"
        
        dialog = gtk.FileChooserDialog(
            title='Select the file to save.',
            action=gtk.FILE_CHOOSER_ACTION_SAVE,
            buttons=(
                gtk.STOCK_CANCEL,
                gtk.RESPONSE_CANCEL,
                gtk.STOCK_SAVE,
                gtk.RESPONSE_OK,
            ))
        
        xmlFilter = gtk.FileFilter()
        xmlFilter.set_name("Micropolis City (*.xml)")
        xmlFilter.add_pattern("*.xml")
        dialog.add_filter(xmlFilter)
        dialog.set_filter(xmlFilter)
        
        unixCtyFilter = gtk.FileFilter()
        unixCtyFilter.set_name("Micropolis/SimCity for UNIX/Macintosh City (*.cty)")
        unixCtyFilter.add_pattern("*.cty")
        dialog.add_filter(unixCtyFilter)
        
        winCtyFilter = gtk.FileFilter()
        winCtyFilter.set_name("SimCity for Windows/DOS/Amiga City (*.cty)")
        winCtyFilter.add_pattern("*.cty")
        dialog.add_filter(winCtyFilter)

        citiesFolder = 'cities'
        dialog.set_current_folder(citiesFolder)

        response = dialog.run()
        if response == gtk.RESPONSE_OK:
            fileName = dialog.get_filename()
            filter = dialog.get_filter()
            print "FILENAME", fileName
            result = False
            if filter == xmlFilter:
                try:
                    self.engine.saveMetaCity(fileName)
                    result = True
                except IOError, e:
                    print "FAILED TO SAVE META CITY", fileName
                    print str(e)
                    result = False
            elif filter == unixCtyFilter:
                try:
                    self.engine.savePlainCity(fileName, False)
                    result = True
                except IOError, e:
                    print 'FAILED TO SAVE CITY', fileName
                    print str(e)
                    result = False
            elif filter == winCtyFilter:
                try:
                    self.engine.savePlainCity(fileName, True)
                    result = True
                except IOError, e:
                    print 'FAILED TO SAVE CITY', fileName
                    print str(e)
                    result = False
            else:
                print "ERROR: file '%s' is not a CTY or XML file"
                result = False
            print "RESULT", result
        elif response == gtk.RESPONSE_CANCEL:
            print 'Closed, no files selected'
        dialog.destroy()


    def newCityDialog(self):
        # @todo "Are you sure you want to start a new game?" dialog.
        print "NEW CITY DIALOG"
        self.startGame()


    def quitDialog(self):
        # @todo "Are you sure you want to quit?" dialog.
        print "QUIT DIALOG"


    def centerOnTileHandler(
        self,
        tileX,
        tileY):

        #print "CENTERONTILEHANDLER", self, tileX, tileY

        editMapView = self.editMapView
        editMapView.setScale(1.0)
        editMapView.centerOnTile(
            tileX,
            tileY)


    def resizeEdges(
        self):

        winRect = self.get_allocation()
        winWidth = winRect.width
        winHeight = winRect.height

        print "WINDOW SIZE", winWidth, winHeight

        extra = 4
        padding = 14

        leftEdge = 120
        topEdge = 120

        self.vpaned1.set_position(topEdge + extra)
        self.vpaned2.set_position(1000)
        self.hpaned1.set_position(150)
        self.hpaned2.set_position(1000)

        editMapView = self.editMapView
        editMapView.panTo(-200, -200)
        editMapView.setScale(1.0)


    def handleRealize(
        self,
        *args):

        #print "handleRealize MicropolisPanedWindow", self, "ARGS", args

        self.firstResize = True


    def handleResize(
        self,
        widget,
        event,
        *args):

        #print "handleResize MicropolisPanedWindow", self, "WIDGET", widget, "EVENT", event, "ARGS", args

        if self.firstResize:
            self.firstResize = False
            self.resizeEdges()


    def createWindowNotebook(self, otherNotebook, notebook, page, x, y):

        print "createWindowNotebook", otherNotebook, notebook, page, x, y

        parent = page.get_parent()
        print "parent", parent, parent == self.notebook1, parent == self.notebook2, parent == self.notebook3

        for n in (self.notebook1, self.notebook2, self.notebook3):
            print n

        if parent == self.notebook1:
            return self.notebook2
        else:
            return self.notebook1


########################################################################
