#!/usr/bin/env python3
"""
Noromaid Integration Module

This module provides an interface for interacting with the Noromaid model
from HuggingFace, handling context management, response caching, and rate
limiting to ensure efficient and effective model interactions.
"""

import os
import time
import json
import hashlib
import asyncio
import logging
from typing import Dict, List, Optional, Union, Any
from datetime import datetime, timedelta
import aiohttp
import requests
from dataclasses import dataclass, field, asdict

# Configure logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("NoromaidIntegration")

@dataclass
class ModelResponse:
    """Data class for storing model responses with metadata."""
    text: str
    timestamp: float = field(default_factory=time.time)
    prompt_hash: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the response to a dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ModelResponse':
        """Create a ModelResponse from a dictionary."""
        return cls(**data)


class ResponseCache:
    """Caches responses from the Noromaid model to reduce API calls."""
    
    def __init__(self, cache_dir: str = ".cache", ttl_minutes: int = 30):
        """Initialize the response cache.
        
        Args:
            cache_dir: Directory to store cache files
            ttl_minutes: Time-to-live for cached responses in minutes
        """
        self.cache_dir = cache_dir
        self.ttl = timedelta(minutes=ttl_minutes)
        
        # Create cache directory if it doesn't exist
        os.makedirs(cache_dir, exist_ok=True)
        logger.info(f"Response cache initialized in {os.path.abspath(cache_dir)}")
    
    def _hash_prompt(self, prompt: str) -> str:
        """Create a hash of the prompt for use as a cache key."""
        return hashlib.md5(prompt.encode()).hexdigest()
    
    def _cache_path(self, prompt_hash: str) -> str:
        """Get the file path for a cached response."""
        return os.path.join(self.cache_dir, f"{prompt_hash}.json")
    
    def get(self, prompt: str) -> Optional[ModelResponse]:
        """Retrieve a cached response if available and not expired.
        
        Args:
            prompt: The prompt text to look up
            
        Returns:
            The cached ModelResponse if available and not expired, None otherwise
        """
        prompt_hash = self._hash_prompt(prompt)
        cache_file = self._cache_path(prompt_hash)
        
        if not os.path.exists(cache_file):
            return None
        
        try:
            with open(cache_file, 'r') as f:
                data = json.load(f)
            
            response = ModelResponse.from_dict(data)
            
            # Check if the cache entry has expired
            if time.time() - response.timestamp > self.ttl.total_seconds():
                logger.debug(f"Cache entry expired for hash {prompt_hash}")
                return None
            
            logger.info(f"Cache hit for prompt hash {prompt_hash}")
            return response
            
        except (json.JSONDecodeError, KeyError) as e:
            logger.warning(f"Error reading cache entry: {e}")
            return None
    
    def save(self, prompt: str, response: ModelResponse) -> None:
        """Save a response to the cache.
        
        Args:
            prompt: The prompt that generated the response
            response: The ModelResponse to cache
        """
        prompt_hash = self._hash_prompt(prompt)
        response.prompt_hash = prompt_hash
        cache_file = self._cache_path(prompt_hash)
        
        try:
            with open(cache_file, 'w') as f:
                json.dump(response.to_dict(), f)
            logger.debug(f"Saved response to cache with hash {prompt_hash}")
        except Exception as e:
            logger.error(f"Failed to save to cache: {e}")


class NoromaidRateLimiter:
    """Manages rate limiting for Noromaid API calls."""
    
    def __init__(self, max_requests_per_minute: int = 5, max_concurrent: int = 3):
        """Initialize the rate limiter.
        
        Args:
            max_requests_per_minute: Maximum number of requests allowed per minute
            max_concurrent: Maximum number of concurrent requests
        """
        self.max_requests_per_minute = max_requests_per_minute
        self.request_times = []
        self.semaphore = asyncio.Semaphore(max_concurrent)
        logger.info(f"Rate limiter initialized: {max_requests_per_minute} req/min, {max_concurrent} concurrent max")
    
    async def wait_for_capacity(self) -> None:
        """Wait until capacity is available to make a request."""
        # Check and remove outdated request timestamps
        now = time.time()
        minute_ago = now - 60
        self.request_times = [t for t in self.request_times if t > minute_ago]
        
        # If at capacity, wait until we can make another request
        while len(self.request_times) >= self.max_requests_per_minute:
            wait_time = self.request_times[0] + 60 - now
            if wait_time > 0:
                logger.info(f"Rate limit reached, waiting {wait_time:.2f} seconds")
                await asyncio.sleep(wait_time)
            
            # Update our timestamps after waiting
            now = time.time()
            minute_ago = now - 60
            self.request_times = [t for t in self.request_times if t > minute_ago]
    
    async def acquire(self) -> None:
        """Acquire permission to make a request."""
        await self.semaphore.acquire()
        await self.wait_for_capacity()
        self.request_times.append(time.time())
    
    def release(self) -> None:
        """Release a request slot."""
        self.semaphore.release()


class NoromaidClient:
    """Client for interacting with the Noromaid model from HuggingFace."""
    
    def __init__(
        self,
        api_token: Optional[str] = None,
        model_name: str = "NeverSleep/Noromaid-13b-v0.3",
        cache_dir: str = ".cache",
        cache_ttl_minutes: int = 30,
        max_requests_per_minute: int = 5,
        max_concurrent_requests: int = 3
    ):
        """Initialize the Noromaid client.
        
        Args:
            api_token: HuggingFace API token (defaults to HUGGINGFACE_TOKEN env var)
            model_name: Name of the model to use
            cache_dir: Directory to store cached responses
            cache_ttl_minutes: Time-to-live for cached responses
            max_requests_per_minute: Maximum requests per minute
            max_concurrent_requests: Maximum concurrent requests
        """
        self.api_token = api_token or os.getenv("HUGGINGFACE_TOKEN")
        if not self.api_token:
            raise ValueError("HuggingFace API token must be provided or set as HUGGINGFACE_TOKEN environment variable")
        
        self.model_name = model_name
        self.api_url = f"https://api-inference.huggingface.co/models/{model_name}"
        self.headers = {"Authorization": f"Bearer {self.api_token}"}
        
        # Initialize cache and rate limiter
        self.cache = ResponseCache(cache_dir=cache_dir, ttl_minutes=cache_ttl_minutes)
        self.rate_limiter = NoromaidRateLimiter(
            max_requests_per_minute=max_requests_per_minute,
            max_concurrent=max_concurrent_requests
        )
        
        # Context management
        self.conversation_history: Dict[str, List[Dict[str, str]]] = {}
        self.max_context_length = 4096  # Maximum context length in tokens (approximate)
        
        logger.info(f"Noromaid client initialized for model: {model_name}")
    
    def _format_prompt(self, prompt: str, conversation_id: Optional[str] = None) -> str:
        """Format the prompt with conversation history if needed."""
        if not conversation_id or conversation_id not in self.conversation_history:
            return prompt
        
        # Simple context formatting - this can be adjusted based on the model's needs
        context = "\n".join([
            f"{'User' if msg['role'] == 'user' else 'Assistant'}: {msg['content']}"
            for msg in self.conversation_history[conversation_id][-5:]  # Use last 5 exchanges
        ])
        
        return f"{context}\nUser: {prompt}"
    
    def _update_conversation_history(
        self, 
        conversation_id: str, 
        prompt: str, 
        response: str
    ) -> None:
        """Update the conversation history with a new exchange."""
        if conversation_id not in self.conversation_history:
            self.conversation_history[conversation_id] = []
        
        # Add the new messages
        self.conversation_history[conversation_id].append({"role": "user", "content": prompt})
        self.conversation_history[conversation_id].append({"role": "assistant", "content": response})
        
        # Simple truncation strategy - can be improved with more sophisticated token counting
        if len(self.conversation_history[conversation_id]) > 20:  # Keep last 10 exchanges
            self.conversation_history[conversation_id] = self.conversation_history[conversation_id][-20:]
    
    def query_sync(
        self, 
        prompt: str, 
        conversation_id: Optional[str] = None,
        use_cache: bool = True,
        **model_params
    ) -> ModelResponse:
        """Query the Noromaid model synchronously.
        
        Args:
            prompt: The prompt to send to the model
            conversation_id: Optional ID for conversation context
            use_cache: Whether to use cached responses
            **model_params: Additional parameters to send to the model API
            
        Returns:
            A ModelResponse object containing the model's response
        """
        # Check cache first if enabled
        if use_cache:
            cached_response = self.cache.get(prompt)
            if cached_response:
                if conversation_id:
                    self._update_conversation_history(
                        conversation_id, prompt, cached_response.text
                    )
                return cached_response
        
        # Format prompt with conversation history if needed
        formatted_prompt = self._format_prompt(prompt, conversation_id)
        
        # Prepare the payload
        payload = {"inputs": formatted_prompt, **model_params}
        
        try:
            # Make the API request
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            
            # Parse the response
            data = response.json()
            if isinstance(data, list) and len(data) > 0:
                generated_text = data[0].get('generated_text', '')
                
                # Clean up the response if needed
                if formatted_prompt in generated_text:
                    generated_text = generated_text[len(formatted_prompt):].strip()
                
                model_response = ModelResponse(
                    text=generated_text,
                    metadata={"raw_response": data}
                )
                
                # Update conversation history if needed
                if conversation_id:
                    self._update_conversation_history(
                        conversation_id, prompt, model_response.text
                    )
                
                # Cache the response if enabled
                if use_cache:
                    self.cache.save(prompt, model_response)
                
                return model_response
            else:
                error_msg = "Invalid response format from API"
                logger.error(error_msg)
                return ModelResponse(text=f"Error: {error_msg}")
                
        except requests.exceptions.RequestException as e:
            error_msg = f"Request error: {str(e)}"
            logger.error(error_msg)
            return ModelResponse(text=f"Error: {error_msg}")
    
    async def query_async(
        self, 
        prompt: str, 
        conversation_id: Optional[str] = None,
        use_cache: bool = True,
        **model_params
    ) -> ModelResponse:
        """Query the Noromaid model asynchronously with rate limiting.
        
        Args:
            prompt: The prompt to send to the model
            conversation_id: Optional ID for conversation context
            use_cache: Whether to use cached responses
            **model_params: Additional parameters to send to the model API
            
        Returns:
            A ModelResponse object containing the model's response
        """
        # Check cache first if enabled
        if use_cache:
            cached_response = self.cache.get(prompt)
            if cached_response:
                if conversation_id:
                    self._update_conversation_history(
                        conversation_id, prompt, cached_response.text
                    )
                return cached_response
        
        # Format prompt with conversation history if needed
        formatted_prompt = self._format_prompt(prompt, conversation_id)
        
        # Prepare the payload
        payload = {"inputs": formatted_prompt, **model_params}
        
        try:
            # Acquire a rate limit slot
            await self.rate_limiter.acquire()
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.api_url,
                    headers=self.headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    response.raise_for_status()
                    data = await response.json()
            
            # Release the rate limit slot
            self.rate_limiter.release()
            
            # Parse the response
            if isinstance(data, list) and len(data) > 0:
                generated_text = data[0].get('generated_text', '')
                
                # Clean up the response if needed
                if formatted_prompt in generated_text:
                    generated_text = generated_text[len(formatted_prompt):].strip()
                
                model_response = ModelResponse(
                    text=generated_text,
                    metadata={"raw_response": data}
                )
                
                # Update conversation history if needed
                if conversation_id:
                    self._update_conversation_history(
                        conversation_id, prompt, model_response.text
                    )
                
                # Cache the response if enabled
                if use_cache:
                    self.cache.save(prompt, model_response)
                
                return model_response
            else:
                error_msg = "Invalid response format from API"
                logger.error(error_msg)
                return ModelResponse(text=f"Error: {error_msg}")
                
        except Exception as e:
            # Release the rate limit slot in case of error
            self.rate_limiter.release()
            
            error_msg = f"Request error: {str(e)}"
            logger.error(error_msg)
            return ModelResponse(text=f"Error: {error_msg}")
    
    def create_conversation(self) -> str:
        """Create a new conversation and return its ID."""
        conversation_id = hashlib.md5(f"{time.time()}_{os.urandom(8).hex()}".encode()).hexdigest()
        self.conversation_history[conversation_id] = []
        return conversation_id
    
    def clear_conversation(self, conversation_id: str) -> bool:
        """Clear a conversation history.
        
        Args:
            conversation_id: The ID of the conversation to clear
            
        Returns:
            True if the conversation was found and cleared, False otherwise
        """
        if conversation_id in self.conversation_history:
            self.conversation_history[conversation_id] = []
            return True
        return False
    
    def delete_conversation(self, conversation_id: str) -> bool:
        """Delete a conversation.
        
        Args:
            conversation_id: The ID of the conversation to delete
            
        Returns:
            True if the conversation was found and deleted, False otherwise
        """
        if conversation_id in self.conversation_history:
            del self.conversation_history[conversation_id]
            return True
        return False


class NoromaidDiscordBot:
    """Integration class for running a Discord bot with Noromaid."""
    
    def __init__(
        self,
        discord_token: Optional[str] = None,
        huggingface_token: Optional[str] = None,
        command_prefix: str = "!ask",
        model_name: str = "NeverSleep/Noromaid-13b-v0.3",
        max_requests_per_minute: int = 5,
    ):
        """Initialize the Discord bot with Noromaid integration.
        
        Args:
            discord_token: Discord bot token
            huggingface_token: HuggingFace API token
            command_prefix: Command prefix for bot commands
            model_name: Name of the Noromaid model to use
            max_requests_per_minute: Maximum requests per minute
        """
        self.discord_token = discord_token or os.getenv("DISCORD_TOKEN")
        if not self.discord_token:
            raise ValueError("Discord token must be provided or set as DISCORD_TOKEN environment variable")
            
        self.command_prefix = command_prefix
        
        # Initialize Discord client
        import discord
        intents = discord.Intents.default()
        intents.message_content = True
        self.client = discord.Client(intents=intents)
        
        # Initialize Noromaid client
        self.noromaid = NoromaidClient(
            api_token=huggingface_token,
            model_name=model_name,
            max_requests_per_minute=max_requests_per_minute
        )
        
        # Map Discord channels to conversation IDs
        self.channel_conversations: Dict[int, str] = {}
        
        # Set up event handlers
        self._setup_event_handlers()
        
        logger.info(f"Noromaid Discord bot initialized with command prefix: {command_prefix}")
    
    def _setup_event_handlers(self):
        """Set up Discord event handlers."""
        @self.client.event
        async def on_ready():
            logger.info(f"Logged in as {self.client.user}")
        
        @self.client.event
        async def on_message(message):
            # Ignore messages from the bot itself
            if message.author == self.client.user:
                return
            
            # Check if the message starts with the command prefix
            if message.content.startswith(self.command_prefix):
                await self._handle_ask_command(message)
    
    async def _handle_ask_command(self, message):
        """Handle the ask command from a Discord message."""
        prompt = message.content[len(self.command_prefix):].strip()
        if not prompt:
            await message.channel.send(f"Please provide a prompt after '{self.command_prefix}'.")
            return
        
        # Get or create conversation ID for this channel
        channel_id = message.channel.id
        if channel_id not in self.channel_conversations:
            self.channel_conversations[channel_id] = self.noromaid.create_conversation()
        
        conversation_id = self.channel_conversations[channel_id]
        
        # Show typing indicator
        async with message.channel.typing():
            try:
                # Query the model
                response = await self.noromaid.query_async(
                    prompt=prompt,
                    conversation_id=conversation_id
                )
                
                # Send the response
                if response.text:
                    # Split into chunks if too long
                    if len(response.text) > 2000:
                        chunks = [response.text[i:i+1900] for i in range(0, len(response.text), 1900)]
                        for i, chunk in enumerate(chunks):
                            prefix = "..." if i > 0 else ""
                            suffix = "..." if i < len(chunks) - 1 else ""
                            await message.channel.send(f"{prefix}{chunk}{suffix}")
                    else:
                        await message.channel.send(response.text)
                else:
                    await message.channel.send("I couldn't generate a response. Please try again.")
                    
            except Exception as e:
                logger.error(f"Error handling message: {e}")
                await message.channel.send(f"An error occurred: {str(e)}")
    
    def run(self):
        """Run the Discord bot."""
        logger.info("Starting Discord bot")
        self.client.run(self.discord_token)


if __name__ == "__main__":
    # Example usage of the module
    discord_token = os.getenv("DISCORD_TOKEN")
    huggingface_token = os.getenv("HUGGINGFACE_TOKEN")
    
    if discord_token and huggingface_token:
        bot = NoromaidDiscordBot(
            discord_token=discord_token,
            huggingface_token=huggingface_token
        )
        bot.run()
    else:
        logger.error("Missing required environment variables: DISCORD_TOKEN and/or HUGGINGFACE_TOKEN")
