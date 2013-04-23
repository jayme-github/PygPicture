#!/usr/bin/env python
# -*- coding: utf8 -*- 

import os
import sys
import platform
import subprocess

import logging
LEVEL = logging.DEBUG
FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logging.basicConfig( filename='pygpicture.log', filemode='w',
                     format=FORMAT,
                     level=LEVEL )
logger = logging.getLogger('PygPicture')

import OpenGL.GL as gl
from OpenGL.GLU import gluPerspective
import pygame, pygame.image
import pygame.locals as pl

from lib.coverflow import CoverFlow

# Default search path for game lnk's
SEARCHPATH = [ os.path.join(os.getcwd(), 'Games') ]

def resize((width, height)):
    if height==0:
        height=1
    gl.glViewport(0, 0, width, height)
    gl.glMatrixMode(gl.GL_PROJECTION)
    gl.glLoadIdentity()
    gluPerspective(45, 1.0*width/height, 0.1, 100.0)
    gl.glMatrixMode(gl.GL_MODELVIEW)
    gl.glLoadIdentity()

def shutdown():
    logger.info( 'Shutting down system' )
    print 'Shutting down system'
    if platform.system() == 'Windows':
        subprocess.call( ['shutdown.exe', '/f', '/s', '/t', '30'] )


def main():
    pygame.init()
    
    logger.info( 'Running on ' + platform.system() )
    if platform.system() == 'Windows':
        import win32com.client
        SEARCHPATH.insert(0, os.path.join( win32com.client.Dispatch('WScript.Shell').SpecialFolders('Desktop'), 'Games' ) )

        # Fullscreen video
        video_flags = pl.OPENGL|pl.DOUBLEBUF|pl.FULLSCREEN
        max_fullscreen_mode = pygame.display.list_modes( 0, video_flags )[0]

    elif platform.system() == 'Linux':
        #video_flags = pl.OPENGL|pl.DOUBLEBUF|pl.FULLSCREEN
        #max_fullscreen_mode = pygame.display.list_modes( 0, video_flags )[0]
        # Window mode
        video_flags = pl.OPENGL|pl.DOUBLEBUF
        max_fullscreen_mode = (800,600)

    lnkpath = None
    for path in SEARCHPATH:
        if os.path.isdir( path ):
            lnkpath = path
            break
    if not lnkpath:
        print 'No path for game links found'
        sys.exit(1)
    logger.info( 'Using "%s" as lnk path' % lnkpath )

    surface = pygame.display.set_mode(max_fullscreen_mode, video_flags)
    pygame.display.set_caption('PygPicture')
    resize( max_fullscreen_mode )

    # init all joisticks
    joysticks = list()
    for i in xrange(pygame.joystick.get_count()):
        joystick = pygame.joystick.Joystick(i)
        joystick.init()
        joysticks.append(joystick)
    logger.info( 'Found and initialized %d joysticks' % len(joysticks) )


    cf = CoverFlow(lnkpath)
    clock = pygame.time.Clock()
    while True:
        pygame.event.pump()
        event = pygame.event.poll()

        if event.type == pl.QUIT:
            break
        if event.type == pl.KEYDOWN:
            kret = cf.handle_key(event)
            if kret == 1:
                break
            elif kret == 2:
                shutdown()
                break
        
        # Check for new / changed joysticks
        # FIXME: UNTESTED This may take some time, maybe we should just do this if joystick count has changed?
        for i in xrange(pygame.joystick.get_count()):
            joystick = pygame.joystick.Joystick(i)
            if not joystick.get_init():
                logger.info( 'New joystick (ID: %d): "%s"' % (i, joystick.get_name()) )
                joystick.init()
                joysticks.append( joystick )

        jret = cf.handle_joystick( joysticks )
        if jret == 1:
            break
        elif jret == 2:
            shutdown()
            break
        
        cf.draw()
        pygame.display.flip()
        clock.tick(35)

if __name__ == '__main__':
    main()
