# PygPicture

(very) simple coverflow game launcher to be used with gamepads.

I was sick of searching the mouse to select the game I wanted to play. BIG PICTURE was no option since I don't like/want the overhead (Steam) on my box.
So I started searching and ended up writing my own little tool ... PygPicture!

Please find the latest W32 exe (genereted with PyInstaller) whithin the [Releases](https://github.com/jayme-github/PygPicture/releases) section.

![ScreenShot](https://github.com/jayme-github/PygPicture/raw/master/screenshot.jpg)



# Installation
* [Download](https://github.com/jayme-github/PygPicture/releases) the recent PygPicture release and unzip
* Extract pygpicture.zip somewhere on your system ( *C:\Programm files (x86)\PygPicture\*  for example )
* Create a folder "Games" on your desktop or in the directory where you stored the pygpicture.exe
* Put links to your games into that folder
* Launch pygpicture.exe

PygPicture will search the "Games" directory for links ( *Filename*.lnk ) and tries to find a matching boxart ( *Filename*.jpg ) to display.
If no boxart was found in the "Games" directory, PygPicture will try to find one at [TheGamesDB.net](http://www.thegamesdb.net/) which is then stored in your Games directory.


# Controls
* **Left/Rigt**: (Joystick/Keyboard): left/right
* **Launch game**: (Joystick): Any button; (Keyboard): Return
* **Quit PygPicture**: (Joystick): Any button + Up; (Keyboard): Escape/q
* **Shutdown system**: (Joystick): Any button + Down; (Keyboard): s

# Powered by
* http://pyopengl.sourceforge.net/
* http://www.pygame.org/
* http://www.pyinstaller.org/
* http://www.thegamesdb.net/
* http://www.janeriksolem.net/2009/08/cover-flow-with-pygame-and-opengl.html
