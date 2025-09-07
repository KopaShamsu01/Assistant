import random
import json
from datetime import datetime, timedelta
import os
import re

class StudyAssistant:
    def __init__(self, db_instance):
        """Initialize study assistant with database"""
        self.db = db_instance
        
        # Study topics and resources
        self.study_topics = {
            'nlp': {
                'beginner': [
                    'Text preprocessing', 'Tokenization', 'Stop words removal',
                    'Stemming and Lemmatization', 'Bag of Words', 'TF-IDF'
                ],
                'intermediate': [
                    'Word embeddings', 'Word2Vec', 'GloVe', 'Sentiment analysis',
                    'Named Entity Recognition', 'Part-of-speech tagging'
                ],
                'advanced': [
                    'BERT and Transformers', 'GPT models', 'Attention mechanism',
                    'Sequence-to-sequence models', 'Transfer learning in NLP'
                ]
            },
            'python': {
                'beginner': [
                    'Variables and data types', 'Control structures', 'Functions',
                    'Lists and dictionaries', 'File handling', 'Exception handling'
                ],
                'intermediate': [
                    'Object-oriented programming', 'Decorators', 'Generators',
                    'Regular expressions', 'Working with APIs', 'Database connections'
                ],
                'advanced': [
                    'Metaclasses', 'Async programming', 'Performance optimization',
                    'Design patterns', 'Testing frameworks', 'Package development'
                ]
            },
            'machine_learning': {
                'beginner': [
                    'Supervised vs Unsupervised learning', 'Linear regression',
                    'Logistic regression', 'Decision trees', 'Cross-validation'
                ],
                'intermediate': [
                    'Random forests', 'SVM', 'K-means clustering', 'Neural networks',
                    'Feature engineering', 'Model evaluation metrics'
                ],
                'advanced': [
                    'Deep learning', 'Convolutional networks', 'Recurrent networks',
                    'Ensemble methods', 'Hyperparameter tuning', 'MLOps'
                ]
            }
        }
        
        # Coding challenges by difficulty
        self.coding_challenges = {
            'beginner': [
                "Write a function to reverse a string",
                "Find the largest number in a list",
                "Check if a number is prime",
                "Count vowels in a string",
                "Calculate factorial recursively"
            ],
            'intermediate': [
                "Implement a binary search algorithm",
                "Find the longest palindromic substring",
                "Merge two sorted arrays",
                "Implement a stack using arrays",
                "Find duplicate elements in array"
            ],
            'advanced': [
                "Implement a LRU cache",
                "Find shortest path in a graph",
                "Design a rate limiter",
                "Implement a trie data structure",
                "Solve N-Queens problem"
            ]
        }
    
    def suggest_study_topic(self, subject, level='beginner'):
        """Suggest a study topic based on recent progress"""
        conn = self.db.db.connect(self.db.db_path)
        cursor = conn.cursor()
        
        # Get recently studied topics
        cursor.execute('''
            SELECT topic FROM study_sessions 
            WHERE subject = ? AND session_date >= ?
            ORDER BY session_date DESC LIMIT 5
        ''', (subject, datetime.now().date() - timedelta(days=7)))
        
        recent_topics = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        # Get all topics for the subject and level
        available_topics = self.study_topics.get(subject.lower(), {}).get(level, [])
        
        if not available_topics:
            return f"No topics available for {subject} at {level} level"
        
        # Filter out recently studied topics
        unstudied_topics = [topic for topic in available_topics 
                          if topic not in recent_topics]
        
        # If all topics recently studied, suggest review
        if not unstudied_topics:
            return f"Consider reviewing: {random.choice(recent_topics)}"
        
        return random.choice(unstudied_topics)
    
    def create_study_plan(self, subject, hours_per_week=5, weeks=4):
        """Create a personalized study plan"""
        topics = []
        for level in ['beginner', 'intermediate', 'advanced']:
            level_topics = self.study_topics.get(subject.lower(), {}).get(level, [])
            topics.extend([(topic, level) for topic in level_topics])
        
        # Calculate topics per week
        topics_per_week = len(topics) // weeks if topics else 1
        hours_per_topic = hours_per_week / topics_per_week if topics_per_week > 0 else hours_per_week
        
        study_plan = {
            'subject': subject,
            'duration_weeks': weeks,
            'hours_per_week': hours_per_week,
            'hours_per_topic': round(hours_per_topic, 1),
            'weekly_schedule': []
        }
        
        # Distribute topics across weeks
        for week in range(weeks):
            start_idx = week * topics_per_week
            end_idx = min((week + 1) * topics_per_week, len(topics))
            week_topics = topics[start_idx:end_idx]
            
            study_plan['weekly_schedule'].append({
                'week': week + 1,
                'topics': week_topics,
                'estimated_hours': len(week_topics) * hours_per_topic
            })
        
        return study_plan
    
    def get_coding_challenge(self, difficulty='beginner'):
        """Get a random coding challenge"""
        challenges = self.coding_challenges.get(difficulty, self.coding_challenges['beginner'])
        return random.choice(challenges)
    
    def track_study_session(self, subject, topic, duration_minutes, notes=None, difficulty_rating=3):
        """Track a completed study session"""
        session_id = self.db.log_study_session(subject, topic, duration_minutes)
        
        # Create achievement notification
        hours = duration_minutes / 60
        self.db.create_notification(
            type='study_achievement',
            title=f'Study Session Completed! 🎉',
            message=f'Great job! You studied {topic} ({subject}) for {hours:.1f} hours',
            priority='low'
        )
        
        return session_id
    
    def get_study_recommendations(self):
        """Get personalized study recommendations"""
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        
        # Get recent study patterns
        cursor.execute('''
            SELECT subject, COUNT(*) as sessions, AVG(duration_minutes) as avg_duration,
                   MAX(session_date) as last_session
            FROM study_sessions 
            WHERE session_date >= ?
            GROUP BY subject
            ORDER BY last_session DESC
        ''', (datetime.now().date() - timedelta(days=14),))
        
        recent_activity = cursor.fetchall()
        conn.close()
        
        recommendations = []
        
        if not recent_activity:
            recommendations.append({
                'type': 'start_studying',
                'message': 'Start your learning journey! Try studying NLP or Python basics.',
                'action': 'Begin with beginner topics'
            })
        else:
            for subject, sessions, avg_duration, last_session in recent_activity:
                days_since = (datetime.now().date() - datetime.strptime(last_session, '%Y-%m-%d').date()).days
                
                if days_since > 3:
                    recommendations.append({
                        'type': 'consistency',
                        'message': f'You haven\'t studied {subject} for {days_since} days. Keep the momentum!',
                        'action': f'Schedule a {subject} session today'
                    })
                
                if avg_duration < 30:
                    recommendations.append({
                        'type': 'duration',
                        'message': f'Consider longer {subject} sessions (current avg: {avg_duration:.0f}min)',
                        'action': 'Aim for 45-60 minute sessions'
                    })
        
        return recommendations
    
    def generate_quiz_questions(self, subject, level='beginner', num_questions=5):
        """Generate quiz questions for a subject"""
        # This is a simplified version - in practice, you'd have a question bank
        question_templates = {
            'nlp': {
                'beginner': [
                    "What is tokenization in NLP?",
                    "What are stop words?",
                    "Explain the difference between stemming and lemmatization",
                    "What is TF-IDF?",
                    "What is the bag of words model?"
                ],
                'intermediate': [
                    "How do word embeddings work?",
                    "What is the difference between Word2Vec and GloVe?",
                    "Explain sentiment analysis techniques",
                    "What is Named Entity Recognition?",
                    "How does part-of-speech tagging work?"
                ]
            },
            'python': {
                'beginner': [
                    "What are the main data types in Python?",
                    "How do you handle exceptions in Python?",
                    "What is the difference between a list and a tuple?",
                    "How do you read a file in Python?",
                    "What is a function in Python?"
                ],
                'intermediate': [
                    "What is a decorator in Python?",
                    "How do generators work?",
                    "Explain object-oriented programming concepts",
                    "What are lambda functions?",
                    "How do you work with APIs in Python?"
                ]
            }
        }
        
        questions = question_templates.get(subject.lower(), {}).get(level, [])
        if not questions:
            return ["No questions available for this topic"]
        
        return random.sample(questions, min(num_questions, len(questions)))

class NLPLearningAssistant:
    """Specialized assistant for NLP learning"""
    
    def __init__(self, db_instance):
        self.db = db_instance
        
        self.nlp_libraries = {
            'nltk': 'Natural Language Toolkit - Great for beginners',
            'spacy': 'Industrial-strength NLP - Fast and efficient',
            'transformers': 'State-of-the-art transformer models',
            'gensim': 'Topic modeling and word embeddings',
            'textblob': 'Simple API for common NLP tasks'
        }
        
        self.nlp_datasets = {
            'sentiment': ['IMDB Movie Reviews', 'Stanford Sentiment Treebank', 'Amazon Product Reviews'],
            'classification': ['20 Newsgroups', 'Reuters-21578', 'AG News'],
            'ner': ['CoNLL-2003', 'OntoNotes 5.0'],
            'qa': ['SQuAD', 'Natural Questions'],
            'summarization': ['CNN/DailyMail', 'XSum']
        }
    
    def suggest_nlp_project(self, skill_level='beginner'):
        """Suggest NLP projects based on skill level"""
        projects = {
            'beginner': [
                {
                    'name': 'Sentiment Analysis Tool',
                    'description': 'Build a tool to analyze sentiment in movie reviews',
                    'libraries': ['nltk', 'sklearn'],
                    'difficulty': 'Easy',
                    'estimated_time': '1-2 weeks'
                },
                {
                    'name': 'Text Summarizer',
                    'description': 'Create an extractive text summarization tool',
                    'libraries': ['nltk', 'sumy'],
                    'difficulty': 'Easy-Medium',
                    'estimated_time': '1 week'
                }
            ],
            'intermediate': [
                {
                    'name': 'Chatbot with Intent Recognition',
                    'description': 'Build a chatbot that can understand user intents',
                    'libraries': ['spacy', 'rasa'],
                    'difficulty': 'Medium',
                    'estimated_time': '3-4 weeks'
                },
                {
                    'name': 'Named Entity Recognition System',
                    'description': 'Train a custom NER model for specific domains',
                    'libraries': ['spacy', 'transformers'],
                    'difficulty': 'Medium',
                    'estimated_time': '2-3 weeks'
                }
            ],
            'advanced': [
                {
                    'name': 'Question Answering System',
                    'description': 'Build a BERT-based QA system',
                    'libraries': ['transformers', 'pytorch'],
                    'difficulty': 'Hard',
                    'estimated_time': '4-6 weeks'
                },
                {
                    'name': 'Text Generation with GPT',
                    'description': 'Fine-tune GPT for domain-specific text generation',
                    'libraries': ['transformers', 'pytorch'],
                    'difficulty': 'Hard',
                    'estimated_time': '6-8 weeks'
                }
            ]
        }
        
        return random.choice(projects.get(skill_level, projects['beginner']))
    
    def create_nlp_learning_path(self):
        """Create a comprehensive NLP learning path"""
        learning_path = {
            'phase_1': {
                'title': 'NLP Fundamentals (4-6 weeks)',
                'topics': [
                    'Text preprocessing and cleaning',
                    'Tokenization and normalization',
                    'Feature extraction (BoW, TF-IDF)',
                    'Basic text classification',
                    'Sentiment analysis'
                ],
                'projects': ['Movie review sentiment classifier'],
                'resources': ['NLTK Book', 'Python for NLP tutorials']
            },
            'phase_2': {
                'title': 'Intermediate NLP (6-8 weeks)',
                'topics': [
                    'Word embeddings (Word2Vec, GloVe)',
                    'Named Entity Recognition',
                    'Part-of-speech tagging',
                    'Language modeling',
                    'Topic modeling'
                ],
                'projects': ['Custom NER system', 'Topic modeling for documents'],
                'resources': ['spaCy documentation', 'Gensim tutorials']
            },
            'phase_3': {
                'title': 'Advanced NLP (8-12 weeks)',
                'topics': [
                    'Neural networks for NLP',
                    'Attention mechanism',
                    'Transformer architecture',
                    'BERT and its variants',
                    'Fine-tuning pre-trained models'
                ],
                'projects': ['BERT-based text classifier', 'Question answering system'],
                'resources': ['Transformers library', 'Papers on ArXiv']
            }
        }
        
        return learning_path

def main_study_interface():
    """Main interface for the study assistant"""
    from personal_assistant_db import PersonalAssistantDB
    
    db = PersonalAssistantDB()
    study_assistant = StudyAssistant(db)
    nlp_assistant = NLPLearningAssistant(db)
    
    while True:
        print("\n" + "="*60)
        print("📚 PERSONAL STUDY ASSISTANT")
        print("="*60)
        print("1. Get study topic suggestion")
        print("2. Track study session")
        print("3. Create study plan")
        print("4. Get coding challenge")
        print("5. NLP project suggestion")
        print("6. Study recommendations")
        print("7. Generate quiz questions")
        print("8. View study progress")
        print("9. Exit")
        
        choice = input("\nEnter your choice (1-9): ").strip()
        
        if choice == "1":
            subject = input("Subject (nlp/python/machine_learning): ").strip()
            level = input("Level (beginner/intermediate/advanced): ").strip() or "beginner"
            
            suggestion = study_assistant.suggest_study_topic(subject, level)
            print(f"\n💡 Suggested topic: {suggestion}")
        
        elif choice == "2":
            subject = input("Subject: ").strip()
            topic = input("Topic studied: ").strip()
            duration = int(input("Duration (minutes): "))
            notes = input("Notes (optional): ").strip() or None
            
            session_id = study_assistant.track_study_session(subject, topic, duration, notes)
            print(f"✅ Study session logged! (ID: {session_id})")
        
        elif choice == "3":
            subject = input("Subject for study plan: ").strip()
            hours = int(input("Hours per week: ") or "5")
            weeks = int(input("Duration in weeks: ") or "4")
            
            plan = study_assistant.create_study_plan(subject, hours, weeks)
            print(f"\n📋 Study Plan for {subject}:")
            for week_plan in plan['weekly_schedule']:
                print(f"Week {week_plan['week']} ({week_plan['estimated_hours']} hours):")
                for topic, level in week_plan['topics']:
                    print(f"  - {topic} ({level})")
        
        elif choice == "4":
            difficulty = input("Difficulty (beginner/intermediate/advanced): ").strip() or "beginner"
            challenge = study_assistant.get_coding_challenge(difficulty)
            print(f"\n💻 Coding Challenge: {challenge}")
        
        elif choice == "5":
            level = input("Your NLP skill level (beginner/intermediate/advanced): ").strip() or "beginner"
            project = nlp_assistant.suggest_nlp_project(level)
            print(f"\n🤖 NLP Project Suggestion:")
            print(f"Name: {project['name']}")
            print(f"Description: {project['description']}")
            print(f"Libraries: {', '.join(project['libraries'])}")
            print(f"Difficulty: {project['difficulty']}")
            print(f"Estimated Time: {project['estimated_time']}")
        
        elif choice == "6":
            recommendations = study_assistant.get_study_recommendations()
            print(f"\n🎯 Study Recommendations:")
            for i, rec in enumerate(recommendations, 1):
                print(f"{i}. {rec['message']}")
                print(f"   Action: {rec['action']}")
        
        elif choice == "7":
            subject = input("Subject for quiz: ").strip()
            level = input("Level: ").strip() or "beginner"
            num_q = int(input("Number of questions (1-10): ") or "5")
            
            questions = study_assistant.generate_quiz_questions(subject, level, num_q)
            print(f"\n❓ Quiz Questions for {subject} ({level}):")
            for i, question in enumerate(questions, 1):
                print(f"{i}. {question}")
        
        elif choice == "8":
            progress = db.get_study_progress(days=14)
            print(f"\n📊 Study Progress (Last 14 days):")
            for subject, sessions, total_minutes in progress:
                hours = total_minutes / 60 if total_minutes else 0
                print(f"• {subject}: {sessions} sessions, {hours:.1f} hours")
        
        elif choice == "9":
            print("👋 Happy studying!")
            break
        
        else:
            print("❌ Invalid choice. Please try again.")

if __name__ == "__main__":
    main_study_interface()