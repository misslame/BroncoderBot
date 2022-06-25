import discord
from datetime import date
from calendar import monthrange

from participant_data_handling.participant_data import ParticipantData
from command_handling.announcement_handler import END_COMPETITION_ANNOUNCEMENT_TIME


def get_first_stats(interaction: discord.Interaction):
    days_left = monthrange(date.today().year, date.today().month)[1] - date.today().day

    # Check if there are participants:
    if (
        ParticipantData.get_instance().participants_stats
        or ParticipantData.get_instance().get_points(
            ParticipantData.get_instance().get_top(1)[0]
        )
        > 0
    ):
        first_id = ParticipantData.get_instance().get_top(1)[0]
        first_place = interaction.guild.get_member(int(first_id)).display_name
        response_message = f"{first_place} is first!"

        if (
            first_place == interaction.user.display_name
        ):  # first place is triggering command!
            response_message = f"You are first place! Keep it up, you have {ParticipantData.get_instance().get_points(interaction.user.id)} point(s)!\n"
        else:
            points_behind = ParticipantData.get_instance().get_points(
                first_id
            ) - ParticipantData.get_instance().get_points(interaction.user.id)
            response_message = f"{first_place} is in first place! You are {points_behind} point(s) behind them!"

        if days_left > 0:
            response_message += (
                f"There are {days_left} days left till the competition ends!\n"
            )
            if days_left <= 5:
                response_message += f"Competition is tight..."
            elif days_left <= 15:
                response_message += f"Motivation maintaining is key!"
            elif days_left <= 20:
                response_message += f"Ah, you have plenty of time."
            elif days_left <= 31:
                response_message += (
                    f"We JUST got started. A lot can change in the next weeks!"
                )
        else:
            response_message += f"If it wasn't announced yet today, results will be! You have until {END_COMPETITION_ANNOUNCEMENT_TIME.strftime} to finish the day a winner!"
    else:
        response_message = "There isn't anyone in first place!"
    return response_message
