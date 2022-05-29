from token_fetching.token_fetch import BOT_TOKEN
import os
import discord
from discord import app_commands
from discord.ext import commands
from submission_handling.selenium import setup, submitAttachmentToLeetcode
from messages.embeds import createSubmissionEmbed

intenderinos = discord.Intents.default()
client = discord.Client(intents=intenderinos)
tree = app_commands.CommandTree(client)

@client.event
async def on_connect():
    await setup()

@client.event
async def on_ready():
    print(f'Logged in as {client.user} (ID: {client.user.id})')
    await tree.sync()
    print('------')
    # testchannel = discord.utils.get(client.get_all_channels(), id=846269630838603796) 
    # await testchannel.send("_ _", embed=createSubmissionEmbed(color=0x00ff00, details={"result_state":"Success", "result_progress":"0 / 60"}))

@tree.command()
async def hello(interaction: discord.Interaction):
    await interaction.response.send_message(f'Hi, {interaction.user.mention}')

@tree.command()
@app_commands.describe(attachment="The code to submit")
async def submit(interaction: discord.Interaction, attachment: discord.Attachment):
    print("recieved submission")
    await interaction.response.send_message(f'Thanks for uploading {attachment.filename}!', ephemeral=True)
    await interaction.followup.send(f'The file uploaded was: {attachment.content_type}', ephemeral=True)
    submission = await submitAttachmentToLeetcode(attachment)
    # check if submission["err"] is true
    await interaction.followup.send(content="_ _", embed=createSubmissionEmbed(details=submission["details"], uploader_name=interaction.user.name))

client.run(BOT_TOKEN)