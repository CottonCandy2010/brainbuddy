/**
 * Interactive Tooltip Tutorial System for Brain Buddy
 * Provides guided tours for first-time users
 */

class BrainBuddyTutorial {
    constructor() {
        this.currentStep = 0;
        this.isActive = false;
        this.tutorials = {
            homepage: [
                {
                    target: '.welcome-title',
                    title: 'Welcome to Brain Buddy Kids!',
                    content: 'This is your learning adventure starting point. Brain Buddy will help you learn amazing things!',
                    position: 'bottom'
                },
                {
                    target: '.btn-brain-buddy',
                    title: 'Start Your Adventure',
                    content: 'Click here to begin your learning journey. You\'ll choose your age and start exploring fun subjects!',
                    position: 'bottom'
                },
                {
                    target: '.study-tools-section',
                    title: 'Study Tools',
                    content: 'Explore different learning tools like curriculum topics, practice questions, and fun activities!',
                    position: 'top'
                }
            ],
            curriculum: [
                {
                    target: '.subject-grid',
                    title: 'Choose Your Subject',
                    content: 'Pick a subject you want to learn about. Each has fun activities designed just for you!',
                    position: 'top'
                },
                {
                    target: '.subject-card:first-child',
                    title: 'Subject Cards',
                    content: 'Each colorful card represents a different subject. Click on one to explore lessons and activities!',
                    position: 'bottom'
                }
            ],
            profile: [
                {
                    target: '.current-avatar',
                    title: 'Your Avatar',
                    content: 'This is your current profile picture. You can change it by selecting from the avatars below!',
                    position: 'bottom'
                },
                {
                    target: '.avatar-selection',
                    title: 'Avatar Gallery',
                    content: 'Choose from 18 different avatars to personalize your profile. Some special avatars unlock as you learn!',
                    position: 'top'
                },
                {
                    target: '.achievement-avatars-section',
                    title: 'Achievement Avatars',
                    content: 'These special avatars unlock when you complete learning challenges. Keep learning to unlock them all!',
                    position: 'top'
                },
                {
                    target: '.family-account-section',
                    title: 'Family Accounts',
                    content: 'Parents can create family accounts to manage multiple children and track learning progress together!',
                    position: 'top'
                }
            ],
            lesson: [
                {
                    target: '.lesson-content',
                    title: 'Lesson Content',
                    content: 'This is where you\'ll learn new things! Read carefully and take your time to understand each concept.',
                    position: 'top'
                },
                {
                    target: '.audio-controls',
                    title: 'Audio Help',
                    content: 'Click the speaker button to hear the lesson read aloud. This helps with learning!',
                    position: 'bottom'
                }
            ]
        };
        
        this.init();
    }

    init() {
        this.createTutorialElements();
        this.checkFirstVisit();
        this.bindEvents();
    }

    createTutorialElements() {
        // Create tooltip overlay
        const overlay = document.createElement('div');
        overlay.id = 'tutorial-overlay';
        overlay.className = 'tutorial-overlay';
        overlay.innerHTML = `
            <div class="tutorial-spotlight"></div>
            <div class="tutorial-tooltip">
                <div class="tooltip-header">
                    <h4 class="tooltip-title"></h4>
                    <button class="tooltip-close" aria-label="Close tutorial">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
                <div class="tooltip-content"></div>
                <div class="tooltip-actions">
                    <button class="btn btn-outline-light btn-sm tutorial-skip">Skip Tutorial</button>
                    <div class="tutorial-navigation">
                        <button class="btn btn-light btn-sm tutorial-prev" disabled>
                            <i class="fas fa-arrow-left"></i> Previous
                        </button>
                        <span class="tutorial-progress">1 / 3</span>
                        <button class="btn btn-primary btn-sm tutorial-next">
                            Next <i class="fas fa-arrow-right"></i>
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(overlay);
        
        // Create tutorial trigger button
        const triggerBtn = document.createElement('button');
        triggerBtn.id = 'tutorial-trigger';
        triggerBtn.className = 'tutorial-trigger';
        triggerBtn.innerHTML = '<i class="fas fa-question-circle"></i>';
        triggerBtn.title = 'Start Tutorial';
        document.body.appendChild(triggerBtn);
        
        // Add CSS styles
        this.addTutorialStyles();
    }

    addTutorialStyles() {
        const style = document.createElement('style');
        style.textContent = `
            .tutorial-overlay {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0, 0, 0, 0.7);
                z-index: 9999;
                display: none;
                pointer-events: none;
            }
            
            .tutorial-overlay.active {
                display: block;
                pointer-events: auto;
            }
            
            .tutorial-spotlight {
                position: absolute;
                border: 3px solid #4a90e2;
                border-radius: 8px;
                box-shadow: 0 0 0 9999px rgba(0, 0, 0, 0.7);
                pointer-events: none;
                transition: all 0.3s ease;
            }
            
            .tutorial-tooltip {
                position: absolute;
                background: white;
                border-radius: 12px;
                box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
                max-width: 350px;
                min-width: 280px;
                z-index: 10000;
                animation: tooltipFadeIn 0.3s ease;
            }
            
            @keyframes tooltipFadeIn {
                from { opacity: 0; transform: scale(0.9); }
                to { opacity: 1; transform: scale(1); }
            }
            
            .tooltip-header {
                padding: 20px 20px 10px;
                border-bottom: 1px solid #eee;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            
            .tooltip-title {
                margin: 0;
                color: #333;
                font-size: 1.1rem;
                font-weight: 600;
            }
            
            .tooltip-close {
                background: none;
                border: none;
                color: #999;
                font-size: 1.2rem;
                cursor: pointer;
                padding: 0;
                width: 24px;
                height: 24px;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            
            .tooltip-close:hover {
                color: #666;
            }
            
            .tooltip-content {
                padding: 15px 20px;
                color: #555;
                line-height: 1.5;
            }
            
            .tooltip-actions {
                padding: 15px 20px;
                background: #f8f9fa;
                border-radius: 0 0 12px 12px;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            
            .tutorial-navigation {
                display: flex;
                align-items: center;
                gap: 10px;
            }
            
            .tutorial-progress {
                color: #666;
                font-size: 0.9rem;
                font-weight: 500;
            }
            
            .tutorial-trigger {
                position: fixed;
                bottom: 20px;
                right: 20px;
                width: 50px;
                height: 50px;
                border-radius: 50%;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                border: none;
                color: white;
                font-size: 1.2rem;
                cursor: pointer;
                box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
                z-index: 1000;
                transition: transform 0.3s ease;
            }
            
            .tutorial-trigger:hover {
                transform: scale(1.1);
            }
            
            .tutorial-trigger.pulse {
                animation: pulse 2s infinite;
            }
            
            @keyframes pulse {
                0% { box-shadow: 0 0 0 0 rgba(70, 144, 226, 0.7); }
                70% { box-shadow: 0 0 0 10px rgba(70, 144, 226, 0); }
                100% { box-shadow: 0 0 0 0 rgba(70, 144, 226, 0); }
            }
            
            .tutorial-highlight {
                position: relative;
                z-index: 10001 !important;
            }
            
            @media (max-width: 768px) {
                .tutorial-tooltip {
                    max-width: 90vw;
                    margin: 10px;
                }
                
                .tutorial-trigger {
                    width: 45px;
                    height: 45px;
                    font-size: 1.1rem;
                }
            }
        `;
        document.head.appendChild(style);
    }

    checkFirstVisit() {
        const hasSeenTutorial = localStorage.getItem('brainbuddy_tutorial_seen');
        const currentPage = this.getCurrentPage();
        
        if (!hasSeenTutorial && currentPage === 'homepage') {
            setTimeout(() => {
                this.showWelcomePrompt();
            }, 2000);
        }
        
        // Show tutorial trigger if user has seen it before
        if (hasSeenTutorial) {
            document.getElementById('tutorial-trigger').style.display = 'block';
        }
    }

    showWelcomePrompt() {
        const welcomed = localStorage.getItem('brainbuddy_welcomed');
        if (welcomed) return;
        
        // Show welcome modal
        const modal = document.createElement('div');
        modal.className = 'tutorial-welcome-modal';
        modal.innerHTML = `
            <div class="welcome-modal-content">
                <div class="welcome-header">
                    <img src="/static/images/brain-buddy-logo.png" alt="Brain Buddy" style="width: 60px; height: auto;">
                    <h3>Welcome to Brain Buddy Kids!</h3>
                </div>
                <div class="welcome-body">
                    <p>Would you like a quick tour to learn how to use Brain Buddy? It only takes a minute!</p>
                </div>
                <div class="welcome-actions">
                    <button class="btn btn-outline-secondary welcome-skip">Skip Tour</button>
                    <button class="btn btn-primary welcome-start">Start Tour</button>
                </div>
            </div>
        `;
        
        const modalStyle = document.createElement('style');
        modalStyle.textContent = `
            .tutorial-welcome-modal {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0, 0, 0, 0.5);
                display: flex;
                align-items: center;
                justify-content: center;
                z-index: 10000;
                animation: fadeIn 0.3s ease;
            }
            
            .welcome-modal-content {
                background: white;
                border-radius: 15px;
                padding: 30px;
                max-width: 400px;
                text-align: center;
                box-shadow: 0 15px 35px rgba(0, 0, 0, 0.2);
            }
            
            .welcome-header h3 {
                color: #4a90e2;
                margin: 15px 0 20px;
            }
            
            .welcome-body p {
                color: #666;
                margin-bottom: 25px;
                line-height: 1.5;
            }
            
            .welcome-actions {
                display: flex;
                gap: 10px;
                justify-content: center;
            }
        `;
        document.head.appendChild(modalStyle);
        document.body.appendChild(modal);
        
        // Bind events
        modal.querySelector('.welcome-start').addEventListener('click', () => {
            modal.remove();
            this.startTutorial();
            localStorage.setItem('brainbuddy_welcomed', 'true');
        });
        
        modal.querySelector('.welcome-skip').addEventListener('click', () => {
            modal.remove();
            localStorage.setItem('brainbuddy_welcomed', 'true');
            localStorage.setItem('brainbuddy_tutorial_seen', 'true');
            document.getElementById('tutorial-trigger').style.display = 'block';
        });
    }

    bindEvents() {
        const overlay = document.getElementById('tutorial-overlay');
        
        // Tutorial navigation
        overlay.querySelector('.tutorial-next').addEventListener('click', () => this.nextStep());
        overlay.querySelector('.tutorial-prev').addEventListener('click', () => this.prevStep());
        overlay.querySelector('.tutorial-skip').addEventListener('click', () => this.endTutorial());
        overlay.querySelector('.tooltip-close').addEventListener('click', () => this.endTutorial());
        
        // Tutorial trigger
        document.getElementById('tutorial-trigger').addEventListener('click', () => this.startTutorial());
        
        // Close on overlay click
        overlay.addEventListener('click', (e) => {
            if (e.target === overlay) {
                this.endTutorial();
            }
        });
    }

    getCurrentPage() {
        const path = window.location.pathname;
        if (path === '/' || path === '') return 'homepage';
        if (path.includes('profile')) return 'profile';
        if (path.includes('curriculum') || path.includes('study')) return 'curriculum';
        if (path.includes('lesson')) return 'lesson';
        return 'other';
    }

    startTutorial() {
        const currentPage = this.getCurrentPage();
        const tutorial = this.tutorials[currentPage];
        
        if (!tutorial || tutorial.length === 0) {
            this.showNoTutorialMessage();
            return;
        }
        
        this.currentStep = 0;
        this.isActive = true;
        this.showStep(tutorial[0]);
        document.getElementById('tutorial-overlay').classList.add('active');
        localStorage.setItem('brainbuddy_tutorial_seen', 'true');
    }

    showStep(step) {
        const target = document.querySelector(step.target);
        if (!target) {
            this.nextStep();
            return;
        }
        
        const overlay = document.getElementById('tutorial-overlay');
        const tooltip = overlay.querySelector('.tutorial-tooltip');
        const spotlight = overlay.querySelector('.tutorial-spotlight');
        
        // Update tooltip content
        overlay.querySelector('.tooltip-title').textContent = step.title;
        overlay.querySelector('.tooltip-content').textContent = step.content;
        
        // Position spotlight on target
        const rect = target.getBoundingClientRect();
        spotlight.style.left = (rect.left - 10) + 'px';
        spotlight.style.top = (rect.top - 10) + 'px';
        spotlight.style.width = (rect.width + 20) + 'px';
        spotlight.style.height = (rect.height + 20) + 'px';
        
        // Position tooltip
        this.positionTooltip(tooltip, rect, step.position);
        
        // Update navigation
        this.updateNavigation();
        
        // Highlight target element
        target.classList.add('tutorial-highlight');
        setTimeout(() => target.classList.remove('tutorial-highlight'), 3000);
    }

    positionTooltip(tooltip, targetRect, position) {
        const margin = 20;
        
        switch (position) {
            case 'bottom':
                tooltip.style.left = Math.max(margin, targetRect.left + (targetRect.width / 2) - (tooltip.offsetWidth / 2)) + 'px';
                tooltip.style.top = (targetRect.bottom + margin) + 'px';
                break;
            case 'top':
                tooltip.style.left = Math.max(margin, targetRect.left + (targetRect.width / 2) - (tooltip.offsetWidth / 2)) + 'px';
                tooltip.style.top = (targetRect.top - tooltip.offsetHeight - margin) + 'px';
                break;
            case 'left':
                tooltip.style.left = (targetRect.left - tooltip.offsetWidth - margin) + 'px';
                tooltip.style.top = Math.max(margin, targetRect.top + (targetRect.height / 2) - (tooltip.offsetHeight / 2)) + 'px';
                break;
            case 'right':
                tooltip.style.left = (targetRect.right + margin) + 'px';
                tooltip.style.top = Math.max(margin, targetRect.top + (targetRect.height / 2) - (tooltip.offsetHeight / 2)) + 'px';
                break;
        }
        
        // Ensure tooltip stays within viewport
        const tooltipRect = tooltip.getBoundingClientRect();
        if (tooltipRect.right > window.innerWidth - margin) {
            tooltip.style.left = (window.innerWidth - tooltip.offsetWidth - margin) + 'px';
        }
        if (tooltipRect.bottom > window.innerHeight - margin) {
            tooltip.style.top = (window.innerHeight - tooltip.offsetHeight - margin) + 'px';
        }
        if (tooltipRect.left < margin) {
            tooltip.style.left = margin + 'px';
        }
        if (tooltipRect.top < margin) {
            tooltip.style.top = margin + 'px';
        }
    }

    updateNavigation() {
        const currentPage = this.getCurrentPage();
        const tutorial = this.tutorials[currentPage];
        const overlay = document.getElementById('tutorial-overlay');
        
        const prevBtn = overlay.querySelector('.tutorial-prev');
        const nextBtn = overlay.querySelector('.tutorial-next');
        const progress = overlay.querySelector('.tutorial-progress');
        
        prevBtn.disabled = this.currentStep === 0;
        
        if (this.currentStep === tutorial.length - 1) {
            nextBtn.textContent = 'Finish';
            nextBtn.innerHTML = 'Finish <i class="fas fa-check"></i>';
        } else {
            nextBtn.innerHTML = 'Next <i class="fas fa-arrow-right"></i>';
        }
        
        progress.textContent = `${this.currentStep + 1} / ${tutorial.length}`;
    }

    nextStep() {
        const currentPage = this.getCurrentPage();
        const tutorial = this.tutorials[currentPage];
        
        if (this.currentStep < tutorial.length - 1) {
            this.currentStep++;
            this.showStep(tutorial[this.currentStep]);
        } else {
            this.endTutorial();
        }
    }

    prevStep() {
        const currentPage = this.getCurrentPage();
        const tutorial = this.tutorials[currentPage];
        
        if (this.currentStep > 0) {
            this.currentStep--;
            this.showStep(tutorial[this.currentStep]);
        }
    }

    endTutorial() {
        document.getElementById('tutorial-overlay').classList.remove('active');
        this.isActive = false;
        this.currentStep = 0;
        
        // Show tutorial trigger
        const trigger = document.getElementById('tutorial-trigger');
        trigger.style.display = 'block';
        
        // Add pulse animation for first-time users
        if (!localStorage.getItem('brainbuddy_tutorial_completed')) {
            trigger.classList.add('pulse');
            localStorage.setItem('brainbuddy_tutorial_completed', 'true');
            
            setTimeout(() => {
                trigger.classList.remove('pulse');
            }, 10000);
        }
    }

    showNoTutorialMessage() {
        const message = document.createElement('div');
        message.className = 'tutorial-message';
        message.innerHTML = `
            <div class="message-content">
                <i class="fas fa-info-circle"></i>
                <p>No tutorial available for this page.</p>
            </div>
        `;
        
        const messageStyle = document.createElement('style');
        messageStyle.textContent = `
            .tutorial-message {
                position: fixed;
                top: 20px;
                right: 20px;
                background: #4a90e2;
                color: white;
                padding: 15px 20px;
                border-radius: 8px;
                box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
                z-index: 10000;
                animation: slideIn 0.3s ease;
            }
            
            @keyframes slideIn {
                from { transform: translateX(100%); }
                to { transform: translateX(0); }
            }
            
            .message-content {
                display: flex;
                align-items: center;
                gap: 10px;
            }
            
            .message-content p {
                margin: 0;
            }
        `;
        
        document.head.appendChild(messageStyle);
        document.body.appendChild(message);
        
        setTimeout(() => {
            message.remove();
        }, 3000);
    }
}

// Initialize tutorial system when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.brainBuddyTutorial = new BrainBuddyTutorial();
});