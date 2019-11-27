GCE-IPX800
==========

.. image:: https://github.com/marcaurele/py-ipx800/workflows/Build%20status/badge.svg
   :alt: Build Status
   :target: https://github.com/marcaurele/py-ipx800/actions

.. image:: https://img.shields.io/pypi/l/gce-ipx800.svg
   :alt: License
   :target: https://pypi.org/project/gce-ipx800/

.. image:: https://img.shields.io/pypi/pyversions/gce-ipx800.svg
   :alt: Python versions
   :target: https://pypi.org/project/gce-ipx800/

A python library to control a GCE-Electronics IPX800 V4 device through its API.

* Python 3.5+ support
* Apache License

IPX800 features implemented
---------------------------

* Control relays


Installation
------------

::

    pip install gce-ipx800

Usage
-----

.. note:: The default API key of the device is `apikey`.

::

    from ipx800 import ipx800, relay

    ipx = ipx800("http://your-device-ip", "apikey")

    r4 = relay(ipx, 4)

    r4.status  # => return a Boolean

    r4.on()

    r4.off()

    r4.togle()

Links
-----

* GCE IPX800 V4 API: https://gce.ovh/wiki/index.php?title=API_V4
