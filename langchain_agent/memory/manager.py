"""
Memory Management Module
========================

Handles conversation memory with persistent storage and auto-cleanup.
"""

import os
import sqlite3
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List

# LangChain Memory components
from langchain.memory import ConversationBufferMemory
from langchain_community.chat_message_histories import SQLChatMessageHistory

# Local configuration
from config import settings

logger = logging.getLogger(__name__)


class MemoryManager:
    """Manages conversation memory with persistent storage and auto-cleanup."""
    
    def __init__(self, memory_dir: str = "memory/data"):
        """Initialize memory manager with local storage."""
        self.memory_dir = memory_dir
        self.retention_days = settings.MEMORY_RETENTION_DAYS
        
        # Create memory directory if it doesn't exist
        os.makedirs(memory_dir, exist_ok=True)
        
        # Initialize database
        self._init_database()
        
        # Clean up old conversations
        self._cleanup_old_conversations()
    
    def _init_database(self):
        """Initialize SQLite database for chat history."""
        db_path = os.path.join(self.memory_dir, "chat_history.db")
        self.db_path = db_path
        
        # Create tables
        with sqlite3.connect(db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    session_id TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    conversation_id INTEGER,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (conversation_id) REFERENCES conversations (id)
                )
            """)
    
    def _cleanup_old_conversations(self):
        """Remove conversations older than retention period."""
        cutoff_date = datetime.now() - timedelta(days=self.retention_days)
        
        with sqlite3.connect(self.db_path) as conn:
            # Delete old conversations and their messages
            conn.execute("""
                DELETE FROM conversations 
                WHERE last_updated < ?
            """, (cutoff_date,))
            
            deleted_count = conn.total_changes
            if deleted_count > 0:
                logger.info(f"🧹 Cleaned up {deleted_count} old conversations")
    
    def get_memory_for_user(self, user_id: str, session_id: str = None) -> ConversationBufferMemory:
        """Get or create memory for a specific user session."""
        if session_id is None:
            session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Create SQLite-based message history
        db_path = os.path.join(self.memory_dir, f"user_{user_id}.db")
        message_history = SQLChatMessageHistory(
            session_id=session_id,
            connection_string=f"sqlite:///{db_path}"
        )
        
        # Create memory with the message history
        memory = ConversationBufferMemory(
            chat_memory=message_history,
            return_messages=True,
            memory_key="chat_history"
        )
        
        return memory
    
    def save_conversation(self, user_id: str, session_id: str, messages: List[Dict]):
        """Save conversation to database."""
        with sqlite3.connect(self.db_path) as conn:
            # Insert or update conversation
            conn.execute("""
                INSERT OR REPLACE INTO conversations (user_id, session_id, last_updated)
                VALUES (?, ?, CURRENT_TIMESTAMP)
            """, (user_id, session_id))
            
            conversation_id = conn.lastrowid
            
            # Save messages
            for message in messages:
                conn.execute("""
                    INSERT INTO messages (conversation_id, role, content)
                    VALUES (?, ?, ?)
                """, (conversation_id, message['role'], message['content']))
    
    def get_user_conversations(self, user_id: str) -> List[Dict]:
        """Get all conversations for a user."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT c.session_id, c.created_at, c.last_updated,
                       COUNT(m.id) as message_count
                FROM conversations c
                LEFT JOIN messages m ON c.id = m.conversation_id
                WHERE c.user_id = ?
                GROUP BY c.id
                ORDER BY c.last_updated DESC
            """, (user_id,))
            
            return [dict(row) for row in cursor.fetchall()]
