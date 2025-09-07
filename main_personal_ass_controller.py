#!/usr/bin/env python3
"""
Personal Assistant - Main Controller
Integrates Gmail, Study Assistant, Notifications, and Claude Desktop
"""

import schedule
import time
import threading
import sqlite3
from datetime import datetime, timedelta
import json
import os
import sys

# Import our modules (make sure all files are in the same directory)
try:
    from personal_assistant_db import PersonalAssistantDB
    from gmail_integration import GmailIntegrator, NotificationManager
    from study_assistant import StudyAssistant, NLPLearningAssistant
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure all assistant files are in the same directory")
    sys.exit(1)

class PersonalAssistant:
    def __init__(self):
        """Initialize the personal assistant"""
        print("🤖 Initializing Personal Assistant...")
        
        # Initialize database
        self.db = PersonalAssistantDB()
        
        # Initialize components
        self.gmail_integrator = GmailIntegrator(self.db)
        self.notification_manager = NotificationManager(self.db)
        self.study_assistant = StudyAssistant(self.db)
        self.nlp_assistant = NLPLearningAssistant(self.db)
        
        # Assistant settings
        self.settings = {
            'email_check_interval': 30,  # minutes
            'study_reminder_times': ['09:00', '14:00', '19:00'],
            'daily_study_goal': 60,  # minutes
            'notification_priority_filter': 'medium'  # show medium and above
        }
        
        print("✅ Personal Assistant initialized!")
    
    def start_background_services(self):
        """Start background services for monitoring"""
        print("🔄 Starting background services...")
        
        # Schedule email checks
        schedule.every(self.settings['email_check_interval']).minutes.do(
            self.check_emails_background
        )
        
        # Schedule study reminders
        for time_str in self.settings['study_reminder_times']:
            schedule.every().day.at(time_str).do(self.create_study_reminder)
        
        # Daily progress review
        schedule.every().day.at("20:00").do(self.daily_progress_review)
        
        # Start scheduler in background thread
        def run_scheduler():
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        
        scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        scheduler_thread.start()
        
        print("✅ Background services started!")
    
    def check_emails_background(self):
        """Background email checking"""
        print("📧 Checking emails...")
        try:
            emails = self.gmail_integrator.check_and_notify_new_emails()
            if emails:
                print(f"   Found {len(emails)} new emails")
        except Exception as e:
            print(f"   Email check error: {e}")
    
    def create_study_reminder(self):
        """Create study reminder notifications"""
        # Check if user has studied today
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT SUM(duration_minutes) FROM study_sessions 
            WHERE session_date = ?
        ''', (datetime.now().date(),))
        
        today_minutes = cursor.fetchone()[0] or 0
        conn.close()
        
        if today_minutes < self.settings['daily_study_goal']:
            remaining = self.settings['daily_study_goal'] - today_minutes
            self.notification_manager.create_study_reminder(
                "General Study",
                f"You need {remaining} more minutes to reach your daily goal!"
            )
    
    def daily_progress_review(self):
        """Create daily progress summary"""
        progress = self.db.get_study_progress(days=1)
        
        if progress:
            total_time = sum(p[2] for p in progress) / 60  # convert to hours
            subjects = [p[0] for p in progress]
            
            summary = f"📊 Daily Summary: {total_time:.1f}h studied across {', '.join(subjects)}"
        else:
            summary = "📊 Daily Summary: No study sessions today. Tomorrow is a new day!"
        
        self.db.create_notification(
            type='daily_summary',
            title='Daily Progress Review',
            message=summary,
            priority='low'
        )
    
    def get_dashboard_info(self):
        """Get dashboard information"""
        dashboard = {
            'notifications': self.db.get_pending_notifications()[:5],
            'recent_study': self.db.get_study_progress(days=7),
            'study_suggestions': [],
            'upcoming_reminders': [],
            'quick_stats': self.get_quick_stats()
        }
        
        # Get study suggestions for main subjects
        for subject in ['nlp', 'python', 'machine_learning']:
            suggestion = self.study_assistant.suggest_study_topic(subject)
            dashboard['study_suggestions'].append({
                'subject': subject,
                'topic': suggestion
            })
        
        return dashboard
    
    def get_quick_stats(self):
        """Get quick statistics"""
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        
        # Total study hours this week
        week_ago = datetime.now().date() - timedelta(days=7)
        cursor.execute('''
            SELECT SUM(duration_minutes) FROM study_sessions 
            WHERE session_date >= ?
        ''', (week_ago,))
        
        week_minutes = cursor.fetchone()[0] or 0
        week_hours = week_minutes / 60
        
        # Unread notifications count
        cursor.execute('SELECT COUNT(*) FROM notifications WHERE is_read = FALSE')
        unread_notifications = cursor.fetchone()[0]
        
        # Active projects count
        cursor.execute('SELECT COUNT(*) FROM coding_projects WHERE status = "active"')
        active_projects = cursor.fetchone()[0]
        
        # Learning resources count
        cursor.execute('SELECT COUNT(*) FROM learning_resources')
        total_resources = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'week_study_hours': round(week_hours, 1),
            'unread_notifications': unread_notifications,
            'active_projects': active_projects,
            'learning_resources': total_resources
        }
    
    def display_dashboard(self):
        """Display the main dashboard"""
        dashboard = self.get_dashboard_info()
        
        print("\n" + "="*80)
        print("🤖 PERSONAL ASSISTANT DASHBOARD")
        print("="*80)
        
        # Quick Stats
        stats = dashboard['quick_stats']
        print(f"📊 QUICK STATS:")
        print(f"   📚 Study Hours (This Week): {stats['week_study_hours']}h")
        print(f"   🔔 Unread Notifications: {stats['unread_notifications']}")
        print(f"   💻 Active Projects: {stats['active_projects']}")
        print(f"   📖 Learning Resources: {stats['learning_resources']}")
        
        # Recent Notifications
        print(f"\n🔔 RECENT NOTIFICATIONS:")
        notifications = dashboard['notifications']
        if notifications:
            for notif in notifications[:3]:
                priority_emoji = {'urgent': '🚨', 'high': '❗', 'medium': '📋', 'low': '💭'}.get(notif[4], '📌')
                print(f"   {priority_emoji} {notif[2]} ({notif[1]})")
        else:
            print("   ✅ No pending notifications!")
        
        # Study Progress
        print(f"\n📚 RECENT STUDY ACTIVITY:")
        progress = dashboard['recent_study']
        if progress:
            for subject, sessions, total_minutes in progress:
                hours = total_minutes / 60
                print(f"   • {subject}: {sessions} sessions, {hours:.1f}h")
        else:
            print("   📝 No recent study sessions")
        
        # Study Suggestions
        print(f"\n💡 STUDY SUGGESTIONS:")
        for suggestion in dashboard['study_suggestions']:
            print(f"   • {suggestion['subject'].upper()}: {suggestion['topic']}")
    
    def claude_desktop_integration(self):
        """Instructions for Claude Desktop integration"""
        integration_guide = """
🤖 CLAUDE DESKTOP INTEGRATION GUIDE

1. SETUP FILES FOR CLAUDE:
   Create these files in a folder that Claude Desktop can access:
   
   📁 assistant_data/
   ├── current_progress.json     (your current study progress)
   ├── notifications.json        (pending notifications)
   ├── study_plan.json          (your study plan)
   └── quick_commands.md        (commands Claude can help with)

2. ASK CLAUDE TO HELP WITH:
   • "Analyze my study progress and suggest improvements"
   • "Help me create a study schedule for NLP"
   • "Review my notifications and prioritize them"
   • "Suggest coding projects based on my current level"
   • "Create quiz questions for [topic]"
   • "Help me debug Python code for my project"

3. WORKFLOW EXAMPLES:
   • Export your data → Share with Claude → Get insights
   • Ask Claude to create study materials
   • Use Claude to explain complex NLP concepts
   • Get help with coding challenges

4. VOICE COMMANDS (if supported):
   • "Show my daily progress"
   • "What should I study next?"
   • "Add study session for Python"
   • "Check my notifications"
        """
        
        return integration_guide
    
    def export_data_for_claude(self, output_dir="assistant_data"):
        """Export data in formats that Claude Desktop can use"""
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # Export current progress
        progress_data = {
            'last_updated': datetime.now().isoformat(),
            'study_progress': self.db.get_study_progress(days=14),
            'quick_stats': self.get_quick_stats(),
            'recent_sessions': []
        }
        
        # Get recent study sessions
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT subject, topic, duration_minutes, session_date, progress_notes 
            FROM study_sessions 
            WHERE session_date >= ? 
            ORDER BY session_date DESC
        ''', (datetime.now().date() - timedelta(days=7),))
        
        sessions = cursor.fetchall()
        for session in sessions:
            progress_data['recent_sessions'].append({
                'subject': session[0],
                'topic': session[1],
                'duration_minutes': session[2],
                'date': session[3],
                'notes': session[4]
            })
        
        conn.close()
        
        # Save files
        with open(f"{output_dir}/current_progress.json", 'w') as f:
            json.dump(progress_data, f, indent=2)
        
        # Export notifications
        notifications = self.db.get_pending_notifications()
        notif_data = []
        for notif in notifications:
            notif_data.append({
                'id': notif[0],
                'type': notif[1],
                'title': notif[2],
                'message': notif[3],
                'priority': notif[4],
                'created_at': notif[7]
            })
        
        with open(f"{output_dir}/notifications.json", 'w') as f:
            json.dump(notif_data, f, indent=2)
        
        # Create quick commands guide
        commands_md = """# Quick Commands for Claude

## Study Assistance
- `analyze_progress`: Review my recent study activity
- `suggest_topic`: Recommend next topic to study  
- `create_quiz`: Generate quiz questions
- `study_plan`: Create a learning schedule

## Project Help
- `code_review`: Help review my code
- `debug_help`: Assist with debugging
- `project_ideas`: Suggest coding projects
- `best_practices`: Share coding best practices

## NLP Specific
- `nlp_concepts`: Explain NLP concepts
- `nlp_projects`: Suggest NLP project ideas
- `nlp_resources`: Recommend learning resources
- `nlp_practice`: Provide practice exercises

## Data Analysis
- `progress_insights`: Analyze my learning patterns
- `time_optimization`: Suggest time management improvements
- `goal_setting`: Help set realistic learning goals
"""
        
        with open(f"{output_dir}/quick_commands.md", 'w') as f:
            f.write(commands_md)
        
        print(f"✅ Data exported to {output_dir}/ for Claude Desktop")
        return output_dir

def main_menu():
    """Main menu interface"""
    assistant = PersonalAssistant()
    
    # Start background services
    assistant.start_background_services()
    
    while True:
        try:
            assistant.display_dashboard()
            
            print(f"\n" + "="*80)
            print("MAIN MENU")
            print("="*80)
            print("1. 📧 Check emails manually")
            print("2. 📚 Study session menu")
            print("3. 🔔 View/manage notifications")
            print("4. 💻 Coding projects")
            print("5. 🤖 NLP tasks")
            print("6. 📊 Detailed progress report")
            print("7. ⚙️  Settings")
            print("8. 🔗 Claude Desktop integration")
            print("9. 📤 Export data for Claude")
            print("10. ❌ Exit")
            
            choice = input("\nEnter your choice (1-10): ").strip()
            
            if choice == "1":
                emails = assistant.gmail_integrator.check_and_notify_new_emails()
                print(f"✅ Email check complete. Found {len(emails)} new emails.")
            
            elif choice == "2":
                # Import and run study interface
                from study_assistant import main_study_interface
                main_study_interface()
            
            elif choice == "3":
                assistant.notification_manager.display_notifications()
                
                # Option to mark as read
                notif_input = input("\nMark notification as read? (enter ID or 'all'): ").strip()
                if notif_input.lower() == 'all':
                    conn = sqlite3.connect(assistant.db.db_path)
                    cursor = conn.cursor()
                    cursor.execute("UPDATE notifications SET is_read = TRUE")
                    conn.commit()
                    conn.close()
                    print("✅ All notifications marked as read")
                elif notif_input.isdigit():
                    conn = sqlite3.connect(assistant.db.db_path)
                    cursor = conn.cursor()
                    cursor.execute("UPDATE notifications SET is_read = TRUE WHERE id = ?", (int(notif_input),))
                    conn.commit()
                    conn.close()
                    print("✅ Notification marked as read")