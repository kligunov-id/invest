from datetime import timedelta
from tinkoff.invest import CandleInterval

class UnsupportedCandleInterval(Exception):
    def __init__(self, candle_interval: CandleInterval):
    	self.candle_interval = candle_interval

    def __str__(self):
    	return f"Candle interval {self.candle_interval.value} has no conversion to timedelta"


def interval_timedelta(candle_interval: CandleInterval) -> timedelta:
	if candle_interval is CandleInterval.CANDLE_INTERVAL_1_MIN:
		return timedelta(minutes=1)
	elif candle_interval is CandleInterval.CANDLE_INTERVAL_5_MIN:
		return timedelta(minutes=5)
	elif candle_interval is CandleInterval.CANDLE_INTERVAL_15_MIN:
		return timedelta(minutes=15)
	elif candle_interval is CandleInterval.CANDLE_INTERVAL_1_HOUR:
		return timedelta(hours=1)
	elif candle_interval is CandleInterval.CANDLE_INTERVAL_1_DAY:
		return timedelta(days=1)
	else:
		raise UnsupportedCandleInterval(candle_interval)
