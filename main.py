import sys
import traceback
import discord
from discord import Attachment, Color, Embed, Guild, Interaction, app_commands
from typing import Literal
import zoneinfo
from datetime import time

from discord.ext import tasks

# IMPORTED CONSTANTS:
from config.config import BOT_TOKEN
from command_handling.timeout_handler import COOLDOWN_SECONDS

# MODULES:
# -------- Command Handling -----------
from command_handling.submission_handler import handle_submission
from command_handling.rank_list_handler import format_rank_list
from command_handling.first_handler import get_first_stats
from command_handling.timeout_handler import readable
from command_handling import admin as admin_commands

# -------- Problem Submission ---------
from messages.problem_view import ProblemView
from messages.embeds import createSubmissionEmbed, createProblemEmbed, getProblemEmbeds
from problem_fetching.problem_fetch import getRandomQuestion, getQuestionByTitleSlug
from submission_handling.selenium import setup, submitAttachmentToLeetcode

# -------- Statistics & Storage --------
from participant_data_handling.participant_data import ParticipantData
from persistent_store import PersistentStore


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
        * remindme: Enroll yourself in competition reminders.
        * stopreminders: Remove yourself from the competition reminders.

****************************************************"""

""" ---------- FUN ---------- """


@tree.command(description="Say hello.")
@app_commands.checks.cooldown(1, COOLDOWN_SECONDS)
async def hello(interaction: discord.Interaction):
    await interaction.response.send_message(f"Hi, {interaction.user.mention}")


""" ---------- PROBLEM SUBMISSION ---------- """


@tree.command(description="See today's problem.")
@app_commands.checks.cooldown(1, COOLDOWN_SECONDS)
async def current_challenge(interaction: discord.Interaction):
    embeds = getProblemEmbeds(store["cotd"])

    await interaction.response.send_message(
        content="Today's challenge:",
        embed=embeds.get("info"),
        view=ProblemView(embeds),
    )


@tree.command(description="Submit your code to be tested and judged.")
@app_commands.checks.cooldown(1, COOLDOWN_SECONDS)
@app_commands.describe(attachment="The code to submit", language="Progamming language")
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
    await interaction.response.defer()
    submission = await handle_submission(interaction, attachment, language)

    response_message = f"Thanks for uploading, {interaction.user.display_name}! Recieved {language} file: {attachment.filename}."

    DIFFICULTIES = {"Easy": 1, "Medium": 2, "Hard": 3}

    if not submission.get("err"):
        difficulty_str = store["cotd"]["difficulty"]

        # TODO: figure out who is first
        was_first = False
        # TODO: add up points from first accepted submission bonus!
        points = DIFFICULTIES[difficulty_str]

        completion_percent = submission.get("details").get("result_progress_percent")

        status = submission.get("details").get("result_state")

        embed = createSubmissionEmbed(
            details=submission["details"], uploader_name=interaction.user.name
        )

        if status == "Accepted":
            ParticipantData.get_instance().update_stats(
                interaction.user.id, difficulty_str, points, was_first
            )
            p = ParticipantData.get_instance().get_points(interaction.user.id)

            # TODO: add timestamp
            await interaction.edit_original_message(
                content=response_message + "\n\n"
                f"{interaction.user.mention} has submited their solution and recieved {points} point{'s'[:points ^ 1]}!\n"
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
    await interaction.response.send_message(
        await format_rank_list(
            interaction, ParticipantData.get_instance().get_top(value), value
        )
    )


@app_commands.checks.cooldown(1, COOLDOWN_SECONDS)
@tree.command(description="provides the Top 10 members.")
async def top10(interaction: discord.Interaction):
    await interaction.response.send_message(
        await format_rank_list(
            interaction, ParticipantData.get_instance().get_top(10), 10
        )
    )


@app_commands.checks.cooldown(1, COOLDOWN_SECONDS)
@tree.command(description="Provides how many points you have.")
async def mypoints(interaction: discord.Interaction):
    await interaction.response.send_message(
        f"You currently have {ParticipantData.get_instance().get_points(interaction.user.id)} point(s)."
    )


@app_commands.checks.cooldown(1, COOLDOWN_SECONDS)
@tree.command(description="Compares you with the first place member.")
async def first(interaction: discord.Interaction):
    await interaction.response.defer()
    await interaction.followup.send(get_first_stats(interaction))


@tree.command(description="Display your personal stats.")
async def get_stats(interaction: discord.Interaction):
    await interaction.response.defer()

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


@tree.command(description="Enroll yourself in competition reminders.")
@app_commands.checks.cooldown(1, COOLDOWN_SECONDS)
async def remindme(interaction: discord.Interaction):
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
    comp_role = discord.utils.get(interaction.guild.roles, name="Broncoder")
    await interaction.user.remove_roles(comp_role)
    await interaction.response.send_message(
        f"Removed {interaction.user.mention} from the competition reminders!"
    )


"""************************************************
    Temporary & Testing Commands
************************************************"""


@app_commands.checks.cooldown(1, COOLDOWN_SECONDS)
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

    submission = await handle_submission(interaction, attachment, language)
    # print(submission)

    response_message = f"Thanks for uploading, {interaction.user.display_name}! Recieved {language} file: {attachment.filename}."

    if not submission.get("err"):

        difficulty_str = store["cotd"]["difficulty"]
        difficulties = {"Easy": 1, "Medium": 2, "Hard": 3}
        DIFFICULTY_POINT = difficulties[difficulty_str]
        WAS_FIRST_SUBMITION = False

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
            # Points.get_instance().addPoints(interaction.user.id, DIFFICULTY_POINT)  # we're not using this anymore, right?
            ParticipantData.get_instance().update_stats(
                interaction.user.id,
                difficulty_str,
                DIFFICULTY_POINT,
                WAS_FIRST_SUBMITION,
            )
            p = ParticipantData.get_instance().get_points(interaction.user.id)
            await interaction.edit_original_message(
                content=response_message + "\n\n"
                f"{interaction.user.mention} has submited their solution and recieved {DIFFICULTY_POINT} point{'s'[:DIFFICULTY_POINT ^ 1]}!\n"
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


def admin_permissions(interaction: discord.Interaction) -> bool:
    return interaction.user.guild_permissions.administrator


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


@tree.error
async def tree_errors(
    interaction: discord.Interaction, error: app_commands.AppCommandError
):
    if isinstance(error, app_commands.CommandOnCooldown):
        await interaction.response.send_message(
            f"You are on cooldown. Try again in {readable(int(error.cooldown.get_retry_after()))}",
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

ANNOUNCEMENT_CHANNEL_ID = 833465079559094312
tz = zoneinfo.ZoneInfo("PST8PDT")
# 7:30 am
ANNOUNCEMENT_TIME = time(hour=7, minute=30, tzinfo=tz)


@tasks.loop(time=ANNOUNCEMENT_TIME)
async def daily_announcement():
    message_channel = client.get_channel(ANNOUNCEMENT_CHANNEL_ID)
    await message_channel.send("This announcement happens at 7:30am PST.")


@daily_announcement.before_loop
async def before():
    await client.wait_until_ready()


@app_commands.check(admin_permissions)
@app_commands.checks.cooldown(1, COOLDOWN_SECONDS)
@tree.command(description="Assigns a new Announcement Channel")
@app_commands.describe(new_announce_channel="Channel")
async def change_announcement_channel(
    interaction: discord.Interaction, new_announce_channel: discord.TextChannel
):
    global ANNOUNCEMENT_CHANNEL_ID
    await interaction.response.send_message(
        f"Updated the announcement channel to {new_announce_channel.mention}"
    )
    ANNOUNCEMENT_CHANNEL_ID = new_announce_channel.id


"""******************************************************
    Run
******************************************************"""
ParticipantData.get_instance().init_points()
admin_commands.map_commands(tree)
client.run(BOT_TOKEN)
