import logging
import asyncio

from typing import Optional

from bot.strategies.base import BaseStrategy
from bot.strategies.models import StrategyName
from bot.strategies.rsi.models import RSI_StrategyConfig

from bot.client import client

class RSI_Strategy(BaseStrategy):

    def __init__(self, account_id: str, figi: str, **kwargs):
        self.account_id = account_id
        self.figi = figi
        self.logger = logging.getLogger(StrategyName.RSI.value)
        self.config = RSI_StrategyConfig(**kwargs)
        self.rsi: Optional[float] = None

    def ema(self, array : list[float]) -> float:
        result = array[0]
        alpha = 2 / (len(array) + 1)
        for entry in array[1:]:
            result = (1 - alpha) * result + alpha * entry
        return result

    async def get_rs(self) -> float:
        close_prices = await client.get_close_prices(
            figi=self.figi,
            n=self.config.interval_length,
            candle_interval=self.config.candle_interval,
            )
        open_prices = await client.get_open_prices(
            figi=self.figi,
            n=self.config.interval_length,
            candle_interval=self.config.candle_interval,
            )
        up = [max(close_price - open_price, 0)
                for close_price, open_price in zip(close_prices, open_prices)]
        down = [max(open_price - close_price, 0)
                for close_price, open_price in zip(close_prices, open_prices)]
        return self.ema(up) / self.ema(down)

    def rs_to_rsi(self, rs: float) -> float:
        return 100 * (1 - 1 / (1 + rs))

    async def update_model(self) -> None:
        self.logger.debug("Evaluating RSI...")
        self.rsi = self.rs_to_rsi(await self.get_rs())
        self.logger.info(f"RSI is {self.rsi}")

    async def post_orders(self) -> None:
        self.logger.debug("Checking if we need to buy")
        if self.rsi < self.config.rsi_buy_treshold:
            self.logger.info("RSI is too low. Buying shares")
            await client.post_order_buy_all(account_id=self.account_id, figi=self.figi)
        if self.rsi > self.config.rsi_sell_treshold:
            self.logger.info("RSI is too high. Selling shares")
            await client.post_order_sell_all(account_id=self.account_id, figi=self.figi)
