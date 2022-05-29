from importlib import import_module

import discord

from ..admin import commands
from persistent_store import PersistentStore

store = PersistentStore.get_instance()

async def __admin_only(interaction: discord.Interaction):
    guild_id = interaction.guild_id
    store_key = str(guild_id) + '_admin_role'

    # Defaults to administrator permissions if no admin role assigned
    if not store_key in store:
        if interaction.user.resolved_permissions.administrator:
            return True
    elif interaction.guild.get_role(store[store_key]) in interaction.user.roles:
        return True

    await interaction.response.send_message('Admin role required to invoke this command', ephemeral=True)
    return False

def map_commands(tree):
    for cmd in [getattr(commands, name) for name in commands.__all__]:
        cmd.add_check(__admin_only)
        tree.add_command(cmd)
