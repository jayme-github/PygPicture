#!/usr/bin/python
# -*- coding: utf8 -*-

import tempfile
import urllib2
import datetime
import shutil
import logging
from urllib import urlencode
from pprint import pprint

try:
    import xml.etree.cElementTree as ElementTree
except ImportError:
    import xml.etree.ElementTree as ElementTree

logger = logging.getLogger('PygPicture.'+__name__)
logger.addHandler(logging.NullHandler())

# XML Convert mapping
CONVERTERS = {
    'id': int,
    'ReleaseDate': lambda text: datetime.datetime.strptime(text, '%m/%d/%Y'),
    'PlatformId': int,
}

class TgdbBase(object):
    def __init__(self):
        self.logger = logging.getLogger( logger.name + '.' + type(self).__name__ )
        self.urlopener = urllib2.build_opener() # default opener with no caching
    
    def _loadUrl(self, url):
        return self.urlopener.open(url)

class Game(TgdbBase):
    def __init__(self, data):
        super(Game, self).__init__()
        self._data = data

    def __str__(self):
        return str(self._data)

    def getBoxartUrl(self):
        # filter front boxart, highest first
        if isinstance( self._data['Game']['Images'], dict ) and 'boxart' in  self._data['Game']['Images']:
            boxart = self._data['Game']['Images']['boxart']
            self.logger.debug( 'getBoxartUrl: ' + str(boxart) )
            if isinstance(boxart, list):
                boxart = sorted( filter( lambda x: x['side'] == 'front' and x.has_key('_text'), boxart ) )[0]
            if boxart:
                return self._data['baseImgUrl'] + boxart['_text']

        self.logger.info( 'getBoxartUrl: No boxart image found' )
        # No boxart image ... 
        return None

    def saveBoxart(self, path):
        url = self.getBoxartUrl()
        if url:
            self.logger.debug( 'saveBoxart(%s) url: %s' % (path, url) )
            with open(path, 'wb') as fp:
                shutil.copyfileobj( self._loadUrl( url ), fp )
            return path
        return None 
        

class Tgdb(TgdbBase):
    def __init__(self, platform = 'PC'):
        super(Tgdb, self).__init__()
        self.config = {}
        # http://wiki.thegamesdb.net/index.php?title=API_Introduction
        self.config['base_url'] = 'http://thegamesdb.net/api'
        self.config['platform'] = platform

    def _loadXml(self, url):
        return ElementTree.fromstring( self._loadUrl(url).read() )

    def _castXml(self, tag, text):
        '''Cast xml attributes '''
        if tag in CONVERTERS:
            return CONVERTERS[tag](text)
        return text

    def _xmlToDict(self, xml):
        ''' Converts an ElementTree to a python dictionary '''
        nodedict = dict()
        
        if len(xml.items()) > 0:
            # if we have attributes, set them
            nodedict.update( dict(xml.items()) )
        
        for child in xml:
            # recursively add the element's children
            newitem = self._xmlToDict(child)
            if nodedict.has_key(child.tag):
                # found duplicate tag, force a list
                if type(nodedict[child.tag]) is type([]):
                    # append to existing list
                    nodedict[child.tag].append(newitem)
                else:
                    # convert to list
                    nodedict[child.tag] = [nodedict[child.tag], newitem]
            else:
                # only one, directly set the dictionary
                nodedict[child.tag] = self._castXml(child.tag, newitem)
    
        if xml.text is None: 
            text = ''
        else: 
            text = xml.text.strip()
        
        if len(nodedict) > 0:            
            # if we have a dictionary add the text as a dictionary value (if there is any)
            if len(text) > 0:
                nodedict['_text'] = text
        else:
            # if we don't have child nodes or attributes, just set the text
            nodedict = text
            
        return nodedict

    def _findGame(self, game):
        '''Search the given game in tgdb'''
        url = '%(base_url)s/GetGamesList.php?' %self.config + urlencode( {'name': game, 'platform': self.config['platform'] } )
        games = self._xmlToDict( self._loadXml( url ) )
        full_match = filter( lambda x: x['GameTitle'].lower().strip() == game.lower().strip(), games['Game'])
        if len(full_match) == 1:
            return full_match[0]

        # Filter latest game (not really smart ... )
        return sorted( games['Game'], key=lambda x: x['ReleaseDate'], reverse=True )[0]

    def _getGame(self, gid):
        ''' Get a game by game ID '''
        url = '%(base_url)s/GetGame.php?' %self.config + urlencode( {'id': gid, 'platform': self.config['platform']} )
        return Game( self._xmlToDict( self._loadXml( url ) ) )

    def __getitem__(self, key):
        if isinstance(key, (int, long)):
            # Item is a game id
            return self._getGame( key )
        # Search for key
        return self._getGame( self._findGame( key )['id'] )

