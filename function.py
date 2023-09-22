from typing import Optional
from urllib.parse import urlencode

import curlify
import requests
from requests import Response
from requests.auth import HTTPBasicAuth


def _req_get(endpoint: str, public_key: str, private_key: str, table: str, record_id: str,
             json_data: Optional[dict] = None) -> Response:
    rsp = requests.get(f'{endpoint}/{table}/{f"{record_id}/" if (json_data is None) else f"?{urlencode(json_data)}"}',
                       auth=(public_key, private_key))
    print("debug _req_get #", curlify.to_curl(rsp.request))
    return rsp


def _req_post(endpoint: str, public_key: str, private_key: str, table: str, json_data: dict) -> Response:
    rsp = requests.post(f'{endpoint}/{table}/', headers={'content-type': 'application/json'},
                        json=json_data, auth=HTTPBasicAuth(public_key, private_key))
    print("debug req post #", curlify.to_curl(rsp.request))
    return rsp


def _req_put(endpoint: str, public_key: str, private_key: str, table: str, record_id: str, json_data: dict) -> Response:
    rsp = requests.put(f'{endpoint}/{table}/{record_id}/', headers={'content-type': 'application/json'},
                       json=json_data, auth=HTTPBasicAuth(public_key, private_key))
    print("debug req put #", curlify.to_curl(rsp.request))
    return rsp


def _req_patch(endpoint: str, public_key: str, private_key: str, table: str, record_id: str,
               json_data: dict) -> Response:
    rsp = requests.patch(f'{endpoint}/{table}/{record_id}/', headers={'content-type': 'application/json'},
                         json=json_data, auth=HTTPBasicAuth(public_key, private_key))
    print("debug _req_patch #", curlify.to_curl(rsp.request))
    return rsp
