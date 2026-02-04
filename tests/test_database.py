import unittest
import os
import sqlite3
from datetime import datetime, timedelta
from database import DatabaseManager

class TestDatabaseManager(unittest.TestCase):
    def setUp(self):
        # Use a temporary file-based DB or in-memory DB for tests
        # In-memory is faster: ':memory:'
        # However, the class takes a filename. Let's pass a test filename.
        self.test_db_name = "test_unit_gym.db"
        self.db = DatabaseManager(self.test_db_name)
        # Clean slate
        self.clear_db()

    def tearDown(self):
        self.db.close()
        if os.path.exists(self.test_db_name):
            os.remove(self.test_db_name)

    def clear_db(self):
        conn = self.db.connect()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM members")
        cursor.execute("DELETE FROM config")
        conn.commit()
        conn.close()

    def test_add_get_member(self):
        # Test adding a member
        success = self.db.add_member("101", "Test User", 25, "123 St", "555-0101")
        self.assertTrue(success, "Failed to add member")
        
        # Test retrieving
        member = self.db.get_member("101")
        self.assertIsNotNone(member)
        self.assertEqual(member[0], "101")
        self.assertEqual(member[1], "Test User")
        
        # Test duplicate
        success_dup = self.db.add_member("101", "Copycat", 25, "", "")
        self.assertFalse(success_dup, "Should not allow duplicate IDs")

    def test_search(self):
        self.db.add_member("201", "Alice Smith", 30, "", "")
        self.db.add_member("202", "Bob Smith", 35, "", "")
        
        results = self.db.search_members("Smith")
        self.assertEqual(len(results), 2)
        
        results_id = self.db.search_members("201")
        self.assertEqual(len(results_id), 1)

    def test_config(self):
        self.db.set_config("gym_name", "SuperGym")
        val = self.db.get_config("gym_name")
        self.assertEqual(val, "SuperGym")
        
        # Default value
        val_none = self.db.get_config("non_existent", "Default")
        self.assertEqual(val_none, "Default")

    def test_membership_logic(self):
        self.db.add_member("301", "Expiry Test", 20, "", "")
        
        # Set expiry to yesterday
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        self.db.set_membership_expiry("301", yesterday)
        
        member = self.db.get_member("301")
        expiry_str = member[6]
        self.assertEqual(expiry_str, yesterday)

    def test_freeze(self):
        self.db.add_member("401", "Freeze Test", 20, "", "")
        
        # Freeze
        self.db.toggle_freeze("401")
        member = self.db.get_member("401")
        self.assertEqual(member[7], 1) # is_frozen
        self.assertIsNotNone(member[8]) # frozen_date
        
        # Unfreeze
        # We need to mock time passing to test date extension accurately, 
        # but for unit test ensuring state toggles is basic requirement.
        self.db.toggle_freeze("401")
        member = self.db.get_member("401")
        self.assertEqual(member[7], 0)
        self.assertIsNone(member[8])

    def test_delete(self):
        self.db.add_member("501", "Delete Me", 20, "", "")
        self.db.delete_member("501")
        member = self.db.get_member("501")
        self.assertIsNone(member)

if __name__ == '__main__':
    unittest.main()
