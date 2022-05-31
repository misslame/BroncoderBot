import discord
from markdownify import markdownify as md

COLOR_NEUTRAL = 0x2E3135
CHECKMARK_EMOJI = " ✅ "
CROSS_EMOJI = " ❌ "
WARNING_EMOJI = " ⚠️ "


def createSubmissionEmbed(
    title="",
    msg=None,
    uploader_name=None,
    challenge_name=None,
    details={},
    color=COLOR_NEUTRAL,
):
    description = ""
    if msg is not None:
        description += msg + "\n\n"
    if uploader_name is not None:
        description += "**Uploader**: {0}\n".format(uploader_name)
    if challenge_name is not None:
        description += "**Challenge**: {0}\n".format(challenge_name)

    if "result_state" in details:
        title = details["result_state"]

    embed = discord.Embed(title=title, description=description)
    if "result_progress" in details:
        result_progress = details["result_progress"]
        result_progress_split = result_progress.split(" / ")
        if len(result_progress_split) == 2:
            num = int(result_progress_split[0])
            den = int(result_progress_split[1])
            completion = num / den
            if completion == 1.0:
                result_progress += CHECKMARK_EMOJI
                embed.color = 0x00FF00
            elif num == 0:
                result_progress += CROSS_EMOJI
                embed.color = 0xFF0000
            else:
                result_progress += WARNING_EMOJI
                embed.color = 0xFFFF00
            embed.add_field(name="Test cases", value=result_progress, inline=False)
        else:
            embed.add_field(name="Test cases", value=result_progress, inline=False)

    if "result_runtime" in details:
        embed.add_field(name="Runtime", value=details["result_runtime"])

    if "result_memory" in details:
        embed.add_field(name="Memory Usage", value=details["result_memory"])

    return embed


def createProblemEmbed(question):
    embed = discord.Embed(
        title=question.get("title"),
        color=COLOR_NEUTRAL,
        url="https://leetcode.com/problems/{}/".format(question["titleSlug"]),
    )
    embed.add_field(name="Difficulty", value=question.get("difficulty"), inline=True)
    embed.add_field(name="Category", value=question.get("categoryTitle"), inline=True)
    embed.set_footer(text="use /submit to upload your answer")
    tags = question.get("topicTags")
    tag_str = ""
    for tag in tags:
        tag_str += "• " + tag.get("name") + "\n"
    embed.add_field(name="Tags", value=tag_str, inline=False)
    return embed


def getProblemEmbeds(problem_raw):

    problem = parseProblem(problem_raw)
    embeds = {}

    infoEmbed = createProblemEmbed(problem_raw)
    embeds["info"] = infoEmbed

    descriptionEmbed = discord.Embed(
        title=problem.get("title"),
        url=f"https://leetcode.com/problems/{problem.get('slug')}",
        color=COLOR_NEUTRAL,
        description=problem.get("description"),
    ).set_footer(text="use /submit to upload your answer")
    embeds["description"] = descriptionEmbed

    if problem.get("examples"):
        examplesEmbed = discord.Embed(
            color=COLOR_NEUTRAL,
            title=problem.get("title"),
            url=f"https://leetcode.com/problems/{problem.get('slug')}",
            description="".join(problem.get("examples")),
        ).set_footer(text="use /submit to upload your answer")

        embeds["examples"] = examplesEmbed

    if problem.get("followup") or problem.get("constraints"):
        constraintsEmbed = discord.Embed(
            color=COLOR_NEUTRAL,
            title=problem.get("title"),
            url=f"https://leetcode.com/problems/{problem.get('slug')}",
            description=(f"{problem.get('constraints')}\n\n{problem.get('followup')}"),
        ).set_footer(text="use /submit to upload your answer")
        embeds["constraints"] = constraintsEmbed

    return embeds


def parseProblem(problem):

    title = problem.get("title")
    slug = problem.get("titleSlug")

    content_html = problem.get("content")

    content_html = content_html.replace("&nbsp;", " ")

    content_md = md(content_html, strip=["img", "pre"])

    # Follow up

    content_md = content_md.split("**Follow")

    followup = ""
    if len(content_md) > 1:
        followup = "**Follow" + content_md[-1]

    content_md = content_md[0]

    # Constraints

    content_md = content_md.split("**Constraints:**")

    constraints = ""
    if len(content_md) > 1:
        constraints = "**Constraints:**\n" + content_md[-1].strip()

    content_md = content_md[0]

    # Examples

    content_md = (
        content_md.replace("\n ", "\n").replace("\n" * 4, "\n").split("**Example")
    )

    description = content_md[0]
    examples = []

    tab = "​ " * 4
    if len(content_md) > 1:
        examples = [
            "**Example"
            + example.replace("**Input", f"{tab}**Input")
            .replace("**Output", f"{tab}**Output")
            .replace("**Explanation", f"{tab}**Explanation")
            for example in content_md[1:]
        ]

    content = {
        "title": title,
        "slug": slug,
        "description": description,
        "followup": followup,
        "constraints": constraints,
        "examples": examples,
    }

    return content
