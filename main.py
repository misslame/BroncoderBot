from token_fetching.token_fetch import BOT_TOKEN
import os
import discord
from discord import Embed, app_commands
from discord.ext import commands
from submission_handling.selenium import setup, submitAttachmentToLeetcode
from messages.embeds import createSubmissionEmbed, createProblemEmbed
from problem_fetching.problem_fetch import getRandomQuestion

intenderinos = discord.Intents.default()
client = discord.Client(intents=intenderinos)
tree = app_commands.CommandTree(client)


# eventually replace this with use of persistent store
class ChallengeOfTheDay:
    def __init__(self):
        self.question = {}
    
    def setQuestion(self, question):
        self.question = question

    def getQuestion(self):
        return self.question
challenge = ChallengeOfTheDay()


@client.event
async def on_connect():
    challenge.setQuestion(await getRandomQuestion())
    await setup(challenge.getQuestion())

@client.event
async def on_ready():
    print(f'Logged in as {client.user} (ID: {client.user.id})')
    await tree.sync()
    print('------')

@tree.command()
async def hello(interaction: discord.Interaction):
    await interaction.response.send_message(f'Hi, {interaction.user.mention}')

@tree.command()
@app_commands.describe(attachment="The code to submit")
async def submit(interaction: discord.Interaction, attachment: discord.Attachment):
    print("recieved submission")
    await interaction.response.send_message(f'Thanks for uploading {attachment.filename}!')
    await interaction.followup.send(f'The file uploaded was: {attachment.content_type}')
    submission = await submitAttachmentToLeetcode(attachment)
    if submission["err"]:
        await interaction.followup.send(embed=createSubmissionEmbed(msg=submission["msg"], uploader_name=interaction.user.name))
    elif not submission["err"]:
        await interaction.followup.send(embed=createSubmissionEmbed(details=submission["details"], uploader_name=interaction.user.name))

@tree.command()
@app_commands.describe()
async def cotd(interaction: discord.Interaction):
    await interaction.response.send_message(content="Today's challenge:", embed=createProblemEmbed(question=challenge.getQuestion()))

client.run(BOT_TOKEN)