from .querty_dto import QueryDTO
from . import db

def query_expenses_from_json(payload: dict) -> list[dict]:
    q = QueryDTO(**payload)              # JSON 一把塞进来
    expenses_list = db.query_expenses(q)    # 调 db
    return [e.to_dict() for e in expenses_list]

def main():
    db.init_db()
    sample_query = {
        "user_id": 1,
        "limit": 50,
        "offset": 0
    }
    results = query_expenses_from_json(sample_query)
    db.delete_expenses(expense_ids=[1], user_id=1)
    print(results)

if __name__ == "__main__":
    main()