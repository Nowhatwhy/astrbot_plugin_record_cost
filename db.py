# db.py（SQLite 版本）
import datetime
from decimal import Decimal
from typing import List, Any
from sqlalchemy import create_engine, text
from .expenses import Expenses
from .querty_dto import QueryDTO

# -----------------------------
#  SQLite 数据库连接
# -----------------------------
engine = create_engine(
    "sqlite:///data/cost.db",  # ← 在当前目录生成 cost.db
    echo=False,
    connect_args={"check_same_thread": False}  # SQLite 线程限制关闭
)

def init_db():
    sql = """
    CREATE TABLE IF NOT EXISTS expenses (
        expense_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        category TEXT NOT NULL,
        title TEXT NOT NULL,
        amount REAL NOT NULL,
        expense_time TEXT NOT NULL,
        note TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
    """

    with engine.begin() as conn:
        conn.execute(text(sql))

# -----------------------------------
# 工具函数：把 DTO 转换为 SQL 参数 dict
# -----------------------------------
def _dto_to_params(query: QueryDTO) -> dict:
    params = {}

    for key, value in query.__dict__.items():
        if value is not None:
            params[key] = value

    return params


# --------------------------
# 查询函数（动态 SQL + DTO）
# --------------------------
def query_expenses(query: QueryDTO) -> List[Expenses]:

    base_sql = """
        SELECT
            expense_id, user_id, category, title, amount,
            expense_time, note, created_at, updated_at
        FROM expenses
        WHERE 1 = 1
    """

    params: dict[str, Any] = {}

    # --- 动态拼条件 ---
    for field, value in query.__dict__.items():
        if value is None:
            continue

        if field == "title_keyword":
            base_sql += " AND title LIKE :keyword"
            params["keyword"] = f"%{value}%"
        elif field == "min_amount":
            base_sql += " AND amount >= :min_amount"
            params["min_amount"] = value
        elif field == "max_amount":
            base_sql += " AND amount <= :max_amount"
            params["max_amount"] = value
        elif field == "start_time":
            base_sql += " AND expense_time >= :start_time"
            params["start_time"] = value
        elif field == "end_time":
            base_sql += " AND expense_time <= :end_time"
            params["end_time"] = value
        elif field in ["limit", "offset"]:
            continue
        else:
            base_sql += f" AND {field} = :{field}"
            params[field] = value

    # 排序 + 分页
    base_sql += " ORDER BY expense_time DESC"
    base_sql += " LIMIT :limit OFFSET :offset"

    params["limit"] = query.limit
    params["offset"] = query.offset

    with engine.connect() as conn:
        result = conn.execute(text(base_sql), params)
        rows = result.fetchall()

    return [Expenses(**row._mapping) for row in rows]


# -----------------------------
# 插入记录（使用实体 Expenses）
# -----------------------------
def insert_expense(exp: Expenses) -> int:

    # 不包含主键字段
    fields = [
        k for k in exp.__dict__.keys()
        if k != "expense_id" and exp.__dict__[k] is not None
    ]

    sql = (
        "INSERT INTO expenses (" +
        ", ".join(fields) +
        ") VALUES (" +
        ", ".join([f":{f}" for f in fields]) +
        ")"
    )

    params = {f: exp.__dict__.get(f) for f in fields}

    # 处理 datetime / decimal
    for k, v in params.items():
        if isinstance(v, datetime.datetime):
            params[k] = v.strftime("%Y-%m-%d %H:%M:%S")
        if isinstance(v, Decimal):
            params[k] = float(v)

    with engine.begin() as conn:
        result = conn.execute(text(sql), params)
        new_id = result.lastrowid

    return new_id


# -----------------------------
# 删除记录（安全：命名参数）
# -----------------------------
def delete_expenses(expense_ids: List[int], user_id: int) -> None:

    if not expense_ids:
        raise ValueError("delete_expenses: 空 ID 列表")

    placeholders = ", ".join(f":id{i}" for i in range(len(expense_ids)))

    sql = f"""
        DELETE FROM expenses
        WHERE expense_id IN ({placeholders})
          AND user_id = :user_id
    """

    params = {f"id{i}": eid for i, eid in enumerate(expense_ids)}
    params["user_id"] = user_id

    with engine.begin() as conn:
        conn.execute(text(sql), params)