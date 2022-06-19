import discord
import zoneinfo
import datetime
from datetime import date, time
from discord import channel

from participant_data_handling.participant_data import ParticipantData

tz =  zoneinfo.ZoneInfo('PST8PDT')

DAILY_HOUR = 6
DAILY_MINUTE = 30
END_HOUR = 23
END_MINUTE = 59
DAILY_ANNOUNCEMENT_TIME = time(hour=DAILY_HOUR, minute=DAILY_MINUTE, tzinfo=tz)
END_COMPETITION_ANNOUNCEMENT_TIME = time(hour=END_HOUR, minute=END_MINUTE, tzinfo=tz)

def get_announcement_message(submission_channel_id):

    todays_month = date.today().month
    tomorrows_month = (date.today() + datetime.timedelta(days=1)).month

    message = ''

    if(date.today().day == 1):
        # First day of the month!
        message += f'Today is the day! The start of the broncoder durby.\n\n__Reminders:__\n • Please partricipate in good faith.\n • Challenges are posted at {DAILY_ANNOUNCEMENT_TIME.strftime("%I : %M %p")}.\n • Submit solution files either through DM to me or in <#{submission_channel_id}> through the /submit command. \n\n **Happy trotting, Broncoders!**'
        message += '\n\n'
    elif(todays_month != tomorrows_month):
        TIME_LEFT = END_HOUR - DAILY_HOUR
        # Last day of the month!
        message += f'Trotting ends today. You have approximately {TIME_LEFT} hours left to complete the last challange. First place will be announced {END_COMPETITION_ANNOUNCEMENT_TIME.strftime("%I : %M %p")}.'
        message += '\n\n'
    
    # Regular daily announcement

    if(date.today().day % 3 == 0):
        message += 'Today\'s problem isn\'t anything to neigh at...'
    elif (date.today().day % 5 == 0):
        message += 'HAY, today\'s MANE goals should include saddling up for today\'s problem.'
    elif(date.today().day % 7 == 0):
        message += 'Break a leg on today\'s problem...on second thought, don\'t. Don\'t want to have to put anyone down and make glue...'
    elif(date.today().day % 2 == 0):
        message += 'Not to stirrup any trouble but quit horsing around and trot on up to today\'s problem.'
    else:
        message += 'I have my Exacta bet on some Broncoders in already for today\'s problem.'
    return message

def get_end_announcement_message(client : discord.Client, guild : discord.Guild):
    
    todays_month = date.today().month
    tomorrows_month = (date.today() + datetime.timedelta(days=1)).month

    if(todays_month != tomorrows_month):
        message = f'The time has come!! Reign yourselves in! End of the Broncoder Derby!.\n\n'
        first = ParticipantData.get_instance().get_top(1)
        if(len(first) >= 1 and ParticipantData.get_instance().get_points(first[0]) > 0):
            FIRST_PLACE = guild.get_member(int(ParticipantData.get_instance().get_top(1)[0]))
            message += f'**Congrats to {FIRST_PLACE.mention}!** :tada: \n\n Here are the stats:'
            message += '\n' + format_rank_list(guild, ParticipantData.get_instance().get_top(10), 10)
        else:
            message += 'Too bad no one participated. Guess everyone turned in to glue.'
    return message


# I REALIZE THIS IS ESSENTIALLY A COPY OF THE FUNTION IN RANK LIST AND THIS IS MESSED UP BUT OH WELL
def format_rank_list(guild : discord.guild, list : list[str], top : int):
    if len(list) >= 1:
        response_message = f'``` Top {top}:\n-------------\n'

        count = 1
        for user in list:
            p = ParticipantData.get_instance().get_points(user)
            response_message += f'{count}.{guild.get_member(int(user)).display_name} [{p} point{"s"[:p ^ 1]}]\n'
            count += 1

        return response_message + '```'
    else:
        return f'no one participated...'