# querty_dto.py
from dataclasses import dataclass, asdict
from typing import Optional

@dataclass
class QueryDTO:
    # 查询条件，全是可选
    user_id: Optional[int] = None
    category: Optional[str] = None
    title_keyword: Optional[str] = None  # 模糊匹配 title
    is_income: Optional[bool] = None
    min_amount: Optional[float] = None
    max_amount: Optional[float] = None
    start_time: Optional[str] = None     # '2025-10-01 00:00:00'
    end_time: Optional[str] = None       # '2025-11-01 00:00:00'
    limit: int = 100                     # 分页：每页多少条
    offset: int = 0                      # 分页：跳过多少条

    def to_dict(self):
        return asdict(self)