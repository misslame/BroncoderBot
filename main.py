import discord
from discord import Attachment, app_commands
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
    await tree.sync()
    print('-------------------------------------')


@tree.command(description="Say hello.")
async def hello(interaction: discord.Interaction):
    await interaction.response.send_message(f'Hi, {interaction.user.mention}')


@tree.command(description="Submit your code.")
@app_commands.describe(attachment="The code to submit", language="progamming language")
async def submit(interaction: discord.Interaction, attachment: discord.Attachment, language: str):
    await interaction.response.defer()
    successful_submission = await handle_submission(interaction, attachment, language)
    if(successful_submission):
        # TODO: change to the difficulty value
        DIFFICULTY_POINT = 1  # TEMPORARY

        Points.get_instance().addPoints(interaction.user.id, DIFFICULTY_POINT)
        # TODO: add timestamp
        await interaction.channel.send(f'{interaction.user.mention} has submited their solution and recieved {DIFFICULTY_POINT} point(s)!')

        ''' ** TESTING ** '''
        await interaction.channel.send(f'{interaction.user.mention} now has {Points.get_instance().getPoints(interaction.user.id)} point(s)!')

        return


@tree.command(description="Test Submit Command.")
async def testsubmit(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    data = {'filename': 'TEST.py', 'id': 980005177400643624, 'proxy_url': 'https://cdn.discordapp.com/attachments/979971398753742859/980005541902430238/TEST.py', 'size': 17,
            'url': 'https://cdn.discordapp.com/attachments/979971398753742859/980005541902430238/TEST.py', 'spoiler': False, 'content_type': 'text/x-python; charset=utf-8'}
    attachment, language = discord.Attachment(
        data=data, state=interaction.client._get_state()), "python"
    successful_submission = await handle_submission(interaction, attachment, language)

    if(successful_submission):
        # TODO: change to the difficulty value
        DIFFICULTY_POINT = 1  # TEMPORARY

        Points.get_instance().addPoints(interaction.user.id, DIFFICULTY_POINT)
        # TODO: add timestamp
        await interaction.channel.send(f'{interaction.user.mention} has submited their solution and recieved {DIFFICULTY_POINT} point(s)!')

        ''' ** TESTING ** '''
        await interaction.channel.send(f'{interaction.user.mention} now has {Points.get_instance().getPoints(interaction.user.id)} point(s)!')

        return


@tree.command(description="Returns the Top 10 Users.")
@app_commands.describe()
async def top10(interaction: discord.Interaction):
    await interaction.response.send_message(await format_rank_list(interaction, Points.get_instance().getTop(10), 10))

Points.get_instance().init_points()
client.run(BOT_TOKEN)
