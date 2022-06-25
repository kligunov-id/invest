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
    logger.debug(f"Checking for available accounts...")
    return bool(await client.get_accounts())

async def set_account_id():
    if await is_available_account():
        logger.debug("Accounts found")
    else:
        logger.warning("No accounts found. Creating a new account...")
        await client.open_sandbox_account()
    accounts = await client.get_accounts()
    settings.account_id = accounts[0].id    

async def init_account():
    if settings.account_id is None:
        await set_account_id()
    else:
        logger.debug("Account is provided in .env")
    logger.info(f"Using account {settings.account_id}")

def create_tasks_for_strategies() -> list[asyncio.Task]:
    strategies = [construct_strategy(strategy_name=settings.strategy_name,
                                        account_id=settings.account_id,
                                        figi=settings.figi)]
    return [asyncio.create_task(strategy.run()) for strategy in strategies]

async def main():
    logger.info("Initializing client...")
    await client.ainit()
    logger.info("Client initialized")
    await init_account()
    logger.info("Starting strategies...")
    tasks = create_tasks_for_strategies()
    logger.info("All strategies are up and running")
    logger.info("Waiting while the strategies are running...")
    for task in tasks:
        await task

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt, shutting down...")
        exit(0)
