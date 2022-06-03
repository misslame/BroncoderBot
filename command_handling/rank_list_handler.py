import discord
from participant_data_handling.participant_data import ParticipantData

async def format_rank_list(interaction: discord.Interaction, list : list[str], top : int):
    if len(list) >= 1:
        response_message = f'``` Top {top}:\n-------------\n'

        count = 1
        for user in list:
            p = ParticipantData.get_instance().get_points(user)
            response_message += f'{count}.{interaction.guild.get_member(int(user)).display_name} [{p} point{"s"[:p ^ 1]}]\n'
            count += 1

        return response_message + '```'
    else:
        return f'Can not do a top {top} when no one is participating'