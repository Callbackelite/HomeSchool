#!/usr/bin/env python3
"""
Savage Homeschool OS - Startup Script
Launch the homeschool operating system with proper configuration.
"""

import os
import sys
import subprocess
import webbrowser
import time
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        print("❌ Error: Python 3.8 or higher is required.")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True

def check_dependencies():
    """Check if required dependencies are installed."""
    required_modules = [
        'flask',
        'flask_sqlalchemy', 
        'flask_login',
        'requests',
        'PIL',
        'apscheduler',
        'werkzeug',
        'PyPDF2',
        'bs4',  # beautifulsoup4
        'lxml'
    ]
    
    missing_modules = []
    
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing_modules.append(module)
    
    if missing_modules:
        print(f"❌ Missing dependencies: {', '.join(missing_modules)}")
        print("Installing dependencies...")
        return install_dependencies()
    else:
        print("✅ All required dependencies are installed.")
        return True

def install_dependencies():
    """Install required dependencies."""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully.")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies.")
        return False

def create_directories():
    """Create necessary directories if they don't exist."""
    directories = [
        "uploads",
        "static/avatars",
        "static/themes",
        "static/sounds",
        "static/fonts",
        "backups",
        "logs",
        "templates",
        "templates/admin",
        "templates/child",
        "templates/parent",
        "templates/lesson"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    print("✅ Directories created/verified.")

def check_database():
    """Check if database exists and is accessible."""
    db_path = Path("savage_homeschool.db")
    if db_path.exists():
        print("✅ Database found.")
    else:
        print("ℹ️  Database will be created on first run.")

def start_server():
    """Start the Flask development server."""
    print("\n🚀 Starting Savage Homeschool OS...")
    print("=" * 50)
    
    # Set environment variables
    os.environ['FLASK_ENV'] = 'development'
    os.environ['FLASK_DEBUG'] = '1'
    
    try:
        # Import and run the app
        from app import app
        
        print("✅ Server started successfully!")
        print("🌐 Open your browser and go to: http://localhost:5000")
        print("🔑 Default admin login: admin / admin123")
        print("\n📝 Quick Start:")
        print("1. Login as admin (admin / admin123)")
        print("2. Add your family members")
        print("3. Upload content from Education.com")
        print("4. Start learning!")
        
        # Open browser after a short delay
        def open_browser():
            time.sleep(2)
            webbrowser.open('http://localhost:5000')
        
        import threading
        threading.Thread(target=open_browser, daemon=True).start()
        
        # Start the Flask app
        app.run(debug=True, host='0.0.0.0', port=5000)
        
    except ImportError as e:
        print(f"❌ Error importing app: {e}")
        print("Make sure all files are in the correct location.")
        return False
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        return False

def main():
    """Main startup function."""
    print("🏠 Savage Homeschool OS - Startup")
    print("=" * 40)
    
    # Check Python version
    if not check_python_version():
        return False
    
    # Check dependencies
    if not check_dependencies():
        return False
    
    # Create directories
    create_directories()
    
    # Check database
    check_database()
    
    # Start server
    return start_server()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Savage Homeschool OS stopped.")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        print("Please check the logs for more details.") 