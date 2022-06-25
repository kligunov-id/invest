import logging
import asyncio

from bot.strategies.base import BaseStrategy
from bot.strategies.models import StrategyName
from bot.strategies.dummy.models import DummyStrategyConfig

class DummyStrategy(BaseStrategy):

    def __init__(self, account_id: str, figi: str, **kwargs):
        self.account_id = account_id
        self.figi = figi
        self.logger = logging.getLogger(StrategyName.DUMMY.value)
        self.config = DummyStrategyConfig(**kwargs)

    async def wait_until_market_open(self):
        self.logger.info("Pretending to be waiting for the market to open...")
        await asyncio.sleep(self.config.duration_of_dummy_operations_in_seconds)

    async def update_model(self):
        self.logger.info("Pretending to be updating model...")
        await asyncio.sleep(self.config.duration_of_dummy_operations_in_seconds)

    async def post_orders(self):
        self.logger.info("Pretending to be posting orders...")
        await asyncio.sleep(self.config.duration_of_dummy_operations_in_seconds)
