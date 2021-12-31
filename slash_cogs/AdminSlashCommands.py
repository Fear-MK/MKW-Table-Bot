from discord.commands import slash_command, SlashCommandGroup, Option, Permission
from discord.ext import commands as ext_commands
import InteractionUtils
import discord
import commands
import common
# import InteractionExceptions
# import TableBotExceptions


EMPTY_CHAR = '\u200b'

class AdminSlash(ext_commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    # @ext_commands.Cog.listener()
    # async def on_application_command_error(self, ctx, error):
    #     if isinstance(error, discord.ApplicationCommandInvokeError):
    #         orig = error.original
    #         if isinstance(orig, (InteractionExceptions.NoPermission, TableBotExceptions.NotBotAdmin)):
    #             await ctx.send("You don't have permission to use this command - you must be at least a Table Bot Admin.")
    
    sha = SlashCommandGroup("sha", "Configure Table Bot's SHA mappings", guild_ids=common.SLASH_GUILDS, checks=[InteractionUtils.bot_admin_check])

    @sha.command(name="add",
    description="Add a SHA-track mapping"
    )
    async def _add_sha(
        self,
        ctx: discord.ApplicationContext,
        sha: Option(str, "SHA to add"),
        track: Option(str, "Track name (paste the name exactly as it appears)")
    ):
        command, message, this_bot, server_prefix, is_lounge = await InteractionUtils.on_interaction_check(ctx.interaction)
        args = [command, sha, track]
        
        await ctx.respond(EMPTY_CHAR)
        await commands.BotAdminCommands.add_sha_track(message, args, message)

    @sha.command(name="remove",
    description="Remove a SHA-track mapping")
    async def _remove_sha(
        self,
        ctx: discord.ApplicationContext,
        sha: Option(str, "SHA to remove")
    ):
        command, message, this_bot, server_prefix, is_lounge = await InteractionUtils.on_interaction_check(ctx.interaction)
        args = [command, sha]

        await ctx.respond(EMPTY_CHAR)
        await commands.BotAdminCommands.remove_sha_track(message, args)
    
    blacklist = SlashCommandGroup("blacklist", "Configure Table Bot's blacklists", guild_ids=common.SLASH_GUILDS, checks=[InteractionUtils.bot_admin_check])
    blacklist_user = blacklist.create_subgroup("user", "Configure Table Bot's blacklisted users")
    blacklist_word = blacklist.create_subgroup("word", "Configure Table Bot's blacklisted words")

    @blacklist_user.command(name="add",
    description="Blacklist a user from using Table Bot")
    async def _add_user_blacklist(
        self,
        ctx: discord.ApplicationContext,
        user: Option(int, "User's Discord ID"),
        reason: Option(str, "Reason for blacklist")
    ):
        command, message, this_bot, server_prefix, is_lounge = await InteractionUtils.on_interaction_check(ctx.interaction)
        args = [command, user, reason]

        await ctx.respond(EMPTY_CHAR)
        await commands.BotAdminCommands.blacklist_user_command(message, args, command)
    
    @blacklist_user.command(name="remove",
    description="Remove a user from Table Bot's blacklisted users")
    async def _remove_user_blacklist(
        self,
        ctx: discord.ApplicationContext,
        user: Option(int, "User's Discord ID")
    ):
        command, message, this_bot, server_prefix, is_lounge = await InteractionUtils.on_interaction_check(ctx.interaction)
        args = [command, user]

        await ctx.respond(EMPTY_CHAR)
        await commands.BotAdminCommands.blacklist_user_command(message, args, command)

    @blacklist_word.command(name="add",
    description="Blacklist a word from being used with Table Bot")
    async def _add_word_blacklist(
        self, 
        ctx: discord.ApplicationContext,
        word: Option(str, "Word to blacklist")
    ):
        command, message, _, _, _ = await InteractionUtils.on_interaction_check(ctx.interaction)
        args = [command, word]
        await ctx.respond(EMPTY_CHAR)
        await commands.BotAdminCommands.add_blacklisted_word_command(message, args)
    
    @blacklist_word.command(name="remove",
    description="Remove a blacklisted word")
    async def _remove_word_blacklist(
        self, 
        ctx: discord.ApplicationContext,
        word: Option(str, "Word to remove from blacklist")
    ):
        command, message, _, _, _ = await InteractionUtils.on_interaction_check(ctx.interaction)
        args = [command, word]
        await ctx.respond(EMPTY_CHAR)
        await commands.BotAdminCommands.remove_blacklisted_word_command(message, args)
    
    @slash_command(name='global_vr',
    description="Turn the /vr command on or off")
    async def _global_vr(
        self,
        ctx: discord.ApplicationContext,
        status: Option(str, "on/off", choices=["on", "off"])
    ):
        command, message, _, _, _ = await InteractionUtils.on_interaction_check(ctx.interaction)
        status = True if status == 'on' else False
        await ctx.respond(EMPTY_CHAR)
        await commands.BotAdminCommands.global_vr_command(message, on=status)
    

def setup(bot):
    bot.add_cog(AdminSlash(bot))