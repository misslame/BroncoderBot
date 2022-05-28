import discord
from discord import app_commands
from points_table.points import Points

from token_fetching.token_fetch import BOT_TOKEN

# Modules
from command_handling.submission_handler import handle_submission
from command_handling.rank_list_handler import format_rank_list
from points_table.points import Points

intenderinos = discord.Intents.default()
intenderinos.members = True
client = discord.Client(intents=intenderinos)
tree = app_commands.CommandTree(client)

@client.event
async def on_ready():
    print(f'Logged in as {client.user} (ID: {client.user.id})')
    Points.get_instance().init_points()
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
            #TODO: change to the difficulty value
            DIFFICULTY_POINT = 1 # TEMPORARY

            Points.get_instance().addPoints(interaction.user.id, DIFFICULTY_POINT)
            await interaction.channel.send(f'{interaction.user.mention} has submited their solution and recieved {DIFFICULTY_POINT} point(s)!') #TODO: add timestamp

            ''' ** TESTING ** '''
            await interaction.channel.send(f'{interaction.user.mention} now has {Points.get_instance().getPoints(interaction.user.id)} point(s)!')


@tree.command()
@app_commands.describe()
async def top10(interaction: discord.Interaction):
    await interaction.response.send_message(await format_rank_list(interaction, Points.get_instance().getTop(10),10))


client.run(BOT_TOKEN)