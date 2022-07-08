import discord
from submission_handling.selenium import submitAttachmentToLeetcode
from messages.embeds import createSubmissionEmbed

"""
Dictionary of supported languages
key: file extension
value: language aliases
"""
SUPPORTED_LANGUAGES = {
    "py": ["python", "py"],
    "java": ["java"],
    "cs": ["c#", "cs", "csharp"],
    "cpp": ["c++", "cpp", "cplusplus"],
    "c": ["c", "see"],
    "js": ["javascript", "js"],
    "rs": ["rust", "rust4lyfe", "rs"],
    "go": ["google", "go"],
}


async def handle_submission(
    interaction: discord.Interaction, attachment: discord.Attachment, language: str
):
    """** TESTING **"""
    # await interaction.channel.send(f'The file uploaded was: {attachment.content_type} language submitted is {language}')

    response_message = f"Thanks for uploading, {interaction.user.display_name}! Recieved {language} file: {attachment.filename}."
    response_message += "\n\nPlease wait while we check your submission..."

    await interaction.response.send_message(response_message)
    return await submitAttachmentToLeetcode(attachment, language)

    """
    submission = None
    extension = get_extension(language)
    if(extension is not None): # found as a supported language
        if(verify_language(attachment, language.lower(), extension)):
            # valid file extension / language
            # print('Valid file was submitted.')
            submited_file = await attachment.read(use_cached=False)
            file_contents = submited_file.decode('utf-8')

            """ ** TESTING ** """
            # await interaction.channel.send(f'File Content is {file_contents}')

            submission = await submitAttachmentToLeetcode(attachment, language)

        else:
            response_message += f'You indicated a {language} submission, that is not a python file!'

    await interaction.followup.send(response_message)

    return submission
    """


def get_extension(
    language_alias,
):  # Finds the key that has the following language alias as a value
    for extension, language_aliases in SUPPORTED_LANGUAGES.items():
        if language_alias in language_aliases:
            return extension
    return None


def verify_language(attachment, language, extension):
    # file verification.
    return attachment.filename[-len(extension) :] == extension
