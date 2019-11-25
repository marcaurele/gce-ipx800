# -*- coding: utf-8 *-*

import requests


class ApiError(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class ipx800:
    def __init__(self, url, api_key="apikey"):
        self.url = url
        self._api_url = f"{url}/api/xdevices.json"
        self.api_key = api_key

    def _send_command(self, params):
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


class relay(ipx800):
    def __init__(self, ipx, relay_id):
        super().__init__(ipx.url, ipx.api_key)
        self.id = relay_id

    @property
    def status(self):
        params = {"Get": "R"}
        response = self._send_command(params)
        return response[f"R{self.id}"] == 1

    def on(self):
        params = {"SetR": self.id}
        result = self._send_command(params)
        return result["status"] == "Success"

    def off(self):
        params = {"ClearR": self.id}
        result = self._send_command(params)
        return result["status"] == "Success"

    def toggle(self):
        params = {"ToggleR": self.id}
        response = self._send_command(params)
        return response[f"R{self.id}"] == 1

    def __repr__(self):
        return f"<ipx800.relay id={self.id}>"

    def __str__(self):
        return f"[IPX800-relay: id={self.id}, status={self.status}"
