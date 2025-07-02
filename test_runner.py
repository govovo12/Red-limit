import asyncio
from workspace.modules.task.recharge_wallet_task import recharge_wallet_async

async def main():
    result = await recharge_wallet_async("qa0002")
    print(f"💰 加值結果：code={result}")

if __name__ == "__main__":
    asyncio.run(main())
