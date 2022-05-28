import discord

'''
Dictionary of supported languages
key: file extension
value: language aliases
'''
supported_languages = {
    'py' : ["python", "py"],
    'java' : ["java"],
    'cs' : ["c#", "cs", "csharp"],
    'cpp' : ["c++", "cpp", "cplusplus"],
    'c' : ["c", "see"],
    'js' : ["javascript", "js"],
    'rs' : ["rust", "rust4lyfe", "rs"],
    'go' : ["google", "go"]
}

async def handle_submission(interaction: discord.Interaction, attachment: discord.Attachment, language: str):
    ''' ** TESTING ** '''
    await interaction.channel.send(f'The file uploaded was: {attachment.content_type} language submitted is {language}')

    successful_submission = False

    response_message = f'Thanks for uploading, {interaction.user.display_name}!. Recieved file: {attachment.filename}\n'

    extension = get_extension(language)
    if(extension is not None): # found as a supported language
        if(verify_language(attachment, language.lower(), extension)):
            # valid file extension / language
            print('Valid file was submitted.')
            submited_file = await attachment.read(use_cached=False)
            file_contents = submited_file.decode('utf-8')

            ''' ** TESTING ** '''
            await interaction.channel.send(f'File Content is {decoded_file}')

            #TODO: successful_submission = METHOD_TO_VERIFY(file_contents)
            successful_submission = True
        else:
            response_message += f'You indicated a {language} submission, that is not a python file!'

    await interaction.response.send_message(response_message, ephemeral=True)

    return successful_submission


def get_extension(language_alias): #Finds the key that has the following language alias as a value
    for extension, language_aliases in supported_languages.items():
        if language_alias in language_aliases:
            return extension
    return None

def verify_language(attachment, language, extension):
    # file verification. 
    return attachment.filename[-len(extension):] == extension