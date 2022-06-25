from typing import Optional

from pydantic import BaseSettings
from bot.strategies.models import StrategyName

class Settings(BaseSettings):
    token: str
    sandbox: bool = True
    figi: str
    strategy_name: StrategyName
    account_id: Optional[str] = None
    
    class Config:
        env_file = ".env"


settings = Settings()
