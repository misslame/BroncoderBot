import discord
from discord import app_commands

from persistent_store import PersistentStore

store = PersistentStore.get_instance()

@app_commands.command()
async def set_admin_role(interaction: discord.Interaction, role: discord.Role):
    guild_id = interaction.guild_id
    store_key = str(guild_id) + '_admin_role'

    store[store_key] = role.id

    await interaction.response.send_message(f'Set admin role as {role.mention}', ephemeral=True)

@app_commands.command()
async def end_early(interaction: discord.Interaction):
    pass

@app_commands.command()
async def refresh_daily(interaction: discord.Interaction):
    pass

@app_commands.command()
async def refresh_status(interaction: discord.Interaction):
    pass

__all__ = [
    'set_admin_role', 'end_early', 'refresh_daily', 'refresh_status'
]
