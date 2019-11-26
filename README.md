# py-ipx800

![](https://github.com/marcaurele/py-ipx800/workflows/Build%20status/badge.svg)

py-ipx800 is a Python3 Library for controlling GCE-Electronics IPX800 V4 via its public API.

## Sample Usage

### Setting up IPX800

    # Setup IPX800 V4
    url = "http://yourhostname.lan"
    api_key = "apikey"

    ipx = ipx800(url, api_key)

### Setting up Relays

    # Use the relay number #4
    r4 = relay(ipx, 4)

### Controlling relays

    > r4.status
    False
    > r4.on()
    > r4.off()
    > r4.toggle()

## Features

- [x] Control relays
