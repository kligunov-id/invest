import math

from tinkoff.invest import Quotation, MoneyValue


def quotation_to_float(quotation: Quotation) -> float:
    return float(quotation.units + quotation.nano / 1e9)

def float_to_quotation(f: float) -> Quotation:
    return Quotation(*math.modf(f))


def money_value_to_float(money_value: MoneyValue) -> float:
    return float(money_value.units + money_value.nano / 1e9)

def float_to_money_value(f: float, currency: str) -> MoneyValue:
    return MoneyValue(currency, *math.modf(f))
