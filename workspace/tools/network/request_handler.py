# workspace/tools/network/request_handler.py

"""
工具模組：request_handler
封裝 HTTP GET / POST 請求，支援錯誤碼與安全回傳。
"""

import requests
from requests import RequestException, Response
from typing import Optional
from workspace.tools.common.result_code import ResultCode
from workspace.tools.common.decorator import tool

@tool
def get(
    url: str,
    headers: Optional[dict] = None,
    timeout: int = 10
) -> tuple[int, Optional[Response]]:
    try:
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        return ResultCode.SUCCESS, response
    except RequestException as e:
        print(f"[GET] ❌ 發送失敗：{e}")
        return ResultCode.TOOL_REQUEST_GET_FAILED, None

@tool
def safe_get(
    url: str,
    headers: Optional[dict] = None,
    timeout: int = 10
) -> Response:
    code, response = get(url, headers=headers, timeout=timeout)
    if code != ResultCode.SUCCESS or response is None:
        raise RuntimeError(f"[safe_get] GET 請求失敗，錯誤碼：{code}")
    return response

@tool
def post(
    url: str,
    headers: Optional[dict] = None,
    json: Optional[dict] = None,
    timeout: int = 10,
    verbose: bool = False
) -> tuple[int, Optional[Response]]:
    if verbose:
        print(f"[POST] URL: {url}")
        print(f"[POST] Headers: {headers}")
        print(f"[POST] Payload: {json}")
    try:
        response = requests.post(url, headers=headers, json=json, timeout=timeout)
        response.raise_for_status()
        return ResultCode.SUCCESS, response
    except RequestException as e:
        print(f"[POST] ❌ 發送失敗：{e}")
        return ResultCode.TOOL_REQUEST_POST_FAILED, None

@tool
def safe_post(
    url: str,
    headers: Optional[dict] = None,
    json: Optional[dict] = None,
    timeout: int = 10
) -> Response:
    code, response = post(url, headers=headers, json=json, timeout=timeout, verbose=False)
    if code != ResultCode.SUCCESS or response is None:
        raise RuntimeError(f"[safe_post] POST 請求失敗，錯誤碼：{code}")
    return response
