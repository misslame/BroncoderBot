import discord
from discord import app_commands

from persistent_store import PersistentStore

store = PersistentStore.get_instance()

@app_commands.command()
async def set_admin_role(interaction: discord.Interaction, role: discord.Role):
    guild_id = interaction.guild_id

    if guild_id not in store:
        guild_store = store[guild_id] = {}
    else:
        guild_store = store[guild_id]

    guild_store['admin_role'] = role.id
    store.update({guild_id: guild_store})

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
