// Savage Homeschool OS - Main JavaScript File

// Global variables
let currentUser = null;
let darkMode = false;
let notifications = [];

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    setupEventListeners();
    loadUserPreferences();
});

// Initialize the application
function initializeApp() {
    console.log('Savage Homeschool OS - Initializing...');
    
    // Check if user is logged in
    if (document.body.classList.contains('logged-in')) {
        currentUser = getUserData();
        updateUserInterface();
    }
    
    // Initialize components
    initializeDarkMode();
    initializeNotifications();
    initializeAnimations();
    initializeTooltips();
    
    console.log('Savage Homeschool OS - Initialized successfully');
}

// Setup event listeners
function setupEventListeners() {
    // Dark mode toggle
    const darkModeToggle = document.getElementById('darkModeToggle');
    if (darkModeToggle) {
        darkModeToggle.addEventListener('click', toggleDarkMode);
    }
    
    // Form submissions
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', handleFormSubmission);
    });
    
    // Auto-save functionality
    const autoSaveInputs = document.querySelectorAll('[data-auto-save]');
    autoSaveInputs.forEach(input => {
        input.addEventListener('input', debounce(handleAutoSave, 1000));
    });
    
    // Keyboard shortcuts
    document.addEventListener('keydown', handleKeyboardShortcuts);
}

// User data management
function getUserData() {
    const userData = localStorage.getItem('userData');
    return userData ? JSON.parse(userData) : null;
}

function updateUserInterface() {
    if (!currentUser) return;
    
    // Update user avatar
    const avatarElements = document.querySelectorAll('.user-avatar');
    avatarElements.forEach(avatar => {
        avatar.textContent = currentUser.initials || 'U';
    });
    
    // Update XP display
    const xpElements = document.querySelectorAll('.xp-display');
    xpElements.forEach(xp => {
        xp.textContent = currentUser.total_xp || 0;
    });
    
    // Update streak display
    const streakElements = document.querySelectorAll('.streak-display');
    streakElements.forEach(streak => {
        streak.textContent = currentUser.streak_days || 0;
    });
}

// Dark mode functionality
function initializeDarkMode() {
    darkMode = localStorage.getItem('darkMode') === 'true';
    applyDarkMode();
}

function toggleDarkMode() {
    darkMode = !darkMode;
    localStorage.setItem('darkMode', darkMode.toString());
    applyDarkMode();
    showNotification('Dark mode ' + (darkMode ? 'enabled' : 'disabled'), 'info');
}

function applyDarkMode() {
    const body = document.body;
    if (darkMode) {
        body.classList.add('dark-mode');
    } else {
        body.classList.remove('dark-mode');
    }
}

// Notification system
function initializeNotifications() {
    // Create notification container if it doesn't exist
    if (!document.getElementById('notificationContainer')) {
        const container = document.createElement('div');
        container.id = 'notificationContainer';
        container.className = 'notification-container';
        document.body.appendChild(container);
    }
}

function showNotification(message, type = 'info', duration = 5000) {
    const container = document.getElementById('notificationContainer');
    const notification = document.createElement('div');
    notification.className = `notification notification-${type} fade-in`;
    notification.innerHTML = `
        <div class="notification-content">
            <i class="fas fa-${getNotificationIcon(type)}"></i>
            <span>${message}</span>
            <button class="notification-close" onclick="this.parentElement.parentElement.remove()">
                <i class="fas fa-times"></i>
            </button>
        </div>
    `;
    
    container.appendChild(notification);
    
    // Auto-remove after duration
    setTimeout(() => {
        if (notification.parentElement) {
            notification.remove();
        }
    }, duration);
    
    // Store notification for history
    notifications.push({
        message,
        type,
        timestamp: new Date()
    });
}

function getNotificationIcon(type) {
    const icons = {
        success: 'check-circle',
        error: 'exclamation-circle',
        warning: 'exclamation-triangle',
        info: 'info-circle'
    };
    return icons[type] || 'info-circle';
}

// Animation system
function initializeAnimations() {
    // Intersection Observer for fade-in animations
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in');
            }
        });
    });
    
    // Observe elements with animation classes
    const animatedElements = document.querySelectorAll('.animate-on-scroll');
    animatedElements.forEach(el => observer.observe(el));
}

// Tooltip system
function initializeTooltips() {
    const tooltipElements = document.querySelectorAll('[data-tooltip]');
    tooltipElements.forEach(element => {
        element.addEventListener('mouseenter', showTooltip);
        element.addEventListener('mouseleave', hideTooltip);
    });
}

function showTooltip(event) {
    const element = event.target;
    const tooltipText = element.getAttribute('data-tooltip');
    
    const tooltip = document.createElement('div');
    tooltip.className = 'tooltip';
    tooltip.textContent = tooltipText;
    
    document.body.appendChild(tooltip);
    
    const rect = element.getBoundingClientRect();
    tooltip.style.left = rect.left + (rect.width / 2) - (tooltip.offsetWidth / 2) + 'px';
    tooltip.style.top = rect.top - tooltip.offsetHeight - 5 + 'px';
}

function hideTooltip() {
    const tooltips = document.querySelectorAll('.tooltip');
    tooltips.forEach(tooltip => tooltip.remove());
}

// Form handling
function handleFormSubmission(event) {
    const form = event.target;
    const submitButton = form.querySelector('button[type="submit"]');
    
    if (submitButton) {
        submitButton.disabled = true;
        submitButton.innerHTML = '<span class="loading-spinner"></span> Processing...';
    }
    
    // Add form validation here if needed
    return true; // Allow form to submit
}

// Auto-save functionality
function handleAutoSave(event) {
    const input = event.target;
    const key = input.getAttribute('data-auto-save');
    const value = input.value;
    
    localStorage.setItem(`auto-save-${key}`, value);
    showNotification('Draft saved automatically', 'info', 2000);
}

// Keyboard shortcuts
function handleKeyboardShortcuts(event) {
    // Ctrl/Cmd + S for save
    if ((event.ctrlKey || event.metaKey) && event.key === 's') {
        event.preventDefault();
        saveCurrentWork();
    }
    
    // Ctrl/Cmd + D for dark mode
    if ((event.ctrlKey || event.metaKey) && event.key === 'd') {
        event.preventDefault();
        toggleDarkMode();
    }
    
    // Escape to close modals
    if (event.key === 'Escape') {
        closeAllModals();
    }
}

// Utility functions
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function saveCurrentWork() {
    // Save current work to localStorage
    const currentWork = {
        timestamp: new Date().toISOString(),
        data: getCurrentWorkData()
    };
    
    localStorage.setItem('currentWork', JSON.stringify(currentWork));
    showNotification('Work saved successfully', 'success');
}

function getCurrentWorkData() {
    // Get data from forms and inputs
    const data = {};
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        const formData = new FormData(form);
        for (let [key, value] of formData.entries()) {
            data[key] = value;
        }
    });
    return data;
}

function closeAllModals() {
    const modals = document.querySelectorAll('.modal');
    modals.forEach(modal => {
        const modalInstance = bootstrap.Modal.getInstance(modal);
        if (modalInstance) {
            modalInstance.hide();
        }
    });
}

// XP and gamification functions
function awardXP(amount, reason) {
    if (!currentUser) return;
    
    currentUser.total_xp = (currentUser.total_xp || 0) + amount;
    updateUserInterface();
    
    // Animate XP gain
    animateXPGain(amount);
    
    // Show notification
    showNotification(`+${amount} XP earned for ${reason}!`, 'success');
    
    // Save to server
    saveXPToServer(amount, reason);
}

function animateXPGain(amount) {
    const xpElement = document.createElement('div');
    xpElement.className = 'xp-gain-animation';
    xpElement.textContent = `+${amount} XP`;
    xpElement.style.cssText = `
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        background: linear-gradient(45deg, #ffc107, #ffca2c);
        color: white;
        padding: 1rem 2rem;
        border-radius: 25px;
        font-weight: bold;
        font-size: 1.2rem;
        z-index: 9999;
        animation: xpGain 2s ease-out forwards;
    `;
    
    document.body.appendChild(xpElement);
    
    setTimeout(() => {
        xpElement.remove();
    }, 2000);
}

// Add CSS animation for XP gain
const style = document.createElement('style');
style.textContent = `
    @keyframes xpGain {
        0% {
            opacity: 0;
            transform: translate(-50%, -50%) scale(0.5);
        }
        50% {
            opacity: 1;
            transform: translate(-50%, -50%) scale(1.2);
        }
        100% {
            opacity: 0;
            transform: translate(-50%, -100%) scale(1);
        }
    }
`;
document.head.appendChild(style);

// Server communication
function saveXPToServer(amount, reason) {
    fetch('/api/award_xp', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            amount: amount,
            reason: reason
        })
    })
    .then(response => response.json())
    .then(data => {
        if (!data.success) {
            console.error('Failed to save XP:', data.message);
        }
    })
    .catch(error => {
        console.error('Error saving XP:', error);
    });
}

// Progress tracking
function updateProgress(lessonId, progress) {
    fetch(`/api/lesson/${lessonId}/progress`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            progress: progress
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            updateProgressUI(lessonId, progress);
        }
    })
    .catch(error => {
        console.error('Error updating progress:', error);
    });
}

function updateProgressUI(lessonId, progress) {
    const progressElement = document.querySelector(`[data-lesson-id="${lessonId}"] .progress-bar`);
    if (progressElement) {
        progressElement.style.width = `${progress}%`;
        progressElement.setAttribute('aria-valuenow', progress);
    }
}

// Break timer functionality
function startBreakTimer(duration = 15) {
    let timeLeft = duration * 60; // Convert to seconds
    const timerDisplay = document.getElementById('timerDisplay');
    const timerContainer = document.getElementById('breakTimer');
    
    if (!timerDisplay || !timerContainer) return;
    
    timerContainer.style.display = 'block';
    
    const timer = setInterval(() => {
        const minutes = Math.floor(timeLeft / 60);
        const seconds = timeLeft % 60;
        
        timerDisplay.textContent = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
        
        if (timeLeft <= 0) {
            clearInterval(timer);
            showNotification('Break time is over! Time to get back to learning!', 'warning');
            timerContainer.style.display = 'none';
        }
        
        timeLeft--;
    }, 1000);
}

// User preferences
function loadUserPreferences() {
    const preferences = localStorage.getItem('userPreferences');
    if (preferences) {
        const prefs = JSON.parse(preferences);
        
        // Apply user preferences
        if (prefs.autoSave) {
            enableAutoSave();
        }
        
        if (prefs.soundEnabled) {
            enableSound();
        }
    }
}

function saveUserPreferences(preferences) {
    localStorage.setItem('userPreferences', JSON.stringify(preferences));
}

// Sound system
function enableSound() {
    // Initialize sound system
    console.log('Sound system enabled');
}

function playSound(soundName) {
    // Play sound effect
    const audio = new Audio(`/static/sounds/${soundName}.mp3`);
    audio.play().catch(error => {
        console.log('Sound playback failed:', error);
    });
}

// Export functions for global use
window.SavageHomeschoolOS = {
    showNotification,
    awardXP,
    updateProgress,
    startBreakTimer,
    toggleDarkMode,
    saveUserPreferences,
    playSound
};

// Error handling
window.addEventListener('error', function(event) {
    console.error('JavaScript error:', event.error);
    showNotification('An error occurred. Please refresh the page.', 'error');
});

// Service Worker registration for offline functionality
if ('serviceWorker' in navigator) {
    window.addEventListener('load', function() {
        navigator.serviceWorker.register('/static/js/sw.js')
            .then(function(registration) {
                console.log('ServiceWorker registration successful');
            })
            .catch(function(err) {
                console.log('ServiceWorker registration failed');
            });
    });
} 