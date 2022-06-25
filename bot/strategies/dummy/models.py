from pydantic import BaseModel

class DummyStrategyConfig(BaseModel):
    duration_of_dummy_operations_in_seconds: float = 0.3
    should_wait_until_market_open: bool = True
