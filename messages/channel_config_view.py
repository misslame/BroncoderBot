import discord
from persistent_store import PersistentStore

store = PersistentStore.get_instance()


class AnnounceButton(discord.ui.Button["ChannelConfigView"]):
    def __init__(self, channel_id):
        self.channel_id = channel_id
        super().__init__(
            style=discord.ButtonStyle.blurple, label="Announcement Channel"
        )

    async def callback(self, interaction: discord.Interaction):
        view: ChannelConfigView = self.view
        self.view.end_interaction()
        store.update({"announcement_channel_id": self.channel_id})
        await interaction.response.edit_message(
            content=f"Your announcement channel has been set to <#{self.channel_id}>",
            view=view,
        )


class SubmissionButton(discord.ui.Button["ChannelConfigView"]):
    def __init__(self, channel_id):
        self.channel_id = channel_id
        super().__init__(style=discord.ButtonStyle.blurple, label="Submission Channel")

    async def callback(self, interaction: discord.Interaction):
        view: ChannelConfigView = self.view
        self.view.end_interaction()
        store.update({"submission_channel_id": self.channel_id})
        await interaction.response.edit_message(
            content=f"Your code submission channel has been set to <#{self.channel_id}>",
            view=view,
        )


class ChannelConfigView(discord.ui.View):
    def __init__(self, channel_id):

        super().__init__()

        self.buttons = {}

        self.buttons["announce"] = AnnounceButton(channel_id)
        self.add_item(self.buttons["announce"])

        self.buttons["submit"] = SubmissionButton(channel_id)
        self.add_item(self.buttons["submit"])

    def end_interaction(self):
        for btn in self.buttons.values():
            btn.disabled = True
