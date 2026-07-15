"""
====================================================================
UNIT TESTS - pytest
====================================================================
"""

import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestKeywordAI:
    """Test Keyword AI"""
    
    def test_greeting_responses(self):
        """Test greeting keywords"""
        from src.ai.providers import KeywordAI
        
        ai = KeywordAI()
        
        assert ai.generate("hi") is not None
        assert ai.generate("hello") is not None
        assert ai.generate("hey") is not None
    
    def test_price_response(self):
        """Test price keyword"""
        from src.ai.providers import KeywordAI
        
        ai = KeywordAI()
        response = ai.generate("what is the price")
        
        assert response is not None
        assert "price" in response.lower() or "product" in response.lower()
    
    def test_menu_response(self):
        """Test menu keyword"""
        from src.ai.providers import KeywordAI
        
        ai = KeywordAI()
        response = ai.generate("show me the menu")
        
        assert response is not None
        assert "menu" in response.lower()
    
    def test_unknown_message(self):
        """Test unknown message falls back to default"""
        from src.ai.providers import KeywordAI
        
        ai = KeywordAI()
        response = ai.generate("asdfghjkl random")
        
        assert response is not None
        assert len(response) > 0


class TestAIManager:
    """Test AI Manager"""
    
    def test_manager_creation(self):
        """Test manager can be created"""
        from src.ai.providers import AIManager
        
        manager = AIManager()
        assert manager is not None
        assert manager.current_provider == "keyword"
    
    def test_keyword_always_available(self):
        """Test keyword AI is always available"""
        from src.ai.providers import AIManager
        
        manager = AIManager()
        response, provider = manager.generate("hello")
        
        assert response is not None
        assert provider == "keyword"


class TestDatabase:
    """Test Database"""
    
    def test_database_init(self):
        """Test database initialization"""
        from src.core.database import Database
        import tempfile
        import os
        
        # Create temp db
        temp_dir = tempfile.mkdtemp()
        db_path = os.path.join(temp_dir, "test.db")
        
        db = Database(db_path)
        db.init_db()
        
        # Check tables exist
        with db.get_cursor() as cursor:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
        
        assert "keywords" in tables
        assert "messages" in tables
        assert "stats" in tables
        
        # Cleanup
        db.close()
        os.remove(db_path)
        os.rmdir(temp_dir)
    
    def test_add_keyword(self):
        """Test adding keywords"""
        from src.core.database import Database
        import tempfile
        import os
        
        temp_dir = tempfile.mkdtemp()
        db_path = os.path.join(temp_dir, "test.db")
        
        db = Database(db_path)
        db.init_db()
        
        result = db.add_keyword("test", "Test response")
        assert result is True
        
        keywords = db.get_all_keywords()
        assert len(keywords) > 0
        
        db.close()
        os.remove(db_path)
        os.rmdir(temp_dir)
    
    def test_find_reply(self):
        """Test finding replies"""
        from src.core.database import Database
        import tempfile
        import os
        
        temp_dir = tempfile.mkdtemp()
        db_path = os.path.join(temp_dir, "test.db")
        
        db = Database(db_path)
        db.init_db()
        
        db.add_keyword("coffee", "We have great coffee!")
        
        response = db.find_reply("I want some coffee")
        assert response == "We have great coffee!"
        
        # Test non-matching
        response = db.find_reply("I want tea")
        assert response is None
        
        db.close()
        os.remove(db_path)
        os.rmdir(temp_dir)


class TestCache:
    """Test AI Cache"""
    
    def test_cache_basic(self):
        """Test basic cache functionality"""
        from src.ai.providers import AICache
        
        cache = AICache()
        
        cache.set("test", "result")
        result = cache.get("test")
        
        assert result == "result"
    
    def test_cache_miss(self):
        """Test cache miss"""
        from src.ai.providers import AICache
        
        cache = AICache()
        
        result = cache.get("nonexistent")
        assert result is None
    
    def test_cache_stats(self):
        """Test cache statistics"""
        from src.ai.providers import AICache
        
        cache = AICache()
        
        cache.get("miss")
        cache.set("hit", "value")
        cache.get("hit")
        
        stats = cache.stats()
        
        assert stats["hits"] == 1
        assert stats["misses"] == 1
        assert stats["size"] == 1


class TestConfig:
    """Test Configuration"""
    
    def test_default_config(self):
        """Test default configuration"""
        from src.core.config import load_config
        
        config = load_config("nonexistent.yaml")
        
        assert config is not None
        assert config.ai.provider == "keyword"
        assert config.ai.max_tokens == 150
    
    def test_config_validation(self):
        """Test config validation"""
        from src.core.config import BotConfig
        
        # Valid config
        config = BotConfig()
        assert config.ai.provider in ["openrouter", "groq", "keyword"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
