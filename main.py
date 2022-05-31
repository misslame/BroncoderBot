import traceback
from typing import Literal
import discord
from discord import Embed, app_commands
from discord.ext import commands
from config.config import BOT_TOKEN
from messages.problem_view import ProblemView
from submission_handling.selenium import setup, submitAttachmentToLeetcode
from messages.embeds import createSubmissionEmbed, createProblemEmbed, getProblemEmbeds
from problem_fetching.problem_fetch import getRandomQuestion, getQuestionByTitleSlug
from discord import Attachment, app_commands
from points_table.points import Points
from persistent_store import PersistentStore


# Modules
from command_handling.submission_handler import handle_submission
from command_handling.rank_list_handler import format_rank_list
from command_handling import admin as admin_commands
from points_table.points import Points

intenderinos = discord.Intents.default()
intenderinos.members = True

activity = discord.activity.Activity(
    type=discord.ActivityType.competing, name="Leetcode"
)

client = discord.Client(intents=intenderinos, activity=activity)
tree = app_commands.CommandTree(client)


persistent_store_cotd = PersistentStore(filename="cotd.json")

store = persistent_store_cotd.get_instance()

@client.event
async def on_connect():

    if "title" not in store:
        print("No existing COTD found, making a new one...")
        challenge = await getRandomQuestion()
        for key in challenge:
            store[key] = challenge[key]
        store.sync()
        title = store["title"]
        print(f"\"{title}\" is the new COTD!")
    else:
        title = store["title"]
        print(f"\"{title}\" is the current COTD!")
    await setup(store)


COOLDOWN_SECONDS = 0


@client.event
async def on_ready():
    print(f"Logged in as {client.user} (ID: {client.user.id})")
    await tree.sync()
    print("-------------------------------------")


@tree.command(description="Say hello.")
async def hello(interaction: discord.Interaction):
    await interaction.response.send_message(f"Hi, {interaction.user.mention}")


@tree.command()
@app_commands.describe()
async def cotd(interaction: discord.Interaction):
    embeds = getProblemEmbeds(store)
    
    await interaction.response.send_message(
        content="Today's challenge:",
        embed=embeds.get("info"),
        view=ProblemView(embeds),
    )


@tree.command(description="Enroll in competition.")
async def enroll(interaction: discord.Integration):
    role = discord.utils.get(interaction.guild.roles,
                             name="Competition Reminders")
    await interaction.user.add_roles(role)
    await interaction.response.send_message(
        f"Added {interaction.user.mention} to competition"
    )

@tree.command(description="Submit your code.")
@app_commands.checks.cooldown(1, COOLDOWN_SECONDS)
@app_commands.describe(attachment="The code to submit", language="Progamming language")
async def submit(
    interaction: discord.Interaction, attachment: discord.Attachment, language: Literal['C++', 'Java', 'Python', 'Python3', 'C', 'C#', 'JavaScript', 'Ruby', 'Swift',
                                                                                        'Go', 'Scala', 'Kotlin', 'Rust', 'PHP', 'TypeScript', 'Racket', 'Erlang', 'Elixir']
):
    await interaction.response.defer()
    submission = await handle_submission(interaction, attachment, language)
    # print(submission)

    response_message = f'Thanks for uploading, {interaction.user.display_name}! Recieved {language} file: {attachment.filename}.'

    if not submission.get("err"):

        difficulty_str = store["difficulty"]
        difficulties = {"Easy": 1, "Medium": 2, "Hard": 3}
        DIFFICULTY_POINT = difficulties[difficulty_str]

        # TODO: add timestamp

        # check cooldown
        # app_commands.checks.cooldown(1, COOLDOWN_SECONDS)

        """ ** TESTING ** """

        completion_percent = submission.get(
            "details").get("result_progress_percent")

        status = submission.get(
            "details").get("result_state")

        embed = createSubmissionEmbed(
            details=submission["details"], uploader_name=interaction.user.name
        )

        if status == "Accepted":
            Points.get_instance().addPoints(interaction.user.id, DIFFICULTY_POINT)
            p = Points.get_instance().getPoints(interaction.user.id)
            await interaction.edit_original_message(
                content=response_message+"\n\n"
                f"{interaction.user.mention} has submited their solution and recieved {DIFFICULTY_POINT} point{'s'[:DIFFICULTY_POINT ^ 1]}!\n"
                f"{interaction.user.mention} now has {p} point{'s'[:p ^ 1]}!",
                embed=embed,
            )
        else:
            await interaction.edit_original_message(content=response_message,embed=embed)

        return
    else:
        await interaction.followup.send(
            content="",
            embed=createSubmissionEmbed(
                msg=submission["msg"], uploader_name=interaction.user.name
            )
        )


@app_commands.checks.cooldown(1, COOLDOWN_SECONDS)
@tree.command(description="Test Submit Command.")
async def testsubmit(interaction: discord.Interaction):
    await interaction.response.defer()
    data = {
        "filename": "racket.rkt",
        "id": 981136663499669554,
        "proxy_url": "https://cdn.discordapp.com/attachments/979971398753742859/981136663499669554/racket.racket.txt",
        "size": 17,
        "url": "https://cdn.discordapp.com/attachments/979971398753742859/981136663499669554/racket.racket.txt",
        "spoiler": False,
        "content_type": "text; charset=utf-8",
    }
    attachment, language = (
        discord.Attachment(data=data, state=interaction.client._get_state()),
        "Racket",
    )


    submission = await handle_submission(interaction, attachment, language)
    # print(submission)

    response_message = f'Thanks for uploading, {interaction.user.display_name}! Recieved {language} file: {attachment.filename}.'

    if not submission.get("err"):

        difficulty_str = store["difficulty"]
        difficulties = {"Easy": 1, "Medium": 2, "Hard": 3}
        DIFFICULTY_POINT = difficulties[difficulty_str]

        # TODO: add timestamp

        # check cooldown
        # app_commands.checks.cooldown(1, COOLDOWN_SECONDS)

        """ ** TESTING ** """

        completion_percent = submission.get(
            "details").get("result_progress_percent")

        status = submission.get(
            "details").get("result_state")

        embed = createSubmissionEmbed(
            details=submission["details"], uploader_name=interaction.user.name
        )

        if status == "Accepted":
            Points.get_instance().addPoints(interaction.user.id, DIFFICULTY_POINT)
            p = Points.get_instance().getPoints(interaction.user.id)
            await interaction.edit_original_message(
                content=response_message+"\n\n"
                f"{interaction.user.mention} has submited their solution and recieved {DIFFICULTY_POINT} point{'s'[:DIFFICULTY_POINT ^ 1]}!\n"
                f"{interaction.user.mention} now has {p} point{'s'[:p ^ 1]}!",
                embed=embed,
            )
        else:
            await interaction.edit_original_message(content=response_message,embed=embed)

        return
    else:
        await interaction.edit_original_message(
            content="",
            embed=createSubmissionEmbed(
                msg=submission["msg"], uploader_name=interaction.user.name
            )
        )

@tree.command(description="Returns the Top 10 Users.")
@app_commands.describe()
async def top10(interaction: discord.Interaction):
    await interaction.response.send_message(
        await format_rank_list(interaction, Points.get_instance().getTop(10), 10)
    )


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
        traceback.print_exception(type(error), error, error.__traceback__)


def readable(seconds: int):
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = (seconds % 3600) % 60

    times = {"hour": h, "minute": m, "second": s}

    return " and ".join([f"{v} {k}{'s'[:v ^ 1]}" for k, v in times.items() if v])


Points.get_instance().init_points()
admin_commands.map_commands(tree)
client.run(BOT_TOKEN)
