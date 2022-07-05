from pydantic import BaseModel
from tinkoff.invest import CandleInterval

class RSI_StrategyConfig(BaseModel):
    rsi_buy_treshold : float = 30
    rsi_sell_treshold : float = 70
    candle_interval : CandleInterval = CandleInterval.CANDLE_INTERVAL_1_MIN
    interval_length : int = 20
