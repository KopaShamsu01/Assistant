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
        unstudied_topics = [