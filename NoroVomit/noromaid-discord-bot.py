import discord
import asyncio
import logging
import os
import sys
import json
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Import custom modules
from noromaid_integration import NoromaidInterface, ModelResponse
from luminous_guardians import NoromaidGuardian

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("noromaid_bot.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("NoromaidDiscordBot")

# Load environment variables
load_dotenv()

class NoromaidDiscordBot:
    """Discord bot that interfaces with the Noromaid model."""
    
    def __init__(self):
        """Initialize the Discord bot with appropriate intents and connections."""
        # Configure Discord client with necessary intents
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True  # For server member awareness
        self.client = discord.Client(intents=intents)
        
        # Set up command prefix
        self.command_prefix = "!ask"
        
        # Initialize Noromaid model interfaces
        self.noromaid = NoromaidInterface(use_cache=True)
        self.guardian = NoromaidGuardian()
        
        # Track active channels for persistent conversations
        self.active_conversations = {}
        
        # Configure event handlers
        self.setup_event_handlers()
        
        logger.info("Noromaid Discord Bot initialized")
    
    def setup_event_handlers(self) -> None:
        """Set up Discord event handlers."""
        @self.client.event
        async def on_ready():
            logger.info(f"Bot connected as {self.client.user}")
            # Set bot status
            activity = discord.Activity(type=discord.ActivityType.listening, name="!ask commands")
            await self.client.change_presence(activity=activity)
        
        @self.client.event
        async def on_message(message):
            # Ignore messages from the bot itself
            if message.author == self.client.user:
                return
            
            await self.process_message(message)
    
    async def process_message(self, message) -> None:
        """Process incoming Discord messages."""
        # Check if the message starts with the command prefix
        if message.content.startswith(self.command_prefix):
            await self.handle_ask_command(message)
        
        # Check if this is a follow-up message in an active conversation
        elif message.channel.id in self.active_conversations:
            # Only process if the last message in this channel was from the bot
            last_message = await self.get_last_bot_message(message.channel)
            if last_message and not message.content.startswith("!"):
                # This is a follow-up in conversation
                await self.handle_conversation_follow_up(message)
    
    async def get_last_bot_message(self, channel) -> Optional[discord.Message]:
        """Get the last message sent by the bot in the channel."""
        async for msg in channel.history(limit=5):
            if msg.author == self.client.user:
                return msg
        return None
    
    async def handle_ask_command(self, message) -> None:
        """Handle !ask commands."""
        # Extract the prompt from the message
        prompt = message.content[len(self.command_prefix):].strip()
        
        if not prompt:
            await message.channel.send("Please provide a query after the `!ask` command.")
            return
        
        # Special commands
        if prompt.lower() == "help":
            await self.send_help_message(message.channel)
            return
        elif prompt.lower() == "reset":
            if message.channel.id in self.active_conversations:
                self.noromaid.clear_history()
                del self.active_conversations[message.channel.id]
                await message.channel.send("🔄 Conversation history has been reset.")
            else:
                await message.channel.send("No active conversation to reset.")
            return
        
        # Prepare typing indicator to show the bot is processing
        async with message.channel.typing():
            try:
                # Track this as an active conversation
                self.active_conversations[message.channel.id] = {
                    "last_interaction": asyncio.get_event_loop().time(),
                    "user_id": message.author.id
                }
                
                # Apply security rituals via guardian
                protected_prompt = self.guardian.protect_prompt(prompt)
                
                # Query the model with history for continuity
                response = await self.noromaid.query(prompt, use_history=True)
                
                # Apply security analysis to the response
                analyzed_response = self.guardian.analyze_response(response.text)
                
                # Send the response, splitting if necessary
                await self.send_response(message.channel, analyzed_response)
                
            except Exception as e:
                logger.error(f"Error processing command: {e}")
                await message.channel.send(f"⚠️ I encountered an error while processing your request: {str(e)}")
    
    async def handle_conversation_follow_up(self, message) -> None:
        """Handle follow-up messages in an active conversation."""
        prompt = message.content
        
        # Prepare typing indicator
        async with message.channel.typing():
            try:
                # Apply security rituals
                protected_prompt = self.guardian.protect_prompt(prompt)
                
                # Query the model (with history since this is a follow-up)
                response = await self.noromaid.query(prompt, use_history=True)
                
                # Apply security analysis
                analyzed_response = self.guardian.analyze_response(response.text)
                
                # Send the response
                await self.send_response(message.channel, analyzed_response)
                
                # Update last interaction time
                self.active_conversations[message.channel.id]["last_interaction"] = asyncio.get_event_loop().time()
                
            except Exception as e:
                logger.error(f"Error processing follow-up: {e}")
                await message.channel.send(f"⚠️ I encountered an error: {str(e)}")
    
    async def send_response(self, channel, response_text: str) -> None:
        """Send a response to Discord, splitting if necessary."""
        # Discord has a 2000 character limit per message
        if len(response_text) <= 1900:
            await channel.send(response_text)
        else:
            # Split the response into chunks
            chunks = self.split_response(response_text)
            for chunk in chunks:
                await channel.send(chunk)
    
    def split_response(self, text: str, max_length: int = 1900) -> list:
        """Split a long response into chunks that fit within Discord's limits."""
        chunks = []
        current_chunk = ""
        
        for paragraph in text.split("\n\n"):
            # If adding this paragraph would exceed the max length, save the chunk and start a new one
            if len(current_chunk) + len(paragraph) + 2 > max_length:
                if current_chunk:
                    chunks.append(current_chunk)
                current_chunk = paragraph
            else:
                if current_chunk:
                    current_chunk += "\n\n" + paragraph
                else:
                    current_chunk = paragraph
        
        # Add the final chunk
        if current_chunk:
            chunks.append(current_chunk)
        
        return chunks
    
    async def send_help_message(self, channel) -> None:
        """Send help information about how to use the bot."""
        help_text = """
**🌟 Noromaid Discord Bot - Help Guide 🌟**

This bot allows you to interact with the Noromaid AI model. Here's how to use it:

**Basic Commands:**
• `!ask <your question>` - Ask the AI a question or give it a prompt
• `!ask help` - Show this help message
• `!ask reset` - Reset the conversation history

**Conversation Mode:**
After using `!ask`, you can continue the conversation by simply typing follow-up messages without any command prefix. The bot will remember the context of your conversation.

**Examples:**
• `!ask What is the best way to secure a Discord bot?`
• `!ask Tell me about the Noromaid model.`
• `!ask Write a short poem about digital entities.`

The bot uses advanced security measures to protect both inputs and outputs, ensuring safe interactions.
"""
        await channel.send(help_text)
    
    async def cleanup_stale_conversations(self) -> None:
        """Periodically clean up stale conversations to free resources."""
        while True:
            current_time = asyncio.get_event_loop().time()
            stale_channels = []
            
            # Find conversations inactive for more than 30 minutes
            for channel_id, data in self.active_conversations.items():
                if current_time - data["last_interaction"] > 1800:  # 30 minutes
                    stale_channels.append(channel_id)
            
            # Remove stale conversations
            for channel_id in stale_channels:
                logger.info(f"Cleaning up stale conversation in channel {channel_id}")
                del self.active_conversations[channel_id]
            
            # Check every 5 minutes
            await asyncio.sleep(300)
    
    def run(self) -> None:
        """Run the Discord bot."""
        token = os.getenv("DISCORD_TOKEN")
        if not token:
            logger.error("No Discord token found. Set the DISCORD_TOKEN environment variable.")
            return
        
        try:
            # Start background tasks
            self.client.loop.create_task(self.cleanup_stale_conversations())
            
            # Connect to Discord
            logger.info("Starting Discord bot...")
            self.client.run(token)
            
        except Exception as e:
            logger.error(f"Error running Discord bot: {e}")


if __name__ == "__main__":
    bot = NoromaidDiscordBot()
    bot.run()
