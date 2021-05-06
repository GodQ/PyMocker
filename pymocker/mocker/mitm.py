from mitmproxy import http
from pymocker.lib.log import get_logger
from pymocker.mocker.rules import process_request, match_any_rule, is_build_in_api
from pymocker.mocker.rules import Request

from pymocker.mocker.stats import HttpRecordStore

import os
import time

import json
import base64
import zlib
import typing  # noqa
from datetime import datetime
from datetime import timezone
import mitmproxy
# from mitmproxy import connection
from mitmproxy import version
from mitmproxy import ctx
from mitmproxy.utils import strutils
from mitmproxy.net.http import cookies

"""
Script for mitmdump
Redirect request from proxy server to real server
"""

_logger = get_logger()


def parse_httpflow_request(flow: http.HTTPFlow) -> Request:
    path = flow.request.path.split('?')[0]
    method = flow.request.method
    params = flow.request.query
    headers = flow.request.headers
    data = flow.request.content
    req = Request(method=method, path=path, params=params, headers=headers, data=data)
    print(req)
    return req


class Printer:
    def request(self, flow: http.HTTPFlow) -> None:
        print('request url: ', flow.request.pretty_url)


class Mocker:
    def request(self, flow: http.HTTPFlow) -> None:
        # pretty_url takes the "Host" header of the request into account, which
        # is useful in transparent mode where we usually only have the IP otherwise.

        req = parse_httpflow_request(flow)
        resp = process_request(req)
        if resp and not resp.empty():
            flow.response = http.HTTPResponse.make(
                resp.status,  # (optional) status code
                resp.data,  # (optional) content
                resp.headers  # (optional) headers
            )


class HarCapture:
    SERVERS_SEEN = set()

    def response(self, flow: mitmproxy.http.HTTPFlow):
        """
           Called when a server response has been received.
        """

        req = parse_httpflow_request(flow)
        if is_build_in_api(req.path) or match_any_rule(req):
            print('skip record')
            return

        # -1 indicates that these values do not apply to current request
        ssl_time = -1
        connect_time = -1

        if flow.server_conn and flow.server_conn not in self.SERVERS_SEEN:
            connect_time = (flow.server_conn.timestamp_tcp_setup -
                            flow.server_conn.timestamp_start)

            if flow.server_conn.timestamp_tls_setup is not None:
                ssl_time = (flow.server_conn.timestamp_tls_setup -
                            flow.server_conn.timestamp_tcp_setup)

            self.SERVERS_SEEN.add(flow.server_conn)

        # Calculate raw timings from timestamps. DNS timings can not be calculated
        # for lack of a way to measure it. The same goes for HAR blocked.
        # mitmproxy will open a server connection as soon as it receives the host
        # and port from the client connection. So, the time spent waiting is actually
        # spent waiting between request.timestamp_end and response.timestamp_start
        # thus it correlates to HAR wait instead.
        timings_raw = {
            'send': flow.request.timestamp_end - flow.request.timestamp_start,
            'receive': flow.response.timestamp_end - flow.response.timestamp_start,
            'wait': flow.response.timestamp_start - flow.request.timestamp_end,
            'connect': connect_time,
            'ssl': ssl_time,
        }

        # HAR timings are integers in ms, so we re-encode the raw timings to that format.
        timings = {
            k: int(1000 * v) if v != -1 else -1
            for k, v in timings_raw.items()
        }

        # full_time is the sum of all timings.
        # Timings set to -1 will be ignored as per spec.
        full_time = sum(v for v in timings.values() if v > -1)

        started_date_time = datetime.fromtimestamp(flow.request.timestamp_start, timezone.utc).isoformat()

        # Response body size and encoding
        response_body_size = len(flow.response.raw_content) if flow.response.raw_content else 0
        response_body_decoded_size = len(flow.response.content) if flow.response.content else 0
        response_body_compression = response_body_decoded_size - response_body_size

        entry = {
            "startedDateTime": started_date_time,
            "time": full_time,
            "request": {
                "method": flow.request.method,
                "url": flow.request.url,
                "httpVersion": flow.request.http_version,
                "cookies": self.format_request_cookies(flow.request.cookies.fields),
                "headers": self.name_value(flow.request.headers),
                "queryString": self.name_value(flow.request.query or {}),
                "headersSize": len(str(flow.request.headers)),
                "bodySize": len(flow.request.content),
            },
            "response": {
                "status": flow.response.status_code,
                "statusText": flow.response.reason,
                "httpVersion": flow.response.http_version,
                "cookies": self.format_response_cookies(flow.response.cookies.fields),
                "headers": self.name_value(flow.response.headers),
                "content": {
                    "size": response_body_size,
                    "compression": response_body_compression,
                    "mimeType": flow.response.headers.get('Content-Type', '')
                },
                "redirectURL": flow.response.headers.get('Location', ''),
                "headersSize": len(str(flow.response.headers)),
                "bodySize": response_body_size,
            },
            "cache": {},
            "timings": timings,
        }

        # Store binary data as base64
        if strutils.is_mostly_bin(flow.response.content):
            entry["response"]["content"]["text"] = base64.b64encode(flow.response.content).decode()
            entry["response"]["content"]["encoding"] = "base64"
        else:
            entry["response"]["content"]["text"] = flow.response.get_text(strict=False)

        if flow.request.method in ["POST", "PUT", "PATCH"]:
            params = [
                {"name": a, "value": b}
                for a, b in flow.request.urlencoded_form.items(multi=True)
            ]
            entry["request"]["postData"] = {
                "mimeType": flow.request.headers.get("Content-Type", ""),
                "text": flow.request.get_text(strict=False),
                "params": params
            }

        if flow.server_conn.connected:
            entry["serverIPAddress"] = str(flow.server_conn.ip_address[0])

        HttpRecordStore.insert_records(entry)

    def format_cookies(self, cookie_list):
        rv = []

        for name, value, attrs in cookie_list:
            cookie_har = {
                "name": name,
                "value": value,
            }

            # HAR only needs some attributes
            for key in ["path", "domain", "comment"]:
                if key in attrs:
                    cookie_har[key] = attrs[key]

            # These keys need to be boolean!
            for key in ["httpOnly", "secure"]:
                cookie_har[key] = bool(key in attrs)

            # Expiration time needs to be formatted
            expire_ts = cookies.get_expiration_ts(attrs)
            if expire_ts is not None:
                cookie_har["expires"] = datetime.fromtimestamp(expire_ts, timezone.utc).isoformat()

            rv.append(cookie_har)

        return rv

    def format_request_cookies(self, fields):
        return self.format_cookies(cookies.group_cookies(fields))

    def format_response_cookies(self, fields):
        return self.format_cookies((c[0], c[1][0], c[1][1]) for c in fields)

    def name_value(self, obj):
        """
            Convert (key, value) pairs to HAR format.
        """
        return [{"name": k, "value": v} for k, v in obj.items()]


addons = [
    Printer(),
    Mocker(),
    HarCapture(),
]
