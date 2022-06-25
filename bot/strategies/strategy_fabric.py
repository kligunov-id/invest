from typing import Dict

from bot.strategies.dummy.DummyStrategy import DummyStrategy
from bot.strategies.base import BaseStrategy
from bot.strategies.errors import UnsupportedStrategyError
from bot.strategies.models import StrategyName

strategies: Dict[StrategyName, BaseStrategy.__class__] = {
    StrategyName.DUMMY: DummyStrategy,
}


def construct_strategy(
                        strategy_name: StrategyName,
                        account_id: str,
                        figi: str,
                        *args,
                        **kwargs
                        ) -> BaseStrategy:
    """
    Creates strategy instance by strategy name. Passes all arguments to strategy constructor.
    """
    if strategy_name not in strategies:
        raise UnsupportedStrategyError(strategy_name)
    return strategies[strategy_name](account_id=account_id, figi=figi, *args, **kwargs)
