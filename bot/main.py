import asyncio
import logging

from bot.settings import settings
from bot.client import client
from bot.strategy import 


logging.basicConfig(
    level=logging.DEBUG,
    format="[%(levelname)-5s] %(asctime)-19s %(name)s: %(message)s",
)

logger = logging.getLogger(__name__)

async def choose_account():
    await response = client.get_accounts()
    if (response.accounts).accounts:
        logger.info("Accounts found")
    else:
        logger.warning("No accounts found. Creating a new account")
        client.sandbox.open_sandbox_account()
        await response = client.get_accounts()

        

async def main():
    logger.info("Initializing client...")
    await client.ainit()
    logger.info("Client initialized")
    await choose_account()



if __name__ == "__main__":
    asyncio.run(main())
