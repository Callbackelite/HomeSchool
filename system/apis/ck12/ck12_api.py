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

class CK12API:
    def __init__(self, cache_dir='uploads/ck12'):
        self.base_url = 'https://www.ck12.org/api/v1'
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'SavageHomeschoolOS/1.0'
        })
        
    def search_content(self, query, subject=None, grade_level=None, limit=20):
        """Search for CK-12 content by topic and filters"""
        endpoint = f"{self.base_url}/content"
        params = {
            'q': query,
            'limit': limit
        }
        
        if subject:
            params['subject'] = subject
        if grade_level:
            params['grade_level'] = grade_level
        
        cache_file = self.cache_dir / f"search_{hashlib.md5(f'{query}_{subject}_{grade_level}'.encode()).hexdigest()}.json"
        
        # Check cache first
        if cache_file.exists():
            cache_age = datetime.now() - datetime.fromtimestamp(cache_file.stat().st_mtime)
            if cache_age.days < 7:  # Cache for 7 days
                with open(cache_file, 'r') as f:
                    data = json.load(f)
                    return self._process_content(data.get('content', []))
        
        try:
            response = self.session.get(endpoint, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            # Cache the response
            with open(cache_file, 'w') as f:
                json.dump(data, f)
            
            return self._process_content(data.get('content', []))
            
        except requests.RequestException as e:
            logger.error(f"CK-12 search error: {e}")
            return []
    
    def get_content_details(self, content_id):
        """Get detailed information about specific content"""
        endpoint = f"{self.base_url}/content/{content_id}"
        
        cache_file = self.cache_dir / f"content_{content_id}.json"
        
        # Check cache first
        if cache_file.exists():
            cache_age = datetime.now() - datetime.fromtimestamp(cache_file.stat().st_mtime)
            if cache_age.days < 30:  # Cache for 30 days
                with open(cache_file, 'r') as f:
                    return json.load(f)
        
        try:
            response = self.session.get(endpoint)
            response.raise_for_status()
            
            content_data = response.json()
            
            # Cache the response
            with open(cache_file, 'w') as f:
                json.dump(content_data, f)
            
            return content_data
            
        except requests.RequestException as e:
            logger.error(f"CK-12 content details error: {e}")
            return None
    
    def get_subjects(self):
        """Get available subjects from CK-12"""
        endpoint = f"{self.base_url}/subjects"
        
        cache_file = self.cache_dir / "subjects.json"
        
        # Check cache first
        if cache_file.exists():
            cache_age = datetime.now() - datetime.fromtimestamp(cache_file.stat().st_mtime)
            if cache_age.days < 30:  # Cache for 30 days
                with open(cache_file, 'r') as f:
                    return json.load(f)
        
        try:
            response = self.session.get(endpoint)
            response.raise_for_status()
            
            subjects_data = response.json()
            
            # Cache the response
            with open(cache_file, 'w') as f:
                json.dump(subjects_data, f)
            
            return subjects_data
            
        except requests.RequestException as e:
            logger.error(f"CK-12 subjects error: {e}")
            return []
    
    def get_concepts(self, subject=None, grade_level=None):
        """Get concepts for a subject and grade level"""
        endpoint = f"{self.base_url}/concepts"
        params = {}
        
        if subject:
            params['subject'] = subject
        if grade_level:
            params['grade_level'] = grade_level
        
        cache_file = self.cache_dir / f"concepts_{subject}_{grade_level}.json"
        
        # Check cache first
        if cache_file.exists():
            cache_age = datetime.now() - datetime.fromtimestamp(cache_file.stat().st_mtime)
            if cache_age.days < 7:  # Cache for 7 days
                with open(cache_file, 'r') as f:
                    return json.load(f)
        
        try:
            response = self.session.get(endpoint, params=params)
            response.raise_for_status()
            
            concepts_data = response.json()
            
            # Cache the response
            with open(cache_file, 'w') as f:
                json.dump(concepts_data, f)
            
            return concepts_data
            
        except requests.RequestException as e:
            logger.error(f"CK-12 concepts error: {e}")
            return []
    
    def get_simulations(self, subject, grade_level=None, limit=10):
        """Get interactive simulations for a subject"""
        simulations = self.search_content("simulation", subject, grade_level, limit)
        
        # Filter for actual simulations
        filtered_simulations = []
        for sim in simulations:
            if 'simulation' in sim.get('type', '').lower() or 'interactive' in sim.get('title', '').lower():
                filtered_simulations.append(sim)
        
        return filtered_simulations[:limit]
    
    def get_practice_problems(self, subject, grade_level=None, limit=10):
        """Get practice problems for a subject"""
        problems = self.search_content("practice problem", subject, grade_level, limit)
        
        # Filter for practice problems
        filtered_problems = []
        for problem in problems:
            if 'problem' in problem.get('type', '').lower() or 'practice' in problem.get('title', '').lower():
                filtered_problems.append(problem)
        
        return filtered_problems[:limit]
    
    def create_stem_lesson(self, subject, topic, grade_level):
        """Create a STEM lesson using CK-12 content"""
        lesson_data = {
            'title': f"CK-12 {subject.title()} - {topic}",
            'subject': subject,
            'grade_level': grade_level,
            'content_type': 'ck12',
            'simulations': [],
            'practice_problems': [],
            'text_content': f"Learn about {topic} through CK-12's interactive content.",
            'estimated_time': 30,
            'xp_value': 20
        }
        
        # Get simulations
        simulations = self.get_simulations(subject, grade_level, limit=3)
        lesson_data['simulations'] = simulations
        
        # Get practice problems
        problems = self.get_practice_problems(subject, grade_level, limit=5)
        lesson_data['practice_problems'] = problems
        
        # Get concept explanations
        concepts = self.get_concepts(subject, grade_level)
        if concepts:
            lesson_data['concepts'] = concepts[:3]  # Use first 3 concepts
        
        return lesson_data
    
    def get_math_content(self, topic, grade_level):
        """Get math-specific content from CK-12"""
        math_content = self.search_content(topic, "math", grade_level, limit=15)
        
        lesson_data = {
            'title': f"CK-12 Math - {topic}",
            'subject': 'math',
            'grade_level': grade_level,
            'content_type': 'ck12_math',
            'interactive_content': [],
            'practice_problems': [],
            'text_content': f"Learn {topic} through CK-12's interactive math content.",
            'estimated_time': 25,
            'xp_value': 18
        }
        
        # Separate interactive content from practice problems
        for content in math_content:
            if 'interactive' in content.get('type', '').lower():
                lesson_data['interactive_content'].append(content)
            elif 'problem' in content.get('type', '').lower():
                lesson_data['practice_problems'].append(content)
        
        return lesson_data
    
    def get_science_content(self, topic, grade_level):
        """Get science-specific content from CK-12"""
        science_content = self.search_content(topic, "science", grade_level, limit=15)
        
        lesson_data = {
            'title': f"CK-12 Science - {topic}",
            'subject': 'science',
            'grade_level': grade_level,
            'content_type': 'ck12_science',
            'simulations': [],
            'experiments': [],
            'explanations': [],
            'text_content': f"Explore {topic} through CK-12's science simulations and experiments.",
            'estimated_time': 35,
            'xp_value': 25
        }
        
        # Categorize content
        for content in science_content:
            content_type = content.get('type', '').lower()
            if 'simulation' in content_type:
                lesson_data['simulations'].append(content)
            elif 'experiment' in content_type:
                lesson_data['experiments'].append(content)
            else:
                lesson_data['explanations'].append(content)
        
        return lesson_data
    
    def convert_to_quiz(self, practice_problem):
        """Convert a CK-12 practice problem to the system's quiz format"""
        if not practice_problem:
            return None
        
        quiz_data = {
            'question': practice_problem.get('question', ''),
            'options': practice_problem.get('options', []),
            'correct_answer': practice_problem.get('correct_answer', ''),
            'explanation': practice_problem.get('explanation', ''),
            'difficulty': practice_problem.get('difficulty', 'medium'),
            'points': 1
        }
        
        return quiz_data
    
    def get_embed_code(self, content_id):
        """Get embed code for CK-12 content"""
        content_details = self.get_content_details(content_id)
        
        if not content_details:
            return None
        
        embed_url = content_details.get('embed_url')
        if embed_url:
            return f'<iframe src="{embed_url}" width="100%" height="600" frameborder="0"></iframe>'
        
        return None
    
    def download_content(self, content_id):
        """Download CK-12 content for offline use"""
        content_details = self.get_content_details(content_id)
        
        if not content_details:
            return None
        
        # Create offline version
        offline_content = {
            'id': content_id,
            'title': content_details.get('title', ''),
            'content': content_details.get('content', ''),
            'type': content_details.get('type', ''),
            'subject': content_details.get('subject', ''),
            'grade_level': content_details.get('grade_level', ''),
            'downloaded_at': datetime.now().isoformat()
        }
        
        # Save to cache
        cache_file = self.cache_dir / f"offline_{content_id}.json"
        with open(cache_file, 'w') as f:
            json.dump(offline_content, f)
        
        return str(cache_file)
    
    def _process_content(self, content_list):
        """Process and filter content results"""
        processed_content = []
        
        for content in content_list:
            processed_item = {
                'id': content.get('id'),
                'title': content.get('title'),
                'description': content.get('description'),
                'type': content.get('type'),
                'subject': content.get('subject'),
                'grade_level': content.get('grade_level'),
                'url': content.get('url'),
                'embed_url': content.get('embed_url'),
                'difficulty': content.get('difficulty', 'medium')
            }
            processed_content.append(processed_item)
        
        return processed_content
    
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
        logger.info("CK-12 cache cleared")

# Usage example
if __name__ == "__main__":
    ck12_api = CK12API()
    
    # Search for math content
    math_content = ck12_api.search_content("fractions", "math", 4)
    print(f"Found {len(math_content)} math content items")
    
    # Get science simulations
    science_sims = ck12_api.get_simulations("science", 5)
    print(f"Found {len(science_sims)} science simulations")
    
    # Create STEM lesson
    stem_lesson = ck12_api.create_stem_lesson("science", "forces", 4)
    print(f"Created lesson: {stem_lesson['title']}")
    
    # Get math content
    math_lesson = ck12_api.get_math_content("algebra", 6)
    print(f"Created math lesson: {math_lesson['title']}")
    
    # Get subjects
    subjects = ck12_api.get_subjects()
    print(f"Available subjects: {len(subjects)}")
    
    # Get cache stats
    stats = ck12_api.get_cache_stats()
    print(f"Cache stats: {stats}") 