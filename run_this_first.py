#!/usr/bin/env python3
"""
Personal Assistant Setup Script
Run this first to set up your personal assistant
"""

import os
import subprocess
import sys

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 7):
        print("❌ Python 3.7 or higher is required")
        print(f"   Current version: {sys.version}")
        return False
    
    print(f"✅ Python version: {sys.version_info.major}.{sys.version_info.minor}")
    return True

def install_packages():
    """Install required Python packages"""
    packages = [
        "schedule",
        "google-auth",
        "google-auth-oauthlib", 
        "google-auth-httplib2",
        "google-api-python-client"
    ]
    
    print("📦 Installing required packages...")
    
    for package in packages:
        try:
            print(f"   Installing {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package, "--quiet"])
            print(f"   ✅ {package} installed")
        except subprocess.CalledProcessError:
            print(f"   ❌ Failed to install {package}")
            print(f"   Try manually: pip install {package}")
            return False
    
    return True

def create_directory_structure():
    """Create necessary directories"""
    directories = [
        "assistant_data",
        "logs",
        "backups"
    ]
    
    print("📁 Creating directory structure...")
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"   ✅ Created {directory}/")
        else:
            print(f"   📁 {directory}/ already exists")

def check_required_files():
    """Check if all required files are present"""
    required_files = [
        "personal_assistant_db.py",
        "gmail_integration.py", 
        "study_assistant.py",
        "main_assistant.py"
    ]
    
    print("📋 Checking required files...")
    
    missing_files = []
    for file in required_files:
        if os.path.exists(file):
            print(f"   ✅ {file}")
        else:
            print(f"   ❌ {file} - MISSING")
            missing_files.append(file)
    
    return len(missing_files) == 0, missing_files

def setup_database():
    """Initialize the database with sample data"""
    try:
        print("🗄️  Setting up database...")
        from personal_assistant_db import setup_sample_data
        setup_sample_data()
        print("   ✅ Database initialized with sample data")
        return True
    except ImportError as e:
        print(f"   ❌ Database setup failed: {e}")
        return False

def create_config_file():
    """Create initial configuration file"""
    config_content = """# Personal Assistant Configuration
# Modify these settings as needed

# Email Settings
EMAIL_CHECK_INTERVAL = 30  # minutes
ENABLE_EMAIL_NOTIFICATIONS = True

# Study Settings
DAILY_STUDY_GOAL = 60  # minutes
STUDY_REMINDER_TIMES = ["09:00", "14:00", "19:00"]

# Notification Settings
NOTIFICATION_PRIORITY_FILTER = "medium"  # show medium and above
ENABLE_DESKTOP_NOTIFICATIONS = True

# Paths
DATA_EXPORT_PATH = "assistant_data"
BACKUP_PATH = "backups"
LOG_PATH = "logs"

# Claude Desktop Integration
CLAUDE_DATA_PATH = "assistant_data"
AUTO_EXPORT_INTERVAL = 60  # minutes
"""
    
    config_file = "config.py"
    if not os.path.exists(config_file):
        with open(config_file, 'w') as f:
            f.write(config_content)
        print(f"✅ Created {config_file}")
    else:
        print(f"📁 {config_file} already exists")

def gmail_setup_instructions():
    """Display Gmail setup instructions"""
    print("\n" + "="*60)
    print("📧 GMAIL INTEGRATION SETUP (OPTIONAL)")
    print("="*60)
    print("""
If you want email integration, follow these steps:

1. 🌐 Go to Google Cloud Console:
   https://console.cloud.google.com/

2. 📋 Create/Select Project:
   - Create new project or select existing one
   - Make note of the project name

3. 🔧 Enable Gmail API:
   - Go to "APIs & Services" > "Library"
   - Search for "Gmail API"
   - Click "Enable"

4. 🔑 Create Credentials:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth 2.0 Client IDs"
   - Choose "Desktop application"
   - Name it "Personal Assistant"

5. 💾 Download Credentials:
   - Click the download button (JSON)
   - Save as 'credentials.json' in this folder
   - Keep this file secure!

6. ⚠️  IMPORTANT: Add your Gmail address to test users:
   - Go to "OAuth consent screen"
   - Add your email to "Test users"

📝 Note: Gmail integration is optional. The assistant works without it!
""")

def create_quick_start_guide():
    """Create a quick start guide"""
    guide_content = """# Personal Assistant - Quick Start Guide

## 🚀 Getting Started

1. **Run the Assistant:**
   ```bash
   python main_assistant.py
   ```

2. **First Time Setup:**
   - The assistant will create sample data
   - Background services will start automatically
   - Dashboard shows your current status

## 📚 Key Features

### Study Tracking
- Log study sessions: subject, topic, duration
- Get personalized topic suggestions
- Track progress across different subjects
- Set and monitor daily study goals

### Notifications
- Automatic study reminders
- Email notifications (if Gmail connected)
- Daily progress summaries
- Priority-based notification system

### Coding Projects
- Track multiple coding projects
- Monitor progress and status
- Store project details and notes
- Set project goals and deadlines

### NLP Learning
- Specialized NLP learning assistance
- Project suggestions by skill level
- Track NLP experiments and models
- Learning resource recommendations

## 🔗 Claude Desktop Integration

1. **Export Data:**
   - Use menu option 9 to export data
   - Files created in `assistant_data/` folder

2. **Share with Claude:**
   - Copy files to Claude Desktop accessible folder
   - Ask Claude to analyze your progress
   - Get personalized learning recommendations

3. **Example Claude Prompts:**
   - "Analyze my study progress and suggest improvements"
   - "Create a study plan based on my current activity"
   - "Help me prioritize my notifications"
   - "Suggest coding projects for my skill level"

## ⚙️ Customization

### Settings (Menu Option 7):
- Email check frequency
- Study reminder times  
- Daily study goals
- Notification preferences

### Database:
- SQLite database stores all your data
- Located at: `personal_assistant.db`
- Can be viewed with DB Browser for SQLite

## 🔧 Troubleshooting

### Common Issues:
1. **Import Errors**: Install packages with `pip install -r requirements.txt`
2. **Gmail Not Working**: Check credentials.json and API setup
3. **Database Issues**: Delete .db file to reset with fresh data
4. **Permission Errors**: Run with appropriate permissions

### Getting Help:
- Check the configuration in `config.py`
- Review log files in `logs/` directory
- Ensure all required files are present

## 📊 Understanding Your Data

### Study Progress:
- Sessions: Number of study sessions
- Hours: Total time spent studying
- Consistency: Percentage of days with study activity

### Notifications:
- Priority levels: urgent > high > medium > low
- Types: email, study_reminder, achievement, summary

### Projects:
- Status: planning > active > paused/completed
- Progress tracked through notes and timestamps

## 🎯 Tips for Success

1. **Consistency**: Use daily reminders to build habits
2. **Goal Setting**: Set realistic daily/weekly study goals
3. **Progress Review**: Check weekly reports to stay motivated
4. **Claude Integration**: Export data regularly for insights
5. **Customization**: Adjust settings to match your schedule

## 📱 Future Enhancements

Potential additions:
- Mobile app integration
- Voice commands
- Advanced analytics
- Integration with calendar apps
- Team collaboration features

---

**Happy Learning! 🎓**
"""
    
    with open("QUICK_START.md", 'w') as f:
        f.write(guide_content)
    
    print("✅ Created QUICK_START.md guide")

def main():
    """Main setup function"""
    print("🤖 PERSONAL ASSISTANT SETUP")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        return False
    
    # Check required files
    files_ok, missing = check_required_files()
    if not files_ok:
        print(f"\n❌ Missing required files: {', '.join(missing)}")
        print("Please ensure all Python files are in the same directory")
        return False
    
    # Install packages
    if not install_packages():
        print("\n❌ Package installation failed")
        return False
    
    # Create directories
    create_directory_structure()
    
    # Create config file
    create_config_file()
    
    # Setup database
    if not setup_database():
        print("\n❌ Database setup failed")
        return False
    
    # Create quick start guide
    create_quick_start_guide()
    
    # Show Gmail setup instructions
    gmail_setup_instructions()
    
    print("\n" + "="*60)
    print("🎉 SETUP COMPLETE!")
    print("="*60)
    
    print("\n✅ What's been set up:")
    print("  📦 All required packages installed")
    print("  🗄️  Database initialized with sample data")
    print("  📁 Directory structure created")
    print("  ⚙️  Configuration file created")
    print("  📋 Quick start guide created")
    
    print("\n🚀 Ready to start!")
    print("  Run: python main_assistant.py")
    
    print("\n📧 Optional: Set up Gmail integration")
    print("  Follow the Gmail setup instructions above")
    
    print("\n📚 Learn more:")
    print("  Read QUICK_START.md for detailed usage guide")
    
    start_now = input("\n🎯 Start the assistant now? (y/n): ").strip().lower()
    
    if start_now == 'y':
        print("\n🚀 Starting Personal Assistant...")
        try:
            from main_assistant import main_menu
            main_menu()
        except ImportError as e:
            print(f"❌ Import error: {e}")
            print("Please check that all files are present and try again")
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
    else:
        print("\n📝 When ready, run: python main_assistant.py")
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        print("\n❌ Setup failed. Please resolve the issues and try again.")
        sys.exit(1)
    else:
        print("\n✅ Setup successful!")