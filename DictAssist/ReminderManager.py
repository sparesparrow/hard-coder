
from datetime import datetime, timedelta
import threading
import schedule
import time
from typing import List, Dict, Optional
import json
from dataclasses import dataclass, asdict
import pytz
import asyncio
from queue import PriorityQueue

@dataclass
class Reminder:
    id: str
    thought_id: int
    content: str
    scheduled_time: datetime
    priority: int = 1  # 1 (high) to 5 (low)
    repeat_interval: Optional[str] = None  # daily, weekly, monthly, none
    status: str = "pending"
    tags: List[str] = None
    
    def to_dict(self):
        return asdict(self)
    
    def __lt__(self, other):
        return self.priority < other.priority

class ReminderManager:
    def __init__(self, thought_manager, voice_interface, db_path: str = "reminders.db"):
        self.thought_manager = thought_manager
        self.voice_interface = voice_interface
        self.db_path = db_path
        self.reminder_queue = PriorityQueue()
        self.active_reminders = {}
        self.setup_database()
        self.reminder_thread = None
        self.is_running = False

    def setup_database(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS reminders
            (id TEXT PRIMARY KEY,
             thought_id INTEGER,
             content TEXT,
             scheduled_time DATETIME,
             priority INTEGER,
             repeat_interval TEXT,
             status TEXT,
             tags TEXT,
             FOREIGN KEY (thought_id) REFERENCES thoughts (id))
        ''')
        conn.commit()
        conn.close()

    def add_reminder(self, thought_id: int, scheduled_time: datetime, 
                    priority: int = 3, repeat_interval: Optional[str] = None,
                    tags: List[str] = None) -> str:
        """Add a new reminder for a thought"""
        # Get thought content
        thought = self.thought_manager.get_thought(thought_id)
        if not thought:
            raise ValueError("Thought not found")

        reminder_id = f"rem_{int(time.time())}_{thought_id}"
        reminder = Reminder(
            id=reminder_id,
            thought_id=thought_id,
            content=thought['content'],
            scheduled_time=scheduled_time,
            priority=priority,
            repeat_interval=repeat_interval,
            tags=tags or []
        )

        # Store in database
        self._store_reminder(reminder)
        
        # Add to priority queue
        self.reminder_queue.put((scheduled_time.timestamp(), reminder))
        
        # Schedule the reminder
        self._schedule_reminder(reminder)
        
        return reminder_id

    def _store_reminder(self, reminder: Reminder):
        """Store reminder in database"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''
            INSERT INTO reminders 
            (id, thought_id, content, scheduled_time, priority, repeat_interval, status, tags)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            reminder.id,
            reminder.thought_id,
            reminder.content,
            reminder.scheduled_time.isoformat(),
            reminder.priority,
            reminder.repeat_interval,
            reminder.status,
            json.dumps(reminder.tags)
        ))
        conn.commit()
        conn.close()

    def _schedule_reminder(self, reminder: Reminder):
        """Schedule a reminder using the schedule library"""
        def reminder_job():
            self._trigger_reminder(reminder)
            
            # Handle repeat intervals
            if reminder.repeat_interval:
                next_time = self._calculate_next_time(
                    reminder.scheduled_time, 
                    reminder.repeat_interval
                )
                new_reminder = Reminder(
                    id=f"rem_{int(time.time())}_{reminder.thought_id}",
                    thought_id=reminder.thought_id,
                    content=reminder.content,
                    scheduled_time=next_time,
                    priority=reminder.priority,
                    repeat_interval=reminder.repeat_interval,
                    tags=reminder.tags
                )
                self.add_reminder(new_reminder)

        # Schedule the job
        schedule.every().day.at(
            reminder.scheduled_time.strftime("%H:%M")
        ).do(reminder_job)

    def _trigger_reminder(self, reminder: Reminder):
        """Handle reminder triggering"""
        # Prepare reminder message
        message = self._format_reminder_message(reminder)
        
        # Deliver via voice
        self.voice_interface.speak(message)
        
        # Update reminder status
        self._update_reminder_status(reminder.id, "completed")
        
        # Generate context-aware follow-up actions
        follow_up_actions = self._generate_follow_up_actions(reminder)
        if follow_up_actions:
            self.voice_interface.speak(
                "Would you like to take any of these follow-up actions?"
            )
            for action in follow_up_actions:
                self.voice_interface.speak(action)

    def _format_reminder_message(self, reminder: Reminder) -> str:
        """Format reminder message with context"""
        message = f"Reminder for your thought: {reminder.content}"
        
        # Add context based on tags
        if reminder.tags:
            message += f"\nContext: {', '.join(reminder.tags)}"
            
        # Add related thoughts if any
        related_thoughts = self._find_related_thoughts(reminder)
        if related_thoughts:
            message += "\nRelated thoughts you might want to review:"
            for thought in related_thoughts[:2]:  # Limit to 2 related thoughts
                message += f"\n- {thought['content']}"
                
        return message

    def _find_related_thoughts(self, reminder: Reminder) -> List[Dict]:
        """Find thoughts related to the reminder"""
        # Use embedding similarity to find related thoughts
        return self.thought_manager.find_similar_thoughts(reminder.content)

    def _generate_follow_up_actions(self, reminder: Reminder) -> List[str]:
        """Generate context-aware follow-up actions"""
        # Use LLM to generate relevant follow-up actions
        prompt = f"""
        Based on this thought: "{reminder.content}"
        Generate 2-3 specific follow-up actions that would be most useful right now.
        Consider the context: {', '.join(reminder.tags) if reminder.tags else 'No specific context'}
        """
        
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a productive thinking assistant."},
                {"role": "user", "content": prompt}
            ]
        )
        
        actions = response.choices[0].message.content.split('\n')
        return [action.strip('- ') for action in actions if action.strip()]

    def start_reminder_service(self):
        """Start the reminder service in a separate thread"""
        self.is_running = True
        self.reminder_thread = threading.Thread(target=self._reminder_loop)
        self.reminder_thread.start()

    def stop_reminder_service(self):
        """Stop the reminder service"""
        self.is_running = False
        if self.reminder_thread:
            self.reminder_thread.join()

    def _reminder_loop(self):
        """Main loop for checking and triggering reminders"""
        while self.is_running:
            schedule.run_pending()
            time.sleep(60)  # Check every minute

    def get_upcoming_reminders(self, days: int = 7) -> List[Reminder]:
        """Get list of upcoming reminders"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        future_date = (datetime.now() + timedelta(days=days)).isoformat()
        
        c.execute('''
            SELECT * FROM reminders 
            WHERE scheduled_time <= ? 
            AND status = 'pending'
            ORDER BY priority, scheduled_time
        ''', (future_date,))
        
        reminders = []
        for row in c.fetchall():
            reminder = Reminder(
                id=row[0],
                thought_id=row[1],
                content=row[2],
                scheduled_time=datetime.fromisoformat(row[3]),
                priority=row[4],
                repeat_interval=row[5],
                status=row[6],
                tags=json.loads(row[7]) if row[7] else []
            )
            reminders.append(reminder)
            
        conn.close()
        return reminders

    def _calculate_next_time(self, current_time: datetime, 
                           repeat_interval: str) -> datetime:
        """Calculate next reminder time based on repeat interval"""
        if repeat_interval == 'daily':
            return current_time + timedelta(days=1)
        elif repeat_interval == 'weekly':
            return current_time + timedelta(weeks=1)
        elif repeat_interval == 'monthly':
            # Add one month (approximately)
            return current_time + timedelta(days=30)
        return None

class ReminderVoiceCommands:
    def __init__(self, reminder_manager: ReminderManager):
        self.reminder_manager = reminder_manager

    def process_command(self, command: str):
        """Process voice commands related to reminders"""
        command = command.lower()
        
        if "remind me" in command:
            # Parse time from command
            scheduled_time = self._parse_time_from_command(command)
            if scheduled_time:
                # Extract thought content
                content = command.split("remind me")[1].split("at")[0].strip()
                
                # Create reminder
                self.reminder_manager.add_reminder(
                    thought_id=self._create_thought(content),
                    scheduled_time=scheduled_time
                )
                return f"Reminder set for {scheduled_time.strftime('%H:%M')}"
                
        elif "show reminders" in command:
            reminders = self.reminder_manager.get_upcoming_reminders()
            return self._format_reminders_response(reminders)
            
        return "Sorry, I didn't understand that reminder command"

    def _parse_time_from_command(self, command: str) -> Optional[datetime]:
        """Extract time from voice command"""
        # Add sophisticated time parsing logic here
        # Could use libraries like dateparser
        pass

    def _create_thought(self, content: str) -> int:
        """Create a thought entry for the reminder"""
        return self.reminder_manager.thought_manager.add_thought(content)

    def _format_reminders_response(self, reminders: List[Reminder]) -> str:
        """Format reminders for voice response"""
        if not reminders:
            return "You have no upcoming reminders."
            
        response = "Here are your upcoming reminders:\n"
        for reminder in reminders:
            time_str = reminder.scheduled_time.strftime("%H:%M")
            response += f"At {time_str}: {reminder.content}\n"
        return response