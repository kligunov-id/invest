import logging
import asyncio

from abc import ABC, abstractmethod
from bot.client import client


class BaseStrategy(ABC):
    logger: logging.Logger
    account_id: str
    figi: str

    @abstractmethod
    def __init__(self, account_id: str, figi: str, *args, **kwargs):
        pass

    async def wait_until_market_open(self) -> None:
        self.logger.debug("Checking if the market is open...")
        while not await client.is_market_open(figi=self.figi):
            self.logger.info(f"Waiting for the market to open...")
            await asyncio.sleep(60)
        self.logger.debug("The market is open")
    
    async def wait_until_orders_executed(self) -> None:
        self.logger.debug("Checking if there are orders in progress")
        while await client.is_order_in_progress(account_id=self.account_id, figi=self.figi):
            self.logger.debug(f"Orders await execution...")
            await asyncio.sleep(1)
        self.logger.debug(f"Orders are executed")


    @abstractmethod
    async def update_model(self) -> None:
        pass

    @abstractmethod
    async def post_orders(self) -> None:
        pass

    async def run(self) -> None:
        while True:
            await self.wait_until_market_open()
            await self.wait_until_orders_executed()
            await self.update_model()
            await self.post_orders()
            await asyncio.sleep(10)
