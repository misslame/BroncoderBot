import discord
from discord import Attachment, app_commands
from points_table.points import Points

from token_fetching.token_fetch import BOT_TOKEN

# Modules
from command_handling.submission_handler import handle_submission
from command_handling.rank_list_handler import format_rank_list
from command_handling import admin as admin_commands
from points_table.points import Points

intenderinos = discord.Intents.default()
intenderinos.members = True
client = discord.Client(intents=intenderinos)
tree = app_commands.CommandTree(client)

COOLDOWN_SECONDS = 60 * 5

@client.event
async def on_ready():
    print(f'Logged in as {client.user} (ID: {client.user.id})')
    await tree.sync()
    print('-------------------------------------')


@tree.command(description="Say hello.")
async def hello(interaction: discord.Interaction):
    await interaction.response.send_message(f'Hi, {interaction.user.mention}')


@tree.command(description="Enroll in competition.")
async def enroll(interaction: discord.Integration):
    role = discord.utils.get(interaction.guild.roles, name="Competition Reminders")
    await interaction.user.add_roles(role)
    await interaction.response.send_message(f'Added {interaction.user.mention} to competition')


@tree.command(description="Submit your code.")
@app_commands.describe(attachment="The code to submit", language="progamming language")
async def submit(interaction: discord.Interaction, attachment: discord.Attachment, language: str):
    await interaction.response.defer()
    successful_submission = await handle_submission(interaction, attachment, language)
    if (successful_submission):
        # TODO: change to the difficulty value
        DIFFICULTY_POINT = 1  # TEMPORARY

        Points.get_instance().addPoints(interaction.user.id, DIFFICULTY_POINT)
        # TODO: add timestamp

        # check cooldown
        # app_commands.checks.cooldown(1, COOLDOWN_SECONDS)

        await interaction.channel.send(
            f'{interaction.user.mention} has submited their solution and recieved {DIFFICULTY_POINT} point(s)!')

        ''' ** TESTING ** '''
        await interaction.channel.send(
            f'{interaction.user.mention} now has {Points.get_instance().getPoints(interaction.user.id)} point(s)!')

        return

@app_commands.checks.cooldown(1, COOLDOWN_SECONDS)
@tree.command(description="Test Submit Command.")
async def testsubmit(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    data = {'filename': 'TEST.py', 'id': 980005177400643624,
            'proxy_url': 'https://cdn.discordapp.com/attachments/979971398753742859/980005541902430238/TEST.py',
            'size': 17,
            'url': 'https://cdn.discordapp.com/attachments/979971398753742859/980005541902430238/TEST.py',
            'spoiler': False, 'content_type': 'text/x-python; charset=utf-8'}
    attachment, language = discord.Attachment(
        data=data, state=interaction.client._get_state()), "python"
    successful_submission = await handle_submission(interaction, attachment, language)

    if (successful_submission):
        # TODO: change to the difficulty value
        DIFFICULTY_POINT = 1  # TEMPORARY

        Points.get_instance().addPoints(interaction.user.id, DIFFICULTY_POINT)
        # TODO: add timestamp
        await interaction.channel.send(
            f'{interaction.user.mention} has submited their solution and recieved {DIFFICULTY_POINT} point(s)!')

        ''' ** TESTING ** '''
        await interaction.channel.send(
            f'{interaction.user.mention} now has {Points.get_instance().getPoints(interaction.user.id)} point(s)!')

        return


@tree.command(description="Returns the Top 10 Users.")
@app_commands.describe()
async def top10(interaction: discord.Interaction):
    await interaction.response.send_message(await format_rank_list(interaction, Points.get_instance().getTop(10), 10))


@tree.error
async def tree_errors(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.CommandOnCooldown):
        await interaction.response.send_message(
            f"You are on cooldown. Try again in {readable(int(error.cooldown.get_retry_after()))}", ephemeral=True)
    else:
        print(error)


def readable(seconds: int):
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = (seconds % 3600) % 60

    times = {"hour": h, "minute": m, "second": s}

    return " and ".join([f"{v} {k}{'s'[:v ^ 1]}" for k, v in times.items() if v])


Points.get_instance().init_points()
admin_commands.map_commands(tree)
client.run(BOT_TOKEN)
