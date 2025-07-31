from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
import json
import datetime
import sqlite3
import logging
from pathlib import Path
import shutil
import zipfile
import hashlib
import base64
import uuid
import random
import string
import re
import collections
import itertools
import functools
import operator
import statistics
import math
import time
import calendar
import tempfile
import subprocess
import platform
import psutil
import requests
from PIL import Image
import PyPDF2
import io
import threading
from apscheduler.schedulers.background import BackgroundScheduler

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'savage_homeschool_os_secret_key_2024'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///savage_homeschool.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs('static/avatars', exist_ok=True)
os.makedirs('static/themes', exist_ok=True)
os.makedirs('static/sounds', exist_ok=True)
os.makedirs('static/fonts', exist_ok=True)
os.makedirs('backups', exist_ok=True)
os.makedirs('logs', exist_ok=True)

# Initialize extensions
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Initialize scheduler for backups
scheduler = BackgroundScheduler()
scheduler.start()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/savage_homeschool.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Database Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # admin, parent, child
    grade_level = db.Column(db.Integer, nullable=True)
    avatar_data = db.Column(db.Text, nullable=True)
    pin = db.Column(db.String(6), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    
    # Additional fields for gamification
    total_xp = db.Column(db.Integer, default=0)
    lessons_completed = db.Column(db.Integer, default=0)
    badges_earned = db.Column(db.Integer, default=0)
    current_level = db.Column(db.Integer, default=1)
    streak_days = db.Column(db.Integer, default=0)
    parent_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    status = db.Column(db.String(20), default='active')  # active, inactive, suspended
    
    # Relationships
    progress = db.relationship('Progress', backref='user', lazy=True)
    activities = db.relationship('ActivityLog', backref='user', lazy=True)
    reading_logs = db.relationship('ReadingLog', backref='user', lazy=True)
    custom_courses = db.relationship('CustomCourse', backref='creator', lazy=True)

class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)  # core, specials, electives, optional
    grade_level = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    lessons = db.relationship('Lesson', backref='subject', lazy=True)

class Lesson(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    grade_level = db.Column(db.Integer, nullable=False)
    level = db.Column(db.Integer, nullable=False)  # 1-5
    lesson_type = db.Column(db.String(50), nullable=False)  # teaching, practice, quiz, custom
    content = db.Column(db.Text, nullable=True)
    file_path = db.Column(db.String(500), nullable=True)
    xp_value = db.Column(db.Integer, default=10)
    estimated_time = db.Column(db.Integer, default=15)  # minutes
    tags = db.Column(db.Text, nullable=True)  # JSON string
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    progress = db.relationship('Progress', backref='lesson', lazy=True)
    quizzes = db.relationship('Quiz', backref='lesson', lazy=True)

class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    lesson_id = db.Column(db.Integer, db.ForeignKey('lesson.id'), nullable=False)
    question = db.Column(db.Text, nullable=False)
    answer = db.Column(db.Text, nullable=False)
    options = db.Column(db.Text, nullable=True)  # JSON string for multiple choice
    question_type = db.Column(db.String(20), default='multiple_choice')  # multiple_choice, true_false, short_answer
    points = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

class Progress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    lesson_id = db.Column(db.Integer, db.ForeignKey('lesson.id'), nullable=False)
    status = db.Column(db.String(20), default='not_started')  # not_started, in_progress, completed, failed
    score = db.Column(db.Float, nullable=True)
    attempts = db.Column(db.Integer, default=0)
    time_spent = db.Column(db.Integer, default=0)  # seconds
    completed_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)



class ActivityLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    activity_type = db.Column(db.String(50), nullable=False)  # login, lesson_start, lesson_complete, quiz_attempt, etc.
    description = db.Column(db.Text, nullable=True)
    lesson_metadata = db.Column(db.Text, nullable=True)  # JSON string for additional data
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

class ReadingLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    book_title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(100), nullable=True)
    isbn = db.Column(db.String(20), nullable=True)
    rating = db.Column(db.Integer, nullable=True)  # 1-5 stars
    review = db.Column(db.Text, nullable=True)
    reading_time = db.Column(db.Integer, default=0)  # minutes
    status = db.Column(db.String(20), default='reading')  # reading, completed, abandoned
    started_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)

class CustomCourse(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    grade_level = db.Column(db.Integer, nullable=False)
    subject_category = db.Column(db.String(50), nullable=False)
    is_shared = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    
    # Relationships
    custom_lessons = db.relationship('CustomLesson', backref='course', lazy=True)

class CustomLesson(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('custom_course.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=True)
    file_path = db.Column(db.String(500), nullable=True)
    xp_value = db.Column(db.Integer, default=10)
    level = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

class SystemSettings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    setting_key = db.Column(db.String(100), unique=True, nullable=False)
    setting_value = db.Column(db.Text, nullable=True)
    description = db.Column(db.Text, nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            return redirect(url_for('admin_dashboard'))
        elif current_user.role == 'parent':
            return redirect(url_for('parent_dashboard'))
        else:
            return redirect(url_for('child_dashboard'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        pin = request.form.get('pin')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.is_active:
            if user.role == 'child' and pin:
                if user.pin == pin:
                    login_user(user)
                    log_activity(user.id, 'login', f'Child {user.username} logged in')
                    return redirect(url_for('child_dashboard'))
            elif user.role in ['admin', 'parent'] and password:
                if check_password_hash(user.password_hash, password):
                    login_user(user)
                    log_activity(user.id, 'login', f'{user.role.title()} {user.username} logged in')
                    return redirect(url_for('admin_dashboard' if user.role == 'admin' else 'parent_dashboard'))
        
        flash('Invalid credentials', 'error')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    log_activity(current_user.id, 'logout', f'{current_user.username} logged out')
    logout_user()
    return redirect(url_for('index'))

@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    users = User.query.filter(User.role != 'admin').all()
    subjects = Subject.query.all()
    recent_activities = ActivityLog.query.order_by(ActivityLog.created_at.desc()).limit(20).all()
    
    return render_template('admin/dashboard.html', users=users, subjects=subjects, activities=recent_activities)

@app.route('/parent/dashboard')
@login_required
def parent_dashboard():
    if current_user.role not in ['admin', 'parent']:
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    children = User.query.filter_by(role='child').all()
    return render_template('parent/dashboard.html', children=children)

@app.route('/child/dashboard')
@login_required
def child_dashboard():
    if current_user.role != 'child':
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    # Get today's lessons
    today_lessons = get_today_lessons(current_user.id)
    progress = get_user_progress(current_user.id)
    rewards = get_user_rewards(current_user.id)
    
    return render_template('child/dashboard.html', 
                         lessons=today_lessons, 
                         progress=progress, 
                         rewards=rewards)

@app.route('/lesson/<int:lesson_id>')
@login_required
def view_lesson(lesson_id):
    lesson = Lesson.query.get_or_404(lesson_id)
    progress = Progress.query.filter_by(user_id=current_user.id, lesson_id=lesson_id).first()
    
    if not progress:
        progress = Progress(user_id=current_user.id, lesson_id=lesson_id, status='not_started')
        db.session.add(progress)
        db.session.commit()
    
    return render_template('lesson/view.html', lesson=lesson, progress=progress)

@app.route('/lesson/<int:lesson_id>/start')
@login_required
def start_lesson(lesson_id):
    lesson = Lesson.query.get_or_404(lesson_id)
    progress = Progress.query.filter_by(user_id=current_user.id, lesson_id=lesson_id).first()
    
    if progress and progress.status == 'completed':
        flash('Lesson already completed', 'info')
        return redirect(url_for('view_lesson', lesson_id=lesson_id))
    
    if not progress:
        progress = Progress(user_id=current_user.id, lesson_id=lesson_id, status='in_progress')
        db.session.add(progress)
    else:
        progress.status = 'in_progress'
        progress.attempts += 1
    
    db.session.commit()
    log_activity(current_user.id, 'lesson_start', f'Started lesson: {lesson.title}')
    
    return redirect(url_for('view_lesson', lesson_id=lesson_id))

@app.route('/lesson/<int:lesson_id>/complete', methods=['POST'])
@login_required
def complete_lesson(lesson_id):
    lesson = Lesson.query.get_or_404(lesson_id)
    progress = Progress.query.filter_by(user_id=current_user.id, lesson_id=lesson_id).first()
    
    if not progress:
        flash('Lesson not started', 'error')
        return redirect(url_for('view_lesson', lesson_id=lesson_id))
    
    score = request.form.get('score', type=float)
    time_spent = request.form.get('time_spent', type=int, default=0)
    
    progress.status = 'completed' if score >= 80 else 'failed'
    progress.score = score
    progress.time_spent = time_spent
    progress.completed_at = datetime.datetime.utcnow()
    db.session.commit()
    
    # Award XP
    if progress.status == 'completed':
        award_xp(current_user.id, lesson.xp_value, f'Completed lesson: {lesson.title}')
        log_activity(current_user.id, 'lesson_complete', f'Completed lesson: {lesson.title} with score {score}')
    else:
        log_activity(current_user.id, 'lesson_failed', f'Failed lesson: {lesson.title} with score {score}')
    
    return jsonify({'status': 'success', 'message': 'Lesson completed'})

@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_lesson():
    if current_user.role not in ['admin', 'parent']:
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        file = request.files.get('file')
        subject = request.form.get('subject')
        grade_level = request.form.get('grade_level', type=int)
        level = request.form.get('level', type=int)
        lesson_type = request.form.get('lesson_type')
        
        if file and file.filename:
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            
            # Process the uploaded file
            lesson = process_uploaded_file(file_path, subject, grade_level, level, lesson_type)
            
            flash('Lesson uploaded successfully', 'success')
            return redirect(url_for('admin_dashboard'))
    
    subjects = Subject.query.all()
    return render_template('admin/upload.html', subjects=subjects)

@app.route('/api/backup', methods=['POST'])
@login_required
def create_backup():
    if current_user.role != 'admin':
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        backup_path = create_system_backup()
        return jsonify({'status': 'success', 'backup_path': backup_path})
    except Exception as e:
        logger.error(f'Backup failed: {e}')
        return jsonify({'error': 'Backup failed'}), 500

@app.route('/api/restore', methods=['POST'])
@login_required
def restore_backup():
    if current_user.role != 'admin':
        return jsonify({'error': 'Access denied'}), 403
    
    backup_file = request.files.get('backup_file')
    if backup_file:
        try:
            restore_system_backup(backup_file)
            return jsonify({'status': 'success'})
        except Exception as e:
            logger.error(f'Restore failed: {e}')
            return jsonify({'error': 'Restore failed'}), 500
    
    return jsonify({'error': 'No backup file provided'}), 400

# Helper functions
def log_activity(user_id, activity_type, description):
    activity = ActivityLog(
        user_id=user_id,
        activity_type=activity_type,
        description=description
    )
    db.session.add(activity)
    db.session.commit()

def award_xp(user_id, xp_amount, reason):
    reward = Reward(
        user_id=user_id,
        reward_type='xp',
        reward_name='Experience Points',
        reward_value=xp_amount,
        description=reason
    )
    db.session.add(reward)
    db.session.commit()

def get_today_lessons(user_id):
    # Get lessons assigned for today based on user's grade level and progress
    user = User.query.get(user_id)
    if not user:
        return []
    
    # Get subjects for user's grade level
    subjects = Subject.query.filter_by(grade_level=user.grade_level).all()
    lessons = []
    
    for subject in subjects:
        # Get next lesson in progression
        progress = Progress.query.filter_by(user_id=user_id).join(Lesson).filter(
            Lesson.subject_id == subject.id
        ).order_by(Progress.created_at.desc()).first()
        
        if not progress or progress.status == 'completed':
            # Get next lesson in sequence
            next_lesson = Lesson.query.filter_by(
                subject_id=subject.id,
                grade_level=user.grade_level
            ).order_by(Lesson.level).first()
            
            if next_lesson:
                lessons.append(next_lesson)
    
    return lessons

def get_user_progress(user_id):
    progress = Progress.query.filter_by(user_id=user_id).all()
    return progress

def get_user_rewards(user_id):
    rewards = Reward.query.filter_by(user_id=user_id).all()
    return rewards

def process_uploaded_file(file_path, subject, grade_level, level, lesson_type):
    # Extract content from file (PDF, image, etc.)
    content = extract_file_content(file_path)
    
    # Generate lesson title
    title = generate_lesson_title(content, subject, grade_level, level)
    
    # Create lesson
    lesson = Lesson(
        title=title,
        subject_id=subject,
        grade_level=grade_level,
        level=level,
        lesson_type=lesson_type,
        content=content,
        file_path=file_path,
        xp_value=calculate_xp_value(grade_level, level),
        tags=json.dumps(['uploaded', subject, f'grade_{grade_level}', f'level_{level}'])
    )
    
    db.session.add(lesson)
    db.session.commit()
    
    return lesson

def extract_file_content(file_path):
    # Extract text content from various file types
    file_ext = os.path.splitext(file_path)[1].lower()
    
    if file_ext == '.pdf':
        return extract_pdf_content(file_path)
    elif file_ext in ['.jpg', '.jpeg', '.png', '.gif']:
        return extract_image_content(file_path)
    else:
        return "Content extracted from uploaded file"

def extract_pdf_content(file_path):
    try:
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
        return text
    except Exception as e:
        logger.error(f'PDF extraction failed: {e}')
        return "PDF content"

def extract_image_content(file_path):
    # For images, return a placeholder
    return "Image content - manual processing required"

def generate_lesson_title(content, subject, grade_level, level):
    # Generate a title based on content and metadata
    return f"Grade {grade_level} - {subject} - Level {level} - Uploaded Lesson"

def calculate_xp_value(grade_level, level):
    # Calculate XP based on grade level and difficulty
    base_xp = 10
    grade_multiplier = grade_level * 2
    level_multiplier = level * 3
    return base_xp + grade_multiplier + level_multiplier

def create_system_backup():
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_filename = f'savage_homeschool_backup_{timestamp}.zip'
    backup_path = os.path.join('backups', backup_filename)
    
    with zipfile.ZipFile(backup_path, 'w') as backup_zip:
        # Backup database
        backup_zip.write('savage_homeschool.db', 'database.db')
        
        # Backup uploads
        for root, dirs, files in os.walk('uploads'):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, 'uploads')
                backup_zip.write(file_path, f'uploads/{arcname}')
        
        # Backup logs
        for root, dirs, files in os.walk('logs'):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, 'logs')
                backup_zip.write(file_path, f'logs/{arcname}')
    
    return backup_path

def restore_system_backup(backup_file):
    # Restore system from backup file
    with zipfile.ZipFile(backup_file, 'r') as backup_zip:
        backup_zip.extractall('temp_restore')
    
    # Restore database
    if os.path.exists('temp_restore/database.db'):
        shutil.copy('temp_restore/database.db', 'savage_homeschool.db')
    
    # Restore uploads
    if os.path.exists('temp_restore/uploads'):
        shutil.rmtree('uploads', ignore_errors=True)
        shutil.copytree('temp_restore/uploads', 'uploads')
    
    # Clean up
    shutil.rmtree('temp_restore')

# Scheduled tasks
def scheduled_backup():
    try:
        create_system_backup()
        logger.info('Scheduled backup completed successfully')
    except Exception as e:
        logger.error(f'Scheduled backup failed: {e}')

# Schedule daily backup at 2 AM
scheduler.add_job(scheduled_backup, 'cron', hour=2)

# Create database tables
with app.app_context():
    db.create_all()
    
    # Create default admin user if none exists
    admin_user = User.query.filter_by(role='admin').first()
    if not admin_user:
        admin_user = User(
            username='admin',
            email='admin@savagehomeschool.com',
            password_hash=generate_password_hash('admin123'),
            role='admin'
        )
        db.session.add(admin_user)
        db.session.commit()

# Add these new routes after the existing routes

@app.route('/child/progress')
@login_required
def child_progress():
    if current_user.role != 'child':
        return redirect(url_for('login'))
    
    # Get user progress data
    subjects = get_user_progress(current_user.id)
    achievements = get_user_achievements(current_user.id)
    recent_activities = get_recent_activities(current_user.id)
    
    return render_template('child/progress.html', 
                         user=current_user,
                         subjects=subjects,
                         achievements=achievements,
                         recent_activities=recent_activities)

@app.route('/child/rewards')
@login_required
def child_rewards():
    if current_user.role != 'child':
        return redirect(url_for('login'))
    
    # Get available rewards
    avatar_rewards = get_rewards_by_category('avatar')
    game_rewards = get_rewards_by_category('game')
    privilege_rewards = get_rewards_by_category('privilege')
    inventory = get_user_inventory(current_user.id)
    
    return render_template('child/rewards.html',
                         user=current_user,
                         avatar_rewards=avatar_rewards,
                         game_rewards=game_rewards,
                         privilege_rewards=privilege_rewards,
                         inventory=inventory)

@app.route('/child/journal')
@login_required
def child_journal():
    if current_user.role != 'child':
        return redirect(url_for('login'))
    
    # Get journal data
    journal_entries = get_journal_entries(current_user.id)
    journal_stats = get_journal_stats(current_user.id)
    daily_prompt = get_daily_prompt()
    
    return render_template('child/journal.html',
                         user=current_user,
                         journal_entries=journal_entries,
                         journal_stats=journal_stats,
                         daily_prompt=daily_prompt)

@app.route('/admin/users')
@login_required
def admin_users():
    if current_user.role != 'admin':
        return redirect(url_for('login'))
    
    # Get all users and stats
    users = User.query.all()
    stats = get_user_stats()
    parents = User.query.filter_by(role='parent').all()
    
    return render_template('admin/users.html',
                         users=users,
                         stats=stats,
                         parents=parents)

# API Routes for functionality

@app.route('/api/purchase_reward', methods=['POST'])
@login_required
def purchase_reward():
    if current_user.role != 'child':
        return jsonify({'success': False, 'message': 'Only children can purchase rewards'})
    
    data = request.get_json()
    reward_id = data.get('reward_id')
    
    reward = Reward.query.get(reward_id)
    if not reward:
        return jsonify({'success': False, 'message': 'Reward not found'})
    
    if current_user.total_xp < reward.xp_cost:
        return jsonify({'success': False, 'message': 'Not enough XP'})
    
    # Purchase the reward
    current_user.total_xp -= reward.xp_cost
    add_to_inventory(current_user.id, reward_id)
    
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Reward purchased successfully'})

@app.route('/api/use_item', methods=['POST'])
@login_required
def use_item():
    data = request.get_json()
    item_id = data.get('item_id')
    
    # Use the item (implement based on item type)
    success = use_inventory_item(current_user.id, item_id)
    
    if success:
        return jsonify({'success': True, 'message': 'Item used successfully'})
    else:
        return jsonify({'success': False, 'message': 'Failed to use item'})

@app.route('/api/mystery_reward', methods=['POST'])
@login_required
def mystery_reward():
    if current_user.role != 'child':
        return jsonify({'success': False, 'message': 'Only children can get mystery rewards'})
    
    if current_user.total_xp < 50:
        return jsonify({'success': False, 'message': 'Not enough XP'})
    
    # Get random reward
    reward = get_random_reward()
    current_user.total_xp -= 50
    add_to_inventory(current_user.id, reward.id)
    
    db.session.commit()
    
    return jsonify({'success': True, 'reward': {
        'name': reward.name,
        'description': reward.description,
        'icon': reward.icon
    }})

@app.route('/api/journal/entry', methods=['POST'])
@login_required
def create_journal_entry():
    if current_user.role != 'child':
        return jsonify({'success': False, 'message': 'Only children can create journal entries'})
    
    title = request.form.get('title', '')
    content = request.form.get('content', '')
    tags = request.form.get('tags', '')
    mood = request.form.get('mood', 'neutral')
    is_draft = request.form.get('is_draft', 'false') == 'true'
    
    if not content:
        return jsonify({'success': False, 'message': 'Content is required'})
    
    # Create journal entry
    entry = JournalEntry(
        user_id=current_user.id,
        title=title,
        content=content,
        tags=tags,
        mood=mood,
        is_draft=is_draft
    )
    
    db.session.add(entry)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Journal entry created successfully'})

@app.route('/api/journal/draft', methods=['POST'])
@login_required
def save_journal_draft():
    if current_user.role != 'child':
        return jsonify({'success': False, 'message': 'Only children can save drafts'})
    
    title = request.form.get('title', '')
    content = request.form.get('content', '')
    tags = request.form.get('tags', '')
    mood = request.form.get('mood', 'neutral')
    
    # Save or update draft
    draft = JournalEntry.query.filter_by(
        user_id=current_user.id, 
        is_draft=True
    ).first()
    
    if draft:
        draft.title = title
        draft.content = content
        draft.tags = tags
        draft.mood = mood
    else:
        draft = JournalEntry(
            user_id=current_user.id,
            title=title,
            content=content,
            tags=tags,
            mood=mood,
            is_draft=True
        )
        db.session.add(draft)
    
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Draft saved successfully'})

@app.route('/api/journal/entry/<int:entry_id>', methods=['GET'])
@login_required
def get_journal_entry(entry_id):
    entry = JournalEntry.query.get_or_404(entry_id)
    
    if entry.user_id != current_user.id and current_user.role != 'admin':
        return jsonify({'success': False, 'message': 'Access denied'})
    
    return jsonify({
        'success': True,
        'entry': {
            'id': entry.id,
            'title': entry.title,
            'content': entry.content,
            'tags': entry.tags,
            'mood': entry.mood
        }
    })

@app.route('/api/journal/entry/<int:entry_id>', methods=['DELETE'])
@login_required
def delete_journal_entry(entry_id):
    entry = JournalEntry.query.get_or_404(entry_id)
    
    if entry.user_id != current_user.id and current_user.role != 'admin':
        return jsonify({'success': False, 'message': 'Access denied'})
    
    db.session.delete(entry)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Entry deleted successfully'})

@app.route('/api/journal/export', methods=['POST'])
@login_required
def export_journal():
    if current_user.role != 'child':
        return jsonify({'success': False, 'message': 'Only children can export journals'})
    
    data = request.get_json()
    format_type = data.get('format', 'txt')
    filters = data.get('filters', {})
    
    # Get filtered entries
    entries = get_filtered_journal_entries(current_user.id, filters)
    
    if format_type == 'pdf':
        return export_journal_pdf(entries)
    elif format_type == 'json':
        return export_journal_json(entries)
    else:
        return export_journal_txt(entries)

@app.route('/api/admin/users', methods=['POST'])
@login_required
def create_user():
    if current_user.role != 'admin':
        return jsonify({'success': False, 'message': 'Admin access required'})
    
    username = request.form.get('username')
    email = request.form.get('email')
    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')
    role = request.form.get('role')
    grade_level = request.form.get('grade_level')
    password = request.form.get('password')
    pin = request.form.get('pin')
    parent_id = request.form.get('parent_id')
    status = request.form.get('status', 'active')
    
    # Check if user already exists
    if User.query.filter_by(username=username).first():
        return jsonify({'success': False, 'message': 'Username already exists'})
    
    if User.query.filter_by(email=email).first():
        return jsonify({'success': False, 'message': 'Email already exists'})
    
    # Create new user
    hashed_password = generate_password_hash(password)
    user = User(
        username=username,
        email=email,
        first_name=first_name,
        last_name=last_name,
        role=role,
        grade_level=grade_level,
        password_hash=hashed_password,
        pin=pin,
        parent_id=parent_id,
        status=status
    )
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'User created successfully'})

@app.route('/api/admin/users/<int:user_id>', methods=['GET'])
@login_required
def get_user_details(user_id):
    if current_user.role != 'admin':
        return jsonify({'success': False, 'message': 'Admin access required'})
    
    user = User.query.get_or_404(user_id)
    
    # Generate HTML for user details
    html = f"""
    <div class="user-details">
        <h4>{user.first_name} {user.last_name}</h4>
        <p><strong>Email:</strong> {user.email}</p>
        <p><strong>Username:</strong> {user.username}</p>
        <p><strong>Role:</strong> {user.role}</p>
        <p><strong>Status:</strong> {user.status}</p>
        <p><strong>Grade Level:</strong> {user.grade_level or 'N/A'}</p>
        <p><strong>Total XP:</strong> {user.total_xp}</p>
        <p><strong>Lessons Completed:</strong> {user.lessons_completed}</p>
        <p><strong>Streak Days:</strong> {user.streak_days}</p>
        <p><strong>Last Login:</strong> {user.last_login or 'Never'}</p>
    </div>
    """
    
    return jsonify({'success': True, 'html': html})

@app.route('/api/admin/users/<int:user_id>/reset-password', methods=['POST'])
@login_required
def reset_user_password(user_id):
    if current_user.role != 'admin':
        return jsonify({'success': False, 'message': 'Admin access required'})
    
    user = User.query.get_or_404(user_id)
    
    # Generate new password
    new_password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
    user.password_hash = generate_password_hash(new_password)
    
    db.session.commit()
    
    return jsonify({'success': True, 'message': f'Password reset to: {new_password}'})

@app.route('/api/admin/users/<int:user_id>/reset-pin', methods=['POST'])
@login_required
def reset_user_pin(user_id):
    if current_user.role != 'admin':
        return jsonify({'success': False, 'message': 'Admin access required'})
    
    user = User.query.get_or_404(user_id)
    
    if user.role != 'child':
        return jsonify({'success': False, 'message': 'Only children have PINs'})
    
    # Generate new PIN
    new_pin = ''.join(random.choices(string.digits, k=4))
    user.pin = new_pin
    
    db.session.commit()
    
    return jsonify({'success': True, 'message': f'PIN reset to: {new_pin}'})

@app.route('/api/admin/users/<int:user_id>', methods=['DELETE'])
@login_required
def delete_user(user_id):
    if current_user.role != 'admin':
        return jsonify({'success': False, 'message': 'Admin access required'})
    
    user = User.query.get_or_404(user_id)
    
    if user.id == current_user.id:
        return jsonify({'success': False, 'message': 'Cannot delete yourself'})
    
    db.session.delete(user)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'User deleted successfully'})

@app.route('/api/admin/users/bulk-action', methods=['POST'])
@login_required
def bulk_user_action():
    if current_user.role != 'admin':
        return jsonify({'success': False, 'message': 'Admin access required'})
    
    data = request.get_json()
    action = data.get('action')
    user_ids = data.get('user_ids', [])
    
    users = User.query.filter(User.id.in_(user_ids)).all()
    
    for user in users:
        if action == 'activate':
            user.status = 'active'
        elif action == 'deactivate':
            user.status = 'inactive'
        elif action == 'delete':
            if user.id != current_user.id:
                db.session.delete(user)
    
    db.session.commit()
    
    return jsonify({'success': True, 'message': f'Bulk action {action} completed'})

# Helper functions

def get_user_achievements(user_id):
    """Get user achievements"""
    # This would query achievements from database
    return []

def get_recent_activities(user_id):
    """Get recent user activities"""
    activities = ActivityLog.query.filter_by(user_id=user_id).order_by(ActivityLog.created_at.desc()).limit(10).all()
    return activities

def get_rewards_by_category(category):
    """Get rewards by category"""
    rewards = Reward.query.filter_by(category=category).all()
    return rewards

def get_user_inventory(user_id):
    """Get user inventory"""
    # This would query user inventory from database
    return []

def get_journal_entries(user_id):
    """Get journal entries for user"""
    entries = JournalEntry.query.filter_by(user_id=user_id, is_draft=False).order_by(JournalEntry.created_at.desc()).all()
    return entries

def get_journal_stats(user_id):
    """Get journal statistics"""
    total_entries = JournalEntry.query.filter_by(user_id=user_id, is_draft=False).count()
    this_month = JournalEntry.query.filter(
        JournalEntry.user_id == user_id,
        JournalEntry.is_draft == False,
        JournalEntry.created_at >= datetime.datetime.now().replace(day=1)
    ).count()
    
    return {
        'total_entries': total_entries,
        'this_month': this_month,
        'avg_length': 0,  # Calculate average word count
        'streak': 0  # Calculate writing streak
    }

def get_daily_prompt():
    """Get daily writing prompt"""
    prompts = [
        "What did you learn today that made you excited?",
        "What was the most challenging part of today's learning?",
        "What would you like to learn more about tomorrow?",
        "How did you feel when you completed today's lesson?",
        "What questions do you still have about today's topic?"
    ]
    return random.choice(prompts)

def add_to_inventory(user_id, reward_id):
    """Add item to user inventory"""
    # This would add item to user inventory
    pass

def use_inventory_item(user_id, item_id):
    """Use inventory item"""
    # This would use inventory item
    return True

def get_random_reward():
    """Get random reward"""
    rewards = Reward.query.all()
    return random.choice(rewards) if rewards else None

def get_filtered_journal_entries(user_id, filters):
    """Get filtered journal entries"""
    query = JournalEntry.query.filter_by(user_id=user_id, is_draft=False)
    
    # Apply filters
    if filters.get('date') == 'week':
        week_ago = datetime.datetime.now() - datetime.timedelta(days=7)
        query = query.filter(JournalEntry.created_at >= week_ago)
    elif filters.get('date') == 'month':
        month_ago = datetime.datetime.now() - datetime.timedelta(days=30)
        query = query.filter(JournalEntry.created_at >= month_ago)
    
    if filters.get('mood') != 'all':
        query = query.filter(JournalEntry.mood == filters['mood'])
    
    return query.order_by(JournalEntry.created_at.desc()).all()

def export_journal_pdf(entries):
    """Export journal as PDF"""
    # This would generate PDF
    return "PDF content"

def export_journal_json(entries):
    """Export journal as JSON"""
    data = []
    for entry in entries:
        data.append({
            'title': entry.title,
            'content': entry.content,
            'tags': entry.tags,
            'mood': entry.mood,
            'created_at': entry.created_at.isoformat()
        })
    return jsonify(data)

def export_journal_txt(entries):
    """Export journal as text"""
    content = ""
    for entry in entries:
        content += f"Title: {entry.title}\n"
        content += f"Date: {entry.created_at}\n"
        content += f"Mood: {entry.mood}\n"
        content += f"Content: {entry.content}\n"
        content += f"Tags: {entry.tags}\n"
        content += "-" * 50 + "\n\n"
    return content

def get_user_stats():
    """Get user statistics"""
    total_users = User.query.count()
    active_users = User.query.filter_by(status='active').count()
    children = User.query.filter_by(role='child').count()
    parents = User.query.filter_by(role='parent').count()
    
    return {
        'total_users': total_users,
        'active_users': active_users,
        'children': children,
        'parents': parents
    }

# Add JournalEntry model
class JournalEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(200), nullable=True)
    content = db.Column(db.Text, nullable=False)
    tags = db.Column(db.String(500), nullable=True)
    mood = db.Column(db.String(50), default='neutral')
    is_draft = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

# Add Reward model
class Reward(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    category = db.Column(db.String(50), nullable=False)  # avatar, game, privilege
    xp_cost = db.Column(db.Integer, nullable=False)
    icon = db.Column(db.String(50), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

# Add Inventory model
class Inventory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    reward_id = db.Column(db.Integer, db.ForeignKey('reward.id'), nullable=False)
    purchased_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    used_at = db.Column(db.DateTime, nullable=True)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 