# Gmail Integration for Personal Assistant
# Note: This requires Gmail API setup - I'll show you the steps below

import os
import pickle
import base64
from datetime import datetime, timedelta
import json
import re
from email.mime.text import MIMEText

# Note: You'll need to install these packages:
# pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client

class GmailIntegrator:
    def __init__(self, db_instance):
        """Initialize Gmail integration with database instance"""
        self.db = db_instance
        self.service = None
        self.credentials_path = 'credentials.json'  # Download from Google Cloud Console
        self.token_path = 'token.pickle'
        
    def setup_gmail_api(self):
        """
        Setup Gmail API - You need to:
        1. Go to Google Cloud Console
        2. Enable Gmail API
        3. Create credentials (OAuth 2.0)
        4. Download credentials.json file
        """
        try:
            from google.auth.transport.requests import Request
            from google_auth_oauthlib.flow import InstalledAppFlow
            from googleapiclient.discovery import build
            
            SCOPES = ['https://www.googleapis.com/auth/gmail.readonly',
                     'https://www.googleapis.com/auth/gmail.send']
            
            creds = None
            
            # Load existing credentials
            if os.path.exists(self.token_path):
                with open(self.token_path, 'rb') as token:
                    creds = pickle.load(token)
            
            # If no valid credentials, get new ones
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    if not os.path.exists(self.credentials_path):
                        print(f"❌ {self.credentials_path} not found!")
                        print("📋 Setup Instructions:")
                        print("1. Go to: https://console.cloud.google.com/")
                        print("2. Enable Gmail API")
                        print("3. Create OAuth 2.0 credentials")
                        print("4. Download as 'credentials.json'")
                        return False
                    
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_path, SCOPES)
                    creds = flow.run_local_server(port=0)
                
                # Save credentials
                with open(self.token_path, 'wb') as token:
                    pickle.dump(creds, token)
            
            self.service = build('gmail', 'v1', credentials=creds)
            print("✅ Gmail API connected successfully!")
            return True
            
        except ImportError:
            print("❌ Google API libraries not installed!")
            print("Run: pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client")
            return False
        except Exception as e:
            print(f"❌ Gmail setup error: {e}")
            return False
    
    def fetch_recent_emails(self, max_results=10, query='is:unread'):
        """Fetch recent emails from Gmail"""
        if not self.service:
            if not self.setup_gmail_api():
                return []
        
        try:
            # Get list of messages
            results = self.service.users().messages().list(
                userId='me', 
                q=query, 
                maxResults=max_results
            ).execute()
            
            messages = results.get('messages', [])
            
            email_data = []
            for message in messages:
                # Get full message details
                msg = self.service.users().messages().get(
                    userId='me', 
                    id=message['id']
                ).execute()
                
                # Extract email details
                headers = msg['payload'].get('headers', [])
                
                sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
                subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
                date_str = next((h['value'] for h in headers if h['name'] == 'Date'), '')
                
                # Get email body
                body = self.extract_email_body(msg['payload'])
                
                # Get snippet
                snippet = msg.get('snippet', '')
                
                # Get labels
                labels = msg.get('labelIds', [])
                
                email_info = {
                    'gmail_id': message['id'],
                    'sender': sender,
                    'subject': subject,
                    'snippet': snippet,
                    'body': body[:1000] if body else snippet,  # Limit body length
                    'labels': labels,
                    'date': date_str
                }
                
                email_data.append(email_info)
                
                # Save to database
                self.db.add_email(
                    gmail_id=message['id'],
                    sender=sender,
                    subject=subject,
                    snippet=snippet,
                    body=body,
                    labels=labels
                )
            
            return email_data
            
        except Exception as e:
            print(f"❌ Error fetching emails: {e}")
            return []
    
    def extract_email_body(self, payload):
        """Extract email body from payload"""
        body = ""
        
        if 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    data = part['body']['data']
                    body = base64.urlsafe_b64decode(data).decode('utf-8')
                    break
        else:
            if payload['mimeType'] == 'text/plain':
                data = payload['body']['data']
                body = base64.urlsafe_b64decode(data).decode('utf-8')
        
        return body
    
    def analyze_emails_for_notifications(self, emails):
        """Analyze emails and create appropriate notifications"""
        important_keywords = [
            'urgent', 'important', 'asap', 'deadline', 'meeting', 
            'interview', 'project', 'submit', 'payment', 'invoice'
        ]
        
        for email in emails:
            priority = 'medium'
            action_required = False
            
            # Check for important keywords
            text_to_check = (email['subject'] + ' ' + email['snippet']).lower()
            
            if any(keyword in text_to_check for keyword in important_keywords):
                priority = 'high'
                action_required = True
            
            # Check if from important domains
            sender_domain = email['sender'].split('@')[-1] if '@' in email['sender'] else ''
            important_domains = ['work.com', 'university.edu', 'bank.com']  # Add your important domains
            
            if any(domain in sender_domain for domain in important_domains):
                priority = 'high'
            
            # Create notification
            self.db.create_notification(
                type='email',
                title=f"New email: {email['subject'][:50]}...",
                message=f"From: {email['sender']}\n{email['snippet'][:100]}...",
                priority=priority
            )
    
    def check_and_notify_new_emails(self):
        """Check for new emails and create notifications"""
        print("🔍 Checking for new emails...")
        
        emails = self.fetch_recent_emails(max_results=5, query='is:unread newer_than:1h')
        
        if emails:
            print(f"📧 Found {len(emails)} recent unread emails")
            self.analyze_emails_for_notifications(emails)
            
            # Create summary notification
            self.db.create_notification(
                type='email_summary',
                title=f"Email Summary: {len(emails)} new emails",
                message=f"You have {len(emails)} new unread emails in the last hour",
                priority='medium'
            )
        else:
            print("📫 No new emails found")
        
        return emails

class NotificationManager:
    def __init__(self, db_instance):
        """Initialize notification manager"""
        self.db = db_instance
    
    def create_study_reminder(self, subject, time_str="now"):
        """Create study reminder notifications"""
        messages = {
            'nlp': "Time for your NLP learning session! 🤖",
            'coding': "Time to code! Start your programming session 💻",
            'python': "Python practice time! 🐍",
            'machine_learning': "ML study time! 📊"
        }
        
        message = messages.get(subject.lower().replace(' ', '_'), 
                              f"Time to study {subject}! 📚")
        
        return self.db.create_notification(
            type='study_reminder',
            title=f"Study Reminder: {subject}",
            message=message,
            priority='medium'
        )
    
    def create_coding_reminder(self, project_name):
        """Create coding project reminder"""
        return self.db.create_notification(
            type='coding_reminder',
            title=f"Coding Reminder: {project_name}",
            message=f"Continue working on your {project_name} project 🚀",
            priority='medium'
        )
    
    def display_notifications(self):
        """Display all pending notifications"""
        notifications = self.db.get_pending_notifications()
        
        if not notifications:
            print("🎉 No pending notifications!")
            return
        
        print("\n" + "="*60)
        print("📢 PENDING NOTIFICATIONS")
        print("="*60)
        
        priority_order = {'urgent': 1, 'high': 2, 'medium': 3, 'low': 4}
        sorted_notifications = sorted(notifications, 
                                    key=lambda x: priority_order.get(x[4], 5))
        
        for notif in sorted_notifications:
            id, type, title, message, priority, is_read, scheduled_for, created_at, action_required, metadata = notif
            
            # Priority emoji
            priority_emoji = {
                'urgent': '🚨',
                'high': '❗',
                'medium': '📋',
                'low': '💭'
            }.get(priority, '📌')
            
            print(f"\n{priority_emoji} {title}")
            print(f"   Type: {type.upper()} | Priority: {priority.upper()}")
            if message:
                print(f"   {message[:100]}{'...' if len(message) > 100 else ''}")
            print(f"   Created: {created_at}")
            
            if action_required:
                print("   ⚠️  ACTION REQUIRED")

# Gmail API Setup Instructions
def print_gmail_setup_instructions():
    print("\n" + "="*60)
    print("📧 GMAIL API SETUP INSTRUCTIONS")
    print("="*60)
    print("""
1. Go to Google Cloud Console: https://console.cloud.google.com/
2. Create a new project or select existing one
3. Enable Gmail API:
   - Go to "APIs & Services" > "Library"
   - Search for "Gmail API"
   - Click "Enable"
4. Create credentials:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth 2.0 Client IDs"
   - Choose "Desktop application"
   - Download the JSON file as 'credentials.json'
5. Place 'credentials.json' in your project folder
6. Install required packages:
   pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
    """)

if __name__ == "__main__":
    # This is a demo - you need to set up Gmail API first
    print_gmail_setup_instructions()
    
    print("\n" + "="*60)
    print("🤖 PERSONAL ASSISTANT - GMAIL INTEGRATION")
    print("="*60)
    
    # For now, create some demo notifications
    from personal_assistant_db import PersonalAssistantDB
    
    db = PersonalAssistantDB()
    notif_manager = NotificationManager(db)
    
    # Create some sample notifications
    notif_manager.create_study_reminder("NLP")
    notif_manager.create_study_reminder("Python")
    notif_manager.create_coding_reminder("Personal Assistant")
    
    # Display notifications
    notif_manager.display_notifications()