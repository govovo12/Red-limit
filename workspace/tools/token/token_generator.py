import hashlib
from workspace.tools.common.decorator import tool

@tool
def generate_api_key(pf_id: str, private_key: str) -> str:
    """
    根據 pf_id 與 private_key 組合產生 SHA256 API Key。
    """
    raw = f"{pf_id}{private_key}0"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()
