Fedora 30::

    sudo usermod -a -G audio `whoami`
    sudo dnf install python3-rtmidi python3-evdev
    virtualenv --system-site-packages ~/.virtualenvs/midipenguin
    . ~/.virtualenvs/midipenguin/bin/activate
    pip install -e '.[test]'
