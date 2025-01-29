import asyncio
from asyncio import Task
from typing import Coroutine, TypeVar

from pdrdb.db.implementation import DBContext, DB
from starlette.types import Receive
from starlette.types import Scope
from starlette.types import Send

T = TypeVar("T")


async def db_context_coroutine_task(task: Coroutine):
    token = DBContext.set(DB())
    await task
    DBContext.reset(token)
    return


def create_db_context_task(task: Coroutine[any, any, T]) -> Task[T]:
    """
    create a separate async task with separate db connection
    """
    return asyncio.get_running_loop().create_task(db_context_coroutine_task(task))


class DBContextMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope: 'Scope', receive: 'Receive', send: 'Send') -> None:
        if scope["type"] != "http":  # pragma: no cover
            await self.app(scope, receive, send)
            return

        return await db_context_coroutine_task(self.app(scope, receive, send))
