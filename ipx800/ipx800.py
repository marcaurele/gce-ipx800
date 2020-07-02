# -*- coding: utf-8 *-*

import collections
import warnings

import requests


class ApiError(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class IPX800:
    """Class representing the IPX800 and its API.

       Attributes:
           relays  the IPX800 relays"""

    def __init__(self, url, api_key="apikey"):
        self.url = url
        self._api_url = f"{url}/api/xdevices.json"
        self.api_key = api_key
        self.relays = GenericSlice(self, Relay, {"Get": "R"})
        self.analogs = GenericSlice(self, Analog, {"Get": "A"})

    def _request(self, params):
        # (bug) IPX4, key must be the first parameter otherwise some
        # calls don't return.
        # params.update({"key": self.api_key})
        params_fix = {"key": self.api_key}
        params_fix.update(params)
        r = requests.get(self._api_url, params=params_fix, timeout=2)
        r.raise_for_status()
        content = r.json()
        result = content.pop("status", None)
        product = content.pop("product", None)
        if product != "IPX800_V4":
            warnings.warn(f"Your device '{product}' might not be compatible")
        if result == "Success":
            return content
        else:
            raise ApiError()


class GenericSlice(collections.abc.Sequence):
    """Slice implementation for an iterable over GCE objects"""

    def __init__(self, ipx, gce_type, request_arg=None):
        self._ipx = ipx
        self._length = None
        self._type = gce_type
        self._rarg = request_arg

    def __getitem__(self, key):
        if isinstance(key, slice):
            return [
                self._type(self._ipx, k + 1)
                for k in range(key.start, key.stop, key.step)
            ]
        elif isinstance(key, int):
            if key < self.__len__():
                return self._type(self._ipx, key + 1)
            else:
                raise IndexError
        else:
            raise TypeError("Slice of 'int' is the only accepted range")

    def __len__(self):
        if self._length is None:
            self._length = len(self._ipx._request(self._rarg))
        return self._length


class Relay(IPX800):
    """Representing an IPX800 relay."""

    def __init__(self, ipx, relay_id: int):
        super().__init__(ipx.url, ipx.api_key)
        self.id = relay_id

    @property
    def status(self) -> bool:
        """Return the current relay status."""
        params = {"Get": "R"}
        response = self._request(params)
        return response[f"R{self.id}"] == 1

    def on(self) -> bool:
        """Turn on a relay and return True if it was successful."""
        params = {"SetR": self.id}
        self._request(params)
        return True

    def off(self) -> bool:
        """Turn off a relay and return True if it was successful."""
        params = {"ClearR": self.id}
        self._request(params)
        return True

    def toggle(self) -> bool:
        """Toggle a relay and return True if it was successful."""
        params = {"ToggleR": self.id}
        self._request(params)
        return True

    def __repr__(self) -> str:
        return f"<ipx800.relay id={self.id}>"

    def __str__(self) -> str:
        return (
            f"[IPX800-relay: id={self.id}, "
            f"status={'On' if self.status else 'Off'}]"
        )


class Analog(IPX800):
    """Representing an IPX800 analog sensor."""

    def __init__(self, ipx, analog_id: int):
        super().__init__(ipx.url, ipx.api_key)
        self.id = analog_id

    @property
    def value(self) -> int:
        """Return the current analog sensor value."""
        params = {"Get": "A"}
        response = self._request(params)
        return response[f"A{self.id}"]

    def __repr__(self) -> str:
        return f"<ipx800.analog_sensor id={self.id}>"

    def __str__(self) -> str:
        return f"[IPX800-analog-sensor: id={self.id}, value={self.value}]"
