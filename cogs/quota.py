from aiosqlite import Connection, Cursor
from nextcord.ext.commands import Bot, Cog

from nextcord.ext import application_checks
from datetime import datetime
from nextcord import *


class Quota(Cog):
    def __init__(self, client: Bot) -> None:
        self.client = client
        client.loop.create_task(self.connect_db())

    async def connect_db(self):
        self.db: Connection = self.client.db
        self.curr: Cursor = await self.db.cursor()

    @Cog.listener()
    async def on_ready(self):
        await self.curr.execute(
            """CREATE TABLE IF NOT EXISTS "quotas" (
            
            memberid INTEGER NOT NULL,
            guildid INTEGER NOT NULL,
            quota INTEGER NOT NULL
            )"""
        )

    @slash_command(name="quota")
    async def quota(self, interaction: Interaction):
        return

    @quota.subcommand(name="add", description="ajouter aux quotas d'un membre")
    async def add_quota(self,interaction: Interaction, member: Member = SlashOption(name="membre", description="le membre auquel ajouter", required=True), amount: int = SlashOption(name="nombre", description="le nombre a ajouter", required=True)):

        await self.curr.execute(
            """SELECT quota FROM 'quotas' WHERE memberid=? AND guildid=?""",
            (member.id, interaction.guild_id),
        )

        quota = await self.curr.fetchone()

        if quota:
            await self.curr.execute(
                """UPDATE "quotas" SET quota=? WHERE memberid=? AND guildid=?""",
                (quota[0] + amount, member.id, interaction.guild_id),
            )
        else:
            await self.curr.execute(
                """INSERT INTO "quotas" VALUES (?,?,?)""",
                (member.id, interaction.guild_id, amount),
            )
            
        p = 's' if amount>1 else ''
        quotaAdded = Embed(title="Quota ajouté!", color=Color.green(), description=f":grapes: **{datetime.now().strftime('%d/%m/%Y')} : {amount} bouteille{p} de vin vendue{p} par {member.mention}.** :grapes:")
        await interaction.response.send_message(embed=quotaAdded)

        await self.db.commit()


    @quota.subcommand(name="set", description="definire les quota d'un membre")
    async def set_quota(self,interaction: Interaction, member: Member = SlashOption(name="membre", description="le membre auquel definire les quota", required=True), amount: int = SlashOption(name="nombre", description="le nombre a ajouter", required=True)):

        await self.curr.execute(
            """SELECT quota FROM 'quotas' WHERE memberid=? AND guildid=?""",
            (member.id, interaction.guild_id),
        )

        quota = await self.curr.fetchone()

        if quota:
            await self.curr.execute(
                """UPDATE "quotas" SET quota=? WHERE memberid=? AND guildid=?""",
                (amount, member.id, interaction.guild_id),
            )
        else:
            await self.curr.execute(
                """INSERT INTO "quotas" VALUES (?,?,?)""",
                (member.id, interaction.guild_id, amount),
            )

        p = 's' if amount>1 else ''
        quotaSat = Embed(title="Quota défini !", color=Color.green(), description=f":grapes: **{datetime.now().strftime('%d/%m/%Y')} : {amount} bouteille{p} de vin vendue{p} par {member.mention} .** :grapes:")
        await interaction.response.send_message(embed=quotaSat)

        await self.db.commit()


    @quota.subcommand(name="reset", description="réinitialiser un/les quota(s)")
    async def reset_quota(self,interaction: Interaction, member: Member = SlashOption(name="membre", description="le membre auquel réinitialiser", required=False)):
        if member:
            await self.curr.execute("""UPDATE 'quotas' SET quota=? WHERE memberid=? AND guildid=?""", (0, member.id, interaction.guild_id))
            
        else:
            await self.curr.execute("""UPDATE 'quotas' SET quota=? WHERE guildid=?""", (0, interaction.guild_id))

        resetEmbed = Embed(title=f"Quota{'s' if not member else ''} réinitialisé!", color=Color.green(), description=f"Vous avez mis à zéro {'la' if member else 'toutes les'} variable des bouteilles vendues {' '.join(['de', member.mention]) if member else ''}.")
        await interaction.response.send_message(embed=resetEmbed)

        await self.db.commit()


    @quota.subcommand(name="list", description="liste des quotas des membres")
    async def quota_list(self,interaction: Interaction):

        quotasliEmbed = Embed(title="Liste des Quotas", color=Color.green())

        valueLi = [0,1000,1500,3000,5000,10000]
        quotasLi=[[],[],[],[],[],[]]

        role = interaction.guild.get_role(1070124988599910520)

        for member in role.members:
            await self.curr.execute("""SELECT quota FROM 'quotas' WHERE memberid=? AND guildid=?""", (member.id, interaction.guild_id))
            response =  await self.curr.fetchone()
            quotas = response[0] if response else 0
 
            quotasLi[-1 if quotas>=10000 else -2 if quotas>=5000 else -3 if quotas>=3000 else -4 if quotas>=1500 else -5 if quotas>=1000 else -6].append(f"``{member.name}`` : {quotas} ")
            
        for li in quotasLi:
            value=valueLi[quotasLi.index(li)]
            if li:
                quotasliEmbed.add_field(name=f"{value}-{valueLi[quotasLi.index(li)+1]}" if value!=10000 else "10000+", value="\n".join(li), inline=False)

        await interaction.response.send_message(embed=quotasliEmbed)

    @slash_command(name="parain", description="parainer 2 employés")
    async def parain(self, interaction: Interaction, member1: Member = SlashOption(name="member1", description="le membre à parrainer", required=True), member2: Member = SlashOption(name="member2", description="le membre auquel parrainer", required=True)):

        parrainEmbed = Embed(title="Parrainage", description=f"L'employé {member1.mention} est devenu Parain de {member2.mention}. \nUne fois la période de parrainage dépassée celui-ci empochera **5 000$**.", color=Color.blue())

        await interaction.response.send_message(embed=parrainEmbed)

    @slash_command(name="promote", description="Promouvoir un employé")
    async def promote(self, interaction: Interaction, member: Member = SlashOption(name="member", description="le membre à parrainer", required=True)):

        promotionEmbed = Embed(title="Promotion!", description=f"L'employé {member.mention} a été promus par {interaction.user.mention}. Bravo à lui !.", color=Color.green())

        await interaction.response.send_message(embed=promotionEmbed)

def setup(client: Bot):
    client.add_cog(Quota(client))
