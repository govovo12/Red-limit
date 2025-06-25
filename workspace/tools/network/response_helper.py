from typing import Any, Optional, Tuple
from workspace.tools.common.decorator import tool
from workspace.tools.common.result_code import ResultCode
from workspace.tools.printer.printer import print_error
from typing import Any, List, Dict, Union

@tool
def get_code_from_dict(data: dict) -> Tuple[int, Optional[int]]:
    """
    擷取錯誤碼欄位（code / error_code）。

    :return: (錯誤碼, code 數值)
    """
    if "code" in data:
        return ResultCode.SUCCESS, data["code"]
    if "error_code" in data:
        return ResultCode.SUCCESS, data["error_code"]
    print_error("response 缺少 code 或 error_code 欄位")
    return ResultCode.TOOL_RESPONSE_KEY_MISSING, None


@tool
def get_data_from_dict(data: dict) -> Tuple[int, Optional[Any]]:
    """
    擷取資料欄位（data）。

    :return: (錯誤碼, 資料內容)
    """
    if "data" in data:
        return ResultCode.SUCCESS, data["data"]
    print_error("response 缺少 data 欄位")
    return ResultCode.TOOL_RESPONSE_KEY_MISSING, None


@tool
def get_token_from_dict(data: dict) -> Tuple[int, Optional[str]]:
    """
    擷取 token 欄位（token 或 access_token）。

    :return: (錯誤碼, token)
    """
    if "token" in data:
        return ResultCode.SUCCESS, data["token"]
    if "access_token" in data:
        return ResultCode.SUCCESS, data["access_token"]
    print_error("response 缺少 token / access_token 欄位")
    return ResultCode.TOOL_RESPONSE_KEY_MISSING, None

@tool
def extract_token(response: dict, key: str = "jwt") -> Tuple[int, Optional[str]]:
    """
    從 response 中提取 token，並驗證欄位完整性。

    :param response: API 回傳的 JSON dict
    :param key: token 欄位的名稱（預設 jwt）
    :return: (錯誤碼, token 或 None)
    """
    if not isinstance(response, dict):
        return ResultCode.TOOL_INVALID_RESPONSE_FORMAT, None

    data = response.get("data", {})
    if not isinstance(data, dict):
        return ResultCode.TOOL_MISSING_DATA_FIELD, None

    token = data.get(key)
    if not token:
        return ResultCode.TOOL_MISSING_TOKEN_FIELD, None

    return ResultCode.SUCCESS, token

def extract_nested(data: dict, path: str, default=None):
    """
    提取巢狀結構中的指定值。
    
    Args:
        data (dict): 要提取的資料
        path (str): 使用點號分隔的鍵路徑，例如 "data.url"
        default (Any, optional): 若找不到值時回傳的預設值
    
    Returns:
        Any: 提取的值，或預設值
    """
    keys = path.split(".")
    current = data
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return default
    return current



@tool
def extract_game_option_list(response: dict) -> list:
    """
    從巢狀結構 response 中擷取每個遊戲的 game_name 和 min_bet。
    回傳格式為：[{ "game_name": str, "min_bet": int }]
    """
    result = []
    try:
        game_list = response.get("data", {}).get("game_option_list", [])
        if not isinstance(game_list, list):
            print_error("❌ response['data']['game_option_list'] 不是 list 結構")
            return []

        for game in game_list:
            game_name = game.get("game_name", "未知")
            options = game.get("game_option", [])
            for opt in options:
                min_bet = opt.get("min_bet", None)
                if min_bet is not None:
                    result.append({"game_name": game_name, "min_bet": min_bet})
    except Exception as e:
        print_error(f"❌ 擷取 game_option 時發生例外：{e}")
    return result

