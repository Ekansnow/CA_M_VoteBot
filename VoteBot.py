import nextcord


"""The nextcord library provides the core functionality for creating and interacting with Discord bots.
The commands extension facilitates the definition and execution of Discord commands recognized by users.
The tasks extension enables the creation and management of asynchronous tasks, enabling background operations while the bot handles other tasks.
"""
from nextcord.ext import commands, tasks

"""The intents object specifies the Discord APIs the bot will utilize. The message_content flag ensures the bot can access and process the content of messages sent by users.
The command_prefix parameter sets the command prefix, prompting the bot to recognize commands beginning with the specified character ("!" in this case).
The help_command parameter disables the default help command, allowing the bot to provide custom help information."""
intents = nextcord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", help_command=None, intents=intents)


class MyVote(commands.Cog):
    # The __init__() method initializes the cog, storing the bot object and a list of emojis for numbered options (👍, 👎, etc.).
    def __init__(self, bot):
        self.bot = bot
        self.numbers = [
            "1️⃣",
            "2️⃣",
            "3️⃣",
            "4️⃣",
            "5️⃣",
            "6️⃣",
            "7️⃣",
            "8️⃣",
            "9️⃣",
            "🔟",
        ]

    """The @commands.command() decorator marks the vote method as a recognized Discord command.
    The minutes parameter specifies the duration of the vote in minutes.
    The title parameter defines the vote's title.
    The options parameter accepts a list of strings representing the vote's options."""

    @commands.command()
    async def vote(self, ctx, minutes: int, title, *options):
        # basic vote of "For" and "Against" i.e. Like or Dislike
        if len(options) == 0:
            voteEmbed = nextcord.Embed(
                title=title, description=f"You have **{minutes}** minutes remaining!"
            )
            msg = await ctx.send(embed=voteEmbed)
            await msg.add_reaction("👍")
            await msg.add_reaction("👎")

            """If no options are provided, it creates two reactions: 👍 (agree) and 👎 (disagree).
            If options are provided, it creates a numbered field for each option and adds a corresponding reaction."""

        else:
            voteEmbed = nextcord.Embed(
                title=title, description=f"You have **{minutes}** minutes remaining!"
            )
            for number, option in enumerate(options):
                voteEmbed.add_field(
                    name=f"{self.numbers[number]}", value=f"**{option}**", inline=False
                )
            msg = await ctx.send(embed=voteEmbed)

            """Add the corresponding reaction to the embed"""
            for x in range(len(voteEmbed.fields)):
                await msg.add_reaction(self.numbers[x])
        self.vote_loop.start(ctx, minutes, title, options, msg)

    """The poll_loop method is decorated with the tasks.loop(minutes=1) decorator, 
    which specifies that the task should run every minute.
    
    ctx: The context object representing the current Discord interaction.
    minutes: The number of minutes the poll should run for.
    title: The title of the poll.
    options: A list of strings representing the poll options.
    msg: The message containing the poll information and reactions."""

    @tasks.loop(minutes=1)
    async def vote_loop(self, ctx, minutes, title, options, msg):
        count = self.vote_loop.current_loop
        remaining_time = minutes - count

        newEmbed = nextcord.Embed(
            title=title, description=f"You have **{remaining_time}** minutes remaining!"
        )
        for number, option in enumerate(options):
            newEmbed.add_field(
                name=f"{self.numbers[number]}", value=f"**{option}**", inline=False
            )
        # embed updated every minute
        await msg.edit(embed=newEmbed)

        if remaining_time == 0:
            # stop the iterative task
            self.vote_loop.stop()
            counts = []
            # Retrieves the reactions from the cached message.
            msg = nextcord.utils.get(bot.cached_messages, id=msg.id)
            reactions = msg.reactions
            # Counts the occurrences of each reaction.

            for reaction in reactions:
                counts.append(reaction.count)
            """ reactions [<Reaction emoji='1️⃣' me=True count=1>, <Reaction emoji='2️⃣' me=True count=2>]
                count     [1, 2]"""
            max_value = max(counts)
            i = 0
            for count in counts:
                if count == max_value:
                    i = i + 1
            # If there is a tie (multiple reactions with the same highest count), the method announces a draw.
            if i > 1:
                await ctx.send("It's a Draw!")
            # Otherwise, the method announces the winning option (winner) based on the winner index.
            else:
                max_index = counts.index(max_value)
                await ctx.send("Times up!")
                if len(options) == 0:
                    # Emoji of most "counted" reaction
                    winneremoji = reactions[max_index]

                    if winneremoji.emoji == "👍":
                        await ctx.send("Voters agree.")
                    if winneremoji.emoji == "👎":
                        await ctx.send("Voters disagree.")

                else:
                    # Option given in command that has max reaction
                    winner = options[max_index]
                    # Its corresponding reaction
                    winneremoji = reactions[max_index]

                    await ctx.send(
                        f"{winneremoji.emoji} **{winner}** has won the Vote!"
                    )


"""Error Handler to mention that voting options should be less than or equal to 10"""


@MyVote.vote.error
async def errorhandler(cog, ctx, error):
    # cog is MyVote object
    if isinstance(error, commands.CommandInvokeError):
        await ctx.send('Voting options should be less than or equal to ten\n( <= 10 )"')
    if isinstance(error, commands.BadArgument):
        await ctx.send(
            'Kindly check the arguments. Examples:-\n!vote 1 "Is Ronaldo better than Messi?"\n!vote 1 "Which number do you like the most?" One Two Three'
        )


# Call !setup to activate vote command
# @bot.command()
# async def setup(ctx):
#     await bot.add_cog(MyVote(bot))
bot.add_cog(MyVote(bot))
bot.run("MTE2MzM3ODY5MzIzODk1NjAzMg.GK9YJ7.BOT TOKEN")
# CommandInvokeError
