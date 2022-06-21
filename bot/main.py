import asyncio
import logging

from bot.settings import settings
from bot.client import client


logging.basicConfig(
    level=logging.DEBUG,
    format="[%(levelname)-5s] %(asctime)-19s %(name)s: %(message)s",
)

logger = logging.getLogger(__name__)

async def get_account_id() -> str:
    """ Chooses random avaible account or
    generates a new one if there is none avaible 
    :returns: String - account id
    """
    logger.info(f"Fetching accounts...")
    response = await client.get_accounts()
    if response.accounts:
        logger.info("Accounts found")
    else:
        logger.warning("No accounts found. Creating a new account")
        await client.open_sandbox_account()
        response = await client.get_accounts()
    return response.accounts[0].id    

async def main():
    logger.info("Initializing client...")
    await client.ainit()
    logger.info("Client initialized")
    account_id = await get_account_id()
    logger.info(f"Using account {account_id}")
    logger.info("Process finished")

if __name__ == "__main__":
    asyncio.run(main())
