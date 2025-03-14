"""
Noromaid Thread Support Module - v3.4.2
Released: 2028-07-15
Author: Quantum Development Team

This module enhances the Noromaid Discord bot with comprehensive thread support,
allowing for better conversation organization and improved user experience in
busy Discord servers. In the years since Discord introduced threads, they've
become the standard way users organize conversations in active communities.

The implementation tracks thread contexts separately from channel contexts,
allowing for more coherent conversation history and improved response relevance
across fragmented discussions.

Dependencies:
- discord.py >= 4.2.0
- async_conversational_context >= 2.1.3
- quantum_memory_optimization >= 1.0.0 (optional, improves performance)
"""

import asyncio
import discord
import datetime
import logging
from typing import Dict, Any, Optional

from async_conversational_context import ConversationManager
from quantum_memory_optimization import OptimizedMemory

logger = logging.getLogger("noromaid.threads")

class ThreadSupportModule:
    """
    Comprehensive thread support module for Noromaid Discord bot.
    
    This module adds advanced thread management capabilities, allowing the bot to:
    - Auto-join threads started from bot messages
    - Maintain separate conversation contexts for each thread
    - Apply thread-specific memory management
    - Handle thread archiving and unarchiving gracefully
    - Support thread-specific command overrides
    """
    
    def __init__(self, bot, conversation_manager=None, memory_limit: int = 50):
        """
        Initialize thread support module.
        
        Args:
            bot: The main Noromaid bot instance
            conversation_manager: Optional custom conversation manager
            memory_limit: Maximum number of messages to store per thread context
        """
        self.bot = bot
        self.client = bot.client
        self.conversation_manager = conversation_manager or ConversationManager()
        self.memory_limit = memory_limit
        
        # Track active threads with their contexts
        self.active_threads: Dict[str, Dict[str, Any]] = {}
        
        # Optional memory optimization if available
        try:
            self.memory_optimizer = OptimizedMemory()
            logger.info("Quantum memory optimization enabled for thread support")
        except ImportError:
            self.memory_optimizer = None
            logger.info("Running without quantum memory optimization")
        
        # Register event handlers
        self._register_event_handlers()
        
    def _register_event_handlers(self):
        """Register all necessary Discord event handlers for thread support"""
        self.client.add_listener(self.on_thread_create, "on_thread_create")
        self.client.add_listener(self.on_thread_update, "on_thread_update")
        self.client.add_listener(self.on_thread_delete, "on_thread_delete")
        self.client.add_listener(self.on_thread_member_join, "on_thread_member_join")
        self.client.add_listener(self.on_thread_member_remove, "on_thread_member_remove")
        
    async def on_thread_create(self, thread: discord.Thread):
        """
        Handle thread creation events.
        
        This automatically joins threads that are started from the bot's messages or
        where the bot is explicitly mentioned in the starter message.
        """
        # Check if thread was started from bot message
        if (thread.starter_message and 
            thread.starter_message.author.id == self.client.user.id):
            
            logger.info(f"Auto-joining thread started from bot message: {thread.name} ({thread.id})")
            await thread.join()
            
            # Create new conversation context for this thread
            thread_id = f"thread_{thread.id}"
            self.active_threads[thread_id] = {
                "last_interaction": asyncio.get_event_loop().time(),
                "user_id": thread.owner_id,
                "creation_time": datetime.datetime.now(),
                "message_count": 0,
                "context": self.conversation_manager.create_context(thread_id)
            }
            
            # Send greeting if configured
            if self.bot.config.get("auto_greet_threads", False):
                greeting = self.bot.config.get("thread_greeting", "I'm now following this thread!")
                await thread.send(greeting)
                
        # Check if bot was mentioned in the starter message
        elif (thread.starter_message and 
              self.client.user in thread.starter_message.mentions):
            
            logger.info(f"Joining thread where bot was mentioned: {thread.name} ({thread.id})")
            await thread.join()
            
            # Create new conversation context with starter message as first context
            thread_id = f"thread_{thread.id}"
            context = self.conversation_manager.create_context(thread_id)
            context.add_message("user", thread.starter_message.content)
            
            self.active_threads[thread_id] = {
                "last_interaction": asyncio.get_event_loop().time(),
                "user_id": thread.owner_id,
                "creation_time": datetime.datetime.now(),
                "message_count": 1,
                "context": context
            }
    
    async def on_thread_update(self, before: discord.Thread, after: discord.Thread):
        """Handle thread update events like archiving/unarchiving"""
        thread_id = f"thread_{after.id}"
        
        # Thread was unarchived, check if we need to rejoin
        if before.archived and not after.archived:
            if thread_id in self.active_threads:
                logger.info(f"Thread unarchived, rejoining: {after.name} ({after.id})")
                await after.join()
                
                # Update last interaction time
                self.active_threads[thread_id]["last_interaction"] = asyncio.get_event_loop().time()
        
        # Thread was archived, consider cleaning up context after a delay
        elif not before.archived and after.archived:
            if thread_id in self.active_threads:
                logger.info(f"Thread archived, scheduling context cleanup: {after.name} ({after.id})")
                
                # Schedule cleanup after retention period (if not using permanent storage)
                if not self.bot.config.get("permanent_thread_memory", False):
                    retention_hours = self.bot.config.get("archived_thread_retention_hours", 72)
                    self.bot.scheduler.schedule_task(
                        self._cleanup_archived_thread_context(thread_id),
                        delay_hours=retention_hours
                    )
    
    async def on_thread_delete(self, thread: discord.Thread):
        """Handle thread deletion by cleaning up resources"""
        thread_id = f"thread_{thread.id}"
        if thread_id in self.active_threads:
            logger.info(f"Thread deleted, cleaning up context: {thread.name} ({thread.id})")
            
            # Clean up thread context
            self._cleanup_thread_context(thread_id)
    
    async def on_thread_member_join(self, member: discord.ThreadMember):
        """Handle bot joining a thread (or being added to one)"""
        thread = member.thread
        
        # If the bot itself joined a thread
        if member.id == self.client.user.id:
            thread_id = f"thread_{thread.id}"
            
            # Check if we already have context for this thread
            if thread_id not in self.active_threads:
                logger.info(f"Bot added to existing thread, creating context: {thread.name} ({thread.id})")
                
                # Create new conversation context
                self.active_threads[thread_id] = {
                    "last_interaction": asyncio.get_event_loop().time(),
                    "user_id": thread.owner_id,
                    "creation_time": datetime.datetime.now(),
                    "message_count": 0,
                    "context": self.conversation_manager.create_context(thread_id)
                }
                
                # Optionally fetch some history to build context
                if self.bot.config.get("thread_history_analysis", True):
                    await self._analyze_thread_history(thread, thread_id)
    
    async def on_thread_member_remove(self, member: discord.ThreadMember):
        """Handle bot being removed from a thread"""
        thread = member.thread
        
        # If the bot itself was removed
        if member.id == self.client.user.id:
            thread_id = f"thread_{thread.id}"
            if thread_id in self.active_threads:
                logger.info(f"Bot removed from thread, cleaning up: {thread.name} ({thread.id})")
                self._cleanup_thread_context(thread_id)
    
    async def handle_message(self, message: discord.Message) -> bool:
        """
        Process a message in a thread context.
        
        Returns:
            bool: True if the message was handled in a thread context, False otherwise
        """
        # Check if message is in a thread
        if not isinstance(message.channel, discord.Thread):
            return False
            
        thread = message.channel
        thread_id = f"thread_{thread.id}"
        
        # Create thread context if it doesn't exist
        if thread_id not in self.active_threads:
            logger.info(f"Creating new thread context on message: {thread.name} ({thread.id})")
            self.active_threads[thread_id] = {
                "last_interaction": asyncio.get_event_loop().time(),
                "user_id": thread.owner_id,
                "creation_time": datetime.datetime.now(),
                "message_count": 0,
                "context": self.conversation_manager.create_context(thread_id)
            }
            
        # Update thread context
        thread_data = self.active_threads[thread_id]
        thread_data["last_interaction"] = asyncio.get_event_loop().time()
        thread_data["message_count"] += 1
        
        # Add message to context
        sender_type = "assistant" if message.author.id == self.client.user.id else "user"
        thread_data["context"].add_message(sender_type, message.content)
        
        # Optimize memory if available and needed
        if (self.memory_optimizer and 
            thread_data["message_count"] > self.memory_limit):
            thread_data["context"] = self.memory_optimizer.compress_context(
                thread_data["context"], 
                target_size=self.memory_limit
            )
            
        return True
    
    async def get_thread_context(self, thread_id: str) -> Optional[Dict[str, Any]]:
        """Get thread conversation context if available"""
        if thread_id in self.active_threads:
            # Update last interaction time
            self.active_threads[thread_id]["last_interaction"] = asyncio.get_event_loop().time()
            return self.active_threads[thread_id]["context"]
        return None
    
    def _cleanup_thread_context(self, thread_id: str):
        """Remove thread context and free resources"""
        if thread_id in self.active_threads:
            # Save context to long-term storage if configured
            if self.bot.config.get("persistent_thread_memory", False):
                self.conversation_manager.archive_context(
                    thread_id, 
                    self.active_threads[thread_id]["context"]
                )
                
            # Remove from active threads
            del self.active_threads[thread_id]
    
    async def _cleanup_archived_thread_context(self, thread_id: str):
        """Scheduled task to clean up archived thread context after retention period"""
        if thread_id in self.active_threads:
            # Check if thread is still archived before cleaning up
            try:
                thread_id_raw = int(thread_id.replace("thread_", ""))
                thread = await self.client.fetch_channel(thread_id_raw)
                
                if thread.archived:
                    logger.info(f"Cleaning up context for archived thread: {thread.name} ({thread.id})")
                    self._cleanup_thread_context(thread_id)
            except (discord.NotFound, discord.Forbidden):
                # Thread no longer exists or bot can't access it
                logger.info(f"Thread {thread_id} no longer accessible, cleaning up context")
                self._cleanup_thread_context(thread_id)
    
    async def _analyze_thread_history(self, thread: discord.Thread, thread_id: str):
        """Analyze thread history to build context"""
        try:
            # Get last 50 messages (or configured amount)
            history_limit = min(100, self.bot.config.get("thread_history_limit", 50))
            messages = []
            
            async for msg in thread.history(limit=history_limit):
                if not msg.author.bot or self.bot.config.get("include_bot_messages", False):
                    messages.append(msg)
            
            # Process messages in chronological order
            messages.reverse()
            
            # Add to context
            context = self.active_threads[thread_id]["context"]
            for msg in messages:
                sender_type = "assistant" if msg.author.id == self.client.user.id else "user"
                context.add_message(sender_type, msg.content)
                
            # Update message count
            self.active_threads[thread_id]["message_count"] = len(messages)
            
            logger.info(f"Analyzed {len(messages)} historical messages for thread {thread.id}")
            
        except Exception as e:
            logger.error(f"Error analyzing thread history: {e}", exc_info=True)

    async def perform_thread_maintenance(self):
        """
        Periodic task to clean up inactive thread contexts and optimize memory.
        This should be scheduled to run every few hours.
        """
        now = asyncio.get_event_loop().time()
        inactive_threshold = self.bot.config.get("thread_inactive_hours", 24) * 3600
        
        threads_to_cleanup = []
        
        for thread_id, data in self.active_threads.items():
            # Check if thread has been inactive for too long
            if now - data["last_interaction"] > inactive_threshold:
                threads_to_cleanup.append(thread_id)
                
        # Clean up inactive threads
        for thread_id in threads_to_cleanup:
            logger.info(f"Cleaning up inactive thread context: {thread_id}")
            self._cleanup_thread_context(thread_id)
            
        # Run memory optimization if available
        if self.memory_optimizer:
            self.memory_optimizer.run_global_optimization(self.active_threads)
