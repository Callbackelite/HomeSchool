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

class OpenLibraryAPI:
    def __init__(self, cache_dir='uploads/openlibrary'):
        self.base_url = 'https://openlibrary.org'
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'SavageHomeschoolOS/1.0'
        })
        
    def search_books(self, query, limit=20, grade_level=None):
        """Search for books by title, author, or subject"""
        endpoint = f"{self.base_url}/search.json"
        params = {
            'q': query,
            'limit': limit
        }
        
        cache_file = self.cache_dir / f"search_{hashlib.md5(query.encode()).hexdigest()}.json"
        
        # Check cache first
        if cache_file.exists():
            cache_age = datetime.now() - datetime.fromtimestamp(cache_file.stat().st_mtime)
            if cache_age.days < 7:  # Cache for 7 days
                with open(cache_file, 'r') as f:
                    data = json.load(f)
                    return self._filter_by_grade_level(data.get('docs', []), grade_level)
        
        try:
            response = self.session.get(endpoint, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            # Cache the response
            with open(cache_file, 'w') as f:
                json.dump(data, f)
            
            return self._filter_by_grade_level(data.get('docs', []), grade_level)
            
        except requests.RequestException as e:
            logger.error(f"OpenLibrary search error: {e}")
            return []
    
    def get_book_details(self, book_id):
        """Get detailed information about a specific book"""
        endpoint = f"{self.base_url}/works/{book_id}.json"
        
        cache_file = self.cache_dir / f"book_{book_id}.json"
        
        # Check cache first
        if cache_file.exists():
            cache_age = datetime.now() - datetime.fromtimestamp(cache_file.stat().st_mtime)
            if cache_age.days < 30:  # Cache for 30 days
                with open(cache_file, 'r') as f:
                    return json.load(f)
        
        try:
            response = self.session.get(endpoint)
            response.raise_for_status()
            
            book_data = response.json()
            
            # Cache the response
            with open(cache_file, 'w') as f:
                json.dump(book_data, f)
            
            return book_data
            
        except requests.RequestException as e:
            logger.error(f"OpenLibrary book details error: {e}")
            return None
    
    def get_author_details(self, author_id):
        """Get information about an author"""
        endpoint = f"{self.base_url}/authors/{author_id}.json"
        
        cache_file = self.cache_dir / f"author_{author_id}.json"
        
        # Check cache first
        if cache_file.exists():
            cache_age = datetime.now() - datetime.fromtimestamp(cache_file.stat().st_mtime)
            if cache_age.days < 30:  # Cache for 30 days
                with open(cache_file, 'r') as f:
                    return json.load(f)
        
        try:
            response = self.session.get(endpoint)
            response.raise_for_status()
            
            author_data = response.json()
            
            # Cache the response
            with open(cache_file, 'w') as f:
                json.dump(author_data, f)
            
            return author_data
            
        except requests.RequestException as e:
            logger.error(f"OpenLibrary author details error: {e}")
            return None
    
    def get_subject_books(self, subject, grade_level=None, limit=20):
        """Get books by subject (e.g., 'science', 'history', 'math')"""
        endpoint = f"{self.base_url}/subjects/{subject}.json"
        
        cache_file = self.cache_dir / f"subject_{subject}.json"
        
        # Check cache first
        if cache_file.exists():
            cache_age = datetime.now() - datetime.fromtimestamp(cache_file.stat().st_mtime)
            if cache_age.days < 7:  # Cache for 7 days
                with open(cache_file, 'r') as f:
                    data = json.load(f)
                    return self._filter_by_grade_level(data.get('works', []), grade_level)[:limit]
        
        try:
            response = self.session.get(endpoint)
            response.raise_for_status()
            
            data = response.json()
            
            # Cache the response
            with open(cache_file, 'w') as f:
                json.dump(data, f)
            
            return self._filter_by_grade_level(data.get('works', []), grade_level)[:limit]
            
        except requests.RequestException as e:
            logger.error(f"OpenLibrary subject search error: {e}")
            return []
    
    def get_grade_level_books(self, grade_level, limit=20):
        """Get books appropriate for a specific grade level"""
        grade_keywords = {
            1: ['beginner', 'early reader', 'picture book'],
            2: ['early reader', 'chapter book', 'beginner'],
            3: ['chapter book', 'intermediate', 'elementary'],
            4: ['intermediate', 'middle grade', 'elementary'],
            5: ['middle grade', 'intermediate', 'upper elementary'],
            6: ['middle grade', 'young adult', 'intermediate'],
            7: ['young adult', 'middle grade', 'teen'],
            8: ['young adult', 'teen', 'adolescent'],
            9: ['young adult', 'teen', 'high school'],
            10: ['young adult', 'teen', 'high school'],
            11: ['young adult', 'teen', 'high school'],
            12: ['young adult', 'adult', 'high school']
        }
        
        keywords = grade_keywords.get(grade_level, ['young adult'])
        all_books = []
        
        for keyword in keywords:
            books = self.search_books(keyword, limit=limit//len(keywords))
            all_books.extend(books)
        
        # Remove duplicates and limit results
        unique_books = []
        seen_ids = set()
        
        for book in all_books:
            book_id = book.get('key', '')
            if book_id not in seen_ids:
                unique_books.append(book)
                seen_ids.add(book_id)
        
        return unique_books[:limit]
    
    def get_reading_recommendations(self, user_id, interests=None, grade_level=None):
        """Get personalized reading recommendations"""
        recommendations = []
        
        # Get books based on interests
        if interests:
            for interest in interests:
                books = self.get_subject_books(interest, grade_level, limit=5)
                recommendations.extend(books)
        
        # Get books based on grade level
        if grade_level:
            grade_books = self.get_grade_level_books(grade_level, limit=10)
            recommendations.extend(grade_books)
        
        # Remove duplicates
        unique_recommendations = []
        seen_ids = set()
        
        for book in recommendations:
            book_id = book.get('key', '')
            if book_id not in seen_ids:
                unique_recommendations.append(book)
                seen_ids.add(book_id)
        
        return unique_recommendations[:15]
    
    def create_reading_lesson(self, book_title, grade_level):
        """Create a reading lesson based on a book"""
        books = self.search_books(book_title, limit=1)
        
        if not books:
            return None
        
        book = books[0]
        book_details = self.get_book_details(book.get('key', ''))
        
        lesson_data = {
            'title': f"Reading: {book.get('title', book_title)}",
            'subject': 'reading',
            'grade_level': grade_level,
            'content_type': 'openlibrary',
            'book_data': book,
            'book_details': book_details,
            'text_content': f"Read and discuss {book.get('title', book_title)} by {book.get('author_name', ['Unknown Author'])[0] if 'author_name' in book else 'Unknown Author'}.",
            'estimated_time': 45,
            'xp_value': 30
        }
        
        return lesson_data
    
    def get_book_cover_url(self, book_id, size='M'):
        """Get book cover image URL"""
        # OpenLibrary cover API
        cover_url = f"https://covers.openlibrary.org/b/id/{book_id}-{size}.jpg"
        return cover_url
    
    def download_book_cover(self, book_id, size='M'):
        """Download and cache book cover image"""
        cover_url = self.get_book_cover_url(book_id, size)
        filename = f"cover_{book_id}_{size}.jpg"
        cover_path = self.cache_dir / filename
        
        # Check if already cached
        if cover_path.exists():
            return str(cover_path)
        
        try:
            response = self.session.get(cover_url, stream=True)
            response.raise_for_status()
            
            with open(cover_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            return str(cover_path)
            
        except requests.RequestException as e:
            logger.error(f"Error downloading cover {book_id}: {e}")
            return None
    
    def _filter_by_grade_level(self, books, grade_level):
        """Filter books by grade level appropriateness"""
        if not grade_level:
            return books
        
        # Simple filtering based on title keywords and subject
        filtered_books = []
        
        for book in books:
            title = book.get('title', '').lower()
            subjects = book.get('subject', [])
            
            # Check for age-appropriate keywords
            is_appropriate = True
            
            if grade_level <= 3:
                # Younger grades - avoid mature content
                mature_keywords = ['adult', 'mature', 'teen', 'young adult']
                for keyword in mature_keywords:
                    if keyword in title or any(keyword in subject.lower() for subject in subjects):
                        is_appropriate = False
                        break
            
            elif grade_level >= 9:
                # Older grades - can include young adult content
                pass  # Allow most content for older students
            
            if is_appropriate:
                filtered_books.append(book)
        
        return filtered_books
    
    def get_reading_level(self, book):
        """Estimate reading level based on book metadata"""
        title = book.get('title', '')
        subjects = book.get('subject', [])
        
        # Simple heuristics for reading level
        if any('picture book' in subject.lower() for subject in subjects):
            return 1
        elif any('early reader' in subject.lower() for subject in subjects):
            return 2
        elif any('chapter book' in subject.lower() for subject in subjects):
            return 3
        elif any('middle grade' in subject.lower() for subject in subjects):
            return 5
        elif any('young adult' in subject.lower() for subject in subjects):
            return 8
        else:
            return 5  # Default to middle grade
    
    def create_reading_list(self, grade_level, subjects=None):
        """Create a curated reading list for a grade level"""
        reading_list = []
        
        if subjects:
            for subject in subjects:
                books = self.get_subject_books(subject, grade_level, limit=5)
                reading_list.extend(books)
        else:
            # Default subjects for each grade level
            default_subjects = {
                1: ['animals', 'nature', 'family'],
                2: ['science', 'history', 'adventure'],
                3: ['mystery', 'fantasy', 'science'],
                4: ['history', 'science', 'adventure'],
                5: ['fantasy', 'science', 'history'],
                6: ['mystery', 'adventure', 'science'],
                7: ['fantasy', 'history', 'science'],
                8: ['young adult', 'science', 'history'],
                9: ['young adult', 'classic', 'science'],
                10: ['young adult', 'classic', 'history'],
                11: ['young adult', 'classic', 'science'],
                12: ['young adult', 'classic', 'literature']
            }
            
            subjects = default_subjects.get(grade_level, ['young adult'])
            for subject in subjects:
                books = self.get_subject_books(subject, grade_level, limit=3)
                reading_list.extend(books)
        
        # Remove duplicates and limit
        unique_books = []
        seen_ids = set()
        
        for book in reading_list:
            book_id = book.get('key', '')
            if book_id not in seen_ids:
                unique_books.append(book)
                seen_ids.add(book_id)
        
        return unique_books[:10]
    
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
        logger.info("OpenLibrary cache cleared")

# Usage example
if __name__ == "__main__":
    ol_api = OpenLibraryAPI()
    
    # Search for books about space
    space_books = ol_api.search_books("space exploration", grade_level=4)
    print(f"Found {len(space_books)} space books")
    
    # Get grade-level recommendations
    grade_books = ol_api.get_grade_level_books(3, limit=5)
    print(f"Found {len(grade_books)} books for grade 3")
    
    # Create reading lesson
    lesson = ol_api.create_reading_lesson("The Hobbit", 6)
    if lesson:
        print(f"Created lesson: {lesson['title']}")
    
    # Get reading recommendations
    recommendations = ol_api.get_reading_recommendations(
        user_id=1, 
        interests=['science', 'adventure'], 
        grade_level=4
    )
    print(f"Found {len(recommendations)} recommendations")
    
    # Get cache stats
    stats = ol_api.get_cache_stats()
    print(f"Cache stats: {stats}")