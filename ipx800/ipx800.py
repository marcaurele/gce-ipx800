import collections
import warnings

import requests


class ApiError(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class IPX800:
    """Class representing the IPX800 and its API.

    Attributes:
        analogs  the analog sensors
        relays  the physical relays
        virtual_inputs  the virtual inputs
        virtual_outputs  the virtual outputs
    """

    def __init__(self, url, api_key="apikey"):
        self.url = url
        self._api_url = f"{url}/api/xdevices.json"
        self.api_key = api_key
        self.counters = GenericSlice(self, Counter, {"Get": "C"})
        self.relays = GenericSlice(self, Relay, {"Get": "R"})
        self.analogs = GenericSlice(self, Analog, {"Get": "A"})
        self.THLextensions = GenericSlice(self, THLExtension, {"Get": "XTHL"})
        self.virtual_inputs = GenericSlice(self, VirtualInput, {"Get": "VI"})
        self.virtual_outputs = GenericSlice(self, VirtualOutput, {"Get": "VO"})

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


class BaseSwitch(IPX800):
    """Base class to abstract switch operations."""

    def __init__(self, ipx, id: int, name: str, code: str):
        super().__init__(ipx.url, ipx.api_key)
        self.id = id
        self._name = name
        self._code = code

    @property
    def status(self) -> bool:
        """Return the current status."""
        params = {"Get": self._code}
        response = self._request(params)
        return response[f"{self._code}{self.id}"] == 1

    def on(self) -> bool:
        """Turn on and return True if it was successful."""
        params = {f"Set{self._code}": self.id}
        self._request(params)
        return True

    def off(self) -> bool:
        """Turn off and return True if it was successful."""
        params = {"Clear{self._code}": self.id}
        self._request(params)
        return True

    def toggle(self) -> bool:
        """Toggle and return True if it was successful."""
        params = {"Toggle{self._code}": self.id}
        self._request(params)
        return True

    def __repr__(self) -> str:
        return f"<ipx800.{self._name} id={self.id}>"

    def __str__(self) -> str:
        return (
            f"[IPX800-{self._name}: id={self.id}, "
            f"status={'On' if self.status else 'Off'}]"
        )


class Relay(BaseSwitch):
    """Representing an IPX800 relay."""

    def __init__(self, ipx, id: int):
        super().__init__(ipx, id, name="relay", code="R")


class VirtualInput(BaseSwitch):
    """Representing an IPX800 virtual input."""

    def __init__(self, ipx, id: int):
        super().__init__(ipx, id, name="virtual-input", code="VI")


class VirtualOutput(BaseSwitch):
    """Reprenting an IPX800 virtual output."""

    def __init__(self, ipx, id: int):
        super().__init__(ipx, id, name="virtual-output", code="VO")


class Analog(IPX800):
    """Representing an IPX800 analog sensor."""

    def __init__(self, ipx, analog_id: int):
        super().__init__(ipx.url, ipx.api_key)
        self.id = analog_id

    def __repr__(self) -> str:
        return f"<ipx800.analog_sensor id={self.id}>"

    def __str__(self) -> str:
        return f"[IPX800-analog-sensor: id={self.id}, value={self.value}]"

    @property
    def value(self) -> int:
        """Return the current analog sensor value."""
        params = {"Get": "A"}
        response = self._request(params)
        return response[f"A{self.id}"]

    @property
    def as_volt(self) -> float:
        """Return the analog sensor value as Volt."""
        return self.value * 0.000050354

    @property
    def as_tc4012(self) -> float:
        """Return the corresponding temperature in +C for a TC4012 sensor."""
        return self.as_volt - 50

    @property
    def as_tc100(self) -> float:
        """Return the corresponding temperature in °C for a TC 100 sensor."""
        return (self.as_volt - 0.25) / 0.028

    @property
    def as_xhtx3_tc5050(self) -> float:
        """Return the corresponding temperature in °C for a
        XHT-X3 TC5050 temperature sensor.
        """
        return (self.as_volt - 1.63) / 0.0326

    @property
    def as_xhtx3_ls100(self) -> float:
        """Return the corresponding value for a
        XHT-X3 LS-100 light sensor.
        """
        return self.value * 0.0015258

    @property
    def as_xhtx3_sh100(self) -> float:
        """Return the corresponding value for a
        XHT-X3 SH-100 humidity sensor.
        """
        return ((self.value * 0.00323) / 211.2 - 0.1515) / 0.00636


class Counter(IPX800):
    """Representing an IPX800 counter."""

    def __init__(self, ipx, counter_id: int):
        super().__init__(ipx.url, ipx.api_key)
        self.id = counter_id

    def __repr__(self) -> str:
        return f"<ipx800.counter id={self.id}>"

    def __str__(self) -> str:
        return f"[IPX800-counter: id={self.id}, value={self.value}]"

    @property
    def value(self) -> int:
        """Return the current counter value."""
        params = {"Get": "C"}
        response = self._request(params)
        return response[f"C{self.id}"]

    def reset(self) -> None:
        """Reset the counter value to 0."""
        params = {f"SetC{self.id:02d}": 0}
        self._request(params)
        return True
    
class THLExtension(IPX800):
    """Representing an IPX800 Extension."""

    def __init__(self, ipx, extension_id: int):
        super().__init__(ipx.url, ipx.api_key)
        self.id = extension_id

    def __repr__(self) -> str:
        return f"<ipx800.extension id={self.id}>"

    def __str__(self) -> str:
        return f"[IPX800-extension: id={self.id}, value={self.value}]"

    @property
    def temperature(self) -> int:
        """Return the temperature value."""
        params = {"Get": "XTHL"}
        response = self._request(params)
        return response[f"THL{self.id}-TEMP"]
    
    @property
    def humidity(self) -> int:
        """Return the humidity value."""
        params = {"Get": "XTHL"}
        response = self._request(params)
        return response[f"THL{self.id}-HUM"]
    
    @property
    def luminosity(self) -> int:
        """Return the luminosity value."""
        params = {"Get": "XTHL"}
        response = self._request(params)
        return response[f"THL{self.id}-LUM"]