import requests
import json
import os
import logging
from datetime import datetime, timedelta
from pathlib import Path
import hashlib
import time
import re

logger = logging.getLogger(__name__)

class WordsAPI:
    def __init__(self, api_key=None, cache_dir='uploads/wordsapi'):
        self.api_key = api_key
        self.base_url = 'https://wordsapiv1.p.rapidapi.com'
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.session = requests.Session()
        
        if api_key:
            self.session.headers.update({
                'X-RapidAPI-Key': api_key,
                'X-RapidAPI-Host': 'wordsapiv1.p.rapidapi.com'
            })
    
    def get_word_definition(self, word):
        """Get comprehensive definition and information for a word"""
        cache_file = self.cache_dir / f"word_{word.lower()}.json"
        
        # Check cache first
        if cache_file.exists():
            cache_age = datetime.now() - datetime.fromtimestamp(cache_file.stat().st_mtime)
            if cache_age.days < 30:  # Cache for 30 days
                with open(cache_file, 'r') as f:
                    return json.load(f)
        
        if not self.api_key:
            # Return basic definition without API key
            return self._get_basic_definition(word)
        
        try:
            response = self.session.get(f"{self.base_url}/words/{word}")
            response.raise_for_status()
            
            word_data = response.json()
            
            # Cache the response
            with open(cache_file, 'w') as f:
                json.dump(word_data, f)
            
            return word_data
            
        except requests.RequestException as e:
            logger.error(f"WordsAPI error for word '{word}': {e}")
            return self._get_basic_definition(word)
    
    def get_word_of_the_day(self):
        """Get a random word for vocabulary building"""
        cache_file = self.cache_dir / "word_of_day.json"
        
        # Check cache first
        if cache_file.exists():
            cache_age = datetime.now() - datetime.fromtimestamp(cache_file.stat().st_mtime)
            if cache_age.days < 1:  # Cache for 1 day
                with open(cache_file, 'r') as f:
                    return json.load(f)
        
        # Use a predefined list of educational words
        educational_words = [
            'serendipity', 'ephemeral', 'ubiquitous', 'eloquent', 'perseverance',
            'resilient', 'innovative', 'authentic', 'diligent', 'curious',
            'analytical', 'creative', 'logical', 'systematic', 'thorough',
            'precise', 'concise', 'articulate', 'profound', 'insightful'
        ]
        
        import random
        word = random.choice(educational_words)
        word_data = self.get_word_definition(word)
        
        # Cache the word of the day
        with open(cache_file, 'w') as f:
            json.dump(word_data, f)
        
        return word_data
    
    def get_synonyms(self, word):
        """Get synonyms for a word"""
        word_data = self.get_word_definition(word)
        
        if word_data and 'results' in word_data:
            synonyms = []
            for result in word_data['results']:
                if 'synonyms' in result:
                    synonyms.extend(result['synonyms'])
            return list(set(synonyms))  # Remove duplicates
        
        return []
    
    def get_antonyms(self, word):
        """Get antonyms for a word"""
        word_data = self.get_word_definition(word)
        
        if word_data and 'results' in word_data:
            antonyms = []
            for result in word_data['results']:
                if 'antonyms' in result:
                    antonyms.extend(result['antonyms'])
            return list(set(antonyms))  # Remove duplicates
        
        return []
    
    def get_word_family(self, word):
        """Get related words (synonyms, antonyms, etc.)"""
        word_data = self.get_word_definition(word)
        
        if not word_data:
            return {}
        
        word_family = {
            'word': word,
            'synonyms': [],
            'antonyms': [],
            'rhymes': [],
            'similar_words': []
        }
        
        if 'results' in word_data:
            for result in word_data['results']:
                if 'synonyms' in result:
                    word_family['synonyms'].extend(result['synonyms'])
                if 'antonyms' in result:
                    word_family['antonyms'].extend(result['antonyms'])
                if 'rhymes' in result:
                    word_family['rhymes'].extend(result['rhymes'])
                if 'similarTo' in result:
                    word_family['similar_words'].extend(result['similarTo'])
        
        # Remove duplicates
        for key in word_family:
            if isinstance(word_family[key], list):
                word_family[key] = list(set(word_family[key]))
        
        return word_family
    
    def create_vocabulary_lesson(self, word, grade_level):
        """Create a vocabulary lesson for a specific word"""
        word_data = self.get_word_definition(word)
        
        if not word_data:
            return None
        
        lesson_data = {
            'title': f"Vocabulary: {word.title()}",
            'subject': 'vocabulary',
            'grade_level': grade_level,
            'content_type': 'wordsapi',
            'word': word,
            'word_data': word_data,
            'text_content': f"Learn the meaning, synonyms, and usage of the word '{word}'.",
            'estimated_time': 15,
            'xp_value': 10
        }
        
        return lesson_data
    
    def get_grade_level_vocabulary(self, grade_level, limit=10):
        """Get vocabulary words appropriate for a grade level"""
        grade_vocabulary = {
            1: ['happy', 'big', 'small', 'fast', 'slow', 'good', 'bad', 'new', 'old', 'hot'],
            2: ['beautiful', 'careful', 'helpful', 'wonderful', 'peaceful', 'colorful', 'powerful', 'thoughtful', 'cheerful', 'graceful'],
            3: ['adventure', 'brave', 'curious', 'determined', 'energetic', 'friendly', 'generous', 'honest', 'imaginative', 'kind'],
            4: ['accomplish', 'brilliant', 'courageous', 'delightful', 'excellent', 'fascinating', 'grateful', 'harmonious', 'incredible', 'joyful'],
            5: ['analytical', 'creative', 'diligent', 'eloquent', 'innovative', 'logical', 'persistent', 'resilient', 'systematic', 'thorough'],
            6: ['articulate', 'comprehensive', 'dedicated', 'enthusiastic', 'fortunate', 'genuine', 'influential', 'magnificent', 'optimistic', 'remarkable'],
            7: ['authentic', 'confident', 'determined', 'enthusiastic', 'fortunate', 'genuine', 'influential', 'magnificent', 'optimistic', 'remarkable'],
            8: ['accomplished', 'brilliant', 'charismatic', 'determined', 'eloquent', 'fascinating', 'generous', 'inspiring', 'knowledgeable', 'passionate'],
            9: ['analytical', 'articulate', 'comprehensive', 'dedicated', 'eloquent', 'innovative', 'logical', 'persistent', 'resilient', 'systematic'],
            10: ['authentic', 'charismatic', 'determined', 'eloquent', 'fascinating', 'generous', 'inspiring', 'knowledgeable', 'passionate', 'remarkable'],
            11: ['accomplished', 'analytical', 'articulate', 'comprehensive', 'dedicated', 'eloquent', 'innovative', 'logical', 'persistent', 'resilient'],
            12: ['authentic', 'charismatic', 'determined', 'eloquent', 'fascinating', 'generous', 'inspiring', 'knowledgeable', 'passionate', 'remarkable']
        }
        
        words = grade_vocabulary.get(grade_level, grade_vocabulary[5])  # Default to grade 5
        return words[:limit]
    
    def create_spelling_lesson(self, words, grade_level):
        """Create a spelling lesson with multiple words"""
        lesson_data = {
            'title': f"Spelling Practice - Grade {grade_level}",
            'subject': 'spelling',
            'grade_level': grade_level,
            'content_type': 'wordsapi',
            'words': words,
            'word_definitions': {},
            'text_content': f"Practice spelling {len(words)} words appropriate for grade {grade_level}.",
            'estimated_time': 20,
            'xp_value': 15
        }
        
        # Get definitions for each word
        for word in words:
            definition = self.get_word_definition(word)
            lesson_data['word_definitions'][word] = definition
        
        return lesson_data
    
    def get_word_pronunciation(self, word):
        """Get pronunciation information for a word"""
        word_data = self.get_word_definition(word)
        
        if word_data and 'pronunciation' in word_data:
            return word_data['pronunciation']
        
        return None
    
    def create_word_game(self, word, game_type='synonym_match'):
        """Create a vocabulary game"""
        word_data = self.get_word_definition(word)
        
        if not word_data:
            return None
        
        game_data = {
            'word': word,
            'game_type': game_type,
            'word_data': word_data,
            'questions': []
        }
        
        if game_type == 'synonym_match':
            synonyms = self.get_synonyms(word)
            if synonyms:
                game_data['questions'] = [
                    {
                        'type': 'multiple_choice',
                        'question': f"What is a synonym for '{word}'?",
                        'correct_answer': synonyms[0] if synonyms else '',
                        'options': synonyms[:4] if len(synonyms) >= 4 else synonyms + ['None of the above']
                    }
                ]
        
        elif game_type == 'definition_match':
            if 'results' in word_data and word_data['results']:
                definition = word_data['results'][0].get('definition', '')
                game_data['questions'] = [
                    {
                        'type': 'true_false',
                        'question': f"True or False: '{word}' means '{definition}'",
                        'correct_answer': 'True'
                    }
                ]
        
        return game_data
    
    def get_etymology(self, word):
        """Get etymology (word origin) information"""
        word_data = self.get_word_definition(word)
        
        if word_data and 'results' in word_data:
            for result in word_data['results']:
                if 'etymology' in result:
                    return result['etymology']
        
        return None
    
    def create_etymology_lesson(self, word, grade_level):
        """Create a lesson about word origins"""
        etymology = self.get_etymology(word)
        
        if not etymology:
            return None
        
        lesson_data = {
            'title': f"Word Origins: {word.title()}",
            'subject': 'vocabulary',
            'grade_level': grade_level,
            'content_type': 'wordsapi_etymology',
            'word': word,
            'etymology': etymology,
            'text_content': f"Learn about the origin and history of the word '{word}'.",
            'estimated_time': 10,
            'xp_value': 8
        }
        
        return lesson_data
    
    def _get_basic_definition(self, word):
        """Get a basic definition when API is not available"""
        # Simple dictionary for common words
        basic_definitions = {
            'happy': {'word': 'happy', 'results': [{'definition': 'feeling or showing pleasure or contentment'}]},
            'big': {'word': 'big', 'results': [{'definition': 'of considerable size or extent'}]},
            'small': {'word': 'small', 'results': [{'definition': 'of a size that is less than normal or usual'}]},
            'fast': {'word': 'fast', 'results': [{'definition': 'moving or capable of moving at high speed'}]},
            'slow': {'word': 'slow', 'results': [{'definition': 'moving or operating at a low speed'}]},
            'good': {'word': 'good', 'results': [{'definition': 'to be desired or approved of'}]},
            'bad': {'word': 'bad', 'results': [{'definition': 'of poor quality or a low standard'}]},
            'new': {'word': 'new', 'results': [{'definition': 'not existing before; made, introduced, or discovered recently'}]},
            'old': {'word': 'old', 'results': [{'definition': 'having lived for a long time; no longer young'}]},
            'hot': {'word': 'hot', 'results': [{'definition': 'having a high degree of heat or a high temperature'}]}
        }
        
        return basic_definitions.get(word.lower(), {
            'word': word,
            'results': [{'definition': f'A word meaning related to {word}'}]
        })
    
    def get_cache_stats(self):
        """Get cache statistics"""
        cache_files = list(self.cache_dir.glob('*'))
        total_size = sum(f.stat().st_size for f in cache_files if f.is_file())
        
        return {
            'total_files': len(cache_files),
            'total_size_mb': total_size / (1024 * 1024),
            'cache_dir': str(self.cache_dir)
        }
    
    def clear_cache(self):
        """Clear all cached content"""
        for file in self.cache_dir.glob('*'):
            if file.is_file():
                file.unlink()
        logger.info("WordsAPI cache cleared")

# Usage example
if __name__ == "__main__":
    words_api = WordsAPI()
    
    # Get word definition
    definition = words_api.get_word_definition("serendipity")
    print(f"Definition: {definition}")
    
    # Get word of the day
    word_of_day = words_api.get_word_of_the_day()
    print(f"Word of the day: {word_of_day['word']}")
    
    # Get synonyms
    synonyms = words_api.get_synonyms("happy")
    print(f"Synonyms for 'happy': {synonyms}")
    
    # Create vocabulary lesson
    lesson = words_api.create_vocabulary_lesson("eloquent", 6)
    if lesson:
        print(f"Created lesson: {lesson['title']}")
    
    # Get grade-level vocabulary
    vocab_words = words_api.get_grade_level_vocabulary(4, limit=5)
    print(f"Grade 4 vocabulary: {vocab_words}")
    
    # Create spelling lesson
    spelling_lesson = words_api.create_spelling_lesson(vocab_words, 4)
    print(f"Created spelling lesson with {len(spelling_lesson['words'])} words")
    
    # Get cache stats
    stats = words_api.get_cache_stats()
    print(f"Cache stats: {stats}")