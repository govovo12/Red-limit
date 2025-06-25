from pathlib import Path
from workspace.tools.network.request_handler import safe_post
from workspace.tools.token.token_lobby_cache import save_lobby_token
from workspace.tools.file.data_loader import load_json
from workspace.tools.env.config_loader import R88_API_BASE_URL, R88_LOBBY_LOGIN_PATH
from workspace.tools.printer.printer import print_info, print_error
from workspace.tools.common.result_code import ResultCode


def get_lobby_token(account: str) -> int:
    """
    呼叫 login API 發送請求，取得大廳 token 並快取。
    """
    try:
        url = f"{R88_API_BASE_URL}{R88_LOBBY_LOGIN_PATH}"
        print_info(f"🔗 發送 API 至：{url}")

        # 從 .cache/api_key.json 載入憑證資訊
        code, result = load_json(Path(".cache/api_key.json"))
        if code != ResultCode.SUCCESS or not isinstance(result, dict):
            raise RuntimeError("❌ 無法讀取 api_key.json")

        headers = {
            "api_key": result.get("api_key"),
            "pf_id": result.get("pf_id"),
            "timestamp": "0"
        }
        payload = {"account": account}

        response = safe_post(url=url, headers=headers, json=payload)
        print_info(f"🧾 回應原始內容：{response.text}")

        full_url = response.json().get("data", {}).get("url")
        if not full_url or "?" not in full_url:
            raise RuntimeError("⚠️ API 回傳中缺少 token URL")

        token = full_url.split("?")[-1]
        if not token:
            raise RuntimeError("⚠️ token 字串擷取失敗")

        save_lobby_token(account, token)
        print_info(f"✅ 大廳 token 快取成功：{token}")
        return ResultCode.SUCCESS


        

    except Exception as e:
        print_error(f"❌ 任務模組執行失敗：{e}")
        return ResultCode.TASK_GET_LOBBY_TOKEN_FAILED



if __name__ == "__main__":
    code = get_lobby_token("qa0002")
    print(f"返回錯誤碼：{code}")
