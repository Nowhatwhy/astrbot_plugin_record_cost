from dataclasses import dataclass, asdict
from typing import Optional, Union
from datetime import datetime
from decimal import Decimal


@dataclass
class Expenses:
    expense_id: Optional[int] = None
    user_id: Optional[int] = None
    category: Optional[str] = None
    title: Optional[str] = None
    amount: Optional[Union[float, Decimal]] = None
    expense_time: Optional[Union[str, datetime]] = None
    note: Optional[str] = None
    created_at: Optional[Union[str, datetime]] = None
    updated_at: Optional[Union[str, datetime]] = None

    def to_dict(self):
        """把 datetime / Decimal 自动转换成可序列化格式"""
        d = asdict(self)

        # datetime → str
        for key in ["expense_time", "created_at", "updated_at"]:
            if isinstance(d[key], datetime):
                d[key] = d[key].isoformat(sep=" ")

        # Decimal → float
        if isinstance(d["amount"], Decimal):
            d["amount"] = float(d["amount"])

        return d