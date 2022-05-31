from token_fetching.token_fetch import BOT_TOKEN
import os
import discord
from discord import app_commands
from discord.ext import commands

intenderinos = discord.Intents.default()
client = discord.Client(intents=intenderinos)
tree = app_commands.CommandTree(client)


@client.event
async def on_ready():
    print(f"Logged in as {client.user} (ID: {client.user.id})")
    await tree.sync()
    print("------")


@tree.command()
async def hello(interaction: discord.Interaction):
    await interaction.response.send_message(f"Hi, {interaction.user.mention}")


@tree.command()
@app_commands.describe(attachment="The code to submit")
async def submit(interaction: discord.Interaction, attachment: discord.Attachment):
    await interaction.response.send_message(
        f"Thanks for uploading {attachment.filename}!", ephemeral=True
    )
    await interaction.channel.send_message(
        f"The file uploaded was: {attachment.content_type}"
    )


client.run(BOT_TOKEN)
