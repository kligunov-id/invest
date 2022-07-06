from datetime import datetime
from typing import Optional, List
from uuid import uuid4

from tinkoff.invest import (
    AsyncClient,
    Account,
    CandleInterval,
    Quotation,
    Order,
    OrderDirection,
    OrderType,
    OrderState,
    PostOrderResponse,
    GetLastPricesResponse,
    GetTradingStatusResponse,
    OpenSandboxAccountResponse,
    CandleInterval,
    HistoricCandle,
    InstrumentIdType,
    SandboxPayInResponse,
)
from tinkoff.invest.grpc.orders_pb2 import (
    ORDER_DIRECTION_SELL,
    ORDER_DIRECTION_BUY,
    ORDER_TYPE_MARKET,
)
from tinkoff.invest.utils import now
from tinkoff.invest.async_services import AsyncServices

from bot.settings import settings
from bot.utils.money_converter import (
    quotation_to_float,
    float_to_quotation,
    money_value_to_float,
    float_to_money_value
)
from bot.utils.candle_interval import interval_timedelta


class ServiceAutoSelectorClient:
    """
    Wrapper for tinkoff.invest.AsyncClient.
    Automatically chooses the right service to call
    """

    def __init__(self, token: str, sandbox: bool = False):
        self.token = token
        self.sandbox = sandbox
        self.client: Optional[AsyncServices] = None

    async def ainit(self):
        self.client = await AsyncClient(token=self.token, app_name="invest_bot").__aenter__()

    async def get_orders(self, **kwargs):
        if self.sandbox:
            return await self.client.sandbox.get_sandbox_orders(**kwargs)
        return await self.client.orders.get_orders(**kwargs)

    async def get_portfolio(self, **kwargs):
        if self.sandbox:
            return await self.client.sandbox.get_sandbox_portfolio(**kwargs)
        return await self.client.operations.get_portfolio(**kwargs)

    async def get_positions(self, **kwargs):
        if self.sandbox:
            return await self.client.sandbox.get_sandbox_positions(**kwargs)
        return await self.client.operations.get_positions(**kwargs)

    async def get_accounts(self):
        if self.sandbox:
            return await self.client.sandbox.get_sandbox_accounts()
        return await self.client.users.get_accounts()

    async def get_all_candles(self, **kwargs):
        async for candle in self.client.get_all_candles(**kwargs):
            yield candle

    async def get_last_prices(self, **kwargs) -> GetLastPricesResponse:
        return await self.client.market_data.get_last_prices(**kwargs)

    async def post_order(self, **kwargs) -> PostOrderResponse:
        if self.sandbox:
            return await self.client.sandbox.post_sandbox_order(**kwargs)
        return await self.client.orders.post_order(**kwargs)

    async def get_order_state(self, **kwargs) -> OrderState:
        if self.sandbox:
            return await self.client.sandbox.get_sandbox_order_state(**kwargs)
        return await self.client.orders.get_order_state(**kwargs)

    async def get_trading_status(self, **kwargs) -> GetTradingStatusResponse:
        return await self.client.market_data.get_trading_status(**kwargs)
    
    async def sandbox_pay_in(self, **kwargs) -> SandboxPayInResponse:
        return await self.client.sandbox.sandbox_pay_in(**kwargs)

    async def open_sandbox_account(self) -> None:
        await self.client.sandbox.open_sandbox_account()
    
    async def get_instrument_by(self, **kwargs):
        return await self.client.instruments.get_instrument_by(**kwargs)

class ClientAdapter:
    """ Wrapper for ServiceAutoSelectorClient implementing higher-level functionality """

    def __init__(self, token: str, sandbox: bool = False):
        self.client = ServiceAutoSelectorClient(token, sandbox)

    async def ainit(self) -> None:
        await self.client.ainit()


    async def open_sandbox_account(self) -> None:
        await self.client.open_sandbox_account()
    
    async def get_accounts(self) -> list[Account]:
        return (await self.client.get_accounts()).accounts


    async def is_market_open(self, figi: str) -> bool:
        trading_status = await self.client.get_trading_status(figi=figi)
        return (trading_status.market_order_available_flag
            and trading_status.api_trade_available_flag)


    async def get_orders(self, account_id: str, figi: str) -> list[Order]:
        orders = []
        for order in (await self.client.get_orders(account_id=account_id)).orders:
            if order.figi == figi:
                orders.append(order)
        return orders

    async def is_order_in_progress(self, account_id: str, figi: str) -> bool:
        return bool(await self.get_orders(account_id=account_id, figi=figi))


    async def post_order_sell(self, account_id: str, figi: str, quantity_lots: int) -> None:
        if quantity_lots <= 0:
            return
        await self.client.post_order(
                    order_id=str(uuid4()),
                    figi=figi,
                    direction=ORDER_DIRECTION_SELL,
                    quantity=quantity_lots,
                    order_type=ORDER_TYPE_MARKET,
                    account_id=account_id,
                )

    async def post_order_buy(self, account_id: str, figi: str, quantity_lots: int) -> None:
        if quantity_lots <= 0:
            return
        await self.client.post_order(
                    order_id=str(uuid4()),
                    figi=figi,
                    direction=ORDER_DIRECTION_BUY,
                    quantity=quantity_lots,
                    order_type=ORDER_TYPE_MARKET,
                    account_id=account_id,
                )

    async def post_order_sell_all(self, account_id: str, figi: str) -> None:
        quantity_lots = await self.get_postition_quantity_lots(account_id, figi)
        await self.post_order_sell(account_id, figi, quantity_lots)

    async def post_order_buy_all(self, account_id: str, figi: str) -> None:
        """ Warning: when price spikes this method can force to buy more than actually can """
        shares_max = await self.get_money_balance(account_id) / await self.get_last_price(figi)
        lot_max = int(shares_max / await self.get_lot_size(figi))
        await self.post_order_buy(account_id, figi, lot_max)

    async def get_last_price(self, figi: str) -> float:
        # API method expects figi to be array of figi-s
        # We wrap figi in an array here because
        # otherwise will be treated as an array of one-letter figi-s
        last_price_entry =  (await self.client.get_last_prices(figi=[figi])).last_prices[0]
        return quotation_to_float(last_price_entry.price)
    
    async def get_candles(
        self, figi: str, n: int,
        candle_interval: CandleInterval=CandleInterval.CANDLE_INTERVAL_1_MIN,
        ) -> list[HistoricCandle]:
        candles = []
        time_now = now()
        async for candle in self.client.get_all_candles(
                figi=figi,
                from_=time_now - n * interval_timedelta(candle_interval),
                to = time_now,
                interval=candle_interval
            ):
            candles.append(candle)
        return candles

    async def get_close_prices(
        self, figi: str, n: int,
        candle_interval: CandleInterval=CandleInterval.CANDLE_INTERVAL_1_MIN,
        ) -> list[float]:
        candles = await self.get_candles(figi, n, candle_interval)
        return [quotation_to_float(candle.close) for candle in candles]

    async def get_open_prices(
        self, figi: str, n: int,
        candle_interval: CandleInterval=CandleInterval.CANDLE_INTERVAL_1_MIN,
        ) -> list[float]:
        candles = await self.get_candles(figi, n, candle_interval)
        return [quotation_to_float(candle.open) for candle in candles]

    async def get_money_balance(self, account_id: str, currency: str="rub") -> float:
        money_positions = (await self.client.get_positions(account_id=account_id)).money
        for money_value in money_positions:
            if money_value.currency == currency:
                return money_value_to_float(money_value)
        return 0
    
    async def sandbox_pay_in(self, account_id: str, amount: float, currency: str="rub") -> None:
        if amount < 0:
            return
        amount_money_value = float_to_money_value(amount, currency)
        await self.client.sandbox_pay_in(account_id=account_id, amount=amount_money_value)

    async def sandbox_withdraw(self, account_id: str, ammount: float, currency: str="rub") -> None:
        await self.sandbox_pay_in(account_id, - amount, currency)


    async def get_postition_quantity_lots(self, account_id: str, figi: str) -> int:
        instruments = (await self.client.get_positions(account_id=account_id)).securities
        for position in instruments:
            if position.figi == figi:
                return int(position.balance / await self.get_lot_size(figi=figi))
        return 0


    async def get_lot_size(self, figi: str) -> int:
        response = await self.client.get_instrument_by(
            id=figi, id_type=InstrumentIdType.INSTRUMENT_ID_TYPE_FIGI
            )
        return response.instrument.lot

client = ClientAdapter(token=settings.token, sandbox=settings.sandbox)
