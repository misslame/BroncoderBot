import discord
from points_table.points import Points

async def format_rank_list(interaction: discord.Interaction, list : list, top : int):
    if len(list) >= 1:
        response_message = f'``` Top {top}:\n-------------\n'

        count = 1
        for user in list:
            response_message += f'{count}.{interaction.guild.get_member(int(user)).display_name} [{Points.get_instance().getPoints(user)} point(s)]\n'

        return response_message + '```'
    else:
        return f'Can not do a top {top} when no one is participating'