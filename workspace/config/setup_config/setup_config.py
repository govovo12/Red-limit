import re
import typer
from pathlib import Path
from dotenv import dotenv_values

# === 設定路徑 ===
ROOT_DIR = Path(__file__).resolve().parents[2]
ENV_USER_PATH = ROOT_DIR / ".env.user"

app = typer.Typer()


# === ✅ PF_ID 驗證邏輯 ===
def validate_pf_id(pf_id: str) -> str:
    if "_" not in pf_id:
        typer.secho("❌ PF_ID 格式錯誤：缺少底線 _，請重新輸入。", fg=typer.colors.RED)
        return None
    if not re.fullmatch(r"[a-zA-Z0-9_]+", pf_id):
        typer.secho("❌ PF_ID 由英文 + 數字組合，請重新輸入。", fg=typer.colors.RED)
        return None
    return pf_id


# === ✅ PRIVATE_KEY 驗證邏輯（嚴格版）
def validate_private_key(key: str) -> str:
    key = key.strip()
    if not re.fullmatch(r"[a-zA-Z0-9]{32}", key):
        typer.secho("❌ PRIVATE_KEY 僅允許英文與數字組合，且長度需為 32 字元，請重新輸入。", fg=typer.colors.RED)
        return None
    return key


# === ✅ BET_LEVEL_MODE 選單（中文 + 限制只能輸入 1 或 2）
def ask_bet_level_mode() -> str:
    typer.echo("請選擇限紅模式：")
    typer.echo("  1. 最大限紅（max）")
    typer.echo("  2. 最小限紅（min）")
    typer.echo("")

    mapping = {
        "1": "max",
        "2": "min"
    }

    while True:
        choice = typer.prompt("請輸入對應數字 [1 or 2]")
        if choice in mapping:
            return mapping[choice]
        typer.secho("❌ 限紅模式僅能為 1（最大限紅）或 2（最小限紅），請重新輸入。", fg=typer.colors.RED)


# === ✅ BET_AMOUNT_RULE 條件選單
def ask_bet_rule() -> str:
    typer.echo("請選擇限紅條件運算方式：")
    typer.echo("  1. 大於（>）")
    typer.echo("  2. 小於（<）")
    typer.echo("  3. 大於等於（>=）")
    typer.echo("  4. 小於等於（<=）")
    typer.echo("  5. 等於（==）")
    typer.echo("  6. 不等於（!=）")
    typer.echo("")

    operator_mapping = {
        "1": ">",
        "2": "<",
        "3": ">=",
        "4": "<=",
        "5": "==",
        "6": "!="
    }

    while True:
        op_choice = typer.prompt("請輸入對應數字 [1~6]")
        if op_choice in operator_mapping:
            break
        typer.secho("❌ 請輸入 1~6 之間的數字！", fg=typer.colors.RED)

    operator = operator_mapping[op_choice]

    while True:
        value = typer.prompt("請輸入限紅數值（例如 10 或 0.05）")
        try:
            float(value)
            break
        except ValueError:
            typer.secho("❌ 請輸入有效的數字！", fg=typer.colors.RED)

    return f"{operator}{value}"


# === ✅ 主命令
@app.command()
def configure():
    # Step 1: PF_ID
    while True:
        pf_id_input = typer.prompt("請輸入 PF_ID")
        validated = validate_pf_id(pf_id_input)
        if validated:
            pf_id = validated
            break

    # Step 2: PRIVATE_KEY
    while True:
        key_input = typer.prompt("請輸入 PRIVATE_KEY")
        validated = validate_private_key(key_input)
        if validated:
            private_key = validated
            break

    # Step 3: BET_LEVEL_MODE
    bet_mode = ask_bet_level_mode()

    # Step 4: BET_AMOUNT_RULE
    bet_rule = ask_bet_rule()

    # Step 5: 寫入 .env.user
    existing_env = dotenv_values(ENV_USER_PATH) if ENV_USER_PATH.exists() else {}
    existing_env.update({
        "PF_ID": pf_id,
        "PRIVATE_KEY": private_key,
        "BET_AMOUNT_RULE": bet_rule,
        "BET_LEVEL_MODE": bet_mode,
    })

    content = "\n".join(
        [f'{key}="{value}"' for key, value in existing_env.items()]
    ) + "\n"

    ENV_USER_PATH.write_text(content, encoding="utf-8")

    typer.echo("\n✅ 已成功更新 .env.user 檔案！")
    typer.echo(f"📄 寫入路徑：{ENV_USER_PATH}")


if __name__ == "__main__":
    app()
