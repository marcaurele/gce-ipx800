# coding: utf-8

import json
from unittest import TestCase
from unittest.mock import Mock, call, patch

from ipx800 import ApiError, ipx800


class IPX800Test(TestCase):
    def setUp(self):
        with open("tests/clearr2.json", "r", encoding="utf-8") as f:
            self.sample_clear_r2 = json.loads(f.read())
        with open("tests/error.json", "r", encoding="utf-8") as f:
            self.sample_error = json.loads(f.read())
        with open("tests/getall.json", "r", encoding="utf-8") as f:
            self.sample_get_all = json.loads(f.read())
        with open("tests/getr.json", "r", encoding="utf-8") as f:
            self.sample_get_r = json.loads(f.read())
        with open("tests/toggler.json", "r", encoding="utf-8") as f:
            self.sample_toggle_r = json.loads(f.read())

    def _mock_response(
        self,
        status=200,
        content="CONTENT",
        json_data=None,
        raise_for_status=None,
    ):
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        if raise_for_status:
            mock_response.raise_for_status.side_effect = raise_for_status
        mock_response.status_code = status
        mock_response.content = content
        if json_data:
            mock_response.json = Mock(return_value=json_data)
        return mock_response

    @patch("requests.get")
    def test_invalid_relay(self, mock_request):
        mock_request.return_value = self._mock_response(
            json_data=self.sample_error
        )

        ipx = ipx800("http://192.0.2.4")
        r999 = ipx.relays[998]
        with self.assertRaises(ApiError):
            r999.status
        self.assertIn(
            call(
                "http://192.0.2.4/api/xdevices.json",
                params={"key": "apikey", "Get": "R"},
                timeout=2,
            ),
            mock_request.call_args_list,
        )
        self.assertEqual(len(mock_request.call_args_list), 1)
