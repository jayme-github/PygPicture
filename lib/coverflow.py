#!/usr/bin/env python
# -*- coding: utf8 -*- 

import os
import datetime
import glob
import subprocess
import sys
import platform
import logging

import OpenGL.GL as gl
import pygame, pygame.image
import pygame.locals as pl

from tgdb import Tgdb

logger = logging.getLogger('PygPicture.'+__name__)
logger.addHandler(logging.NullHandler())

def resource_path(relative):
    if getattr(sys, 'frozen', None):
        basedir = sys._MEIPASS
    else:
        basedir = os.path.dirname(__file__)
    logger.info( 'resource_path: ' + basedir )
    return os.path.join( basedir, relative )


class Game(object):
    ''' Simple helper to store game info '''
    def __init__(self, lnk):
        self.logger = logging.getLogger( logger.name + '.' + type(self).__name__ )
        if not os.path.isfile( lnk ):
            raise ValueError('lnk has to be a valid link file')

        self.tgdb = Tgdb()
        self.lnk = lnk
        self.imgpath = os.path.splitext(self.lnk)[0] + '.jpg'
        self.name = os.path.splitext( os.path.basename(self.lnk) )[0]
        self.logger.debug( 'Init game "%s"' % self.name )

    def __str__(self):
        return '<Game "%s", "%s", "%s">' %( self.name, os.path.basename(self.lnk),
                                            os.path.basename(self.getImagePath()) )

    def getImagePath(self):
        ''' Download cover image for this game '''
        if os.path.isfile( self.imgpath ):
            self.logger.debug( 'getImagePath: Image found, returning path: ' + self.imgpath )
            return self.imgpath
        else:
            self.logger.debug( 'getImagePath: No image found, fetching from TGDB' )
            # Fetch boxart from tgdb
            tgdbgame = self.tgdb[self.name]
            if tgdbgame:
                self.logger.debug( 'getImagePath: game: "%s"' % (str(tgdbgame)) )
                self.logger.debug( 'getImagePath: saving to: ' + self.imgpath )
                if tgdbgame.saveBoxart( self.imgpath ) != None:
                    return self.imgpath
        # Fallback
        return resource_path('default.jpg')

    def getSurface(self):
        ''' Return pygame surface for image '''
        return pygame.image.load( self.getImagePath() )

class CoverFlow(object):
    '''
    Based on the coverflow example from Jan Erik Solem
    <http://www.janeriksolem.net/2009/08/cover-flow-with-pygame-and-opengl.html>
    '''
    def __init__(self, lnkpath = None):
        self.logger = logging.getLogger( logger.name + '.' + type(self).__name__ )
        self.zoom = -7.0 #distance to camera (zoom)
        self.textures = []
        self.rd = [1.9,  0.0, -0.5] #right delta
        self.ld = [-1.9,  0.0, -0.5] #left delta
        self.t = 0 #for transitions between images
        self.s = 0 #for transitions between images
        self.ndx = 0 #start by showing the first image
        self._lastgame = None
        
        self.lnkpath = lnkpath
        
        self.lastgamepath = os.path.join( self.lnkpath, '.lastgame' )
        self.gamelist = self.get_gamelist()
        self.logger.debug( 'Init CoverFlow with %d games' % self.gamecount() )


        #opengl stuff
        gl.glEnable(gl.GL_TEXTURE_2D)
        self.load_textures()

        gl.glShadeModel(gl.GL_SMOOTH)
        gl.glClearColor(0.0, 0.0, 0.0, 0.0)
        gl.glClearDepth(1.0)
        gl.glEnable(gl.GL_DEPTH_TEST)
        gl.glDepthFunc(gl.GL_LEQUAL)
        gl.glHint( gl.GL_PERSPECTIVE_CORRECTION_HINT, gl.GL_NICEST )
        gl.glEnable( gl.GL_LIGHT1 )

    
    def gamecount(self):
        return len( self.gamelist )

    def get_gamelist(self):
        gamelist = []
        for lnk in glob.glob( os.path.join(self.lnkpath, '*.lnk') ):
            game = Game( lnk )
            if not game in gamelist:
                # Push last started game to index 0
                if lnk == self.lastgame():
                    gamelist.insert( 0, game )
                else:
                    gamelist.append( game )
        return gamelist

    def load_textures(self):
        if self.gamecount() <= 1:
            # Make sure that this is always a list
            self.textures = gl.glGenTextures( 2 )
        else:
            self.textures = gl.glGenTextures( self.gamecount() )
        c = 0
        for game in self.gamelist:
            textureSurface = game.getSurface()
            textureData = pygame.image.tostring(textureSurface, "RGBX", 1)
    
            gl.glBindTexture( gl.GL_TEXTURE_2D, self.textures[c] )
            gl.glTexImage2D( gl.GL_TEXTURE_2D, 0, gl.GL_RGBA, textureSurface.get_width(), textureSurface.get_height(), 0,
                      		gl.GL_RGBA, gl.GL_UNSIGNED_BYTE, textureData )
            gl.glTexParameteri( gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_NEAREST )
            gl.glTexParameteri( gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_NEAREST )
            c += 1
    
    def reset(self):
        self.t = 0
        self.s = 0
        self.draw()
    
    def draw(self):
    
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        gl.glLoadIdentity()
        gl.glTranslatef(0.0, 0.0, self.zoom)
   
        # center quad
        pos = (self.ndx) % self.gamecount()
        gl.glBindTexture(gl.GL_TEXTURE_2D, self.textures[pos])
        gl.glBegin(gl.GL_QUADS)
        gl.glNormal3f(0.0, 0.0, 1.0)
        gl.glTexCoord2f(0.0, 0.0); gl.glVertex3f(-1.25+self.t*self.ld[0]+self.s*self.rd[0], -1.6+self.t*self.ld[1]+self.s*self.rd[1],  1.0+self.t*self.ld[2]+self.s*self.rd[2])    # Bottom Left Of The Texture and Quad
        gl.glTexCoord2f(1.0, 0.0); gl.glVertex3f( 1.25+self.t*self.ld[0]+self.s*self.rd[0], -1.6+self.t*self.ld[1]+self.s*self.rd[1],  1.0+self.t*self.ld[2]+self.s*self.rd[2])    # Bottom Right Of The Texture and Quad
        gl.glTexCoord2f(1.0, 1.0); gl.glVertex3f( 1.25+self.t*self.ld[0]+self.s*self.rd[0],  1.6+self.t*self.ld[1]+self.s*self.rd[1],  1.0+self.t*self.ld[2]+self.s*self.rd[2])    # Top Right Of The Texture and Quad
        gl.glTexCoord2f(0.0, 1.0); gl.glVertex3f(-1.25+self.t*self.ld[0]+self.s*self.rd[0],  1.6+self.t*self.ld[1]+self.s*self.rd[1],  1.0+self.t*self.ld[2]+self.s*self.rd[2])    # Top Left Of The Texture and Quad
        gl.glEnd()
    
        # right quad
        pos = (self.ndx+1) % self.gamecount()
        gl.glBindTexture(gl.GL_TEXTURE_2D, self.textures[pos])
        gl.glBegin(gl.GL_QUADS)
        gl.glNormal3f(0.0, 0.0, 1.0)
        gl.glTexCoord2f(0.0, 0.0); gl.glVertex3f(-1.25+(1-self.t+self.s)*self.rd[0], -1.6+(1-self.t+self.s)*self.rd[1],  1.0+(1-self.t+self.s)*self.rd[2])    # Bottom Left Of The Texture and Quad
        gl.glTexCoord2f(1.0, 0.0); gl.glVertex3f( 1.25+(1-self.t+self.s)*self.rd[0], -1.6+(1-self.t+self.s)*self.rd[1],  1.0+(1-self.t+self.s)*self.rd[2])    # Bottom Right Of The Texture and Quad
        gl.glTexCoord2f(1.0, 1.0); gl.glVertex3f( 1.25+(1-self.t+self.s)*self.rd[0],  1.6+(1-self.t+self.s)*self.rd[1],  1.0+(1-self.t+self.s)*self.rd[2])    # Top Right Of The Texture and Quad
        gl.glTexCoord2f(0.0, 1.0); gl.glVertex3f(-1.25+(1-self.t+self.s)*self.rd[0],  1.6+(1-self.t+self.s)*self.rd[1],  1.0+(1-self.t+self.s)*self.rd[2])    # Top Left Of The Texture and Quad
        gl.glEnd()
    
        # left quad
        pos = (self.ndx-1) % self.gamecount()
        gl.glBindTexture(gl.GL_TEXTURE_2D, self.textures[pos])
        gl.glBegin(gl.GL_QUADS)
        gl.glNormal3f(0.0, 0.0, 1.0)
        gl.glTexCoord2f(0.0, 0.0); gl.glVertex3f(-1.25+(1+self.t-self.s)*self.ld[0], -1.6+(1+self.t-self.s)*self.ld[1],  1.0+(1+self.t-self.s)*self.ld[2])    # Bottom Left Of The Texture and Quad
        gl.glTexCoord2f(1.0, 0.0); gl.glVertex3f( 1.25+(1+self.t-self.s)*self.ld[0], -1.6+(1+self.t-self.s)*self.ld[1],  1.0+(1+self.t-self.s)*self.ld[2])    # Bottom Right Of The Texture and Quad
        gl.glTexCoord2f(1.0, 1.0); gl.glVertex3f( 1.25+(1+self.t-self.s)*self.ld[0],  1.6+(1+self.t-self.s)*self.ld[1],  1.0+(1+self.t-self.s)*self.ld[2])    # Top Right Of The Texture and Quad
        gl.glTexCoord2f(0.0, 1.0); gl.glVertex3f(-1.25+(1+self.t-self.s)*self.ld[0],  1.6+(1+self.t-self.s)*self.ld[1],  1.0+(1+self.t-self.s)*self.ld[2])    # Top Left Of The Texture and Quad
        gl.glEnd()


    def _left(self):
        for i in range(10):
            self.s += 0.1
            pygame.time.delay(50)
            self.draw()
            pygame.display.flip()
        self.ndx -= 1
        self.reset()
    def _right(self):
        for i in range(10):
            self.t += 0.1
            pygame.time.delay(50)
            self.draw()
            pygame.display.flip()
        self.ndx += 1
        self.reset()

    def handle_key(self, event):
        if event.key in (pl.K_ESCAPE, pl.K_q):
            return 1
        elif event.key == pl.K_s:
            return 2
        elif event.key == pl.K_z:
            self.zoom -= 0.10
        elif event.key == pl.K_x:
            self.zoom += 0.10
        elif event.key == pl.K_LEFT:
            self._left()
        elif event.key == pl.K_RIGHT:
            self._right()
        elif event.key == pl.K_RETURN:
            self.launch_game()
        return 0

    def handle_joystick(self, joysticks):
        up = down = False
        for joystick in joysticks:
            # horizontal
            if joystick.get_axis(0) > 0.5:
                self._right()
            if joystick.get_axis(0) < -0.5:
                self._left()

            # vertical
            if joystick.get_axis(1) > 0.5:
                down = True
            elif joystick.get_axis(1) < -0.5:
                up = True

            # buttons              
            if joystick.get_button(0):
                if up:
                    #break out, quit app
                    return 1
                elif down:
                    #break out, shutdown
                    return 2
                else:
                    self.launch_game()
        return 0

    def selected_game(self):
        ''' Return the current selected game '''
        return self.gamelist[ self.ndx % self.gamecount() ]

    def _save_lastgame(self):
        ''' Save the selected game to .lastgame file '''
        fp = open( self.lastgamepath, 'w' )
        fp.write( self.selected_game().lnk + '\n' )
        fp.close()

    def lastgame(self):
        ''' Read the last launched game from .lastgame file '''
        if not os.path.isfile( self.lastgamepath ):
            # Create file if it does not exist
            open( self.lastgamepath, 'w+' ).close()
            return None

        if not self._lastgame:
            fp = open( self.lastgamepath, 'r' )
            self._lastgame = fp.readline().strip()
            fp.close()
        return self._lastgame

    def launch_game(self):
        ''' Launch the selected game '''
        print 'Launching game "%s": "%s"' % ( datetime.datetime.today(), self.selected_game() )
        self._save_lastgame()
        if platform.system() == 'Windows':
            subprocess.call( ['start', '', '/B', '/WAIT', self.selected_game().lnk], shell=True )

