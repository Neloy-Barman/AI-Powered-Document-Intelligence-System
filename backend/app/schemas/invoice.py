from decimal import Decimal
from typing import Annotated, Optional

from pydantic import BaseModel, Field, PlainSerializer

# Money is stored as Decimal instead of float so monetary values keep exact
# two-decimal precision. float cannot preserve trailing zeros (1020.00 is
# serialized as 1020.0), so the serializer formats the value as a string with
# exactly two decimal places, e.g. Decimal("1020") -> "1020.00".
Money = Annotated[
    Decimal,
    PlainSerializer(lambda value: format(value, ".2f"), return_type=str),
]


class LineItem(BaseModel):
    description: Optional[str] = None
    quantity: Optional[float] = Field(
        default=None, json_schema_extra={"non_zero": True}
    )  # non_zero: True means a zero value is invalid for this field
    # unit_price: Optional[float] = None
    # amount: Optional[float] = None
    unit_price: Optional[Money] = Field(
        default=None, json_schema_extra={"non_zero": True}
    )  # non_zero: True means a zero value is invalid for this field
    amount: Optional[Money] = None


class Invoice(BaseModel):
    invoice_number: Optional[str] = None
    invoice_date: Optional[str] = None
    supplier_name: Optional[str] = None
    customer_name: Optional[str] = None
    # subtotal: Optional[float] = None
    # tax: Optional[float] = None
    # total: Optional[float] = None
    subtotal: Optional[Money] = None
    tax: Optional[Money] = None
    total: Optional[Money] = None
    currency: Optional[str] = None
    line_items: list[LineItem] = []
