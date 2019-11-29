# -*- coding: utf-8 *-*

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
        self.relays = RelaySlice(self)

    def _request(self, params):
        # (bug) IPX4, key must be the first parameter otherwise some
        # calls don't return.
        # params.update({"key": self.api_key})
        params_fix = {"key": self.api_key}
        params_fix.update(params)
        r = requests.get(self._api_url, params=params_fix, timeout=2)
        r.raise_for_status()
        result = r.json()
        if result["status"] == "Success":
            return result
        else:
            raise ApiError()


class RelaySlice(object):
    """Slice implementation for have an iterable over the Relay object."""

    def __init__(self, ipx):
        self._ipx = ipx

    def __getitem__(self, key):
        if isinstance(key, slice):
            return [
                Relay(self._ipx, k + 1)
                for k in range(key.start, key.stop, key.step)
            ]
        else:
            return Relay(self._ipx, key + 1)


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
        """Turn on a relay and return a boolean if it was successful."""
        params = {"SetR": self.id}
        result = self._request(params)
        return result["status"] == "Success"

    def off(self) -> bool:
        """Turn off a relay and return a boolean if it was successful."""
        params = {"ClearR": self.id}
        result = self._request(params)
        return result["status"] == "Success"

    def toggle(self) -> bool:
        """Toggle a relay and return a boolean if it was successful."""
        params = {"ToggleR": self.id}
        result = self._request(params)
        return result["status"] == "Success"

    def __repr__(self) -> str:
        return f"<ipx800.relay id={self.id}>"

    def __str__(self) -> str:
        return f"[IPX800-relay: id={self.id}, status={self.status}"
