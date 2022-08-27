import discord
from datetime import date
from calendar import monthrange

from participant_data_handling.participant_data import ParticipantData
from command_handling.announcement_handler import END_COMPETITION_ANNOUNCEMENT_TIME



def get_first_stats(interaction: discord.Interaction):
    days_left = monthrange(date.today().year, date.today().month)[1] - date.today().day
    response_message = ""

    # Check if there are participants:
    if (
        ParticipantData.get_instance().participants_stats
        and ParticipantData.get_instance().get_points(
            ParticipantData.get_instance().get_top(1)[0]
        )
        > 0
    ):
        first_ids = ParticipantData.get_instance().get_firsts()

        #check case: there are users logged but no one has gotten points yet
        if(ParticipantData.get_instance().get_points(first_ids[0]) > 0):

            # get list of users in first place
            first_places = list(
                map(
                    lambda id: interaction.guild.get_member(int(id)).display_name, first_ids
                )
            )
            
            # check if user is in first place
            user_is_first = first_places.__contains__(interaction.user.display_name)
            # remove user from list
            if user_is_first:
                first_places.remove(interaction.user.display_name)

            # makes string containing list of people in first place (except user)
            first_place_message = ""
            if len(first_places) == 0:
                first_place_message = f"{first_places[0]}"
            else:
                # form list of first place
                for i in range(0, len(first_places)):
                    first_place_message += first_places[i]
                    if i == len(first_places) - 2:
                        first_place_message += ", and "
                    if i < len(first_places) - 2:
                        first_place_message += ", "

    #comparing user score with list of 1st places
            if user_is_first:  #case 1: only you are 1st place
                response_message = f"You are first place! Keep it up, you have {ParticipantData.get_instance().get_points(interaction.user.id)} point(s)!\n"
                
                #case 2: tied with other users
                if not len(first_places) == 0:
                    response_message = f"You are tied with {first_place_message}\n"

            else: #case 3: user is not in first place
                points_behind = ParticipantData.get_instance().get_points(
                    first_ids[0]
                ) - ParticipantData.get_instance().get_points(interaction.user.id)
                verb = "is" if len(first_places) == 1 else "are"
                response_message = f"{first_place_message} {verb} in first place! You are {points_behind} point(s) behind them!\n"
        else:
            response_message = f'Everyone has 0 points. You have a chance to be the winner!\n'
    #if there are no participants logged,
    else:
        response_message = f'There are no participants as of now.\n'

#printing out days left output
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

    return response_message