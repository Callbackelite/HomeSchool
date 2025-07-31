import requests
import json
import os
import logging
from datetime import datetime, timedelta
from pathlib import Path
import hashlib
import time
from PIL import Image
import io

logger = logging.getLogger(__name__)

class NASAAPI:
    def __init__(self, api_key=None, cache_dir='uploads/nasa'):
        self.api_key = api_key or 'DEMO_KEY'  # Use demo key if none provided
        self.base_url = 'https://api.nasa.gov'
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.session = requests.Session()
        
    def get_apod(self, date=None):
        """Get NASA's Astronomy Picture of the Day"""
        endpoint = f"{self.base_url}/planetary/apod"
        params = {'api_key': self.api_key}
        
        if date:
            params['date'] = date
        
        cache_file = self.cache_dir / f"apod_{date or 'today'}.json"
        
        # Check cache first
        if cache_file.exists():
            cache_age = datetime.now() - datetime.fromtimestamp(cache_file.stat().st_mtime)
            if cache_age.days < 1:  # Cache for 1 day
                with open(cache_file, 'r') as f:
                    return json.load(f)
        
        try:
            response = self.session.get(endpoint, params=params)
            response.raise_for_status()
            
            apod_data = response.json()
            
            # Cache the response
            with open(cache_file, 'w') as f:
                json.dump(apod_data, f)
            
            return apod_data
            
        except requests.RequestException as e:
            logger.error(f"NASA APOD API error: {e}")
            return None
    
    def get_mars_photos(self, sol=None, camera='all', limit=10):
        """Get Mars rover photos"""
        endpoint = f"{self.base_url}/mars-photos/api/v1/rovers/curiosity/photos"
        params = {
            'api_key': self.api_key,
            'camera': camera
        }
        
        if sol:
            params['sol'] = sol
        else:
            # Use latest available sol
            params['sol'] = 1000
        
        cache_file = self.cache_dir / f"mars_photos_{sol or 'latest'}_{camera}.json"
        
        # Check cache first
        if cache_file.exists():
            cache_age = datetime.now() - datetime.fromtimestamp(cache_file.stat().st_mtime)
            if cache_age.days < 7:  # Cache for 7 days
                with open(cache_file, 'r') as f:
                    data = json.load(f)
                    return data['photos'][:limit]
        
        try:
            response = self.session.get(endpoint, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            # Cache the response
            with open(cache_file, 'w') as f:
                json.dump(data, f)
            
            return data['photos'][:limit]
            
        except requests.RequestException as e:
            logger.error(f"NASA Mars API error: {e}")
            return []
    
    def get_earth_imagery(self, lat, lon, date=None, dim=0.15):
        """Get Earth imagery from NASA's EPIC API"""
        endpoint = f"{self.base_url}/EPIC/api/natural"
        params = {'api_key': self.api_key}
        
        if date:
            params['date'] = date
        
        cache_file = self.cache_dir / f"earth_{lat}_{lon}_{date or 'latest'}.json"
        
        # Check cache first
        if cache_file.exists():
            cache_age = datetime.now() - datetime.fromtimestamp(cache_file.stat().st_mtime)
            if cache_age.days < 1:  # Cache for 1 day
                with open(cache_file, 'r') as f:
                    return json.load(f)
        
        try:
            response = self.session.get(endpoint, params=params)
            response.raise_for_status()
            
            earth_data = response.json()
            
            # Cache the response
            with open(cache_file, 'w') as f:
                json.dump(earth_data, f)
            
            return earth_data
            
        except requests.RequestException as e:
            logger.error(f"NASA Earth API error: {e}")
            return None
    
    def search_nasa_images(self, query, limit=20):
        """Search NASA's image library"""
        endpoint = f"{self.base_url}/search"
        params = {
            'q': query,
            'media_type': 'image',
            'api_key': self.api_key
        }
        
        cache_file = self.cache_dir / f"search_{hashlib.md5(query.encode()).hexdigest()}.json"
        
        # Check cache first
        if cache_file.exists():
            cache_age = datetime.now() - datetime.fromtimestamp(cache_file.stat().st_mtime)
            if cache_age.days < 7:  # Cache for 7 days
                with open(cache_file, 'r') as f:
                    data = json.load(f)
                    return data['collection']['items'][:limit]
        
        try:
            response = self.session.get(endpoint, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            # Cache the response
            with open(cache_file, 'w') as f:
                json.dump(data, f)
            
            return data['collection']['items'][:limit]
            
        except requests.RequestException as e:
            logger.error(f"NASA Search API error: {e}")
            return []
    
    def get_space_weather(self):
        """Get space weather data"""
        endpoint = f"{self.base_url}/DONKI/WSJ"
        params = {'api_key': self.api_key}
        
        cache_file = self.cache_dir / "space_weather.json"
        
        # Check cache first
        if cache_file.exists():
            cache_age = datetime.now() - datetime.fromtimestamp(cache_file.stat().st_mtime)
            if cache_age.hours < 6:  # Cache for 6 hours
                with open(cache_file, 'r') as f:
                    return json.load(f)
        
        try:
            response = self.session.get(endpoint, params=params)
            response.raise_for_status()
            
            weather_data = response.json()
            
            # Cache the response
            with open(cache_file, 'w') as f:
                json.dump(weather_data, f)
            
            return weather_data
            
        except requests.RequestException as e:
            logger.error(f"NASA Space Weather API error: {e}")
            return None
    
    def download_image(self, image_url, filename=None):
        """Download and cache an image"""
        if not filename:
            filename = hashlib.md5(image_url.encode()).hexdigest() + '.jpg'
        
        image_path = self.cache_dir / filename
        
        # Check if already cached
        if image_path.exists():
            return str(image_path)
        
        try:
            response = self.session.get(image_url, stream=True)
            response.raise_for_status()
            
            with open(image_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            return str(image_path)
            
        except requests.RequestException as e:
            logger.error(f"Error downloading image {image_url}: {e}")
            return None
    
    def create_science_lesson(self, topic, grade_level):
        """Create a science lesson using NASA content"""
        lesson_data = {
            'title': f"NASA Science - {topic}",
            'subject': 'science',
            'grade_level': grade_level,
            'content_type': 'nasa',
            'images': [],
            'videos': [],
            'text_content': f"Learn about {topic} through NASA's amazing discoveries and images.",
            'estimated_time': 25,
            'xp_value': 20
        }
        
        # Get relevant images
        images = self.search_nasa_images(topic, limit=5)
        for image in images:
            if 'links' in image and len(image['links']) > 0:
                image_url = image['links'][0]['href']
                local_path = self.download_image(image_url)
                if local_path:
                    lesson_data['images'].append({
                        'url': image_url,
                        'local_path': local_path,
                        'title': image.get('data', [{}])[0].get('title', 'NASA Image'),
                        'description': image.get('data', [{}])[0].get('description', '')
                    })
        
        # Add APOD if relevant
        apod = self.get_apod()
        if apod and topic.lower() in apod.get('title', '').lower():
            lesson_data['images'].append({
                'url': apod['url'],
                'local_path': self.download_image(apod['url']),
                'title': apod['title'],
                'description': apod['explanation']
            })
        
        return lesson_data
    
    def get_space_mission_data(self, mission_name):
        """Get data about specific space missions"""
        endpoint = f"{self.base_url}/techport/api/projects"
        params = {'api_key': self.api_key}
        
        cache_file = self.cache_dir / f"mission_{mission_name.lower().replace(' ', '_')}.json"
        
        # Check cache first
        if cache_file.exists():
            cache_age = datetime.now() - datetime.fromtimestamp(cache_file.stat().st_mtime)
            if cache_age.days < 30:  # Cache for 30 days
                with open(cache_file, 'r') as f:
                    return json.load(f)
        
        try:
            response = self.session.get(endpoint, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            # Filter for specific mission
            mission_data = None
            for project in data.get('projects', []):
                if mission_name.lower() in project.get('title', '').lower():
                    mission_data = project
                    break
            
            if mission_data:
                # Cache the response
                with open(cache_file, 'w') as f:
                    json.dump(mission_data, f)
            
            return mission_data
            
        except requests.RequestException as e:
            logger.error(f"NASA TechPort API error: {e}")
            return None
    
    def create_astronomy_lesson(self, celestial_object):
        """Create an astronomy lesson about a specific celestial object"""
        lesson_data = {
            'title': f"Exploring {celestial_object}",
            'subject': 'science',
            'grade_level': 5,  # Default to 5th grade
            'content_type': 'nasa_astronomy',
            'celestial_object': celestial_object,
            'images': [],
            'text_content': f"Discover amazing facts about {celestial_object} through NASA's observations.",
            'estimated_time': 30,
            'xp_value': 25
        }
        
        # Search for images of the celestial object
        images = self.search_nasa_images(celestial_object, limit=10)
        for image in images:
            if 'links' in image and len(image['links']) > 0:
                image_url = image['links'][0]['href']
                local_path = self.download_image(image_url)
                if local_path:
                    lesson_data['images'].append({
                        'url': image_url,
                        'local_path': local_path,
                        'title': image.get('data', [{}])[0].get('title', f'{celestial_object} Image'),
                        'description': image.get('data', [{}])[0].get('description', '')
                    })
        
        return lesson_data
    
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
        logger.info("NASA API cache cleared")

# Usage example
if __name__ == "__main__":
    nasa_api = NASAAPI()
    
    # Get today's APOD
    apod = nasa_api.get_apod()
    if apod:
        print(f"Today's APOD: {apod['title']}")
    
    # Create a science lesson about Mars
    mars_lesson = nasa_api.create_science_lesson("Mars", 4)
    print(f"Created lesson: {mars_lesson['title']}")
    
    # Get Mars photos
    mars_photos = nasa_api.get_mars_photos(limit=5)
    print(f"Found {len(mars_photos)} Mars photos")
    
    # Create astronomy lesson
    astronomy_lesson = nasa_api.create_astronomy_lesson("Jupiter")
    print(f"Created astronomy lesson: {astronomy_lesson['title']}")
    
    # Get cache stats
    stats = nasa_api.get_cache_stats()
    print(f"Cache stats: {stats}")