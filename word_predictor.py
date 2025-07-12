import json
import random
import re
from collections import defaultdict, Counter

class WordPredictor:
    def __init__(self):
        # Common sentence templates for accessibility
        self.sentence_templates = {
            'greetings': [
                "Hello, how are you?",
                "Good morning!",
                "Good afternoon!",
                "Good evening!",
                "Nice to meet you!",
                "How are you doing?"
            ],
            'basic_needs': [
                "I need help",
                "I am hungry",
                "I am thirsty", 
                "I need to go to the bathroom",
                "I am tired",
                "I feel sick",
                "I am cold",
                "I am hot"
            ],
            'emotions': [
                "I am happy",
                "I am sad",
                "I am angry",
                "I am excited",
                "I am worried",
                "I am confused",
                "I love you",
                "I miss you"
            ],
            'requests': [
                "Can you help me?",
                "Please wait",
                "Thank you",
                "You're welcome",
                "Excuse me",
                "I'm sorry",
                "Please repeat that",
                "I don't understand"
            ],
            'daily_activities': [
                "I want to eat",
                "I want to drink water",
                "I want to go home",
                "I want to sleep",
                "I want to watch TV",
                "I want to go outside",
                "I want to call someone",
                "I want to rest"
            ],
            'yes_no': [
                "Yes",
                "No",
                "Maybe",
                "I don't know",
                "I agree",
                "I disagree"
            ]
        }
        
        # Complete word associations matching tutorial gestures
        self.word_associations = {
            # Numbers (8 gestures)
            'zero': ['numbers'], 'one': ['numbers'], 'two': ['numbers'], 'three': ['numbers'],
            'four': ['numbers'], 'five': ['numbers'], 'peace': ['emotions', 'greetings'], 'okay': ['yes_no', 'agreement'],

            # Emotions (8 gestures)
            'good': ['emotions', 'positive'], 'bad': ['emotions', 'negative'], 'love': ['emotions', 'positive'],
            'happy': ['emotions', 'positive'], 'sad': ['emotions', 'negative'], 'worried': ['emotions', 'negative'],
            'tired': ['emotions', 'negative'], 'grateful': ['emotions', 'positive'],

            # Basic Needs (8 gestures)
            'help': ['requests', 'urgent'], 'stop': ['requests', 'urgent'], 'eat': ['basic_needs'],
            'drink': ['basic_needs'], 'sleep': ['basic_needs'], 'hot': ['basic_needs'],
            'cold': ['basic_needs'], 'bathroom': ['basic_needs', 'urgent'],

            # Social (9 gestures)
            'hello': ['greetings'], 'bye': ['greetings'], 'yes': ['yes_no'], 'no': ['yes_no'],
            'please': ['requests', 'polite'], 'thanks': ['greetings', 'polite'], 'you': ['social'],
            'me': ['social'], 'call': ['daily_activities']
        }

        # Expanded sentence templates for all sectors
        self.sentence_templates = {
            'greetings': [
                "Hello! How are you?", "Good morning!", "Good afternoon!", "Good evening!",
                "Nice to meet you!", "How are you doing?", "Hello there!", "Hi! Great to see you!",
                "Welcome!", "Good to see you again!", "Hello! Hope you're well!",
                "Hi! How's your day?", "Greetings!", "Hello! What's new?", "Hi there!"
            ],
            'emotions': [
                "I am happy!", "I feel good!", "I love this!", "I am excited!",
                "I feel sad", "I am worried", "I feel scared", "I am angry",
                "I feel calm", "I am grateful", "I feel proud", "I am confused",
                "I feel tired", "I am hurt", "I feel comfortable", "I am surprised"
            ],
            'basic_needs': [
                "I need help!", "I am hungry", "I am thirsty", "I need to rest",
                "I need to go to the bathroom", "I am tired", "I feel sick", "I am cold",
                "I am hot", "I need water", "I want to eat", "I need to sleep",
                "I need medicine", "I want to sit down", "I need fresh air"
            ],
            'requests': [
                "Can you help me?", "Please wait", "Please stop", "Come here please",
                "Please listen", "Look at this", "Please be quiet", "Can you speak louder?",
                "Please repeat that", "I don't understand", "Can you explain?", "Help me please",
                "Please give me that", "Can you show me?", "Please wait for me"
            ],
            'daily_activities': [
                "I want to work", "Let's play together", "I need to study", "Time to exercise",
                "I want to cook", "Let's clean up", "I need to drive", "Let's go for a walk",
                "I want to read", "Time to write", "Let's watch something", "I love music",
                "Let's go shopping", "I want to travel", "Time to rest", "Let's celebrate"
            ],
            'social': [
                "Nice to meet you!", "You are my friend", "I love my family", "Let's talk",
                "Thank you so much", "I am sorry", "Excuse me please", "You're welcome",
                "Let's call someone", "I'll text you", "See you later", "Take care",
                "Have a great day", "Good luck", "Congratulations!"
            ],
            'objects': [
                "I need my phone", "Where is my computer?", "I want to read a book",
                "I need a pen", "Can I have a cup?", "I want some food",
                "I need my car", "I'm going home", "I need money", "Where are my keys?",
                "Open the door", "Close the window", "I need a chair", "Clean the table",
                "I want to go to bed", "I need new clothes", "Where are my shoes?"
            ],
            'numbers': [
                "I need one thing", "Give me two please", "I want three items",
                "There are four people", "I have five dollars", "Count to ten",
                "I need more help", "That's too many", "Give me all of them",
                "I don't want any", "Just half please", "Make it double"
            ],
            'yes_no': [
                "Yes, I agree", "No, I don't want that", "Maybe later",
                "I don't know", "That's correct", "That's wrong",
                "Absolutely yes", "Definitely no", "I'm not sure",
                "Yes please", "No thank you", "Perhaps"
            ]
        }

        # Complete word semantic mappings for tutorial gestures
        self.word_semantics = {
            # Numbers
            'zero': {'type': 'number', 'value': 0}, 'one': {'type': 'number', 'value': 1},
            'two': {'type': 'number', 'value': 2}, 'three': {'type': 'number', 'value': 3},
            'four': {'type': 'number', 'value': 4}, 'five': {'type': 'number', 'value': 5},
            'peace': {'type': 'emotion', 'sentiment': 'positive'}, 'okay': {'type': 'agreement', 'sentiment': 'neutral'},

            # Emotions
            'good': {'type': 'emotion', 'sentiment': 'positive'}, 'bad': {'type': 'emotion', 'sentiment': 'negative'},
            'love': {'type': 'emotion', 'sentiment': 'very_positive'}, 'happy': {'type': 'emotion', 'sentiment': 'positive'},
            'sad': {'type': 'emotion', 'sentiment': 'negative'}, 'worried': {'type': 'emotion', 'sentiment': 'negative'},
            'tired': {'type': 'emotion', 'sentiment': 'negative'}, 'grateful': {'type': 'emotion', 'sentiment': 'positive'},

            # Basic Needs
            'help': {'type': 'request', 'urgency': 'high'}, 'stop': {'type': 'request', 'urgency': 'high'},
            'eat': {'type': 'need', 'category': 'food'}, 'drink': {'type': 'need', 'category': 'water'},
            'sleep': {'type': 'need', 'category': 'rest'}, 'bathroom': {'type': 'need', 'urgency': 'high'},
            'hot': {'type': 'condition', 'temperature': 'high'}, 'cold': {'type': 'condition', 'temperature': 'low'},

            # Social
            'hello': {'type': 'greeting', 'sentiment': 'positive'}, 'bye': {'type': 'farewell', 'sentiment': 'neutral'},
            'yes': {'type': 'agreement', 'response': 'positive'}, 'no': {'type': 'agreement', 'response': 'negative'},
            'please': {'type': 'politeness', 'level': 'high'}, 'thanks': {'type': 'politeness', 'level': 'high'},
            'you': {'type': 'pronoun', 'person': 'second'}, 'me': {'type': 'pronoun', 'person': 'first'},
            'call': {'type': 'action', 'category': 'communication'}
        }
    
    def predict_sentences(self, words):
        """AI-powered sentence prediction based on collected words"""
        if not words:
            return self.get_default_sentences()

        # Generate AI-powered sentences
        ai_sentences = self.generate_ai_sentences(words)

        # Get template-based sentences for fallback
        template_sentences = self.get_template_sentences(words)

        # Create custom rule-based sentences
        custom_sentences = self.create_custom_sentences(words)

        # Combine all suggestions with AI sentences prioritized
        all_sentences = ai_sentences + custom_sentences + template_sentences

        # Remove duplicates while preserving order
        unique_sentences = list(dict.fromkeys(all_sentences))

        # Return top 15 suggestions for better variety
        return unique_sentences[:15]

    def generate_ai_sentences(self, words):
        """Generate natural sentences using AI-like pattern matching and context analysis"""
        sentences = []
        words_lower = [word.lower() for word in words]

        # Analyze word types and context
        word_types = self.analyze_word_types(words_lower)
        context = self.determine_context(words_lower)

        # Generate sentences based on context and patterns
        if context['is_greeting']:
            sentences.extend(self.generate_greeting_sentences(words_lower, word_types))

        if context['is_request']:
            sentences.extend(self.generate_request_sentences(words_lower, word_types))

        if context['is_emotional']:
            sentences.extend(self.generate_emotional_sentences(words_lower, word_types))

        if context['has_numbers']:
            sentences.extend(self.generate_quantity_sentences(words_lower, word_types))

        if context['is_action']:
            sentences.extend(self.generate_action_sentences(words_lower, word_types))

        # Generate combination sentences using multiple words
        sentences.extend(self.generate_combination_sentences(words_lower, word_types))

        # Generate contextual variations
        sentences.extend(self.generate_contextual_variations(words_lower, context))

        return sentences[:8]  # Return top 8 AI-generated sentences

    def analyze_word_types(self, words):
        """Analyze the types and semantics of words"""
        analysis = {
            'greetings': [],
            'emotions': [],
            'actions': [],
            'numbers': [],
            'pronouns': [],
            'adjectives': [],
            'requests': []
        }

        for word in words:
            if word in self.word_semantics:
                semantic = self.word_semantics[word]
                word_type = semantic.get('type', 'unknown')

                if word_type == 'greeting':
                    analysis['greetings'].append(word)
                elif word_type == 'emotion':
                    analysis['emotions'].append(word)
                elif word_type == 'action':
                    analysis['actions'].append(word)
                elif word_type == 'number':
                    analysis['numbers'].append(word)
                elif word_type == 'pronoun':
                    analysis['pronouns'].append(word)
                elif word_type == 'adjective':
                    analysis['adjectives'].append(word)
                elif word_type in ['agreement', 'farewell']:
                    analysis['requests'].append(word)

        return analysis

    def determine_context(self, words):
        """Determine the overall context and intent of the words"""
        context = {
            'is_greeting': False,
            'is_request': False,
            'is_emotional': False,
            'has_numbers': False,
            'is_action': False,
            'sentiment': 'neutral',
            'urgency': 'normal'
        }

        for word in words:
            if word in self.word_semantics:
                semantic = self.word_semantics[word]

                if semantic.get('type') == 'greeting':
                    context['is_greeting'] = True
                elif semantic.get('type') == 'emotion':
                    context['is_emotional'] = True
                elif semantic.get('type') == 'action':
                    context['is_action'] = True
                elif semantic.get('type') == 'number':
                    context['has_numbers'] = True

                if semantic.get('urgency') == 'high':
                    context['urgency'] = 'high'
                    context['is_request'] = True

                if semantic.get('sentiment'):
                    context['sentiment'] = semantic['sentiment']

        # Additional context rules
        if 'help' in words or 'stop' in words:
            context['is_request'] = True
            context['urgency'] = 'high'

        if 'you' in words:
            context['is_request'] = True

        return context

    def generate_greeting_sentences(self, words, word_types):
        """Generate greeting-based sentences"""
        sentences = []

        if 'hello' in words:
            sentences.extend([
                "Hello! How are you?",
                "Hello there!",
                "Hi! Nice to see you!",
                "Hello! How can I help you?"
            ])

            if 'good' in words:
                sentences.extend([
                    "Hello! I hope you're having a good day!",
                    "Good to see you! Hello!",
                    "Hello! Everything is good!"
                ])

        if 'good' in words and 'you' in words:
            sentences.extend([
                "Good for you!",
                "That's good! How are you?",
                "You're doing good!"
            ])

        if 'bye' in words:
            sentences.extend([
                "Goodbye! Take care!",
                "Bye! See you later!",
                "Goodbye! Have a good day!"
            ])

            if 'good' in words:
                sentences.append("Goodbye! Have a good time!")

        return sentences

    def generate_request_sentences(self, words, word_types):
        """Generate request-based sentences"""
        sentences = []

        if 'help' in words:
            sentences.extend([
                "Can you help me please?",
                "I need your help!",
                "Help me with this!",
                "Could you help me out?"
            ])

            if 'you' in words:
                sentences.extend([
                    "Can you help me?",
                    "I need you to help me!",
                    "You can help me!"
                ])

        if 'stop' in words:
            sentences.extend([
                "Please stop!",
                "Stop right there!",
                "I need you to stop!",
                "Stop what you're doing!"
            ])

            if 'you' in words:
                sentences.append("You need to stop!")

        if 'call' in words:
            sentences.extend([
                "Please call me!",
                "I need to make a call!",
                "Can you call someone?",
                "Let's make a phone call!"
            ])

            if 'you' in words:
                sentences.extend([
                    "I will call you!",
                    "You should call me!",
                    "Can you call me?"
                ])

        return sentences

    def generate_emotional_sentences(self, words, word_types):
        """Generate emotion-based sentences"""
        sentences = []

        if 'love' in words:
            sentences.extend([
                "I love this!",
                "Love is wonderful!",
                "I feel so much love!",
                "This is lovely!"
            ])

            if 'you' in words:
                sentences.extend([
                    "I love you!",
                    "You are loved!",
                    "I love being with you!"
                ])

        if 'peace' in words:
            sentences.extend([
                "Peace and love!",
                "I feel peaceful!",
                "Let's have peace!",
                "Peace to everyone!"
            ])

            if 'good' in words:
                sentences.append("Good vibes and peace!")

        if 'good' in words:
            sentences.extend([
                "I feel good!",
                "This is really good!",
                "Everything is good!",
                "Good feelings all around!"
            ])

        return sentences

    def generate_quantity_sentences(self, words, word_types):
        """Generate sentences with numbers and quantities"""
        sentences = []
        numbers = word_types['numbers']

        for number in numbers:
            sentences.extend([
                f"I need {number} things!",
                f"Give me {number} please!",
                f"There are {number} of them!",
                f"I want {number} items!",
                f"Count to {number}!"
            ])

            if 'you' in words:
                sentences.extend([
                    f"You have {number}!",
                    f"Can you give me {number}?",
                    f"You need {number} things!"
                ])

            if 'help' in words:
                sentences.append(f"Help me with {number} things!")

            if 'good' in words:
                sentences.append(f"{number.title()} is a good number!")

        return sentences

    def generate_action_sentences(self, words, word_types):
        """Generate action-based sentences"""
        sentences = []

        if 'call' in words:
            sentences.extend([
                "Let's make a call!",
                "Time to call someone!",
                "I want to call now!",
                "Calling is important!"
            ])

        if 'help' in words:
            sentences.extend([
                "Let's help each other!",
                "Helping is caring!",
                "I want to help!",
                "Help is on the way!"
            ])

        if 'stop' in words:
            sentences.extend([
                "Time to stop!",
                "Let's stop here!",
                "Stop and think!",
                "Stop everything!"
            ])

        return sentences

    def generate_combination_sentences(self, words, word_types):
        """Generate sentences using combinations of words"""
        sentences = []
        words_str = " ".join(words)

        # Smart combinations based on word patterns
        if len(words) >= 2:
            # Create natural combinations
            if 'hello' in words and 'you' in words:
                sentences.extend([
                    "Hello! How are you doing?",
                    "Hello you! Nice to see you!",
                    "Hello there! You look great!"
                ])

            if 'good' in words and 'help' in words:
                sentences.extend([
                    "Good! I need help!",
                    "Help me do something good!",
                    "Good help is appreciated!"
                ])

            if 'love' in words and 'peace' in words:
                sentences.extend([
                    "Love and peace to all!",
                    "I love peace and harmony!",
                    "Peace, love, and happiness!"
                ])

            if any(num in words for num in ['one', 'two', 'three', 'four', 'five']) and 'good' in words:
                numbers = [w for w in words if w in ['one', 'two', 'three', 'four', 'five']]
                if numbers:
                    sentences.append(f"I have {numbers[0]} good things!")

            # Generic combination for any words
            sentences.extend([
                f"I want to talk about {words_str}!",
                f"Let's discuss {words_str}!",
                f"These words are important: {words_str}!",
                f"I'm thinking about {words_str}!"
            ])

        return sentences

    def generate_contextual_variations(self, words, context):
        """Generate contextual variations based on sentiment and urgency"""
        sentences = []

        if context['urgency'] == 'high':
            sentences.extend([
                "This is urgent!",
                "I need immediate attention!",
                "Please respond quickly!",
                "This is important!"
            ])

        if context['sentiment'] == 'positive':
            sentences.extend([
                "I'm feeling positive about this!",
                "This makes me happy!",
                "Everything is wonderful!",
                "I'm in a great mood!"
            ])
        elif context['sentiment'] == 'very_positive':
            sentences.extend([
                "I'm absolutely thrilled!",
                "This is amazing!",
                "I couldn't be happier!",
                "This is the best!"
            ])

        if context['is_emotional'] and context['is_request']:
            sentences.extend([
                "I really need your help with this!",
                "This is emotionally important to me!",
                "Please understand how I feel!"
            ])

        return sentences

    def get_template_sentences(self, words):
        """Get template-based sentences for fallback"""
        relevant_categories = set()
        for word in words:
            if word.lower() in self.word_associations:
                categories = self.word_associations[word.lower()]
                # Only add categories that exist in sentence_templates
                for category in categories:
                    if category in self.sentence_templates:
                        relevant_categories.add(category)

        if not relevant_categories:
            relevant_categories = set(self.sentence_templates.keys())

        suggested_sentences = []
        for category in relevant_categories:
            if category in self.sentence_templates:
                suggested_sentences.extend(self.sentence_templates[category][:3])  # Limit per category

        return suggested_sentences
    
    def create_custom_sentences(self, words):
        """Create custom sentences using the provided words"""
        custom_sentences = []
        words_lower = [word.lower() for word in words]
        
        # Simple sentence patterns
        if 'hello' in words_lower:
            custom_sentences.append("Hello!")
        
        if 'good' in words_lower:
            custom_sentences.append("Good!")
            if 'you' in words_lower:
                custom_sentences.append("Good for you!")
        
        if 'help' in words_lower:
            custom_sentences.append("Help me!")
            if 'you' in words_lower:
                custom_sentences.append("Can you help?")
        
        if 'love' in words_lower:
            custom_sentences.append("Love!")
            if 'you' in words_lower:
                custom_sentences.append("I love you!")
        
        if 'stop' in words_lower:
            custom_sentences.append("Stop!")
            custom_sentences.append("Please stop!")
        
        if 'okay' in words_lower:
            custom_sentences.append("Okay!")
            custom_sentences.append("That's okay!")
        
        if 'call' in words_lower:
            custom_sentences.append("Call me!")
            if 'you' in words_lower:
                custom_sentences.append("I will call you!")
        
        if 'bye' in words_lower:
            custom_sentences.append("Bye!")
            custom_sentences.append("Goodbye!")
        
        # Number-based sentences
        numbers = ['one', 'two', 'three', 'four', 'five']
        found_numbers = [word for word in words_lower if word in numbers]
        if found_numbers:
            custom_sentences.append(f"I need {found_numbers[0]}!")
            custom_sentences.append(f"Give me {found_numbers[0]}!")
        
        # Combine multiple words
        if len(words) > 1:
            custom_sentences.append(" ".join(words).title() + "!")
        
        return custom_sentences
    
    def get_default_sentences(self):
        """Return default sentences when no words are provided"""
        default = []
        for category in ['greetings', 'basic_needs', 'requests']:
            default.extend(self.sentence_templates[category][:3])
        return default[:10]
    
    def get_all_categories(self):
        """Return all available sentence categories"""
        return list(self.sentence_templates.keys())
    
    def get_sentences_by_category(self, category):
        """Get sentences from a specific category"""
        return self.sentence_templates.get(category, [])
