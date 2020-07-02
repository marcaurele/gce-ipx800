# coding: utf-8

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
    def test_relay_status(self, mock_request):
        mock_request.side_effect = [
            self._mock_response(json_file="tests/getr.json"),
            self._mock_response(json_file="tests/getr.json"),
            self._mock_response(json_file="tests/getr.json"),
            self._mock_response(json_file="tests/getr.json"),
        ]

        ipx = ipx800("http://192.0.2.4")
        assert ipx.relays[0].status
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
    def test_relay_error(self, mock_request):
        mock_request.return_value = self._mock_response(
            json_file="tests/error.json"
        )

        ipx = ipx800("http://192.0.2.4")
        with self.assertRaises(ApiError):
            ipx.relays[3].on()
