import sys
import traceback
import discord
from discord import Color, Guild, Interaction, app_commands

from token_fetching.token_fetch import BOT_TOKEN

# Modules
from participant_data_handling.participant_data import ParticipantData
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
    print(f'Logged in as {client.user} (ID: {client.user.id})')
    # Get guild (server) using ID (find better way) - ADD FOR ALL
    # Need to update for our server
    guilds = client.guilds
    # [print(g) for g in guilds]
    for guild in guilds:
        role = discord.utils.get(guild.roles, name="Broncoder")
        # print(role)
        if role is None: # create role if DNE
            await guild.create_role(name="Broncoder", color=Color.brand_red())
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
        # TODO: THE FOLLOWING ATTRIBUTES
        DIFFICULTY = "hard"  # TEMPORARY
        WAS_FIRST_SUBMITION = False
        POINTS_RECIEVED = 3

        ParticipantData.get_instance().update_stats(interaction.user.id,  DIFFICULTY, POINTS_RECIEVED, WAS_FIRST_SUBMITION)
        # TODO: add timestamp
        await interaction.channel.send(
            f'{interaction.user.mention} has submited their solution and recieved {POINTS_RECIEVED} point(s)!')

        ''' ** TESTING ** '''
        await interaction.channel.send(
            f'{interaction.user.mention} now has {ParticipantData.get_instance().get_points(interaction.user.id)} point(s)!')

        return

@app_commands.checks.cooldown(1, COOLDOWN_SECONDS)
@tree.command(description="Test Submit Command.")
async def testsubmit(interaction: discord.Interaction):
    await interaction.response.defer()
    data = {'filename': 'TEST.py', 'id': 980005177400643624,
            'proxy_url': 'https://cdn.discordapp.com/attachments/979971398753742859/980005541902430238/TEST.py',
            'size': 17,
            'url': 'https://cdn.discordapp.com/attachments/979971398753742859/980005541902430238/TEST.py',
            'spoiler': False, 'content_type': 'text/x-python; charset=utf-8'}
    attachment, language = discord.Attachment(
        data=data, state=interaction.client._get_state()), "python"
    successful_submission = await handle_submission(interaction, attachment, language)

    if (successful_submission):
        # TODO: THE FOLLOWING ATTRIBUTES
        DIFFICULTY = "hard"  # TEMPORARY
        WAS_FIRST_SUBMITION = False
        POINTS_RECIEVED = 3

        ParticipantData.get_instance().update_stats(interaction.user.id,  DIFFICULTY, POINTS_RECIEVED,  WAS_FIRST_SUBMITION)
        # TODO: add timestamp
        await interaction.channel.send(
            f'{interaction.user.mention} has submited their solution and recieved {POINTS_RECIEVED} point(s)!')

        ''' ** TESTING ** '''
        await interaction.channel.send(
            f'{interaction.user.mention} now has {ParticipantData.get_instance().get_points(interaction.user.id)} point(s)!')

        return

@app_commands.checks.cooldown(1, COOLDOWN_SECONDS)
@tree.command(description="provides the Top 10 members.")
async def top10(interaction: discord.Interaction):
    await interaction.response.send_message(await format_rank_list(interaction, ParticipantData.get_instance().get_top(10), 10))

@app_commands.checks.cooldown(1, COOLDOWN_SECONDS)
@tree.command(description="Provides the Top given value members.")
@app_commands.describe(value="What number of the top members you want to see")
async def top(interaction: discord.Interaction, value: int):
    await interaction.response.send_message(await format_rank_list(interaction, ParticipantData.get_instance().get_top(value), value))

@app_commands.checks.cooldown(1, COOLDOWN_SECONDS)
@tree.command(description="Provides how many points you have.")
async def mypoints(interaction: discord.Interaction):
    await interaction.response.send_message(f'You currently have {ParticipantData.get_instance().get_points(interaction.user.id)} point(s).')

@app_commands.checks.cooldown(1, COOLDOWN_SECONDS)
@tree.command(description="Compares you with the first place member.")
async def first(interaction: discord.Interaction):
    await interaction.response.defer()
    await interaction.followup.send(get_first_stats(interaction))

@tree.command(description="Enroll yourself in competition reminders.")
@app_commands.checks.cooldown(1, COOLDOWN_SECONDS)
async def remindme(interaction: discord.Interaction):
    if('Broncoder' in [u.name for u in interaction.user.roles]):
        # Add file?
        await interaction.response.send_message(f'{interaction.user.mention} already has the role assigned')
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

@tree.command(description="Display your personal stats")
async def get_stats(interaction: discord.Interaction):
    await interaction.response.defer()
    
    ParticipantData.get_instance().add_participant(interaction.user.id)
    await interaction.followup.send(f'{interaction.user.mention} stats:' + ParticipantData.get_instance().get_participant_printed_stats(interaction.user.id))

'''******************************************************
    ERROR HANDLING
******************************************************'''
@tree.error
async def tree_errors(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.CommandOnCooldown):
        await interaction.response.send_message(f"You are on cooldown. Try again in {readable(int(error.cooldown.get_retry_after()))}", ephemeral=True)
    else:
        print('Ignoring exception in command {}:'.format(interaction.command), file=sys.stderr)
        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

@stopreminders.error
async def stopreminders_error(interaction: discord.Interaction, error: app_commands.MissingRole):
    if isinstance(error, app_commands.MissingRole):
        file = discord.File("./assets/BroncoBonk.png")
        await interaction.response.send_message(f'{interaction.user.mention} does not have the reminder role.', file=file)

ParticipantData.get_instance().init_points()
client.run(BOT_TOKEN)
