import requests
import json
import os
import logging
from datetime import datetime, timedelta
import sqlite3
from pathlib import Path
import hashlib
import time

logger = logging.getLogger(__name__)

class KhanAcademyAPI:
    def __init__(self, cache_dir='uploads/khan_academy'):
        self.base_url = 'https://www.khanacademy.org/api/v1'
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'SavageHomeschoolOS/1.0'
        })
        
    def search_videos(self, topic, grade_level=None, limit=10):
        """Search for Khan Academy videos by topic and grade level"""
        try:
            params = {
                'query': topic,
                'limit': limit
            }
            
            if grade_level:
                params['grade_level'] = grade_level
            
            response = self.session.get(f"{self.base_url}/videos", params=params)
            response.raise_for_status()
            
            videos = response.json()
            return self._process_videos(videos)
            
        except requests.RequestException as e:
            logger.error(f"Khan Academy API error: {e}")
            return self._get_cached_videos(topic, grade_level)
    
    def get_video_content(self, video_id):
        """Get detailed video content and metadata"""
        cache_file = self.cache_dir / f"video_{video_id}.json"
        
        # Check cache first
        if cache_file.exists():
            cache_age = datetime.now() - datetime.fromtimestamp(cache_file.stat().st_mtime)
            if cache_age.days < 7:  # Cache for 7 days
                with open(cache_file, 'r') as f:
                    return json.load(f)
        
        try:
            response = self.session.get(f"{self.base_url}/videos/{video_id}")
            response.raise_for_status()
            
            video_data = response.json()
            
            # Cache the response
            with open(cache_file, 'w') as f:
                json.dump(video_data, f)
            
            return video_data
            
        except requests.RequestException as e:
            logger.error(f"Error fetching video {video_id}: {e}")
            return None
    
    def get_exercises(self, subject, grade_level=None):
        """Get interactive exercises for a subject"""
        try:
            params = {'subject': subject}
            if grade_level:
                params['grade_level'] = grade_level
            
            response = self.session.get(f"{self.base_url}/exercises", params=params)
            response.raise_for_status()
            
            exercises = response.json()
            return self._process_exercises(exercises)
            
        except requests.RequestException as e:
            logger.error(f"Error fetching exercises: {e}")
            return []
    
    def download_video(self, video_id, quality='medium'):
        """Download video for offline use"""
        video_data = self.get_video_content(video_id)
        if not video_data:
            return None
        
        video_url = video_data.get('download_urls', {}).get(quality)
        if not video_url:
            return None
        
        video_filename = f"khan_video_{video_id}.mp4"
        video_path = self.cache_dir / video_filename
        
        try:
            response = self.session.get(video_url, stream=True)
            response.raise_for_status()
            
            with open(video_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            return str(video_path)
            
        except requests.RequestException as e:
            logger.error(f"Error downloading video {video_id}: {e}")
            return None
    
    def get_subject_content(self, subject, grade_level=None):
        """Get comprehensive content for a subject"""
        content = {
            'videos': [],
            'exercises': [],
            'topics': []
        }
        
        # Get videos
        videos = self.search_videos(subject, grade_level, limit=20)
        content['videos'] = videos
        
        # Get exercises
        exercises = self.get_exercises(subject, grade_level)
        content['exercises'] = exercises
        
        # Get topics
        topics = self._get_subject_topics(subject)
        content['topics'] = topics
        
        return content
    
    def create_lesson_from_khan(self, subject, grade_level, topic):
        """Create a lesson using Khan Academy content"""
        content = self.get_subject_content(subject, grade_level)
        
        lesson_data = {
            'title': f"Khan Academy - {subject} - {topic}",
            'subject': subject,
            'grade_level': grade_level,
            'content_type': 'khan_academy',
            'videos': content['videos'][:3],  # Use first 3 videos
            'exercises': content['exercises'][:5],  # Use first 5 exercises
            'estimated_time': 30,  # 30 minutes
            'xp_value': 15
        }
        
        return lesson_data
    
    def _process_videos(self, videos):
        """Process and filter video results"""
        processed_videos = []
        
        for video in videos:
            processed_video = {
                'id': video.get('id'),
                'title': video.get('title'),
                'description': video.get('description'),
                'duration': video.get('duration'),
                'thumbnail': video.get('thumbnail_url'),
                'url': video.get('url'),
                'subject': video.get('subject'),
                'grade_level': video.get('grade_level')
            }
            processed_videos.append(processed_video)
        
        return processed_videos
    
    def _process_exercises(self, exercises):
        """Process and filter exercise results"""
        processed_exercises = []
        
        for exercise in exercises:
            processed_exercise = {
                'id': exercise.get('id'),
                'title': exercise.get('title'),
                'description': exercise.get('description'),
                'type': exercise.get('type'),
                'difficulty': exercise.get('difficulty'),
                'subject': exercise.get('subject')
            }
            processed_exercises.append(processed_exercise)
        
        return processed_exercises
    
    def _get_subject_topics(self, subject):
        """Get topics for a subject"""
        try:
            response = self.session.get(f"{self.base_url}/subjects/{subject}/topics")
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Error fetching topics for {subject}: {e}")
            return []
    
    def _get_cached_videos(self, topic, grade_level):
        """Get cached videos when API is unavailable"""
        cache_file = self.cache_dir / f"search_{hashlib.md5(f'{topic}_{grade_level}'.encode()).hexdigest()}.json"
        
        if cache_file.exists():
            with open(cache_file, 'r') as f:
                return json.load(f)
        
        return []
    
    def clear_cache(self):
        """Clear all cached content"""
        for file in self.cache_dir.glob('*'):
            if file.is_file():
                file.unlink()
        logger.info("Khan Academy cache cleared")
    
    def get_cache_stats(self):
        """Get cache statistics"""
        cache_files = list(self.cache_dir.glob('*'))
        total_size = sum(f.stat().st_size for f in cache_files if f.is_file())
        
        return {
            'total_files': len(cache_files),
            'total_size_mb': total_size / (1024 * 1024),
            'cache_dir': str(self.cache_dir)
        }

# Usage example
if __name__ == "__main__":
    khan_api = KhanAcademyAPI()
    
    # Search for math videos
    videos = khan_api.search_videos("fractions", grade_level=3)
    print(f"Found {len(videos)} videos")
    
    # Get lesson content
    lesson = khan_api.create_lesson_from_khan("math", 3, "fractions")
    print(f"Created lesson: {lesson['title']}")
    
    # Get cache stats
    stats = khan_api.get_cache_stats()
    print(f"Cache stats: {stats}") 