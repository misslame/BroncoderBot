import discord

COLOR_NEUTRAL = 0x2e3135
CHECKMARK_EMOJI = " ✅ "
CROSS_EMOJI = " ❌ "
WARNING_EMOJI = " ⚠️ "

def createSubmissionEmbed(title="", msg=None, uploader_name=None, challenge_name=None, details={}, color=COLOR_NEUTRAL):
    description=""
    if msg is not None:
        description += msg + "\n\n"
    if uploader_name is not None:
        description += "**Uploader**: {0}\n".format(uploader_name)
    if challenge_name is not None:
        description += "**Challenge**: {0}\n".format(challenge_name)
    
    if "result_state" in details:
        title = details["result_state"]

    embed=discord.Embed(title=title, description=description)
    if "result_progress" in details:
        result_progress = details["result_progress"]
        result_progress_split = result_progress.split(" / ")
        if len(result_progress_split) == 2:
            num = int(result_progress_split[0])
            den = int(result_progress_split[1])
            completion = num/den
            if completion == 1.0:
                result_progress += CHECKMARK_EMOJI
                embed.color=0x00ff00
            elif num == 0:
                result_progress += CROSS_EMOJI
                embed.color=0xff0000
            else:
                result_progress += WARNING_EMOJI
                embed.color=0xffff00
            embed.add_field(name="Test cases", value=result_progress, inline=False)
        else:
            embed.add_field(name="Test cases", value=result_progress, inline=False)

    if "result_runtime" in details:
        embed.add_field(name="Runtime", value=details["result_runtime"])

    if "result_memory" in details:
        embed.add_field(name="Memory Usage", value=details["result_memory"])
    
    return embed

def createProblemEmbed(question):
    embed = discord.Embed(title=question.get("title"), color=0xff00ff, url="https://leetcode.com/problems/{}/".format(question["titleSlug"]))
    embed.add_field(name="Difficulty", value=question.get("difficulty"), inline=True)
    embed.add_field(name="Category", value=question.get("categoryTitle"), inline=True)
    embed.set_footer(text = "use /submit to upload your answer")
    tags = question.get("topicTags")
    tag_str = ""
    for tag in tags:
        tag_str += "• " + tag.get("name") + "\n"
    embed.add_field(name="Tags", value=tag_str, inline=False)
    return embed



    