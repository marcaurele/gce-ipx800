import json
from unittest import TestCase
from unittest.mock import Mock, call, patch

from ipx800 import ApiError, ipx800


class IPX800Test(TestCase):
    def _mock_response(
        self,
        status=200,
        content="CONTENT",
        json_file=None,
        raise_for_status=None,
    ):
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        if raise_for_status:
            mock_response.raise_for_status.side_effect = raise_for_status
        mock_response.status_code = status
        mock_response.content = content
        if json_file:
            with open(json_file, "r", encoding="utf-8") as f:
                mock_response.json.return_value = json.loads(f.read())
        return mock_response

    def test_invalid_relay_index(self):
        ipx = ipx800("http://192.0.2.4")
        with self.assertRaises(TypeError):
            ipx.relays["abc"]

    @patch("requests.get")
    def test_invalid_relay(self, mock_request):
        mock_request.return_value = self._mock_response(
            json_file="tests/error.json"
        )

        ipx = ipx800("http://192.0.2.4")
        with self.assertRaises(ApiError):
            ipx.relays[998].status
        self.assertIn(
            call(
                "http://192.0.2.4/api/xdevices.json",
                params={"key": "apikey", "Get": "R"},
                timeout=2,
            ),
            mock_request.call_args_list,
        )
        self.assertEqual(len(mock_request.call_args_list), 1)

    @patch("requests.get")
    def test_relay_length(self, mock_request):
        mock_request.return_value = self._mock_response(
            json_file="tests/getr.json"
        )

        ipx = ipx800("http://192.0.2.4")
        self.assertEqual(len(ipx.relays), 56)

    @patch("requests.get")
    def test_relay_iteration(self, mock_request):
        mock_request.side_effect = [
            self._mock_response(json_file="tests/getr.json") for i in range(56)
        ]
        ipx = ipx800("http://192.0.2.4")
        self.assertEqual(len([r for r in ipx.relays]), 56)

    @patch("requests.get")
    def test_relay_status(self, mock_request):
        mock_request.side_effect = [
            self._mock_response(json_file="tests/getr.json"),
            self._mock_response(json_file="tests/getr.json"),
            self._mock_response(json_file="tests/getr.json"),
            self._mock_response(json_file="tests/getr.json"),
        ]

        ipx = ipx800("http://192.0.2.4")
        assert ipx.relays[0].status is False
        assert ipx.relays[5].status
        assert ipx.relays[1].status is False

    @patch("requests.get")
    def test_relay_off(self, mock_request):
        mock_request.side_effect = [
            self._mock_response(json_file="tests/getr.json"),
            self._mock_response(json_file="tests/clearr2.json"),
        ]

        ipx = ipx800("http://192.0.2.4")
        assert ipx.relays[1].off()

    @patch("requests.get")
    def test_relay_on(self, mock_request):
        mock_request.side_effect = [
            self._mock_response(json_file="tests/getr.json"),
            self._mock_response(json_file="tests/setr2.json"),
        ]

        ipx = ipx800("http://192.0.2.4")
        assert ipx.relays[1].on()

    @patch("requests.get")
    def test_relay_toggle(self, mock_request):
        mock_request.side_effect = [
            self._mock_response(json_file="tests/getr.json"),
            self._mock_response(json_file="tests/setr2.json"),
        ]

        ipx = ipx800("http://192.0.2.4")
        assert ipx.relays[1].toggle()

    @patch("requests.get")
    def test_relay_str(self, mock_request):
        mock_request.side_effect = [
            self._mock_response(json_file="tests/getr.json"),
            self._mock_response(json_file="tests/getr.json"),
            self._mock_response(json_file="tests/getr.json"),
        ]

        ipx = ipx800("http://192.0.2.4")
        self.assertEqual(str(ipx.relays[5]), "[IPX800-relay: id=6, status=On]")
        self.assertEqual(
            str(ipx.relays[2]), "[IPX800-relay: id=3, status=Off]"
        )

    @patch("requests.get")
    def test_relay_error(self, mock_request):
        mock_request.return_value = self._mock_response(
            json_file="tests/error.json"
        )

        ipx = ipx800("http://192.0.2.4")
        with self.assertRaises(ApiError):
            ipx.relays[3].on()

    @patch("requests.get")
    def test_virtuals_length(self, mock_request):
        mock_request.side_effect = [
            self._mock_response(json_file="tests/getvi.json"),
            self._mock_response(json_file="tests/getvo.json"),
        ]

        ipx = ipx800("http://192.0.2.4")
        self.assertEqual(len(ipx.virtual_inputs), 128)
        self.assertEqual(len(ipx.virtual_outputs), 128)

    @patch("requests.get")
    def test_virtuals_iteration(self, mock_request):
        mock_request.side_effect = [
            self._mock_response(json_file="tests/getvi.json")
            for i in range(128)
        ]
        ipx = ipx800("http://192.0.2.4")
        self.assertEqual(len([r for r in ipx.virtual_inputs]), 128)

    @patch("requests.get")
    def test_virtuals_status(self, mock_request):
        mock_request.side_effect = [
            self._mock_response(json_file="tests/getvi.json"),
            self._mock_response(json_file="tests/getvi.json"),
            self._mock_response(json_file="tests/getvo.json"),
            self._mock_response(json_file="tests/getvo.json"),
            self._mock_response(json_file="tests/getvi.json"),
        ]

        ipx = ipx800("http://192.0.2.4")
        assert ipx.virtual_inputs[31].status
        assert ipx.virtual_outputs[31].status
        assert ipx.virtual_inputs[13].status is False

    @patch("requests.get")
    def test_virtual_input_str(self, mock_request):
        mock_request.side_effect = [
            self._mock_response(json_file="tests/getvi.json"),
            self._mock_response(json_file="tests/getvi.json"),
            self._mock_response(json_file="tests/getvi.json"),
        ]

        ipx = ipx800("http://192.0.2.4")
        self.assertEqual(
            str(ipx.virtual_inputs[0]),
            "[IPX800-virtual-input: id=1, status=Off]",
        )
        self.assertEqual(
            str(ipx.virtual_inputs[31]),
            "[IPX800-virtual-input: id=32, status=On]",
        )

    @patch("requests.get")
    def test_virtual_output_str(self, mock_request):
        mock_request.side_effect = [
            self._mock_response(json_file="tests/getvo.json"),
            self._mock_response(json_file="tests/getvo.json"),
            self._mock_response(json_file="tests/getvo.json"),
        ]

        ipx = ipx800("http://192.0.2.4")
        self.assertEqual(
            str(ipx.virtual_outputs[31]),
            "[IPX800-virtual-output: id=32, status=On]",
        )
        self.assertEqual(
            str(ipx.virtual_outputs[2]),
            "[IPX800-virtual-output: id=3, status=Off]",
        )

    @patch("requests.get")
    def test_analog_sensors_length(self, mock_request):
        mock_request.return_value = self._mock_response(
            json_file="tests/geta.json"
        )

        ipx = ipx800("http://192.0.2.4")
        self.assertEqual(len(ipx.analogs), 4)

    @patch("requests.get")
    def test_analog_sensors_value(self, mock_request):
        mock_request.side_effect = [
            self._mock_response(json_file="tests/geta.json"),
            self._mock_response(json_file="tests/geta.json"),
            self._mock_response(json_file="tests/geta.json"),
            self._mock_response(json_file="tests/geta.json"),
        ]

        ipx = ipx800("http://192.0.2.4")
        assert ipx.analogs[0].value == 47611
        assert ipx.analogs[1].value == 18328
        assert ipx.analogs[2].value == 0

    @patch("requests.get")
    def test_analog_sensor_str(self, mock_request):
        mock_request.side_effect = [
            self._mock_response(json_file="tests/geta.json"),
            self._mock_response(json_file="tests/geta.json"),
        ]

        ipx = ipx800("http://192.0.2.4")
        self.assertEqual(
            str(ipx.analogs[0]), "[IPX800-analog-sensor: id=1, value=47611]"
        )

    @patch("requests.get")
    def test_analog_sensor_values(self, mock_request):
        mock_request.side_effect = [
            self._mock_response(json_file="tests/geta.json"),
            self._mock_response(json_file="tests/geta.json"),
            self._mock_response(json_file="tests/geta.json"),
            self._mock_response(json_file="tests/geta.json"),
            self._mock_response(json_file="tests/geta.json"),
            self._mock_response(json_file="tests/geta.json"),
            self._mock_response(json_file="tests/geta.json"),
        ]

        ipx = ipx800("http://192.0.2.4")
        sensor = ipx.analogs[0]
        self.assertEqual(sensor.as_volt, 2.3974042939999998)
        self.assertEqual(sensor.as_tc4012, -47.602595706)
        self.assertEqual(sensor.as_tc100, 76.69301049999999)
        self.assertEqual(sensor.as_xhtx3_tc5050, 23.540009018404906)
        self.assertEqual(sensor.as_xhtx3_ls100, 72.6448638)
        self.assertEqual(sensor.as_xhtx3_sh100, 90.66693616590432)

    @patch("requests.get")
    def test_analog_counters_length(self, mock_request):
        mock_request.return_value = self._mock_response(
            json_file="tests/getc.json"
        )

        ipx = ipx800("http://192.0.2.4")
        self.assertEqual(len(ipx.counters), 16)

    @patch("requests.get")
    def test_analog_counters_value(self, mock_request):
        mock_request.side_effect = [
            self._mock_response(json_file="tests/getc.json"),
            self._mock_response(json_file="tests/getc.json"),
            self._mock_response(json_file="tests/getc.json"),
        ]

        ipx = ipx800("http://192.0.2.4")
        assert ipx.counters[0].value == 15
        assert ipx.counters[1].value == 0

    @patch("requests.get")
    def test_analog_counter_str(self, mock_request):
        mock_request.side_effect = [
            self._mock_response(json_file="tests/getc.json"),
            self._mock_response(json_file="tests/getc.json"),
        ]

        ipx = ipx800("http://192.0.2.4")
        self.assertEqual(
            str(ipx.counters[0]), "[IPX800-counter: id=1, value=15]"
        )
