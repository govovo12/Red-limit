from workspace.modules.recharge.query_money_carry import query_money_carry

if __name__ == "__main__":
    account = "qa0001"  # 你要測的帳號
    code, balance = query_money_carry(account)

    print(f"查詢結果：code={code}, balance={balance}")
