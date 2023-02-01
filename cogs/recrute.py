from aiosqlite import Connection, Cursor
from nextcord.ext.commands import Bot, Cog

from nextcord.ext import application_checks

from nextcord import *


class Recrute(Cog):
    def __init__(self, client: Bot) -> None:
        self.client = client
        client.loop.create_task(self.connect_db())

    async def connect_db(self):
        self.db: Connection = self.client.db
        self.curr: Cursor = await self.db.cursor()

    @Cog.listener()
    async def on_ready(self):
        return


def setup(client: Bot):
    client.add_cog(Recrute(client))
