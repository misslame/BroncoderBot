import discord


class InfoButton(discord.ui.Button["ProblemView"]):
    def __init__(self, embed: discord.Embed):
        self.embed = embed
        super().__init__(
            style=discord.ButtonStyle.secondary, label="Info", disabled=True
        )

    async def callback(self, interaction: discord.Interaction):
        view: ProblemView = self.view
        if view.user_id != 0 and view.user_id != interaction.user.id:
            return
        self.view.set_current("info")
        await interaction.response.edit_message(
            content="**Today's challenge:**", embed=self.embed, view=view
        )


class DescriptionButton(discord.ui.Button["ProblemView"]):
    def __init__(self, embed: discord.Embed):
        self.embed = embed
        super().__init__(style=discord.ButtonStyle.success, label="Description")

    async def callback(self, interaction: discord.Interaction):
        view: ProblemView = self.view
        if view.user_id != 0 and view.user_id != interaction.user.id:
            return

        self.view.set_current("description")
        await interaction.response.edit_message(
            content="**Today's challenge:**", embed=self.embed, view=view
        )


class ExamplesButton(discord.ui.Button["ProblemView"]):
    def __init__(self, embed: discord.Embed):
        self.embed = embed
        super().__init__(style=discord.ButtonStyle.blurple, label="Examples")

    async def callback(self, interaction: discord.Interaction):
        view: ProblemView = self.view
        if view.user_id != 0 and view.user_id != interaction.user.id:
            return

        self.view.set_current("examples")
        await interaction.response.edit_message(
            content="**Today's challenge:**", embed=self.embed, view=view
        )


class ConstraintsButton(discord.ui.Button["ProblemView"]):
    def __init__(self, embed: discord.Embed):
        self.embed = embed
        super().__init__(style=discord.ButtonStyle.danger, label="Constraints")

    async def callback(self, interaction: discord.Interaction):
        view: ProblemView = self.view
        if view.user_id != 0 and view.user_id != interaction.user.id:
            return

        self.view.set_current("constraints")
        await interaction.response.edit_message(
            content="**Today's challenge:**", embed=self.embed, view=view
        )


class ProblemView(discord.ui.View):
    def __init__(self, embeds, timeout=180, user_id=0):

        super().__init__()
        self.timeout = timeout
        self.buttons = {}

        self.current = "info"
        self.buttons["info"] = InfoButton(embeds["info"])
        self.add_item(self.buttons["info"])

        self.user_id = user_id

        if embeds.get("description"):
            self.buttons["description"] = DescriptionButton(embeds["description"])
            self.add_item(self.buttons["description"])

        if embeds.get("examples"):
            self.buttons["examples"] = ExamplesButton(embeds["examples"])
            self.add_item(self.buttons["examples"])

        if embeds.get("constraints"):
            self.buttons["constraints"] = ConstraintsButton(embeds["constraints"])
            self.add_item(self.buttons["constraints"])

    def set_current(self, new):
        self.buttons.get(self.current).disabled = False
        self.buttons.get(new).disabled = True

        self.current = new
