
# Reads in the bot token. 
# To get this token:  https://discordpy.readthedocs.io/en/stable/discord.html#discord-intro
inFile = open("token_fetching/token.txt", "r")

BOT_TOKEN = inFile.read()

inFile.close()