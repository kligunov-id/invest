import logging

from abc import ABC, abstractmethod
from bot.client import client


class BaseStrategy(ABC):
    logger: logging.Logger
    account_id: str
    figi: str

    @abstractmethod
    def __init__(self, account_id: str, figi: str, *args, **kwargs):
        pass

    async def wait_until_market_open(self):
        self.logger.debug("Checking if the market is open...")
        trading_status = await client.get_trading_status(figi=self.figi)
        while not (
            trading_status.market_order_available_flag and trading_status.api_trade_available_flag
        ):
            self.logger.info(f"Waiting for the market to open...")
            await asyncio.sleep(60)
            trading_status = await client.get_trading_status(figi=self.figi)
        self.logger.debug("The market is open")

    @abstractmethod
    async def update_model(self):
        pass

    @abstractmethod
    async def post_orders(self):
        pass

    async def run(self):
        while True:
            await self.wait_until_market_open()
            await self.update_model()
            await self.post_orders()
