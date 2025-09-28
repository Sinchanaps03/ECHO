from pymongo import MongoClient
from datetime import datetime, timezone
import logging
import os
from bson import ObjectId

logger = logging.getLogger(__name__)

class DatabaseService:
    def __init__(self):
        """Initialize MongoDB connection"""
        self.client = None
        self.db = None
        self.collection = None
        self.connected = False
        
        try:
            # Get MongoDB URI from environment
            mongo_uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/echosketch')
            
            # Connect to MongoDB with timeout
            self.client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
            
            # Get database (will be created if doesn't exist)
            db_name = mongo_uri.split('/')[-1] if '/' in mongo_uri else 'echosketch'
            self.db = self.client[db_name]
            
            # Get collection for sessions
            self.collection = self.db.sessions
            
            # Test connection
            self.client.admin.command('ismaster')
            self.connected = True
            logger.info(f"Connected to MongoDB: {db_name}")
            
        except Exception as e:
            logger.warning(f"Could not connect to MongoDB: {e}")
            logger.info("Running without database persistence")
            self.client = None
            self.connected = False
    
    def save_session(self, session_data: dict) -> str:
        """Save session data to database"""
        try:
            if self.collection is None:
                logger.warning("No database connection - session not saved")
                return "no_db_session"
            
            # Add timestamp if not present
            if 'timestamp' not in session_data:
                session_data['timestamp'] = self.get_current_timestamp()
            
            # Insert document
            result = self.collection.insert_one(session_data)
            session_id = str(result.inserted_id)
            
            logger.info(f"Session saved with ID: {session_id}")
            return session_id
            
        except Exception as e:
            logger.error(f"Error saving session: {e}")
            return "error_session"
    
    def get_session(self, session_id: str) -> dict:
        """Get session data by ID"""
        try:
            if self.collection is None:
                logger.warning("No database connection")
                return None
            
            if session_id in ["no_db_session", "error_session"]:
                return None
            
            # Find document by ObjectId
            document = self.collection.find_one({'_id': ObjectId(session_id)})
            
            if document:
                # Convert ObjectId to string for JSON serialization
                document['_id'] = str(document['_id'])
                logger.info(f"Retrieved session: {session_id}")
                return document
            else:
                logger.warning(f"Session not found: {session_id}")
                return None
                
        except Exception as e:
            logger.error(f"Error retrieving session: {e}")
            return None
    
    def get_recent_sessions(self, limit: int = 10) -> list:
        """Get recent sessions"""
        try:
            if not self.collection:
                return []
            
            # Find recent sessions sorted by timestamp
            sessions = list(self.collection.find().sort('timestamp', -1).limit(limit))
            
            # Convert ObjectIds to strings
            for session in sessions:
                session['_id'] = str(session['_id'])
            
            logger.info(f"Retrieved {len(sessions)} recent sessions")
            return sessions
            
        except Exception as e:
            logger.error(f"Error retrieving recent sessions: {e}")
            return []
    
    def delete_session(self, session_id: str) -> bool:
        """Delete a session by ID"""
        try:
            if not self.collection:
                return False
            
            if session_id in ["no_db_session", "error_session"]:
                return False
            
            result = self.collection.delete_one({'_id': ObjectId(session_id)})
            
            if result.deleted_count > 0:
                logger.info(f"Session deleted: {session_id}")
                return True
            else:
                logger.warning(f"Session not found for deletion: {session_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error deleting session: {e}")
            return False
    
    def update_session(self, session_id: str, update_data: dict) -> bool:
        """Update session data"""
        try:
            if not self.collection:
                return False
            
            if session_id in ["no_db_session", "error_session"]:
                return False
            
            # Add updated timestamp
            update_data['updated_at'] = self.get_current_timestamp()
            
            result = self.collection.update_one(
                {'_id': ObjectId(session_id)},
                {'$set': update_data}
            )
            
            if result.modified_count > 0:
                logger.info(f"Session updated: {session_id}")
                return True
            else:
                logger.warning(f"Session not found for update: {session_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error updating session: {e}")
            return False
    
    def search_sessions(self, query: str, limit: int = 20) -> list:
        """Search sessions by transcript content"""
        try:
            if not self.collection:
                return []
            
            # Create text search query
            search_query = {
                '$or': [
                    {'transcript': {'$regex': query, '$options': 'i'}},
                    {'visual_concepts.keywords': {'$in': [query]}},
                    {'visual_concepts.enhanced_prompt': {'$regex': query, '$options': 'i'}}
                ]
            }
            
            sessions = list(self.collection.find(search_query).sort('timestamp', -1).limit(limit))
            
            # Convert ObjectIds to strings
            for session in sessions:
                session['_id'] = str(session['_id'])
            
            logger.info(f"Found {len(sessions)} sessions matching: {query}")
            return sessions
            
        except Exception as e:
            logger.error(f"Error searching sessions: {e}")
            return []
    
    def get_statistics(self) -> dict:
        """Get database statistics"""
        try:
            if not self.collection:
                return {'total_sessions': 0, 'database_connected': False}
            
            stats = {
                'total_sessions': self.collection.count_documents({}),
                'database_connected': True,
                'database_name': self.db.name,
                'collection_name': self.collection.name
            }
            
            # Get date range
            oldest = self.collection.find().sort('timestamp', 1).limit(1)
            newest = self.collection.find().sort('timestamp', -1).limit(1)
            
            oldest_list = list(oldest)
            newest_list = list(newest)
            
            if oldest_list and newest_list:
                stats['oldest_session'] = oldest_list[0]['timestamp']
                stats['newest_session'] = newest_list[0]['timestamp']
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting statistics: {e}")
            return {'total_sessions': 0, 'database_connected': False, 'error': str(e)}
    
    def get_current_timestamp(self) -> datetime:
        """Get current timestamp in UTC"""
        return datetime.now(timezone.utc)
    
    def close_connection(self):
        """Close database connection"""
        try:
            if self.client:
                self.client.close()
                logger.info("Database connection closed")
        except Exception as e:
            logger.error(f"Error closing database connection: {e}")
    
    def __del__(self):
        """Cleanup when object is destroyed"""
        try:
            # Only attempt to close if we're not shutting down
            import sys
            if not hasattr(sys, '_called_from_test') and hasattr(self, 'client') and self.client:
                self.client.close()
        except:
            # Silently ignore errors during interpreter shutdown
            pass