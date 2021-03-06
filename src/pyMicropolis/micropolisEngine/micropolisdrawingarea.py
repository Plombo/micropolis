# micropolisdrawingarea.py
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
# Micropolis Drawing Area
# Don Hopkins


########################################################################
# Import stuff


import sys
import os
import time
import gtk
import gtkcompat
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
import micropolispiemenus
from pyMicropolis.tileEngine import tileengine, tiledrawingarea, tiletool
from pyMicropolis.glTileEngine import gltileengine, bytearray
import micropolistool


########################################################################
# Globals
# @todo This should go through some kind of a resource manager.


Sprites = [
    {
        'id': 1,
        'name': 'train',
        'frames': 5,
    },
    {
        'id': 2,
        'name': 'helicopter',
        'frames': 8,
    },
    {
        'id': 3,
        'name': 'airplane',
        'frames': 11,
    },
    {
        'id': 4,
        'name': 'boat',
        'frames': 8,
    },
    {
        'id': 5,
        'name': 'monster',
        'frames': 16,
    },
    {
        'id': 6,
        'name': 'tornado',
        'frames': 3,
    },
    {
        'id': 7,
        'name': 'explosion',
        'frames': 6,
    },
    {
        'id': 8,
        'name': 'bus',
        'frames': 4,
    },
]
for spriteData in Sprites:
    images = []
    spriteData['images'] = images
    for i in range(0, spriteData['frames']):
        fileName = 'images/micropolisEngine/obj%d-%d.png' % (
            spriteData['id'],
            i,
        )
        fileName = os.path.join(os.path.dirname(__file__), "../.." , fileName)
        fileName = os.path.abspath(fileName)
        image = cairo.ImageSurface.create_from_png(fileName)
        images.append(image)


########################################################################
# Utilities


def PRINT(*args):
    print args


########################################################################


class MicropolisDrawingArea(tiledrawingarea.TileDrawingArea):


    def __init__(
        self,
        engine=None,
        interests=('city', 'tick'),
        sprite=micropolisengine.SPRITE_NOTUSED,
        showData=True,
        showRobots=True,
        showSprites=True,
        showChalk=True,
        mapStyle='all',
        overlayAlpha=0.5,
        engaged=True,
        **args):

        args['tileCount'] = micropolisengine.TILE_COUNT
        args['sourceTileSize'] = micropolisengine.BITS_PER_TILE
        args['worldCols'] = micropolisengine.WORLD_W
        args['worldRows'] = micropolisengine.WORLD_H

        self.engine = engine
        self.showData = showData
        self.showRobots = showRobots
        self.showSprites = showSprites
        self.showChalk = showChalk
        self.mapStyle = mapStyle
        self.overlayAlpha = overlayAlpha
        self.engaged = engaged

        tiledrawingarea.TileDrawingArea.__init__(self, **args)

        self.sprite = sprite

        engine.expressInterest(
            self,
            interests)
        engine.addView(self)

        self.blinkFlag = True

        self.reset()
        
        if isinstance(self, EditableMicropolisDrawingArea):
            gltengine = gltileengine.GLTileEngine(self.engine, self.engine.getMapBuffer())
            print 'GLTileEngine object: ' + str(gltengine)
            self.tileBuffer = bytearray.getByteArray(512*512*4)
            self.lastWidth = -1
            self.lastHeight = -1
            #if gltengine.initGL(512, 512, self.tileBuffer.array): print 'GL initialized OK'
            #else: print 'Failed to initialize GL'
            self.gltengine = gltengine


    def update(self, name, *args):

        #print "MicropolisDrawingArea update", self, name, args

        self.queue_draw()


    def makeTileMap(self):
        tiledrawingarea.TileDrawingArea.makeTileMap(self)

        if False:
            # Remap some of the tiles so we can see them for debugging.
            self.tileMap[micropolisengine.REDGE] = micropolisengine.FIRE
            self.tileMap[micropolisengine.CHANNEL] = micropolisengine.RADTILE


    def reset(self):
        self.selectToolByName('Bulldozer')


    def configTileEngine(self, tengine):

        engine = self.engine
        buffer = engine.getMapBuffer()
        #print "Map buffer", buffer
        tengine.setBuffer(buffer)
        tengine.width = micropolisengine.WORLD_W
        tengine.height = micropolisengine.WORLD_H

        from micropolisengine import ZONEBIT, PWRBIT, ALLBITS, LIGHTNINGBOLT

        def tileFunction(col, row, tile):
            if (tile & ZONEBIT) and not (tile & PWRBIT) and random.random() < 0.5:
                tile = LIGHTNINGBOLT | (tile & ALLBITS)
            return tile

        self.tileFunction = tileFunction

        # Unsigned short tile values, in column major order.
        tengine.tileFormat = tileengine.TILE_FORMAT_SHORT_UNSIGNED
        tengine.colBytes = micropolisengine.BYTES_PER_TILE * micropolisengine.WORLD_H
        tengine.rowBytes = micropolisengine.BYTES_PER_TILE
        tengine.tileMask = micropolisengine.LOMASK


    def getCell(self, col, row):

        return self.engine.getTile(col, row)


    def beforeDraw(
        self):

        engine = self.engine
        self.blinkFlag = (engine.tickCount() % 60) < 30


    def drawOverlays(
        self,
        ctx):

        # We don't need this function anymore and it maxes CPU usage when overlays are enabled
        return
        if self.showData:
            self.drawData(ctx)

        if self.showRobots:
            self.drawRobots(ctx)

        if self.showSprites:
            self.drawSprites(ctx)

        if self.showChalk:
            self.drawChalk(ctx)

        if self.showCursor:
            tool = self.getActiveTool()
            if tool:
                tool.drawCursor(self, ctx)

    def setMapStyle(self, mapStyle):
        self.mapStyle = mapStyle


    def drawData(self, ctx):
        mapStyle = self.mapStyle
        engine = self.engine
        dataImage, dataAlpha, width, height = \
            engine.getDataImageAlphaSize(mapStyle)
        if not dataImage:
            return
        
        # screenshot
        try: f = open('screenshot.png', 'rb'); f.close()
        except IOError: dataImage.write_to_png('screenshot.png')

        width = 1.0 / width
        height = 1.0 / height

        ctx.save()

        tileSize = self.tileSize

        ctx.translate(self.panX, self.panY)

        ctx.scale(
            self.worldCols * tileSize,
            self.worldRows * tileSize)

        ctx.rectangle(0, 0, 1, 1)
        ctx.clip()

        imageWidth = dataImage.get_width()
        imageHeight = dataImage.get_height()

        ctx.scale(
            width / imageWidth,
            height / imageHeight)

        ctx.set_source_surface(
            dataImage,
            0,
            0)
        ctx.paint_with_alpha(dataAlpha)

        ctx.restore()


    def drawSprites(self, ctx):
        engine = self.engine
        sprite = engine.spriteList
        while True:
            if not sprite:
                break
            self.drawSprite(ctx, sprite)
            sprite = sprite.next


    def drawSprite(self, ctx, sprite):

        spriteType = sprite.type
        spriteFrame = sprite.frame

        if (spriteFrame == 0 or
            spriteType == micropolisengine.SPRITE_NOTUSED or
            spriteType >= micropolisengine.SPRITE_COUNT):
            return

        ctx.save()

        x = sprite.x
        y = sprite.y
        width = sprite.width
        height = sprite.height
        tileSize = self.tileSize

        ctx.translate(self.panX, self.panY)
        ctx.scale(tileSize / 16.0, tileSize / 16.0)

        ctx.translate(x + sprite.xOffset, y + sprite.yOffset)

        image = Sprites[spriteType - 1]['images'][spriteFrame - 1]

        ctx.set_source_surface(
            image,
            0,
            0)
        #ctx.rectangle(0, 0, 1, 1)
        ctx.paint()

        ctx.restore()


    def drawRobots(self, ctx):
        engine = self.engine
        robots = engine.robots

        if not robots:
            return

        ctx.save()

        tileSize = self.tileSize

        ctx.translate(self.panX, self.panY)
        ctx.scale(tileSize / 16.0, tileSize / 16.0)

        for robot in robots:
            robot.draw(ctx)

        ctx.restore()


    def drawChalk(self, ctx):
        pass # TODO: drawChalk


    def tickEngine(self):

        # Don't do anything! The engine ticks itself.
        return


    def makePie(self):

        pie = micropolispiemenus.MakePie(lambda toolName: self.selectToolByName(toolName))
        self.pie = pie


    def handleButtonPress(
        self,
        widget,
        event):

        self.handlePieButtonPress(
            widget,
            event)


    def handleKey(
        self,
        key):

        if key == 'm':
            self.engine.heatSteps = 1
            self.engine.heatRule = 0
            return True
        elif key == 'n':
            self.engine.heatSteps = 1
            self.engine.heatRule = 1
            return True
        elif key == 'o':
            self.engine.heatSteps = 0
            return True

        return False


    def engage(self):
        self.engaged = True


    def disengage(self):
        self.engaged = False


########################################################################


class EditableMicropolisDrawingAreaCairo(MicropolisDrawingArea):
    pass

# Much of this class is copy-pasta from tiledrawingarea.TileDrawingArea. Eventually
# most of the copied code should be removable from that class, though.
class EditableMicropolisDrawingAreaGL(gtk.DrawingArea):
    def __init__(
        self,
        engine=None,
        interests=('city', 'tick'),
        sprite=micropolisengine.SPRITE_NOTUSED,
        showData=True,
        showRobots=True,
        showSprites=True,
        showChalk=True,
        mapStyle='all',
        overlayAlpha=0.5,
        engaged=True,
        **args):

        self.tileCount = micropolisengine.TILE_COUNT
        self.sourceTileSize = micropolisengine.BITS_PER_TILE
        self.worldCols = micropolisengine.WORLD_W
        self.worldRows = micropolisengine.WORLD_H
        self.pannable = True
        self.tileSize = 16
        self.scale = 1.0
        self.panX = 0
        self.panY = 0

        self.engine = engine
        self.showData = showData
        self.showRobots = showRobots
        self.showSprites = showSprites
        self.showChalk = showChalk
        self.mapStyle = mapStyle
        self.overlayAlpha = overlayAlpha
        self.engaged = engaged
        self.trackingTool = None
        self.selectedTool = None
        self.pie = None
        self.cursorX = -1
        self.cursorY = -1
        self.cursorRow = 0
        self.cursorCol = 0
        self.down = False

        gtk.DrawingArea.__init__(self, **args)
        self.set_double_buffered(False)
        self.set_can_focus(True)

        self.sprite = sprite

        engine.expressInterest(
            self,
            interests)
        engine.addView(self)

        self.blinkFlag = True

        self.selectToolByName('Bulldozer')
        self.show()
        
        winRect = self.get_allocation()
        winWidth = winRect.width
        winHeight = winRect.height

        gltengine = gltileengine.GLTileEngine(self.engine, self.engine.getMapBuffer())
        self.lastWidth = -1
        self.lastHeight = -1
        self.gltengine = gltengine
        
        # XXX temporary Cairo stuff
        self.overlayBuffer = None
        self.overlaySurface = None

        self.connect(gtkcompat.expose_event, self.handleExpose)
        self.connect('configure-event', self.handleConfigure)
        self.connect('button_press_event', self.handleButtonPress)
        self.connect('button_release_event', self.handleButtonRelease)
        self.connect('motion_notify_event', self.handleMotionNotify)
        self.connect('enter_notify_event', self.handleEnterNotify)
        self.set_events(gtk.gdk.ENTER_NOTIFY_MASK |
                        gtk.gdk.POINTER_MOTION_MASK |
                        gtk.gdk.BUTTON_PRESS_MASK |
                        gtk.gdk.BUTTON_RELEASE_MASK)

    def handleConfigure(self, widget, event, *args):
        # set up render destination
        winRect = self.get_allocation()
        winWidth = winRect.width
        winHeight = winRect.height
        #self.tileBuffer = bytearray.getByteArray(winHeight * winWidth * 4)
        self.lastWidth = winWidth
        self.lastHeight = winHeight
        if gtkcompat.gtk_major_version == 3:
            self.gltengine.setWindow(self.get_window().get_xid())
        else:
            self.gltengine.setWindow(self.get_window().xid)
        if not self.gltengine.setSize(winWidth, winHeight, None):
            print 'Error in EGL/OpenGL initialization'
            sys.exit(1)
        self.actuallyDraw()

    def handleExpose(self, widget, event, *args):
        self.actuallyDraw()
        return False

    def draw(self, widget=None, event=None):
        pass
    
    def actuallyDraw(self):
        panX = self.panX
        panY = self.panY
        
        # start drawing the frame
        self.gltengine.startFrame(int(-panX), int(-panY), self.scale)

        # render tiles
        self.gltengine.renderTiles()
        
        # draw cursor
        tool = self.getActiveTool()
        if tool and self.cursorX >= 0 and self.cursorY >= 0:
            # tool.drawCursor uses Cairo, so do our own thing here
            tileX = int(self.cursorX / self.tileSize)
            tileY = int(self.cursorY / self.tileSize)
            
            toolResult = self.engine.predictToolSuccess(tool.toolIndex, tileX, tileY)
            
            x = int(self.cursorX) - self.tileSize * tool.cursorHotCol
            y = int(self.cursorY) - self.tileSize * tool.cursorHotRow
            canBuild = (toolResult == micropolisengine.TOOLRESULT_OK)
            self.gltengine.drawCursor(x, y, tool.cursorCols, tool.cursorRows, canBuild)
        
        # draw sprites
        self.drawSprites()
        
        # draw map overlay if there is one
        self.drawOverlay()
        
        # finish drawing the frame
        self.gltengine.finishFrame()

    def drawSprites(self):
        sprite = self.engine.spriteList
        while sprite:
            self.gltengine.drawSprite(sprite)
            sprite = sprite.next

    def drawOverlay(self):
        overlayTypes = {
            'powergrid': (self.engine.getPowerGridMapBuffer(), micropolisengine.MAP_TYPE_POWER),
            'trafficdensity': (self.engine.getTrafficDensityMapBuffer(), micropolisengine.MAP_TYPE_TRAFFIC_DENSITY),
            'pollutiondensity': (self.engine.getPollutionDensityMapBuffer(), micropolisengine.MAP_TYPE_POLLUTION),
            'populationdensity': (self.engine.getPopulationDensityMapBuffer(), micropolisengine.MAP_TYPE_POPULATION_DENSITY),
            'crimerate': (self.engine.getCrimeRateMapBuffer(), micropolisengine.MAP_TYPE_CRIME),
            'landvalue': (self.engine.getLandValueMapBuffer(), micropolisengine.MAP_TYPE_LAND_VALUE),
            'firecoverage': (self.engine.getFireCoverageMapBuffer(), micropolisengine.MAP_TYPE_FIRE_RADIUS),
            'policecoverage': (self.engine.getPoliceCoverageMapBuffer(), micropolisengine.MAP_TYPE_POLICE_RADIUS),
            'rateofgrowth': (self.engine.getRateOfGrowthMapBuffer(), micropolisengine.MAP_TYPE_RATE_OF_GROWTH),
        }
        if self.mapStyle in overlayTypes.keys():
            self.gltengine.drawOverlay(*overlayTypes[self.mapStyle])
    
    def update(self, name, *args):
        winRect = self.get_allocation()
        winWidth = winRect.width
        winHeight = winRect.height
        if winWidth <= 1 or winHeight <= 1: return

        self.queue_draw()
    
    def engage(self):
        self.engaged = True

    def disengage(self):
        self.engaged = False
    
    def updateView(self):
        self.queue_draw()
    
    def panTo(self, x, y):
        self.panX = x
        self.panY = y

    def panBy(self, dx, dy):
        self.panTo(
            self.panX + dx,
            self.panY + dy)
    
    def setScale(self, scale):
        if self.scale == scale:
            return

        if not self.window:
            return

        self.scale = scale
    
    def centerOnTile(self, tileX, tileY):
        tileSize = self.tileSize

        px = -tileSize * tileX
        py = -tileSize * tileY

        rect = self.get_allocation()
        winWidth = rect.width
        winHeight = rect.height

        px += winWidth / 2
        py += winHeight / 2

        #print "centerOnTile", "tile", tileX, tileY, "tileSize", self.tileSize, "scale", self.scale, "p", px, py

        self.panTo(px, py)
    
    def makePie(self):
        pie = micropolispiemenus.MakePie(lambda toolName: self.selectToolByName(toolName))
        self.pie = pie
    
    def getPie(self):
        pie = self.pie
        if pie:
            return pie

        self.makePie()

        return self.pie
    
    def getActiveTool(self):
        return self.trackingTool or self.selectedTool
    
    def selectToolByName(self, toolName):
        print "selectToolByName", toolName

        tool = tiletool.TileTool.getToolByName(toolName)

        lastTool = self.selectedTool
        if lastTool:
            tool.deselect(self)

        if tool:
            tool.select(self)

        self.selectedTool = tool
    
    def handleButtonPress(self, widget, event):
        if event.button == 1: # left button

            self.down = True
            self.downX = event.x
            self.downY = event.y

            tool = self.getActiveTool()
            #print "Active tool:", tool
            if tool:
                tool.handleMouseDown(self, event)

        elif event.button == 3: # right button

            pie = self.getPie()

            if pie:

                win_x, win_y, state = gtkcompat.event_get_pointer(event)

                #print "POP UP PIE", pie, win_x, win_y, state
                #print "WIN", win_x, win_y

                x, y = event.get_root_coords()

                #print "ROOT", x, y

                pie.popUp(x, y, False)

    def handleButtonRelease(self, widget, event):
        #print "handleButtonRelease TileDrawingArea", self
        self.handleMouseDrag(event)
        self.down = False

        tool = self.getActiveTool()
        if tool:
            tool.handleMouseUp(self, event)

    def handleMouseDrag(self, event):
        tool = self.getActiveTool()
        if tool:
            tool.handleMouseDrag(self, event)

    def handleMouseHover(self, event):
        tool = self.getActiveTool()
        if tool:
            tool.handleMouseHover(self, event)

    def getEventXY(self, event):
        if (hasattr(event, 'is_hint') and
            event.is_hint):
            x, y, state = gtkcompat.event_get_pointer(event)
        else:
            x = event.x
            y = event.y

        tileSize = self.tileSize

        return (
            (x/self.scale - self.panX) / tileSize,
            (y/self.scale - self.panY) / tileSize,
        )


    def getEventColRow(self, event):
        if (hasattr(event, 'is_hint') and
            event.is_hint):
            x, y, state = gtkcompat.event_get_pointer(event)
        else:
            x = event.x
            y = event.y

        tileSize = self.tileSize
        col = int((x/self.scale - self.panX) / tileSize)
        row = int((y/self.scale - self.panY) / tileSize)

        return (col, row)

    def handleMotionNotify(self, widget, event):
        if not event:
            x, y, state = self.window.get_pointer()
        elif hasattr(event, 'is_hint') and event.is_hint:
            x, y, state = gtkcompat.event_get_pointer(event)
        else:
            x = event.x
            y = event.y
            state = event.state

        self.mouseX = x
        self.mouseY = y

        tool = self.getActiveTool()
        if tool:
            # TODO finish
            #tool.setCursorPos(self, x - self.panX, y - self.panY)
            self.cursorX = x/self.scale - self.panX
            self.cursorY = y/self.scale - self.panY

        if self.down:
            self.handleMouseDrag(event)
        else:
            self.handleMouseHover(event)

    def handleEnterNotify(self, widget, event):
        self.grab_focus()

    # TODO finish me!!!
    '''def handleKeyPress(self, widget, event):
        key = event.keyval

        if ((not self.trackingTool) and
            (key in self.panKeys)):
            panTool = tiletool.TileTool.getToolByName('Pan')
            #print "panTool", panTool
            if panTool:
                self.trackingToolTrigger = key
                self.trackingTool = panTool
                panTool.startPanning(self)
                #print "Activated panTool", panTool
                return

        if self.handleKey(key):
            return

        tool = self.getActiveTool()
        if tool:
            if tool.handleKeyDown(self, event):
                return

        # TODO: This might be handled by the pan tool.
        if key == ord('=') or key == ord('+'):
            self.changeScale(self.scale * 1.1)
        elif key == ord('-'):
            self.changeScale(self.scale / 1.1)
        elif key == ord('r'):
            self.changeScale(1.0)'''

    def setMapStyle(self, mapStyle):
        self.mapStyle = mapStyle


# comment out one of the two lines below to select which class to actually use
# note that the defined macros in gltileengine.cpp need to change depending on which we are using
#EditableMicropolisDrawingArea = EditableMicropolisDrawingAreaCairo
EditableMicropolisDrawingArea = EditableMicropolisDrawingAreaGL

########################################################################


class NoticeMicropolisDrawingArea(MicropolisDrawingArea):


    def __init__(
        self,
        follow=None,
        centerOnTileHandler=None,
        **args):

        args['keyable'] = False
        args['clickable'] = False
        args['zoomable'] = False
        args['pannable'] = False
        args['menuable'] = False
        args['showCursor'] = False
        args['scale'] = 2

        MicropolisDrawingArea.__init__(self, **args)

        self.follow = follow
        self.centerOnTileHandler = centerOnTileHandler


    def handleMouseHover(
        self,
        event):

        pass


    def handleButtonPress(
        self,
        widget,
        event):

        centerOnTileHandler = self.centerOnTileHandler
        if centerOnTileHandler:
            centerX, centerY = self.getCenterTile()
            centerOnTileHandler(centerX, centerY)


    def handleMouseDrag(
        self,
        event):

        pass


    def handleButtonRelease(
        self,
        widget,
        event):

        pass


    def handleMouseScroll(
        self,
        widget,
        event):

        pass


    def beforeDraw(
        self):

        MicropolisDrawingArea.beforeDraw(self)

        engine = self.engine
        self.blinkFlag = (engine.tickCount() % 30) < 15

        sprite = self.sprite
        if sprite != micropolisengine.SPRITE_NOTUSED:
            s = engine.getSprite(sprite)
            if s:
                fudge = 8
                x = ((s.x + s.xHot + fudge) / 16.0)
                y = ((s.y + s.yHot + fudge) / 16.0)
                self.centerOnTile(x, y)


########################################################################


class NavigationMicropolisDrawingArea(MicropolisDrawingArea):


    def __init__(
        self,
        **args):

        args['keyable'] = False
        args['clickable'] = False
        args['zoomable'] = False
        args['pannable'] = False
        args['menuable'] = False
        args['showCursor'] = False
        args['showRobots'] = False
        args['showSprites'] = False
        args['scale'] = 1.0 / micropolisengine.EDITOR_TILE_SIZE
        args['overlayAlpha'] = 0.8

        MicropolisDrawingArea.__init__(self, **args)

        self.currentView = None
        self.panning = False
        self.panningView = None
        self.panningStartCursorX = 0
        self.panningStartCursorY = 0
        self.panningStartPanX = 0
        self.panningStartPanY = 0
        self.mapBuffer = bytearray.getByteArray(120 * 100 * 4)


    def drawOverlays(self, ctx):

        MicropolisDrawingArea.drawOverlays(self, ctx)

        self.drawOtherViews(ctx)


    def getViewBox(self, view):

        viewRect = view.get_allocation()
        viewWidth = viewRect.width
        viewHeight = viewRect.height

        tileSize = self.tileSize
        # @todo Validate the view.tileSize before using it. View might not be drawn yet, and we get the wrong size.
        viewTileSize = view.tileSize
        viewScale = float(tileSize) / float(viewTileSize)

        x = self.panX - (view.panX * viewScale)
        y = self.panY - (view.panY * viewScale)
        width = viewWidth * viewScale
        height = viewHeight * viewScale

        #print "GETVIEWBOX", "view", view, "pan", view.panX, view.panY, "tileSize", view.tileSize, "pos", x, y, "size", width, height

        return x, y, width, height


    def drawOtherViews(self, ctx):

        if self.panning:
            currentView = self.panningView
        else:
            currentView = self.currentView

        views = self.engine.views
        #print "drawOtherViews", views

        for view in views:

            if not view.pannable:
                continue

            x, y, width, height = self.getViewBox(view)

            if view == currentView:

                pad = 4

                ctx.rectangle(
                    x - pad,
                    y - pad,
                    width + (pad * 2),
                    height + (pad * 2))


                ctx.set_line_width(
                    pad * 2)

                ctx.set_source_rgb(
                    0.0,
                    0.0,
                    1.0)

                ctx.stroke_preserve()

                ctx.set_line_width(
                    pad)

                ctx.set_source_rgb(
                    1.0,
                    1.0,
                    0.0)

                ctx.stroke()

            else:

                pad = 2

                ctx.rectangle(
                    x - pad,
                    y - pad,
                    width + (pad * 2),
                    height + (pad * 2))

                ctx.set_line_width(
                    pad * 2)

                ctx.set_source_rgb(
                    1.0,
                    1.0,
                    1.0)

                ctx.stroke_preserve()

                ctx.set_line_width(
                    pad)

                ctx.set_source_rgb(
                    0.0,
                    0.0,
                    0.0)

                ctx.stroke()


    def getCursorPosition(
        self,
        event):

        if not event:
            x, y, state = self.window.get_pointer()
        elif (hasattr(event, 'is_hint') and
              event.is_hint):
            x, y, state = gtkcompat.event_get_pointer(event)
        else:
            x = event.x
            y = event.y
            state = event.state

        return x, y


    def handleMouseHover(
        self,
        event):

        x, y = self.getCursorPosition(event)

        views = self.engine.views
        found = []

        for view in views:

            if not view.pannable:
                continue

            viewX, viewY, viewWidth, viewHeight = self.getViewBox(view)

            if ((x >= viewX) and
                (x < (viewX + viewWidth)) and
                (y >= viewY) and
                (y < (viewY + viewHeight))):
                found.append(view)

        if found:
            self.currentView = found[-1]
        else:
            self.currentView = None


    def handleButtonPress(
        self,
        widget,
        event):

        if not self.currentView:
            self.panning = False
            self.down = False
            return

        x, y = self.getCursorPosition(event)
        view = self.currentView

        self.down = True
        self.panning = True
        self.panningView = view
        self.panningStartCursorX = x
        self.panningStartCursorY = y
        self.panningStartPanX = view.panX
        self.panningStartPanY = view.panY


    def handleMouseDrag(
        self,
        event):

        if not self.panning:
            return

        x, y = self.getCursorPosition(event)
        view = self.panningView

        dx = self.panningStartCursorX - x
        dy = self.panningStartCursorY - y
        scale = view.tileSize / self.tileSize
        dx *= scale
        dy *= scale

        view.panTo(self.panningStartPanX + dx, self.panningStartPanY + dy)


    def handleButtonRelease(
        self,
        widget,
        event):

        if not self.panning:
            return

        self.handleMouseDrag(
            event)

        self.down = False
        self.panning = False
        self.panningView = None


    def handleMouseScroll(
        self,
        widget,
        event):

        view = self.currentView
        if ((not view) and
            (not view.zoomable)):
            pass

        direction = event.direction

        if direction == gtk.gdk.SCROLL_UP:
            view.changeScale(view.scale * view.scrollWheelZoomScale)
        elif direction == gtk.gdk.SCROLL_DOWN:
            view.changeScale(view.scale / view.scrollWheelZoomScale)


########################################################################


class PreviewMicropolisDrawingArea(MicropolisDrawingArea):


    def __init__(
        self,
        **args):

        args['keyable'] = False
        args['clickable'] = True
        args['zoomable'] = False
        args['pannable'] = False
        args['menuable'] = False
        args['showCursor'] = False
        args['showRobots'] = False
        args['showSprites'] = False
        args['scale'] = 3.0 / micropolisengine.EDITOR_TILE_SIZE
        args['overlayAlpha'] = 0.8

        MicropolisDrawingArea.__init__(self, **args)


    def handleMouseHover(
        self,
        event):

        pass


    def handleButtonPress(
        self,
        widget,
        event):

        pass


    def handleMouseDrag(
        self,
        event):

        pass


    def handleButtonRelease(
        self,
        widget,
        event):

        pass


    def handleMouseScroll(
        self,
        widget,
        event):

        pass


########################################################################
