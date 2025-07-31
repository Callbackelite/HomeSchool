# Savage Homeschool OS

A comprehensive, feature-rich homeschool operating system built for families who want complete control over their children's education. Built with Python Flask and designed to be fun, engaging, and academically rigorous.

## 🚀 Features

### Core System
- **Multi-User Support**: Admin, Parent, and Child roles with appropriate permissions
- **Grade-Level Progression**: K-12 support with 5 levels per subject
- **Gamification**: XP system, badges, rewards, and progress tracking
- **Offline-First**: Works completely offline with local database
- **Cross-Platform**: Web interface works on Windows and Android tablets

### Content Management
- **Education.com Integration**: Upload and auto-process content from Education.com
- **API Integrations**: Khan Academy, NASA, OpenLibrary, CK-12, WordsAPI
- **Custom Lesson Builder**: Create your own lessons and courses
- **Auto-Generation**: AI-powered lesson creation from uploaded content

### Learning Features
- **Core Subjects**: Math, Reading, Writing, Science, History, Spelling
- **Specials**: Art, Music, PE, Typing, Technology
- **Electives**: Coding, Finance, Sign Language, Engineering, Cooking
- **Optional Tracks**: Faith, Character Building, Emotional Intelligence

### Parent/Admin Tools
- **Progress Tracking**: Detailed analytics and reports
- **Custom Rewards**: Set up real-world incentives
- **Schedule Management**: Flexible lesson assignment
- **Backup System**: Automatic and manual backups

### Student Experience
- **Personalized Dashboard**: Custom avatars and themes
- **Break Timers**: Built-in break management
- **Reading Log**: Track books and reading progress
- **Reward Shop**: Spend XP on unlockables

## 🛠 Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd SavageHomeschoolOS
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python app.py
   ```

4. **Access the system**
   - Open your browser and go to `http://localhost:5000`
   - Default admin login: `admin` / `admin123`
   - **Important**: Change the default password after first login!

## 📚 Quick Start Guide

### First Time Setup

1. **Login as Admin**
   - Username: `admin`
   - Password: `admin123`

2. **Add Your Family Members**
   - Go to Admin Dashboard → Users tab
   - Click "Add User" for each family member
   - Set appropriate roles (Parent/Child)
   - For children, set grade level and PIN

3. **Upload Content**
   - Use the Upload tab to add content from Education.com
   - Or use API integration to auto-generate lessons
   - Content will be automatically categorized and assigned XP

4. **Set Up Daily Schedule**
   - Assign lessons to children
   - Set up rewards and incentives
   - Configure break times and limits

### For Parents

1. **Monitor Progress**
   - View detailed progress reports
   - Track time spent on lessons
   - See strengths and areas for improvement

2. **Customize Rewards**
   - Set up real-world incentives
   - Create custom badges
   - Configure XP values

3. **Manage Content**
   - Upload new lessons
   - Create custom courses
   - Import from educational APIs

### For Students

1. **Daily Routine**
   - Login with username and PIN
   - See today's assigned lessons
   - Complete lessons to earn XP
   - Take breaks using the timer

2. **Track Progress**
   - View XP and badges earned
   - See subject progress bars
   - Check reading log

3. **Rewards**
   - Spend XP in the reward shop
   - Unlock avatar items and themes
   - Earn special badges for achievements

## 🔧 Configuration

### Database
- SQLite database (local storage)
- Automatic backups to `backups/` folder
- Can be restored from backup files

### API Keys (Optional)
For enhanced content, you can add API keys:
- **NASA API**: Get space and science content
- **WordsAPI**: Enhanced vocabulary features
- **OpenLibrary**: Book recommendations

### Customization
- **Themes**: Dark mode and seasonal themes
- **Avatars**: Customizable student avatars
- **Rewards**: Configurable reward system
- **Subjects**: Add custom subjects and electives

## 📊 System Requirements

### Minimum
- **OS**: Windows 10/11 or Android 8+
- **RAM**: 2GB
- **Storage**: 1GB free space
- **Browser**: Chrome, Firefox, Safari, or Edge

### Recommended
- **OS**: Windows 11 or Android 10+
- **RAM**: 4GB
- **Storage**: 5GB free space
- **Browser**: Chrome or Firefox (latest version)

## 🔒 Security Features

- **Local Storage**: All data stored locally
- **User Authentication**: Secure login system
- **Role-Based Access**: Appropriate permissions per user
- **Data Encryption**: Sensitive data encrypted
- **Backup Security**: Encrypted backup files

## 🚀 Advanced Features

### API Integrations
- **Khan Academy**: Video lessons and exercises
- **NASA**: Space science content and images
- **OpenLibrary**: Book recommendations and reading lists
- **CK-12**: Interactive STEM simulations
- **WordsAPI**: Vocabulary and spelling support

### Content Management
- **Auto-Processing**: Upload PDFs and auto-generate lessons
- **Smart Tagging**: Automatic subject and grade classification
- **Progress Tracking**: Detailed analytics and reports
- **Custom Courses**: Create multi-lesson courses

### Gamification
- **XP System**: Earn points for completing lessons
- **Badges**: Unlock achievements and milestones
- **Reward Shop**: Spend XP on virtual and real rewards
- **Streaks**: Track daily learning streaks

## 🐛 Troubleshooting

### Common Issues

**App won't start**
- Check Python version (3.8+ required)
- Install missing dependencies: `pip install -r requirements.txt`
- Check port 5000 isn't in use

**Can't login**
- Default admin: `admin` / `admin123`
- Check user exists in database
- Reset database if needed

**Upload not working**
- Check file format (PDF, DOC, DOCX, TXT)
- Ensure file size under 16MB
- Check upload folder permissions

**API content not loading**
- Check internet connection
- Verify API keys (if using paid APIs)
- Check cache folder permissions

### Getting Help

1. **Check Logs**: Look in `logs/savage_homeschool.log`
2. **Database Issues**: Check `savage_homeschool.db` file
3. **Backup/Restore**: Use backup system to reset if needed

## 🔄 Updates

### Version History
- **v1.0**: Initial release with core features
- **v1.1**: Added API integrations
- **v1.2**: Enhanced gamification system
- **v1.3**: Improved content management

### Upcoming Features
- **Mobile App**: Native Android/iOS apps
- **Cloud Sync**: Optional cloud backup
- **AI Tutor**: Intelligent lesson recommendations
- **Multi-Family**: Support for homeschool co-ops

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

This is a personal homeschool system, but contributions are welcome:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📞 Support

For support or questions:
- Check the troubleshooting section above
- Review the logs in `logs/` folder
- Create an issue on GitHub

## 🎯 Roadmap

### Short Term (Next 3 Months)
- [ ] Mobile app development
- [ ] Enhanced API integrations
- [ ] Advanced analytics
- [ ] Custom theme builder

### Medium Term (3-6 Months)
- [ ] Cloud sync option
- [ ] Multi-family support
- [ ] AI-powered recommendations
- [ ] Advanced reporting

### Long Term (6+ Months)
- [ ] Commercial version
- [ ] School district integration
- [ ] Advanced AI features
- [ ] Internationalization

---

**Built with ❤️ for homeschool families who want the best education for their children.**

*Savage Homeschool OS - Empowering families to take control of their children's education.* 