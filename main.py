import discord
from discord.ext import commands, tasks
import os
import random
from datetime import datetime, timezone
from dotenv import load_dotenv
import logging
import asyncio

# Load environment variables
load_dotenv()

# Bot configuration
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Global variables
announcements_enabled = True
announcement_channel_id = None

# List of announcement messages
ANNOUNCEMENT_MESSAGES = [
    "Flip 'em all—charge!",
    "Flip 'em all—strike now!",
    "Flip 'em all—attack together!",
    "Flip 'em all—show no mercy!",
    "Flip 'em all—dominate!",
    "Flip 'em all—unleash the Pride!",
    "Flip 'em all—crush them!",
    "Flip 'em all—hold nothing back!",
    "Flip 'em all—claws forward!",
    "Flip 'em all—victory is ours!"
]

@bot.event
async def on_ready():
    """Called when the bot is ready and connected to Discord."""
    print(f'{bot.user} has connected to Discord!')
    print(f'Bot is in {len(bot.guilds)} guild(s)')
    
    # Start the announcement scheduler
    if not announcement_scheduler.is_running():
        announcement_scheduler.start()

@bot.command(name='setchannel')
@commands.has_permissions(administrator=True)
async def set_announcement_channel(ctx):
    """Set the current channel as the announcement channel."""
    global announcement_channel_id
    announcement_channel_id = ctx.channel.id
    await ctx.send(f'✅ Announcement channel set to {ctx.channel.mention}')
    print(f'Announcement channel set to: {ctx.channel.name} (ID: {announcement_channel_id})')

@bot.command(name='announcements')
@commands.has_permissions(administrator=True)
async def toggle_announcements(ctx, status: str = None):
    """Toggle announcements on/off or check current status."""
    global announcements_enabled
    
    if status is None:
        # Show current status
        status_text = "enabled" if announcements_enabled else "disabled"
        await ctx.send(f'📢 Announcements are currently **{status_text}**')
        return
    
    if status.lower() in ['on', 'enable', 'true', '1']:
        announcements_enabled = True
        await ctx.send('✅ Announcements have been **enabled**')
        print('Announcements enabled')
    elif status.lower() in ['off', 'disable', 'false', '0']:
        announcements_enabled = False
        await ctx.send('❌ Announcements have been **disabled**')
        print('Announcements disabled')
    else:
        await ctx.send('❌ Invalid status. Use: `on`, `off`, `enable`, or `disable`')

@bot.command(name='test')
@commands.has_permissions(administrator=True)
async def test_announcement(ctx):
    """Send a test announcement to verify the bot is working."""
    if announcement_channel_id is None:
        await ctx.send('❌ No announcement channel set. Use `!setchannel` first.')
        return
    
    message = random.choice(ANNOUNCEMENT_MESSAGES)
    channel = bot.get_channel(announcement_channel_id)
    
    if channel:
        await channel.send(f'🧪 **TEST ANNOUNCEMENT:** {message}')
        await ctx.send('✅ Test announcement sent!')
    else:
        await ctx.send('❌ Could not find the announcement channel.')

@bot.command(name='status')
async def bot_status(ctx):
    """Show the current bot status and configuration."""
    status_text = "enabled" if announcements_enabled else "disabled"
    channel_info = "Not set" if announcement_channel_id is None else f"<#{announcement_channel_id}>"
    
    embed = discord.Embed(
        title="🤖 FoE Rally Bot Status",
        color=discord.Color.blue(),
        timestamp=datetime.now(timezone.utc)
    )
    embed.add_field(name="Announcements", value=status_text, inline=True)
    embed.add_field(name="Announcement Channel", value=channel_info, inline=True)
    embed.add_field(name="Next Announcement", value="3 minutes before the next hour", inline=False)
    embed.add_field(name="Available Messages", value=f"{len(ANNOUNCEMENT_MESSAGES)} different messages", inline=True)
    
    await ctx.send(embed=embed)

@tasks.loop(minutes=1)
async def announcement_scheduler():
    """Check every minute if it's time to send an announcement."""
    global announcements_enabled, announcement_channel_id
    
    if not announcements_enabled or announcement_channel_id is None:
        return
    
    now = datetime.now(timezone.utc)
    
    # Check if it's 3 minutes before the hour (57 minutes past the hour)
    if now.minute == 57:
        channel = bot.get_channel(announcement_channel_id)
        if channel:
            message = random.choice(ANNOUNCEMENT_MESSAGES)
            try:
                await channel.send(f'⚔️ **RALLY CALL:** {message}')
                print(f'Announcement sent at {now.strftime("%H:%M:%S")}: {message}')
            except Exception as e:
                print(f'Error sending announcement: {e}')

@announcement_scheduler.before_loop
async def before_announcement_scheduler():
    """Wait until the bot is ready before starting the scheduler."""
    await bot.wait_until_ready()

@bot.event
async def on_command_error(ctx, error):
    """Handle command errors gracefully."""
    if isinstance(error, commands.MissingPermissions):
        await ctx.send('❌ You need administrator permissions to use this command.')
    elif isinstance(error, commands.CommandNotFound):
        await ctx.send('❌ Command not found. Use `!help` to see available commands.')
    else:
        await ctx.send(f'❌ An error occurred: {str(error)}')

# Error handling for the scheduler
@announcement_scheduler.error
async def announcement_scheduler_error(error):
    """Handle errors in the announcement scheduler."""
    print(f'Error in announcement scheduler: {error}')

if __name__ == "__main__":
    # Get the Discord token from environment variables
    token = os.getenv('DISCORD_TOKEN')
    
    if not token:
        print("❌ Error: DISCORD_TOKEN not found in environment variables!")
        print("Please create a .env file with your Discord bot token:")
        print("DISCORD_TOKEN=your_bot_token_here")
        exit(1)
    
    print("🤖 Starting FoE Rally Bot...")
    print("📢 Bot will send announcements 3 minutes before every hour")
    print("🔧 Use !help to see available commands")
    
    # Run the bot
    bot.run(token)
