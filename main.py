import asyncio
from datetime import datetime, time, timedelta
import discord
from discord import app_commands
from discord.ext import tasks

from points_table.points import Points

from token_fetching.token_fetch import BOT_TOKEN

# Modules
from points_table.points import Points
from command_handling.submission_handler import handle_submission
from command_handling.rank_list_handler import format_rank_list
from command_handling.first_handler import get_first_stats
from command_handling.timeout_handler import COOLDOWN_SECONDS, readable

intenderinos = discord.Intents.default()
intenderinos.members = True
client = discord.Client(intents=intenderinos)
tree = app_commands.CommandTree(client)

@client.event
async def on_ready():
    client.loop.create_task(called_once_a_day())
    print(f'Logged in as {client.user} (ID: {client.user.id})')
    await tree.sync()
    print('-------------------------------------')


''' **************************************************
    COMMANDS
    currently supported commands:
        * hello : Say hello.
        * submit : Submit your code.
        * top10: Provides the Top 10 members
        * top: Provides the Top given value members.
        * mypoints: Provides how many points you have.
        * first: Compares you with the first place member.
        * remindme: Enroll yourself in competition reminders.
        * stopreminders: Remove yourself from the competition reminders.

****************************************************'''

@tree.command(description="Say hello.")
async def hello(interaction: discord.Interaction):
    await interaction.response.send_message(f'Hi, {interaction.user.mention}')

@tree.command(description="Submit your code.")
@app_commands.checks.cooldown(1, COOLDOWN_SECONDS)
@app_commands.describe(attachment="The code to submit", language="progamming language")
async def submit(interaction: discord.Interaction, attachment: discord.Attachment, language: str):
    await interaction.response.defer()
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

@app_commands.checks.cooldown(1, COOLDOWN_SECONDS)
@tree.command(description="provides the Top 10 members.")
async def top10(interaction: discord.Interaction):
    await interaction.response.send_message(await format_rank_list(interaction, Points.get_instance().getTop(10), 10))

@app_commands.checks.cooldown(1, COOLDOWN_SECONDS)
@tree.command(description="Provides the Top given value members.")
@app_commands.describe(value="What number of the top members you want to see")
async def top(interaction: discord.Interaction, value: int):
    await interaction.response.send_message(await format_rank_list(interaction, Points.get_instance().getTop(value), value))

@app_commands.checks.cooldown(1, COOLDOWN_SECONDS)
@tree.command(description="Provides how many points you have.")
async def mypoints(interaction: discord.Interaction):
    await interaction.response.send_message(f'You currently have {Points.get_instance().getPoints(interaction.user.id)} point(s).')

@app_commands.checks.cooldown(1, COOLDOWN_SECONDS)
@tree.command(description="Compares you with the first place member.")
async def first(interaction: discord.Interaction):
    await interaction.response.defer()
    await interaction.followup.send(get_first_stats(interaction))

@tree.command(description="Enroll yourself in competition reminders.")
async def remindme(interaction: discord.Interaction):
    role = discord.utils.get(interaction.guild.roles, name="Broncoder")
    await interaction.user.add_roles(role)
    await interaction.response.send_message(f'Added {interaction.user.mention} to competition')

# only allow people in competitor role to call this
@tree.command(description="Remove yourself from the competition reminders.")
@app_commands.checks.cooldown(1, COOLDOWN_SECONDS)
@app_commands.checks.has_role("Broncoder")
# add error catch to not crash
async def stopreminders(interaction: discord.Interaction):
    comp_role = discord.utils.get(interaction.guild.roles, name="Broncoder")
    await interaction.user.remove_roles(comp_role)
    await interaction.response.send_message(f'Removed {interaction.user.mention} from the competition reminders')

@stopreminders.error
async def stopreminders_error(interaction: discord.Interaction, error: app_commands.MissingRole):
    if isinstance(error, app_commands.MissingRole):
        file = discord.File("./assets/mort.jpg")
        await interaction.response.send_message(f'{interaction.user.mention} does not have the reminder role.', file=file)

'''******************************************************
    ERROR HANDLING
******************************************************'''
@tree.error
async def tree_errors(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.CommandOnCooldown):
        await interaction.response.send_message(f"You are on cooldown. Try again in {readable(int(error.cooldown.get_retry_after()))}", ephemeral=True)

'''******************************************************
    ANNOUNCEMENT HANDLING
******************************************************'''

target_channel_id = 833465079559094312
WHEN = time(23, 34, 0)

today = datetime.now()


@tasks.loop(minutes=1)
async def called_once_a_day():
    global today
    today = today.replace(hour=22, minute=30, second=0)
    now = datetime.utcnow()
    message_channel = client.get_channel(target_channel_id)
    if now > today:
        print("now>today")
        await message_channel.send("useless scheduled announcement")
        today + timedelta(days=1)
    print(f"Got channel {message_channel}")
    await message_channel.send("useless scheduled announcement")


@called_once_a_day.before_loop
async def before():
    now = datetime.utcnow()
    target_time = datetime.combine(now.date(), WHEN)
    seconds_until_target = (target_time - now).total_seconds()
    await asyncio.sleep(seconds_until_target)
    await client.wait_until_ready()
    print("Finished waiting")

Points.get_instance().init_points()
client.run(BOT_TOKEN)