# -*- mode: python -*-
import os
def Datafiles(*filenames, **kw):
    
    def datafile(path, strip_path=True):
        parts = path.split('/')
        path = name = os.path.join(*parts)
        if strip_path:
            name = os.path.basename(path)
        return name, path, 'DATA'

    strip_path = kw.get('strip_path', True)
    return TOC(
        datafile(filename, strip_path=strip_path)
        for filename in filenames
        if os.path.isfile(filename))

files = Datafiles( os.path.join('lib', 'default.jpg') )


a = Analysis(['pygpicture.py'],
             pathex=['F:\\'],
             hiddenimports=[],
             hookspath=None)
pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts + [('O','','OPTION')],
          a.binaries,
          a.zipfiles,
          a.datas,
          files,
          name=os.path.join('dist', 'pygpicture.exe'),
          debug=False,
          strip=None,
          upx=True,
          console=True )
