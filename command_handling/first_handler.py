import discord

from participant_data_handling.participant_data import ParticipantData


def get_first_stats(interaction: discord.Interaction):
    days_left = 31 #TODO: Get this dynamically!
    seconds_left = 100 #TODO: Get this dynamically!

    top = ParticipantData.get_instance().get_top(10)
    #interaction.guild.get_member(int()).display_name
    #handles 0 participant case
    if len(top) < 1:
        response_message = f'There are no participants as of now.\n'
    else:    
        #handles 0 points participants only
        highest_score = ParticipantData.get_instance().get_points(top[0])
        if  highest_score == 0:
            response_message = f'Everyone has 0 points. You have a chance to be the winner!\n'
        else:
            tie = 0
            end = False
            #check for ties / iterate through list
            while(tie < len(top) - 1 and not end):
                if ParticipantData.get_instance().get_points(top[tie + 1]) == highest_score :
                    tie += 1
                else:
                    end = True
            
            #1 winner
            if tie == 0:
                first_place = interaction.guild.get_member(int(top[0])).display_name

                response_message = f'{first_place} is first!'

            
                if(first_place == interaction.user.display_name): # first place is triggering command!
                    response_message = f'You are first place! Keep it up, you have {ParticipantData.get_instance().get_points(interaction.user.id)} point(s)!\n'
                else:
                    points_behind = ParticipantData.get_instance().get_top(1) - ParticipantData.get_instance().get_points(interaction.user.id)
                    response_message = f'{first_place} is in first place! You are {points_behind} point(s) behind them!'
            
            #tie winners
            else:
                among_first = False
                response_message =f'There are multiple people in first:\n'
                for i in range(tie + 1) :
                    response_message += f'{interaction.guild.get_member(int(top[i])).display_name} [{ParticipantData.get_instance().get_points(top[i])} point(s)]\n'
                    if(int(top[i]) == interaction.user.id):
                        among_first = True
                if(among_first):
                    response_message += f'\nYou are neck in neck for first place!\n'
                else:
                    points_behind = highest_score - ParticipantData.get_instance().get_points(interaction.user.id)
                    response_message += f'\nYou are {points_behind} point(s) behind them!\n\n'   

        
    if days_left > 0:
        response_message += f'There are {days_left} days left till the competition ends!\n'
        if days_left <= 5:
            response_message += f'Competition is tight...'
        elif days_left <= 15:
            response_message += f'Motivation maintaining is key!'
        elif days_left <= 20: 
            response_message += f'Ah, you have plenty of time.'
        elif days_left <= 31:
            response_message += f'We JUST got started. A lot can change in the next weeks!'
    else:
        response_message += f'If it wasn\'t announced yet today, results will be! You have {seconds_left} to finish the day a winner!'
    
    return response_message

