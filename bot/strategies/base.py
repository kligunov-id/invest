from abc import ABC, abstractmethod


class BaseStrategy(ABC):
    @abstractmethod
    def __init__(self, account_id: str, figi: str, *args, **kwargs):
        pass

    @abstractmethod
    async def wait_until_market_open(self):
        pass

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
