import sqlite3
import logging
from datetime import datetime, timedelta

class DatabaseManager:
    def __init__(self, db_name="gym.db"):
        self.db_name = db_name
        self.init_db()

    def connect(self):
        try:
            return sqlite3.connect(self.db_name)
        except sqlite3.Error as e:
            logging.error(f"Failed to connect to database: {e}")
            raise

    def init_db(self):
        try:
            conn = self.connect()
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS members (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                age INTEGER,
                address TEXT,
                phone TEXT,
                registration_date TEXT,
                membership_end_date TEXT,
                is_frozen INTEGER DEFAULT 0,
                frozen_date TEXT
            )
        ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS config (
                    key TEXT PRIMARY KEY,
                    value TEXT
                )
            ''')
            conn.commit()
            conn.close()
        except Exception as e:
            logging.error(f"Error initializing database: {e}")

    def get_config(self, key, default=None):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute('SELECT value FROM config WHERE key = ?', (key,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else default

    def set_config(self, key, value):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute('INSERT OR REPLACE INTO config (key, value) VALUES (?, ?)', (key, value))
        conn.commit()
        conn.close()


    def add_member(self, user_id, name, age, address, phone, registration_date=None, membership_end_date=None):
        conn = self.connect()
        cursor = conn.cursor()
        
        # Default Logic
        if not registration_date:
            registration_date = datetime.now().strftime("%Y-%m-%d")
            
        if not membership_end_date:
            # Default 30 days if not provided
            start_dt = datetime.strptime(registration_date, "%Y-%m-%d")
            membership_end_date = (start_dt + timedelta(days=30)).strftime("%Y-%m-%d")
        
        try:
            cursor.execute('''
                INSERT INTO members (id, name, age, address, phone, registration_date, membership_end_date)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, name, age, address, phone, registration_date, membership_end_date))
            conn.commit()
            logging.info(f"New member registered: {name} (ID: {user_id})")
            return True
        except sqlite3.IntegrityError:
            logging.warning(f"Failed to add member, ID exists: {user_id}")
            return False
        except Exception as e:
            logging.error(f"Error adding member {user_id}: {e}")
            return False
        finally:
            conn.close()

    def get_member(self, user_id):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM members WHERE id = ?', (user_id,))
        member = cursor.fetchone()
        conn.close()
        return member

    def get_all_members(self):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute('SELECT id, name, membership_end_date, is_frozen FROM members')
        members = cursor.fetchall()
        conn.close()
        return members

    def search_members(self, query):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, membership_end_date, is_frozen FROM members WHERE name LIKE ? OR id LIKE ?", ('%' + query + '%', '%' + query + '%'))
        members = cursor.fetchall()
        conn.close()
        return members

    def update_member(self, user_id, name, age, address, phone):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE members SET name=?, age=?, address=?, phone=? WHERE id=?
        ''', (name, age, address, phone, user_id))
        conn.commit()
        conn.close()

    def set_membership_expiry(self, user_id, new_date_str):
        """Sets a specific expiration date and unfreezes if needed."""
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute('UPDATE members SET membership_end_date = ?, is_frozen = 0, frozen_date = NULL WHERE id = ?', 
                       (new_date_str, user_id))
        conn.commit()
        conn.close()


    def toggle_freeze(self, user_id):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute('SELECT is_frozen, frozen_date, membership_end_date FROM members WHERE id = ?', (user_id,))
        record = cursor.fetchone()
        
        if record:
            is_frozen, frozen_date_str, end_date_str = record
            
            if is_frozen:
                # Unfreeze
                # Calculate how long they were frozen
                if frozen_date_str:
                    frozen_date = datetime.strptime(frozen_date_str, "%Y-%m-%d")
                    now = datetime.now()
                    delta = now - frozen_date
                    
                    # Add that time to the end date
                    end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
                    new_end_date = end_date + delta
                    
                    cursor.execute('UPDATE members SET is_frozen=0, frozen_date=NULL, membership_end_date=? WHERE id=?', 
                                   (new_end_date.strftime("%Y-%m-%d"), user_id))
            else:
                # Freeze
                cursor.execute('UPDATE members SET is_frozen=1, frozen_date=? WHERE id=?', 
                               (datetime.now().strftime("%Y-%m-%d"), user_id))
            
            conn.commit()
        conn.close()

    def delete_member(self, user_id):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM members WHERE id = ?', (user_id,))
        conn.commit()
        conn.close()
