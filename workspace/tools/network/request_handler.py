# workspace/tools/network/request_handler.py

from typing import Optional
import requests
from requests import Response, RequestException

from workspace.tools.common.result_code import ResultCode
from workspace.tools.common.decorator import tool


@tool
def post(url: str, headers: Optional[dict] = None, json: Optional[dict] = None, timeout: int = 10) -> tuple[int, Optional[Response]]:
    """
    發送 POST 請求，回傳錯誤碼與 Response。
    """
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
def safe_post(url: str, headers: Optional[dict] = None, json: Optional[dict] = None, timeout: int = 10) -> Response:
    """
    安全封裝的 POST，失敗直接 raise，成功回傳 Response。
    """
    code, response = post(url, headers=headers, json=json, timeout=timeout)
    if code != ResultCode.SUCCESS or response is None:
        raise RuntimeError(f"POST 請求失敗，錯誤碼：{code}")
    return response

@tool
def get(url: str, headers: Optional[dict] = None, params: Optional[dict] = None, timeout: int = 10) -> tuple[int, Optional[Response]]:
    """
    發送 GET 請求，回傳錯誤碼與 Response。
    """
    print(f"[GET] URL: {url}")
    print(f"[GET] Headers: {headers}")
    print(f"[GET] Params: {params}")
    try:
        response = requests.get(url, headers=headers, params=params, timeout=timeout)
        response.raise_for_status()
        return ResultCode.SUCCESS, response
    except RequestException as e:
        print(f"[GET] ❌ 發送失敗：{e}")
        return ResultCode.TOOL_REQUEST_GET_FAILED, None

@tool
def safe_get(url: str, headers: Optional[dict] = None, params: Optional[dict] = None, timeout: int = 10) -> Response:
    """
    安全封裝的 GET，失敗直接 raise，成功回傳 Response。
    """
    code, response = get(url, headers=headers, params=params, timeout=timeout)
    if code != ResultCode.SUCCESS or response is None:
        raise RuntimeError(f"GET 請求失敗，錯誤碼：{code}")
    return response

def safe_post_lobby(url: str, payload: dict, headers: dict) -> dict:
    """
    發送 POST 請求，專用於大廳登入流程。
    
    Args:
        url (str): API URL
        payload (dict): 傳送的資料
        headers (dict): 自訂的標頭
    
    Returns:
        dict: 回傳 JSON 結構（字典）
    
    Raises:
        TaskModuleError: 請求失敗時拋出
    """
    try:
        response = post(url, headers=headers, json=payload)
        return response.json()
    except Exception as e:
        raise RuntimeError(f"POST 請求失敗：{e}")


