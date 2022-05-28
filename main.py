import discord
from discord import app_commands

from token_fetching.token_fetch import BOT_TOKEN

# Modules
from submission_handling.submission_commands import handle_submission


intenderinos = discord.Intents.default()
client = discord.Client(intents=intenderinos)
tree = app_commands.CommandTree(client)

@client.event
async def on_ready():
    print(f'Logged in as {client.user} (ID: {client.user.id})')
    await tree.sync()
    print('-------------------------------------')

@tree.command()
async def hello(interaction: discord.Interaction):
    await interaction.response.send_message(f'Hi, {interaction.user.mention}')

@tree.command()
@app_commands.describe(attachment="The code to submit", language = "progamming language")
async def submit(interaction: discord.Interaction, attachment: discord.Attachment, language: str):
        successful_submission = await handle_submission(interaction, attachment, language)

        if(successful_submission):
            # Add points to the user
            await interaction.channel.send(f'{interaction.user.mention} has submited their solution!') #TODO: add timestamp

client.run(BOT_TOKEN)