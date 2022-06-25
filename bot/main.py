import asyncio
import logging

from typing import List

from bot.settings import settings
from bot.client import client
from bot.strategies.strategy_fabric import construct_strategy

logging.basicConfig(
    level=logging.DEBUG,
    format="[%(levelname)-5s] %(asctime)-19s %(name)s: %(message)s",
)

logger = logging.getLogger(__name__)

async def is_available_account() -> bool:
    logger.info(f"Checking for available accounts...")
    return bool(await client.get_accounts())

async def get_account_id() -> str:
    if await is_available_account():
        logger.info("Accounts found")
    else:
        logger.warning("No accounts found. Creating a new account...")
        await client.open_sandbox_account()
    accounts = await client.get_accounts()
    return accounts[0].id    

def create_tasks_for_strategies(account_id) -> list[asyncio.Task]:
    strategies = [construct_strategy(strategy_name=settings.strategy_name,
                                        account_id=account_id,
                                        figi=settings.figi)]
    return [asyncio.create_task(strategy.run()) for strategy in strategies]

async def main():
    logger.info("Initializing client...")
    await client.ainit()
    logger.info("Client initialized")
    account_id = await get_account_id()
    logger.info(f"Using account {account_id}")
    logger.info("Starting strategies...")
    tasks = create_tasks_for_strategies(account_id)
    logger.info("All strategies are up and running")
    logger.info("Waiting while the strategies are running...")
    for task in tasks:
        await task

if __name__ == "__main__":
    asyncio.run(main())
