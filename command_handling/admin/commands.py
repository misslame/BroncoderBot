import discord
from discord import app_commands

from persistent_store import PersistentStore
from problem_fetching.problem_fetch import getQuestionByTitleSlug, getRandomQuestion
from submission_handling.selenium import changeProblem

store = PersistentStore.get_instance()


@app_commands.command()
async def set_admin_role(interaction: discord.Interaction, role: discord.Role):
    guild_id = interaction.guild_id

    if guild_id not in store:
        guild_store = store[guild_id] = {}
    else:
        guild_store = store[guild_id]

    guild_store["admin_role"] = role.id
    store.update({guild_id: guild_store})

    await interaction.response.send_message(
        f"Set admin role as {role.mention}", ephemeral=True
    )


@app_commands.command()
async def end_early(interaction: discord.Interaction):
    pass


@app_commands.command()
async def refresh_daily(interaction: discord.Interaction):
    pass


@app_commands.command()
async def refresh_status(interaction: discord.Interaction):
    pass


@app_commands.command(description="Change the problem of the day.")
@app_commands.describe(title_slug="Problem title slug (the thing after the url)")
async def change_cotd(interaction: discord.Interaction, title_slug: str):
    await interaction.response.defer()
    problem = await getQuestionByTitleSlug(title_slug)
    if "errors" in problem:
        await interaction.followup.send(
            f"There was a problem setting the challenge of the day to {title_slug}"
        )
        return
    await changeProblem(title_slug)
    store.update({"cotd": problem})

    await interaction.followup.send(f'Set challenge of the day to {problem["title"]}')
    return


@app_commands.command(description="Randomize problem of the day")
async def randomize_cotd(interaction: discord.Interaction):
    await interaction.response.defer()
    problem = await getRandomQuestion()
    if "errors" in problem:
        await interaction.followup.send(
            f"There was a problem setting the challenge of the day"
        )
        return
    await changeProblem(problem["titleSlug"])
    store.update({"cotd": problem})

    await interaction.followup.send(f'Set challenge of the day to {problem["title"]}')
    return


# I have put this in an unfortunate spot but... oh well.
# async def randomize_cotd():
#     problem = await getRandomQuestion()
#     while "errors" in problem:
#         print("There was a problem setting up the challenge of the day... retrying")
#         problem = await getRandomQuestion()
#     await changeProblem(problem["titleSlug"])
#     store.update({"cotd": problem})


async def update(problem):
    store.update({"cotd": problem})


__all__ = [
    "set_admin_role",
    "end_early",
    "refresh_daily",
    "refresh_status",
    "change_cotd",
    "randomize_cotd",
]
