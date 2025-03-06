GCE-IPX800
==========

.. image:: https://img.shields.io/pypi/v/gce-ipx800?color=blue
   :alt: Pypi version
   :target: https://pypi.org/project/gce-ipx800/

.. image:: https://github.com/marcaurele/gce-ipx800/workflows/Build%20status/badge.svg
   :alt: Build Status
   :target: https://github.com/marcaurele/gce-ipx800/actions

.. image:: https://codecov.io/gh/marcaurele/gce-ipx800/branch/main/graph/badge.svg
   :alt: Code coverage
   :target: https://codecov.io/gh/marcaurele/gce-ipx800

.. image:: https://img.shields.io/pypi/l/gce-ipx800.svg
   :alt: License
   :target: https://pypi.org/project/gce-ipx800/

.. image:: https://img.shields.io/pypi/pyversions/gce-ipx800.svg
   :alt: Python versions
   :target: https://pypi.org/project/gce-ipx800/

A python library to control a GCE-Electronics IPX800 V4 device through its API.

* Python 3.8+ support
* Apache License

IPX800 features implemented
---------------------------

* Analog sensors (``ipx.analogs[]``)
* Control:

  - relays (``ipx.relays[]``)
  - virtual inputs (``ipx.virtual_inputs[]``)
  - virtual outputs (``ipx.virtual_outputs[]``)

* Counters (``ipx.counters[]``)
* THL extensions (``ipx.THLextensions[]``)

Installation
------------

.. code-block:: console

    > pip install gce-ipx800

Usage
-----

.. note:: The default API key of the device is `apikey`.

.. code-block:: python

    from ipx800 import ipx800

    ipx = ipx800("http://your-device-ip", "apikey")

    r4 = ipx.relays[3]

    r4.status  # => return a Boolean

    r4.on()

    r4.off()

    r4.toggle()

    len(ipx.relays)  # => 56

    THL0 = ipx.THLextensions[0]

    THL0_humidity=THL0.humidity
    THL0_luminosity=THL0.luminosity
    THL0_temperature=THL0.temperature

Links
-----

* GCE IPX800 V4 API: https://gce.ovh/wiki/index.php?title=API_V4

Licence
-------

Licensed under Apache License Version 2.0
