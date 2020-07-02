===================================================================
 midipenguin – tools for using a Linux laptop as a MIDI controller
===================================================================


|travis-badge|_ |license-badge|_ |black-badge|_

.. |travis-badge| image:: https://travis-ci.com/akaihola/midipenguin.svg?branch=master
.. _travis-badge: https://travis-ci.com/akaihola/midipenguin
.. |license-badge| image:: https://img.shields.io/badge/License-BSD%203--Clause-blue.svg
.. _license-badge: https://github.com/akaihola/midipenguin/blob/master/LICENSE.rst
.. |black-badge| image:: https://img.shields.io/badge/code%20style-black-000000.svg
.. _black-badge: https://github.com/psf/black


Installation
============

Fedora 30::

    sudo usermod -a -G audio `whoami`
    sudo dnf install python3-rtmidi python3-evdev
    virtualenv --system-site-packages ~/.virtualenvs/midipenguin
    . ~/.virtualenvs/midipenguin/bin/activate
    pip install -e '.[test]'


GitHub stars trend
==================

|stargazers|_

.. |stargazers| image:: https://starchart.cc/akaihola/midipenguin.svg
.. _stargazers: https://starchart.cc/akaihola/midipenguin
