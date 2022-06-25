from pydantic import BaseModel

class DummyStrategyConfig(BaseModel):
    duration_of_dummy_operations_in_seconds: float = 0.3
