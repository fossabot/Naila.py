from discord.ext import commands

from bot import Bot
from utils.ctx import Context
from utils.database.Reminders import Reminders as Reminder
from utils.functions.text import escape, pagify
from utils.functions.time import get_relative_delta, parse_time


class Reminders(commands.Cog):
    def __init__(self, bot):
        self.bot: Bot = bot

    @commands.group(case_insensitive=True)
    async def remind(self, ctx: Context):
        if not ctx.invoked_subcommand:
            await ctx.send_help(ctx.command)

    @remind.command(name="me")
    async def remind_me(self, ctx: Context, time: str, *, reminder: str):
        if len(reminder) > 1500:
            return await ctx.send_error("That's quite a long reminder... let's slow down a bit!")
        await Reminder(ctx).add(ctx.author.id, time, reminder)
        await ctx.reply(
            f"{ctx.author.mention}, I will remind you about this"
            f" {get_relative_delta(parse_time(time), append_small=True, bold_string=True)}"
        )

    @remind.command(name="here")
    async def remind_here(self, ctx: Context, time: str, *, reminder: str):
        if len(reminder) > 1500:
            return await ctx.send_error("That's quite a long reminder... let's slow down a bit!")
        await Reminder(ctx).add(ctx.channel.id, time, escape(reminder, False, False, False))
        await ctx.reply(
            f"{ctx.author.mention}, I will remind you about this"
            f" {get_relative_delta(parse_time(time), append_small=True, bold_string=True)}"
        )

    @commands.command()
    async def reminders(self, ctx: Context):
        reminders = await Reminder(ctx).list()
        to_send = "**Your reminders:**\n"
        if reminders:
            for reminder in reminders:
                if reminder["channel_id"] == ctx.author.id:
                    location = "Private Messages"
                else:
                    location = f"<#{reminder['channel_id']}>"
                to_send += f"\n**{reminder['id']}**: {location}: \"{reminder['reminder']}\" -" \
                           f" {get_relative_delta(reminder['expires'], append_small=True, append_seconds=False)}"
        else:
            to_send += "\n**You don't currently have any reminders set!**"
        to_send += f"\n\nSet a reminder with `{ctx.prefix}remind <here|me> <time> <reminder>`\n" \
                   f"Remove a reminder with `{ctx.prefix}delreminder <id>`"
        pages = pagify(to_send)
        for page in pages:
            await ctx.reply(page)

    @commands.command(aliases=["delreminder"])
    async def deletereminder(self, ctx: Context, reminder_id: int):
        deleted = await Reminder(ctx).delete(reminder_id)
        if deleted == "UPDATE 1":
            return await ctx.reply("I have deleted that reminder!")
        await ctx.send_error("Hmm I couldn't seem to find that reminder for you, make sure the id is correct!")


def setup(bot):
    bot.add_cog(Reminders(bot))
