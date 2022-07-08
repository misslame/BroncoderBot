import sys
import traceback
import discord
from discord import Attachment, Color, Embed, Guild, Interaction, app_commands
from typing import Literal
import datetime
from datetime import date, time
from discord.ext import tasks
import random

# IMPORTED CONSTANTS:
from config.config import BOT_TOKEN
from command_handling.timeout_handler import COOLDOWN_SECONDS
from command_handling.announcement_handler import DAILY_ANNOUNCEMENT_TIME
from command_handling.announcement_handler import END_COMPETITION_ANNOUNCEMENT_TIME

# MODULES:
# -------- Command Handling -----------
from command_handling.submission_handler import handle_submission
from command_handling.rank_list_handler import format_rank_list
from command_handling.first_handler import get_first_stats
from command_handling.timeout_handler import readable
from command_handling.announcement_handler import (
    get_announcement_message,
    get_end_announcement_message,
    randomize_cotd,
)
from command_handling import admin as admin_commands

# -------- Problem Submission ---------
from messages.problem_view import ProblemView
from messages.embeds import createSubmissionEmbed, createProblemEmbed, getProblemEmbeds
from problem_fetching.problem_fetch import getRandomQuestion, getQuestionByTitleSlug
from submission_handling.selenium import setup, submitAttachmentToLeetcode

# -------- Statistics & Storage --------
from participant_data_handling.participant_data import ParticipantData
from persistent_store import PersistentStore

from messages.channel_config_view import ChannelConfigView

"""****************************************************
    Bot Connect & Set Up
****************************************************"""

intenderinos = discord.Intents.default()
intenderinos.members = True

activity = discord.activity.Activity(
    type=discord.ActivityType.competing, name="Leetcode"
)

client = discord.Client(intents=intenderinos, activity=activity)
tree = app_commands.CommandTree(client)
store = PersistentStore.get_instance()


@client.event
async def on_connect():  # Before on_ready
    if "first_submission" not in store:
        store.__setitem__("first_submission", False)
    if "announcement_channel_id" not in store:
        store.__setitem__("announcement_channel_id", 0)
        store.__setitem__("submission_channel_id", 0)
    if "cotd" not in store:
        print("No existing COTD found, making a new one...")
        store["cotd"] = {}
        challenge = await getRandomQuestion()
        store.update({"cotd": challenge})
        title = store["cotd"]["title"]
        print(f'"{title}" is the new COTD!')
    else:
        title = store["cotd"]["title"]
        print(f'"{title}" is the current COTD!')
    await setup(store["cotd"])


@client.event
async def on_ready():
    print(f"Logged in as {client.user} (ID: {client.user.id})")
    # Get guild (server) using ID (find better way) - ADD FOR ALL
    # Need to update for our server
    guilds = client.guilds
    # [print(g) for g in guilds]
    for guild in guilds:
        role = discord.utils.get(guild.roles, name="Broncoder")
        # print(role)
        if role is None:  # create role if DNE
            await guild.create_role(name="Broncoder", color=Color.brand_red())
    await tree.sync()
    print("-------------------------------------")
    daily_announcement.start()


@client.event
async def on_guild_join(guild: Guild):
    default_announcement_msg = discord.Embed(
        title="BroncoderBot Announcements ",
        description="This is the default channel for BroncoderBot announcements. To change this channel, use `/configure_bot_channels`",
        color=discord.Color.from_str("#FFB500"),
    )
    default_announcement_msg.set_thumbnail(url=client.user.avatar.url)

    store.update({"announcement_channel_id": guild.text_channels[0].id})
    await guild.text_channels[0].send(embed=default_announcement_msg)


""" **************************************************
    COMMANDS
    currently supported commands:
        ---------------------------
        FUN
        * hello : Say hello.

        ---------------------------
        PROBLEM SUBMISSION
        * current_challenge : See today\'s problem.
        * submit : Submit your code to be tested and judged.

        ---------------------------
        STATS
        * top: Provides the Top given value members.
        * top10: Provides the Top 10 members
        * mypoints: Provides how many points you have.
        * first: Compares you with the first place member.
        * get_stats: Display your personal stats.

        ---------------------------
        UTILITY
        * rules: Provides the rules and instructions to use the bot for the competition.
        * supported_commands: Provides a list of supported non admin commands.
        * remindme: Enroll yourself in competition reminders.
        * stopreminders: Remove yourself from the competition reminders.

****************************************************"""

""" ---------- FUN ---------- """

greeting = [
    "greeting",
    "aloha",
    "good afternoon",
    "good day",
    "good evening",
    "good morning",
    "good night",
    "greetings",
    "guten Tag",
    "hello",
    "hey",
    "hola",
    "how's it going?",
    "how's it hanging?",
    "konnichi wa",
    "saulutions",
    "sup",
    "what's happening?",
    "what's new?",
    "what's up?",
    "whazzup!!!",
    "yo holla how do?",
    "how goes it?",
    "how ya doing?",
    "sup",
    "sup, b?",
    "what's cooking?",
    "what's crack-a-lackin",
    "what's cracking?",
    "What's in the bag?",
    "what's popping",
    "what's shaking?",
    "what's the dizzle?",
    "what's the haps?",
    "what's the rumpus?",
    "what's up?",
    "yello",
]


@tree.command(description="Say hello.")
@app_commands.checks.cooldown(1, 1)
async def hello(interaction: discord.Interaction):
    await check_submission_channel()
    entry = random.randrange(0, len(greeting) - 1)
    await interaction.response.send_message(
        f"{greeting[entry]} {interaction.user.mention}"
    )


""" ---------- PROBLEM SUBMISSION ---------- """


@tree.command(description="See today's problem.")
@app_commands.checks.cooldown(1, COOLDOWN_SECONDS)
async def current_challenge(interaction: discord.Interaction):
    await check_submission_channel()
    embeds = getProblemEmbeds(store["cotd"])

    await interaction.response.send_message(
        content="Today's challenge:",
        embed=embeds.get("info"),
        view=ProblemView(embeds, None, interaction.user.id),
    )


@tree.command(description="Submit your code to be tested and judged.")
@app_commands.checks.cooldown(1, COOLDOWN_SECONDS)
@app_commands.describe(attachment="The code to submit", language="Programming language")
async def submit(
    interaction: discord.Interaction,
    attachment: discord.Attachment,
    language: Literal[
        "C++",
        "Java",
        "Python",
        "Python3",
        "C",
        "C#",
        "JavaScript",
        "Ruby",
        "Swift",
        "Go",
        "Scala",
        "Kotlin",
        "Rust",
        "PHP",
        "TypeScript",
        "Racket",
        "Erlang",
        "Elixir",
    ],
):
    await check_submission_channel()
    submission = await handle_submission(interaction, attachment, language)

    response_message = f"Thanks for uploading, {interaction.user.display_name}! Received {language} file: {attachment.filename}."

    DIFFICULTIES = {"Easy": 1, "Medium": 2, "Hard": 3}

    if not submission.get("err"):
        difficulty_str = store["cotd"]["difficulty"]
        points = DIFFICULTIES[difficulty_str]
        BONUS_POINTS = 1
        was_first_submission = False

        completion_percent = submission.get("details").get("result_progress_percent")

        status = submission.get("details").get("result_state")

        embed = createSubmissionEmbed(
            details=submission["details"], uploader_name=interaction.user.name
        )

        if status == "Accepted":
            if store.__getitem__("first_submission") == False:
                was_first_submission = True
                store.update({"first_submission": True})
                points += BONUS_POINTS
                response_message += "\n**Congrats, you're the first person to submit! Here's an additional bonus point!**"

            ParticipantData.get_instance().update_stats(
                interaction.user.id, difficulty_str, points, was_first_submission
            )
            p = ParticipantData.get_instance().get_points(interaction.user.id)

            # TODO: add timestamp
            await interaction.edit_original_message(
                content=response_message + "\n\n"
                f"{interaction.user.mention} has submitted their solution and received {points} point{'s'[:points ^ 1]}!\n"
                f"{interaction.user.mention} now has {p} point{'s'[:p ^ 1]}!",
                embed=embed,
            )
        else:
            await interaction.edit_original_message(
                content=response_message, embed=embed
            )
    else:
        await interaction.followup.send(
            content="",
            embed=createSubmissionEmbed(
                msg=submission["msg"], uploader_name=interaction.user.name
            ),
        )


""" ---------- STATS ---------- """


@app_commands.checks.cooldown(1, COOLDOWN_SECONDS)
@tree.command(description="Provides the Top given value members.")
@app_commands.describe(value="What number of the top members you want to see")
async def top(interaction: discord.Interaction, value: int):
    await check_submission_channel()
    await interaction.response.send_message(
        await format_rank_list(
            interaction, ParticipantData.get_instance().get_top(value), value
        )
    )


@app_commands.checks.cooldown(1, COOLDOWN_SECONDS)
@tree.command(description="provides the Top 10 members.")
async def top10(interaction: discord.Interaction):
    await check_submission_channel()
    await interaction.response.send_message(
        await format_rank_list(
            interaction, ParticipantData.get_instance().get_top(10), 10
        )
    )


@app_commands.checks.cooldown(1, COOLDOWN_SECONDS)
@tree.command(description="Provides how many points you have.")
async def mypoints(interaction: discord.Interaction):
    await check_submission_channel()
    await interaction.response.send_message(
        f"You currently have {ParticipantData.get_instance().get_points(interaction.user.id)} point(s)."
    )


@app_commands.checks.cooldown(1, COOLDOWN_SECONDS)
@tree.command(description="Compares you with the first place member.")
async def first(interaction: discord.Interaction):
    await check_submission_channel()
    await interaction.followup.send(get_first_stats(interaction))


@tree.command(description="Display your personal stats.")
async def get_stats(interaction: discord.Interaction):
    await check_submission_channel()

    ParticipantData.get_instance().add_participant(interaction.user.id)
    participant_stats_embed = discord.Embed(
        title=f"{interaction.user.display_name}'s Stats:",
        description=ParticipantData.get_instance().get_participant_printed_stats(
            interaction.user.id
        ),
        color=discord.Color.from_str("#FFB500"),
    )
    participant_stats_embed.set_thumbnail(url=interaction.user.display_avatar.url)
    participant_stats_embed.add_field(
        name="Badge",
        value=ParticipantData.get_instance().get_badge(interaction.user.id),
    )

    await interaction.followup.send(embed=participant_stats_embed)


""" ---------- UTILITY ---------- """


@tree.command(
    description="Provides the rules and instructions to use the bot for the competition."
)
@app_commands.checks.cooldown(1, COOLDOWN_SECONDS)
async def rules(interaction: discord.Interaction):
    await interaction.response.send_message(
        f'**Rules**\n---------\n • Please partricipate in good faith. Don\'t cheat! This competition is to help you improve on your leetcode skills and facilitate fun in our server. If you cheat you are defeating the purpose.\n\n • Challenges are posted at {DAILY_ANNOUNCEMENT_TIME.strftime("%I : %M %p")} in the announcement channel.\n\n • Submit solution files either through DM to me or in the submission channel through the /submit command.\n\n • Opt in to reminder pings through the /remindme command and opt out through the /stopreminders command.\n\n\n ***Happy Trotting Broncoder!***'
    )


@tree.command(description="Provides a list of supported non admin commands.")
@app_commands.checks.cooldown(1, COOLDOWN_SECONDS)
async def supported_commands(interaction: discord.Interaction):
    await interaction.response.send_message(
        f"**************************************************\n    COMMANDS\n    currently supported commands:\n        ---------------------------\n        FUN\n        * hello : Say hello.\n\n        ---------------------------\n        PROBLEM SUBMISSION\n        * current_challenge : See today's problem.\n        * submit : Submit your code to be tested and judged.\n\n        ---------------------------\n        STATS\n        * top: Provides the Top given value members.\n        * top10: Provides the Top 10 members\n        * mypoints: Provides how many points you have.\n        * first: Compares you with the first place member.\n        * get_stats: Display your personal stats.\n\n        ---------------------------\n        UTILITY\n        * rules: Provides the rules and instructions to use the bot for the competition.\n        * supported_commands: Provides a list of supported non admin commands.\n       * remindme: Enroll yourself in competition reminders.\n        * stopreminders: Remove yourself from the competition reminders.\n\n****************************************************"
    )


@tree.command(description="Enroll yourself in competition reminders.")
@app_commands.checks.cooldown(1, COOLDOWN_SECONDS)
async def remindme(interaction: discord.Interaction):
    await check_submission_channel()
    if "Broncoder" in [u.name for u in interaction.user.roles]:
        # Add file?
        await interaction.response.send_message(
            f"{interaction.user.mention} already has the role assigned"
        )
    role = discord.utils.get(interaction.guild.roles, name="Broncoder")
    await interaction.user.add_roles(role)
    await interaction.response.send_message(
        f"Added {interaction.user.mention} to be reminded of competition changes!"
    )


# only allow people in competitor role to call this
@tree.command(description="Remove yourself from the competition reminders.")
@app_commands.checks.cooldown(1, COOLDOWN_SECONDS)
@app_commands.checks.has_role("Broncoder")
# add error catch to not crash
async def stopreminders(interaction: discord.Interaction):
    await check_submission_channel()
    comp_role = discord.utils.get(interaction.guild.roles, name="Broncoder")
    await interaction.user.remove_roles(comp_role)
    await interaction.response.send_message(
        f"Removed {interaction.user.mention} from the competition reminders!"
    )


"""************************************************
    Temporary & Testing Commands
************************************************"""


@tree.command(description="Test announcement command.")
async def test_announcement(interaction: discord.Interaction):
    ANNOUNCEMENT_CHANNEL_ID = store.__getitem__("announcement_channel_id")
    SUBMISSION_CHANNEL_ID = store.__getitem__("submission_channel_id")

    role = discord.utils.get(
        client.get_channel(ANNOUNCEMENT_CHANNEL_ID).guild.roles, name="Broncoder"
    )
    embeds = getProblemEmbeds(store["cotd"])

    message = f"{role.mention}s, " + get_announcement_message(SUBMISSION_CHANNEL_ID)
    await client.get_channel(ANNOUNCEMENT_CHANNEL_ID).send(message)
    await client.get_channel(ANNOUNCEMENT_CHANNEL_ID).send(
        content="Today's challenge:",
        embed=embeds.get("info"),
        view=ProblemView(embeds, None),
    )


@tree.command(description="Test announcement command.")
async def test_end_announcement(interaction: discord.Interaction):
    ANNOUNCEMENT_CHANNEL_ID = store.__getitem__("announcement_channel_id")

    role = discord.utils.get(
        client.get_channel(ANNOUNCEMENT_CHANNEL_ID).guild.roles, name="Broncoder"
    )

    message = f"{role.mention}s, " + get_end_announcement_message(
        client, client.get_channel(ANNOUNCEMENT_CHANNEL_ID).guild
    )
    await client.get_channel(ANNOUNCEMENT_CHANNEL_ID).send(message)


@app_commands.checks.cooldown(1, 1)
@tree.command(description="Test Submit Command.")
async def testsubmit(interaction: discord.Interaction):

    await interaction.response.defer()
    data = {
        "filename": "test_submit_python.txt",
        "id": 981136663499669554,
        "proxy_url": "https://cdn.discordapp.com/attachments/846269630838603796/986811994952851456/test_submit_python.txt",
        "size": 17,
        "url": "https://cdn.discordapp.com/attachments/846269630838603796/986811994952851456/test_submit_python.txt",
        "spoiler": False,
        "content_type": "text; charset=utf-8",
    }
    attachment, language = (
        discord.Attachment(data=data, state=interaction.client._get_state()),
        "Python",
    )
    """ - used to test for first submission
    submission = {
        "msg": "Submission to leetcode.com completed", 
        "err": False, 
        "details": {
            "result_state": "Accepted"
        }
    }
    """

    submission = await handle_submission(interaction, attachment, language)
    # print(submission)

    response_message = f"Thanks for uploading, {interaction.user.display_name}! Received {language} file: {attachment.filename}."

    if not submission.get("err"):

        difficulty_str = store["cotd"]["difficulty"]
        difficulties = {"Easy": 1, "Medium": 2, "Hard": 3}
        DIFFICULTY_POINT = difficulties[difficulty_str]
        BONUS_POINTS = 1
        was_first_submission = False

        # TODO: add timestamp

        # check cooldown
        # app_commands.checks.cooldown(1, COOLDOWN_SECONDS)

        """ ** TESTING ** """

        completion_percent = submission.get("details").get("result_progress_percent")

        status = submission.get("details").get("result_state")

        embed = createSubmissionEmbed(
            details=submission["details"], uploader_name=interaction.user.name
        )

        if status == "Accepted":
            if store.__getitem__("first_submission") == False:
                was_first_submission = True
                store.update({"first_submission": True})
                DIFFICULTY_POINT += BONUS_POINTS
                response_message += "\n**Congrats, you're the first person to submit! Here's an additional bonus point!**"

            # Points.get_instance().addPoints(interaction.user.id, DIFFICULTY_POINT)  # we're not using this anymore, right?
            ParticipantData.get_instance().update_stats(
                interaction.user.id,
                difficulty_str,
                DIFFICULTY_POINT,
                was_first_submission,
            )
            p = ParticipantData.get_instance().get_points(interaction.user.id)

            await interaction.edit_original_message(
                content=response_message + "\n\n"
                f"{interaction.user.mention} has submitted their solution and received {DIFFICULTY_POINT} point{'s'[:DIFFICULTY_POINT ^ 1]}!\n"
                f"{interaction.user.mention} now has {p} point{'s'[:p ^ 1]}!",
                embed=embed,
            )
        else:
            await interaction.edit_original_message(
                content=response_message, embed=embed
            )

        return
    else:
        await interaction.edit_original_message(
            content="",
            embed=createSubmissionEmbed(
                msg=submission["msg"], uploader_name=interaction.user.name
            ),
        )


"""
@app_commands.check(admin_permissions)
@tree.command(description="Grant temp points")
@app_commands.describe(setting="Target Category", point_value="Point Amount")
async def givepoints(interaction: discord.Interaction, setting:str, point_value: int):
    await interaction.response.send_message(
        f"I have updated your point value for {interaction.user.id}"
    )
    ParticipantData.get_instance().add_points(interaction.user.id, setting, point_value)
"""

"""******************************************************
    ERROR HANDLING
******************************************************"""


async def check_submission_channel():
    assert (
            store.__getitem__("submission_channel_id") != 0
        ), "Code submission channel not set"

@tree.error
async def tree_errors(
    interaction: discord.Interaction, error: app_commands.AppCommandError
):
    if isinstance(error, app_commands.CommandOnCooldown):
        await interaction.response.send_message(
            f"You are on cooldown. Try again in {readable(int(error.cooldown.get_retry_after()))}",
            ephemeral=True,
        )
    elif isinstance(error, app_commands.CheckFailure):
        await interaction.response.send_message(
            "You do not have the permission to execute this command!",
            ephemeral=True,
        )
    elif isinstance(error, app_commands.CommandInvokeError):
        error_message = "An error has occurred. Please contact an admin regarding what steps you took for this error message to occur."
        if store.__getitem__("submission_channel_id") == 0:
            error_message = (
                "No code submission channel set. Please notify an admin to fix this."
            )

        await interaction.response.send_message(
            content=error_message,
            ephemeral=True,
        )
    else:
        print(
            "Ignoring exception in command {}:".format(interaction.command),
            file=sys.stderr,
        )
        traceback.print_exception(
            type(error), error, error.__traceback__, file=sys.stderr
        )


@stopreminders.error
async def stopreminders_error(
    interaction: discord.Interaction, error: app_commands.MissingRole
):
    if isinstance(error, app_commands.MissingRole):
        file = discord.File("./assets/BroncoBonk.png")
        await interaction.response.send_message(
            f"{interaction.user.mention} does not have the reminder role.", file=file
        )


"""******************************************************
    ANNOUNCEMENT HANDLING
******************************************************"""


@tasks.loop(time=DAILY_ANNOUNCEMENT_TIME)
async def daily_announcement():
    ANNOUNCEMENT_CHANNEL_ID = store.__getitem__("announcement_channel_id")
    SUBMISSION_CHANNEL_ID = store.__getitem__("submission_channel_id")

    role = discord.utils.get(
        client.get_channel(ANNOUNCEMENT_CHANNEL_ID).guild.roles, name="Broncoder"
    )
    embeds = getProblemEmbeds(store["cotd"])

    message = f"{role.mention}s, " + get_announcement_message(SUBMISSION_CHANNEL_ID)
    await client.get_channel(ANNOUNCEMENT_CHANNEL_ID).send(message)
    await randomize_cotd()
    await client.get_channel(ANNOUNCEMENT_CHANNEL_ID).send(
        content="Today's challenge:",
        embed=embeds.get("info"),
        view=ProblemView(embeds),
    )


@tasks.loop(time=END_COMPETITION_ANNOUNCEMENT_TIME)
async def end_competition_announcement():
    ANNOUNCEMENT_CHANNEL_ID = store.__getitem__("announcement_channel_id")

    role = discord.utils.get(
        client.get_channel(ANNOUNCEMENT_CHANNEL_ID).guild.roles, name="Broncoder"
    )

    message = f"{role.mention}s, " + get_end_announcement_message(
        client, client.get_channel(ANNOUNCEMENT_CHANNEL_ID).guild
    )
    ParticipantData.get_instance().clear()
    await client.get_channel(ANNOUNCEMENT_CHANNEL_ID).send(message)


@daily_announcement.before_loop
async def before():
    await client.wait_until_ready()


def admin_permissions(interaction: discord.Interaction) -> bool:
    return interaction.user.guild_permissions.administrator


@app_commands.check(admin_permissions)
@app_commands.checks.cooldown(1, 1)
@tree.command(description="Configures Bot Channels")
@app_commands.describe(channel="Channel")
async def configure_bot_channels(
    interaction: discord.Interaction, channel: discord.TextChannel
):

    await interaction.response.send_message(
        content=f"What would you like {channel.mention} to serve as? Choose from the buttons below.",
        view=ChannelConfigView(channel.id),
    )


"""******************************************************
    Run
******************************************************"""
ParticipantData.get_instance().init_points()
admin_commands.map_commands(tree)
client.run(BOT_TOKEN)
