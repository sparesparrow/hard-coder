from datetime import datetime
import json
from typing import List, Dict
import sqlite3

class ThoughtManager:
    def __init__(self, db_path: str = "thoughts.db"):
        self.db_path = db_path
        self.setup_database()

    def setup_database(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS thoughts
            (id INTEGER PRIMARY KEY AUTOINCREMENT,
             content TEXT,
             timestamp DATETIME,
             category TEXT,
             status TEXT)
        ''')
        conn.commit()
        conn.close()

    def add_thought(self, content: str, category: str = "general"):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''
            INSERT INTO thoughts (content, timestamp, category, status)
            VALUES (?, ?, ?, ?)
        ''', (content, datetime.now(), category, "pending"))
        conn.commit()
        conn.close()

    def get_todays_thoughts(self) -> List[Dict]:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        today = datetime.now().date()
        c.execute('''
            SELECT * FROM thoughts 
            WHERE date(timestamp) = date(?)
        ''', (today,))
        thoughts = [{
            "id": row[0],
            "content": row[1],
            "timestamp": row[2],
            "category": row[3],
            "status": row[4]
        } for row in c.fetchall()]
        conn.close()
        return thoughts

class Assistant:
    def __init__(self):
        self.thought_manager = ThoughtManager()

    def capture_thought(self, thought: str):
        """Function to capture and store user's thoughts"""
        self.thought_manager.add_thought(thought)
        return "Thought captured successfully!"

    def evening_review(self) -> str:
        """Function to provide evening review of captured thoughts"""
        thoughts = self.thought_manager.get_todays_thoughts()
        
        if not thoughts:
            return "No thoughts captured today."

        review = "Here's your thought review for today:\n\n"
        
        # Group thoughts by category
        categorized_thoughts = {}
        for thought in thoughts:
            category = thought["category"]
            if category not in categorized_thoughts:
                categorized_thoughts[category] = []
            categorized_thoughts[category].append(thought)

        # Generate review text
        for category, category_thoughts in categorized_thoughts.items():
            review += f"\n{category.upper()}:\n"
            for thought in category_thoughts:
                review += f"- {thought['content']}\n"
                # Add suggestions for improvement
                review += "  Suggestion: Consider exploring this topic further or breaking it down into actionable items.\n"

        return review

def main():
    assistant = Assistant()
    
    # Example usage
    while True:
        print("\n1. Capture thought")
        print("2. Evening review")
        print("3. Exit")
        
        choice = input("Choose an option: ")
        
        if choice == "1":
            thought = input("Enter your thought: ")
            print(assistant.capture_thought(thought))
        
        elif choice == "2":
            print(assistant.evening_review())
        
        elif choice == "3":
            break
        
        else:
            print("Invalid option. Please try again.")

if __name__ == "__main__":
    main()
