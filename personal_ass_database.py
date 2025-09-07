import sqlite3
import json
from datetime import datetime, timedelta
import os

class PersonalAssistantDB:
    def __init__(self, db_path="personal_assistant.db"):
        """Initialize the personal assistant database"""
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Create all necessary tables for the personal assistant"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Gmail/Email tracking
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS emails (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                gmail_id TEXT UNIQUE,
                sender TEXT,
                subject TEXT,
                snippet TEXT,
                body TEXT,
                received_date TIMESTAMP,
                is_read BOOLEAN DEFAULT FALSE,
                is_important BOOLEAN DEFAULT FALSE,
                labels TEXT,  -- JSON array of labels
                attachments TEXT,  -- JSON array of attachment info
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Notifications system
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type TEXT NOT NULL,  -- 'email', 'reminder', 'study', 'coding'
                title TEXT NOT NULL,
                message TEXT,
                priority TEXT DEFAULT 'medium',  -- 'low', 'medium', 'high', 'urgent'
                is_read BOOLEAN DEFAULT FALSE,
                scheduled_for TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                action_required BOOLEAN DEFAULT FALSE,
                metadata TEXT  -- JSON for additional data
            )
        ''')
        
        # Study/Learning tracking
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS study_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subject TEXT NOT NULL,
                topic TEXT,
                duration_minutes INTEGER,
                study_type TEXT,  -- 'reading', 'practice', 'video', 'coding', 'nlp'
                progress_notes TEXT,
                difficulty_rating INTEGER CHECK (difficulty_rating BETWEEN 1 AND 5),
                session_date DATE,
                goals TEXT,  -- JSON array of session goals
                achievements TEXT,  -- JSON array of what was accomplished
                next_steps TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Learning resources/materials
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS learning_resources (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                type TEXT,  -- 'book', 'video', 'article', 'course', 'tutorial'
                subject TEXT,  -- 'coding', 'nlp', 'general'
                url TEXT,
                local_path TEXT,
                description TEXT,
                progress_percentage INTEGER DEFAULT 0,
                rating INTEGER CHECK (rating BETWEEN 1 AND 5),
                notes TEXT,
                tags TEXT,  -- JSON array
                added_date DATE DEFAULT (DATE('now')),
                completed_date DATE,
                is_favorite BOOLEAN DEFAULT FALSE
            )
        ''')
        
        # Coding projects and progress
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS coding_projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                language TEXT,  -- 'python', 'javascript', etc.
                github_url TEXT,
                local_path TEXT,
                status TEXT DEFAULT 'active',  -- 'planning', 'active', 'paused', 'completed'
                difficulty TEXT DEFAULT 'medium',
                technologies TEXT,  -- JSON array
                goals TEXT,  -- JSON array
                progress_notes TEXT,
                last_worked_date DATE,
                created_date DATE DEFAULT (DATE('now')),
                estimated_hours INTEGER,
                actual_hours INTEGER DEFAULT 0
            )
        ''')
        
        # NLP tasks and experiments
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS nlp_tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_name TEXT NOT NULL,
                task_type TEXT,  -- 'sentiment_analysis', 'text_classification', 'ner', etc.
                dataset_name TEXT,
                model_used TEXT,
                accuracy_score REAL,
                parameters TEXT,  -- JSON of model parameters
                notes TEXT,
                code_path TEXT,
                results_path TEXT,
                created_date DATE DEFAULT (DATE('now')),
                completion_date DATE,
                status TEXT DEFAULT 'in_progress'  -- 'planning', 'in_progress', 'completed', 'failed'
            )
        ''')
        
        # Daily goals and habits
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS daily_goals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                goal TEXT NOT NULL,
                category TEXT,  -- 'study', 'coding', 'health', 'personal'
                target_date DATE,
                is_completed BOOLEAN DEFAULT FALSE,
                completion_date DATE,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Assistant conversations/interactions
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS assistant_interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                interaction_type TEXT,  -- 'query', 'task_help', 'study_help', 'notification'
                user_input TEXT,
                assistant_response TEXT,
                context_data TEXT,  -- JSON of relevant context
                satisfaction_rating INTEGER CHECK (satisfaction_rating BETWEEN 1 AND 5),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        print(f"Personal Assistant Database initialized: {self.db_path}")
    
    def add_email(self, gmail_id, sender, subject, snippet, body=None, labels=None):
        """Add email to tracking"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        labels_json = json.dumps(labels) if labels else None
        
        cursor.execute('''
            INSERT OR IGNORE INTO emails 
            (gmail_id, sender, subject, snippet, body, received_date, labels)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (gmail_id, sender, subject, snippet, body, datetime.now(), labels_json))
        
        conn.commit()
        conn.close()
    
    def create_notification(self, type, title, message, priority='medium', scheduled_for=None):
        """Create a new notification"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO notifications (type, title, message, priority, scheduled_for)
            VALUES (?, ?, ?, ?, ?)
        ''', (type, title, message, priority, scheduled_for))
        
        notification_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return notification_id
    
    def log_study_session(self, subject, topic, duration_minutes, study_type='reading'):
        """Log a study session"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO study_sessions 
            (subject, topic, duration_minutes, study_type, session_date)
            VALUES (?, ?, ?, ?, ?)
        ''', (subject, topic, duration_minutes, study_type, datetime.now().date()))
        
        session_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return session_id
    
    def add_learning_resource(self, title, resource_type, subject, url=None, description=None):
        """Add a learning resource"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO learning_resources 
            (title, type, subject, url, description)
            VALUES (?, ?, ?, ?, ?)
        ''', (title, resource_type, subject, url, description))
        
        resource_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return resource_id
    
    def create_coding_project(self, name, description, language, local_path=None):
        """Create a new coding project"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO coding_projects 
            (name, description, language, local_path)
            VALUES (?, ?, ?, ?)
        ''', (name, description, language, local_path))
        
        project_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return project_id
    
    def log_nlp_task(self, task_name, task_type, dataset_name=None, model_used=None):
        """Log an NLP task/experiment"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO nlp_tasks 
            (task_name, task_type, dataset_name, model_used)
            VALUES (?, ?, ?, ?)
        ''', (task_name, task_type, dataset_name, model_used))
        
        task_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return task_id
    
    def get_pending_notifications(self):
        """Get all unread notifications"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM notifications 
            WHERE is_read = FALSE 
            ORDER BY priority DESC, created_at DESC
        ''')
        
        notifications = cursor.fetchall()
        conn.close()
        
        return notifications
    
    def get_study_progress(self, subject=None, days=7):
        """Get study progress for the last N days"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        date_filter = datetime.now().date() - timedelta(days=days)
        
        if subject:
            cursor.execute('''
                SELECT subject, COUNT(*) as sessions, SUM(duration_minutes) as total_minutes
                FROM study_sessions 
                WHERE session_date >= ? AND subject = ?
                GROUP BY subject
            ''', (date_filter, subject))
        else:
            cursor.execute('''
                SELECT subject, COUNT(*) as sessions, SUM(duration_minutes) as total_minutes
                FROM study_sessions 
                WHERE session_date >= ?
                GROUP BY subject
                ORDER BY total_minutes DESC
            ''', (date_filter,))
        
        progress = cursor.fetchall()
        conn.close()
        
        return progress

def setup_sample_data():
    """Add some sample data to test the system"""
    db = PersonalAssistantDB()
    
    print("Adding sample data...")
    
    # Sample notifications
    db.create_notification('reminder', 'Study NLP', 'Time for daily NLP learning session', 'high')
    db.create_notification('email', 'Important Email', 'You have 3 unread important emails', 'medium')
    db.create_notification('coding', 'Code Review', 'Complete code review for Python project', 'medium')
    
    # Sample study sessions
    db.log_study_session('NLP', 'Text Preprocessing', 60, 'practice')
    db.log_study_session('Python', 'Data Structures', 45, 'coding')
    db.log_study_session('Machine Learning', 'Neural Networks', 90, 'reading')
    
    # Sample learning resources
    db.add_learning_resource('Natural Language Processing with Python', 'book', 'nlp', 
                           'https://nltk.org/book/', 'Comprehensive NLP guide')
    db.add_learning_resource('Python Crash Course', 'book', 'coding',
                           description='Great Python learning resource')
    
    # Sample coding projects
    db.create_coding_project('Personal Assistant', 'AI-powered personal assistant', 'python')
    db.create_coding_project('Text Classifier', 'NLP text classification tool', 'python')
    
    # Sample NLP tasks
    db.log_nlp_task('Sentiment Analysis', 'sentiment_analysis', 'IMDB Reviews', 'BERT')
    db.log_nlp_task('Named Entity Recognition', 'ner', 'CoNLL-2003', 'spaCy')
    
    print("Sample data added successfully!")
    print(f"Database location: {os.path.abspath(db.db_path)}")

if __name__ == "__main__":
    setup_sample_data()
    
    # Test the database
    db = PersonalAssistantDB()
    
    print("\n" + "="*60)
    print("PERSONAL ASSISTANT DATABASE STATUS")
    print("="*60)
    
    # Show notifications
    notifications = db.get_pending_notifications()
    print(f"\n📢 Pending Notifications: {len(notifications)}")
    for notif in notifications:
        print(f"  • {notif[2]} ({notif[1]}) - Priority: {notif[4]}")
    
    # Show study progress
    progress = db.get_study_progress()
    print(f"\n📚 Study Progress (Last 7 days):")
    for prog in progress:
        hours = prog[2] / 60 if prog[2] else 0
        print(f"  • {prog[0]}: {prog[1]} sessions, {hours:.1f} hours")
    
    print(f"\n🎉 Your personal assistant database is ready!")
    print("Next: Set up Gmail integration and notification system")