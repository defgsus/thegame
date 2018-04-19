### "The Game"

It's about 16 years since i worked on a 2d orthographic pixel adventure.
It was a *huge project* at the time, fully written in turbo pascal / assembler.

I'd like to reenact the fun, this time in python and 
definitely with modern graphic capabilities, but keeping the
oldschool pixel style.

This repo is just a cloud backup for the moment. We'll see
where it goes..

![screenshot](./screenshot.png)

#### setup

For the game itself:

```bash
virtualenv -p python3 env
source env/bin/activate
git clone https://github.com/defgsus/thegame.git
cd thegame
pip install -r requirements
python main.py
```

Of course we need **"The Editor"** as well. 
I've decided to use Qt there because of a couple of years 
of experience with Qt in C++. 

The best python bindings seem to be [PySide](https://wiki.qt.io/PySide), 
although there are a few problems at the moment. 
Either you want **Qt5+** which is wrapped by [PySide2](https://wiki.qt.io/Qt_for_Python)
but which does not come pre-packaged yet, and even requires you
to build Qt yourself on some platforms, or you go with **Qt4** which
is fine for me at the moment but it only works with Python up to **3.4**
(where the default Python 3 package for Debian is 3.5).

So to run the editor, [install Python 3.4](https://askubuntu.com/questions/849190/python-3-4-on-ubuntu-16-04) alongside and do:

```bash
virtualenv -p python3.4 env3.4
source env3.4/bin/activate
cd thegame
pip install -r requirements-editor.txt
python main_editor.py
```

.. and wait 15 minutes or so..
