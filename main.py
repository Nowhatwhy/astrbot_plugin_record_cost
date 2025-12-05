from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star, register
from astrbot.api import logger

from . import db
from .expenses import Expenses
from .querty_dto import QueryDTO
from datetime import datetime
# 处理收入支出

@register("astrbot_plugin_record_cost", "Nowhatwhy", "可以让你的机器人给你记录每日开销", "1.0.0")
class MyPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)

    async def initialize(self):
        """可选择实现异步的插件初始化方法，当实例化该插件类之后会自动调用该方法。"""
        db.init_db()

    @filter.llm_tool(name="query_expenses")
    async def query_expenses_tool(
        self, 
        event: AstrMessageEvent, 
        query: dict
    ):
        '''查询记录。

        Args:
            query(object): 查询条件对象，字段包括：
                - category(string): 类别（餐饮/零食/日用/购物/交通/饮品/水果/服饰/娱乐/住房/人情/通许/医疗/学习/工资/奖金/红包/转账/其他，可选）
                - title_keyword(string): 标题关键字（可选）
                - is_income(boolean): 是否是收入
                - min_amount(number): 最小金额（可选）
                - max_amount(number): 最大金额（可选）
                - start_time(string): 开始时间（YYYY-MM-DD HH:MM:SS，可选）
                - end_time(string): 结束时间（YYYY-MM-DD HH:MM:SS，可选）
                - limit(number): 返回条数限制（默认100）
                - offset(number): 分页偏移量（默认0）
        '''
        user_id = event.get_sender_id()
        query["user_id"] = user_id
        dto = QueryDTO(**query)
        records = db.query_expenses(dto)
        record_list = [str(r) for r in records]
        return record_list

    @filter.llm_tool(name="insert_expense")
    async def insert_expense_tool(
        self, 
        event: AstrMessageEvent, 
        expense: dict
    ):
        '''插入一条记录。

        Args:
            expense(object): 记录对象，字段包括：
                - category(string): 类别（餐饮/零食/日用/购物/交通/饮品/水果/服饰/娱乐/住房/人情/通许/医疗/学习/工资/奖金/红包/转账/其他）
                - is_income(boolean): 是否是收入
                - title(string): 标题
                - amount(number): 金额
                - expense_time(string): 时间（YYYY-MM-DD HH:MM:SS）
                - note(string): 备注（可选）
        '''
        user_id = event.get_sender_id()
        expense["user_id"] = user_id
        expense_obj = Expenses(**expense)
        new_id = db.insert_expense(expense_obj)
        return {"编号": new_id}

    @filter.llm_tool(name="delete_expenses")
    async def delete_expenses_tool(
        self, 
        event: AstrMessageEvent, 
        expense_ids: list[int]
    ):
        '''删除指定的记录。

        Args:
            expense_ids(array): 要删除的记录 ID 列表
        '''
        user_id = event.get_sender_id()
        db.delete_expenses(expense_ids, int(user_id))
        return {"status": "success"}

    @filter.llm_tool(name="update_expense")
    async def update_expense_tool(
        self, 
        event: AstrMessageEvent, 
        expense: dict
    ):
        '''更新一条记录，根据 expense_id 定位，其他字段为要更新的内容。

        Args:
            expense(object): 记录对象，字段包括：
                - expense_id(number): 编号
                - category(string): 类别（餐饮/零食/日用/购物/交通/饮品/水果/服饰/娱乐/住房/人情/通许/医疗/学习/工资/奖金/红包/转账/其他，可选）
                - is_income(boolean): 是否是收入（可选）
                - title(string): 标题（可选）
                - amount(number): 金额（可选）
                - expense_time(string): 时间（YYYY-MM-DD HH:MM:SS，可选）
                - note(string): 备注（可选）
        '''
        user_id = event.get_sender_id()
        expense["user_id"] = user_id
        expense_obj = Expenses(**expense)
        db.update_expense(expense_obj)
        return {"status": "success"}

    @filter.command("记录开销")
    async def record_cost(self, event: AstrMessageEvent):
        """这是一个记录开销指令"""
        user_name = event.get_sender_name()
        message_str = event.message_str
        message_chain = event.get_messages()
        logger.info(message_chain)
        yield event.plain_result(f"记录开销: {user_name}, 你发了 {message_str}!")

    @filter.command("terminate")
    async def terminate(self):
        """可选择实现异步的插件销毁方法，当插件被卸载/停用时会调用。"""
