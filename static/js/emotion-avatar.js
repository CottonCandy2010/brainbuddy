/**
 * Emotion Avatar System - Frontend Component
 * Manages dynamic avatar expressions based on student emotions and learning context
 */

class EmotionAvatarManager {
    constructor() {
        this.currentExpression = null;
        this.studentId = 'demo_student';
        this.sessionId = this.generateSessionId();
        this.expressionContainer = null;
        this.messageContainer = null;
        this.animationInterval = null;
        this.isInitialized = false;
        
        this.init();
    }
    
    init() {
        // Wait for DOM to be ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.initializeComponents());
        } else {
            this.initializeComponents();
        }
    }
    
    initializeComponents() {
        this.createAvatarContainer();
        this.loadInitialExpression();
        this.setupEventListeners();
        this.startPeriodicUpdates();
        this.isInitialized = true;
    }
    
    createAvatarContainer() {
        // Create floating avatar container if it doesn't exist
        if (!document.getElementById('emotion-avatar-container')) {
            const avatarContainer = document.createElement('div');
            avatarContainer.id = 'emotion-avatar-container';
            avatarContainer.className = 'emotion-avatar-container';
            avatarContainer.innerHTML = `
                <div class="avatar-display" id="avatar-display">
                    <div class="avatar-face" id="avatar-face">
                        <div class="avatar-eyes" id="avatar-eyes"></div>
                        <div class="avatar-mouth" id="avatar-mouth"></div>
                        <div class="avatar-accessories" id="avatar-accessories"></div>
                    </div>
                    <div class="avatar-effects" id="avatar-effects"></div>
                </div>
                <div class="avatar-message" id="avatar-message" style="display: none;">
                    <div class="message-bubble">
                        <span class="message-text" id="message-text"></span>
                    </div>
                </div>
                <div class="emotion-suggestions" id="emotion-suggestions" style="display: none;"></div>
            `;
            
            document.body.appendChild(avatarContainer);
            this.expressionContainer = document.getElementById('avatar-display');
            this.messageContainer = document.getElementById('avatar-message');
        }
    }
    
    generateSessionId() {
        return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }
    
    async loadInitialExpression() {
        try {
            const response = await fetch(`/api/avatar-expression?student_id=${this.studentId}&session_id=${this.sessionId}`);
            const expressionData = await response.json();
            
            if (expressionData && !expressionData.error) {
                this.updateAvatarExpression(expressionData);
            }
        } catch (error) {
            console.log('Loading default avatar expression');
            this.showDefaultExpression();
        }
    }
    
    async triggerExpressionChange(learningEvent, context = {}) {
        try {
            const requestData = {
                student_id: this.studentId,
                learning_event: learningEvent,
                context: {
                    ...context,
                    session_id: this.sessionId,
                    timestamp: new Date().toISOString()
                }
            };
            
            const response = await fetch('/api/avatar-expression/trigger', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(requestData)
            });
            
            const expressionData = await response.json();
            
            if (expressionData && !expressionData.error) {
                this.updateAvatarExpression(expressionData);
                
                // Show message if present
                if (expressionData.message) {
                    this.showMessage(expressionData.message, expressionData.message_duration || 3000);
                }
            }
        } catch (error) {
            console.log('Avatar expression update unavailable');
        }
    }
    
    async triggerCelebration(achievementType) {
        try {
            const response = await fetch('/api/avatar-expression/celebration', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    achievement_type: achievementType
                })
            });
            
            const celebrationData = await response.json();
            
            if (celebrationData && !celebrationData.error) {
                this.showCelebration(celebrationData);
            }
        } catch (error) {
            console.log('Celebration display unavailable');
        }
    }
    
    updateAvatarExpression(expressionData) {
        if (!this.expressionContainer) return;
        
        this.currentExpression = expressionData;
        const expression = expressionData.expression;
        
        // Update avatar visual elements
        this.updateAvatarFace(expression);
        this.updateAvatarEffects(expression);
        this.updateAvatarAnimation(expression);
        this.updateAvatarColors(expression);
        
        // Update theme-based background
        if (expressionData.theme) {
            this.updateThemeBackground(expressionData.theme);
        }
    }
    
    updateAvatarFace(expression) {
        const faceElement = document.getElementById('avatar-face');
        const eyesElement = document.getElementById('avatar-eyes');
        const mouthElement = document.getElementById('avatar-mouth');
        const accessoriesElement = document.getElementById('avatar-accessories');
        
        if (!faceElement) return;
        
        // Update facial expression classes
        faceElement.className = `avatar-face expression-${expression.facial_expression}`;
        
        // Update eyes
        if (eyesElement) {
            eyesElement.className = `avatar-eyes eyes-${expression.eyes}`;
        }
        
        // Update mouth
        if (mouthElement) {
            mouthElement.className = `avatar-mouth mouth-${expression.facial_expression}`;
        }
        
        // Update accessories
        if (accessoriesElement && expression.accessories) {
            accessoriesElement.innerHTML = '';
            expression.accessories.forEach(accessory => {
                const accessoryDiv = document.createElement('div');
                accessoryDiv.className = `accessory accessory-${accessory}`;
                accessoriesElement.appendChild(accessoryDiv);
            });
        }
    }
    
    updateAvatarEffects(expression) {
        const effectsElement = document.getElementById('avatar-effects');
        if (!effectsElement) return;
        
        effectsElement.innerHTML = '';
        
        // Add regular effects
        if (expression.accessories) {
            expression.accessories.forEach(effect => {
                const effectDiv = document.createElement('div');
                effectDiv.className = `effect effect-${effect}`;
                effectsElement.appendChild(effectDiv);
            });
        }
        
        // Add special celebration effects
        if (expression.special_effects) {
            expression.special_effects.forEach(effect => {
                const effectDiv = document.createElement('div');
                effectDiv.className = `special-effect effect-${effect}`;
                effectsElement.appendChild(effectDiv);
            });
        }
        
        // Add background effects
        if (expression.background_effects) {
            expression.background_effects.forEach(effect => {
                const effectDiv = document.createElement('div');
                effectDiv.className = `background-effect effect-${effect}`;
                effectsElement.appendChild(effectDiv);
            });
        }
    }
    
    updateAvatarAnimation(expression) {
        if (!this.expressionContainer) return;
        
        // Remove existing animation classes
        this.expressionContainer.classList.remove(
            'anim-bounce', 'anim-jump', 'anim-steady', 'anim-lean-forward',
            'anim-head-tilt', 'anim-gentle-sway', 'anim-chest-out', 
            'anim-slow-blink', 'anim-power-stance', 'anim-wiggle',
            'anim-celebration-dance', 'anim-reveal-unlock', 'anim-perfect-spin', 'anim-power-surge'
        );
        
        // Add new animation class
        if (expression.animation) {
            this.expressionContainer.classList.add(`anim-${expression.animation}`);
        }
    }
    
    updateAvatarColors(expression) {
        if (!expression.colors || !this.expressionContainer) return;
        
        // Apply color theme to avatar
        const colorVars = {
            '--avatar-primary': expression.colors[0] || '#FFD700',
            '--avatar-secondary': expression.colors[1] || '#FF69B4',
            '--avatar-accent': expression.colors[2] || '#00BFFF'
        };
        
        Object.entries(colorVars).forEach(([property, value]) => {
            this.expressionContainer.style.setProperty(property, value);
        });
    }
    
    updateThemeBackground(theme) {
        const container = document.getElementById('emotion-avatar-container');
        if (!container) return;
        
        // Remove existing theme classes
        container.classList.remove('theme-sunrise', 'theme-study-room', 'theme-cozy-room', 'theme-playground');
        
        // Add new theme class
        if (theme.background) {
            container.classList.add(`theme-${theme.background}`);
        }
    }
    
    showMessage(message, duration = 3000) {
        if (!this.messageContainer) return;
        
        const messageText = document.getElementById('message-text');
        if (messageText) {
            messageText.textContent = message;
        }
        
        this.messageContainer.style.display = 'block';
        this.messageContainer.classList.add('message-show');
        
        setTimeout(() => {
            this.hideMessage();
        }, duration);
    }
    
    hideMessage() {
        if (!this.messageContainer) return;
        
        this.messageContainer.classList.remove('message-show');
        setTimeout(() => {
            this.messageContainer.style.display = 'none';
        }, 300);
    }
    
    showCelebration(celebrationData) {
        // Trigger special celebration expression
        this.updateAvatarExpression(celebrationData);
        
        // Show celebration message
        if (celebrationData.message) {
            this.showMessage(celebrationData.message, celebrationData.duration || 4000);
        }
        
        // Add celebration overlay effects
        this.addCelebrationOverlay(celebrationData.achievement);
    }
    
    addCelebrationOverlay(achievementType) {
        const overlay = document.createElement('div');
        overlay.className = `celebration-overlay celebration-${achievementType}`;
        overlay.innerHTML = `
            <div class="celebration-particles"></div>
            <div class="celebration-text">${this.getCelebrationText(achievementType)}</div>
        `;
        
        document.body.appendChild(overlay);
        
        setTimeout(() => {
            overlay.remove();
        }, 5000);
    }
    
    getCelebrationText(achievementType) {
        const celebrations = {
            'quest_complete': 'Quest Completed! 🎉',
            'avatar_unlock': 'New Avatar Unlocked! ⭐',
            'perfect_score': 'Perfect Score! 🌟',
            'streak_milestone': 'Amazing Streak! 🔥'
        };
        
        return celebrations[achievementType] || 'Great Achievement! 🎊';
    }
    
    async loadEmotionSuggestions() {
        try {
            const response = await fetch(`/api/emotion-suggestions?student_id=${this.studentId}`);
            const data = await response.json();
            
            if (data.suggestions && data.suggestions.length > 0) {
                this.showEmotionSuggestions(data.suggestions);
            }
        } catch (error) {
            console.log('Emotion suggestions unavailable');
        }
    }
    
    showEmotionSuggestions(suggestions) {
        const suggestionsContainer = document.getElementById('emotion-suggestions');
        if (!suggestionsContainer) return;
        
        suggestionsContainer.innerHTML = '';
        
        suggestions.forEach(suggestion => {
            const suggestionDiv = document.createElement('div');
            suggestionDiv.className = 'suggestion-item';
            suggestionDiv.innerHTML = `
                <button class="suggestion-btn" data-action="${suggestion.action}">
                    ${suggestion.message}
                </button>
            `;
            suggestionsContainer.appendChild(suggestionDiv);
        });
        
        suggestionsContainer.style.display = 'block';
    }
    
    setupEventListeners() {
        // Listen for learning events
        document.addEventListener('brainbuddy:lesson-start', (e) => {
            this.triggerExpressionChange('lesson_start', { subject: e.detail.subject });
        });
        
        document.addEventListener('brainbuddy:correct-answer', () => {
            this.triggerExpressionChange('correct_answer');
        });
        
        document.addEventListener('brainbuddy:incorrect-answer', () => {
            this.triggerExpressionChange('incorrect_answer');
        });
        
        document.addEventListener('brainbuddy:lesson-complete', () => {
            this.triggerExpressionChange('lesson_complete');
        });
        
        document.addEventListener('brainbuddy:quest-complete', (e) => {
            this.triggerCelebration('quest_complete');
        });
        
        document.addEventListener('brainbuddy:avatar-unlock', () => {
            this.triggerCelebration('avatar_unlock');
        });
        
        document.addEventListener('brainbuddy:perfect-score', () => {
            this.triggerCelebration('perfect_score');
        });
        
        // Listen for suggestion clicks
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('suggestion-btn')) {
                const action = e.target.dataset.action;
                this.handleSuggestionClick(action);
            }
        });
    }
    
    handleSuggestionClick(action) {
        switch (action) {
            case 'take_break':
                this.triggerExpressionChange('taking_break');
                break;
            case 'easier_question':
                // Trigger easier difficulty
                document.dispatchEvent(new CustomEvent('brainbuddy:request-easier'));
                break;
            case 'hint':
                // Show hint
                document.dispatchEvent(new CustomEvent('brainbuddy:request-hint'));
                break;
        }
        
        // Hide suggestions after click
        const suggestionsContainer = document.getElementById('emotion-suggestions');
        if (suggestionsContainer) {
            suggestionsContainer.style.display = 'none';
        }
    }
    
    startPeriodicUpdates() {
        // Update avatar expression every 30 seconds
        setInterval(() => {
            this.loadInitialExpression();
        }, 30000);
        
        // Check for emotion suggestions every 2 minutes
        setInterval(() => {
            this.loadEmotionSuggestions();
        }, 120000);
    }
    
    showDefaultExpression() {
        if (!this.expressionContainer) return;
        
        this.expressionContainer.className = 'avatar-display default-expression';
        
        const defaultExpression = {
            facial_expression: 'smile',
            eyes: 'bright',
            accessories: ['sparkles'],
            animation: 'bounce',
            colors: ['#FFD700', '#FF69B4', '#00BFFF']
        };
        
        this.updateAvatarFace(defaultExpression);
        this.updateAvatarAnimation(defaultExpression);
        this.updateAvatarColors(defaultExpression);
    }
    
    // Public methods for external integration
    triggerEvent(eventType, context = {}) {
        if (!this.isInitialized) {
            setTimeout(() => this.triggerEvent(eventType, context), 100);
            return;
        }
        
        this.triggerExpressionChange(eventType, context);
    }
    
    celebrate(achievementType) {
        if (!this.isInitialized) {
            setTimeout(() => this.celebrate(achievementType), 100);
            return;
        }
        
        this.triggerCelebration(achievementType);
    }
    
    setStudentId(studentId) {
        this.studentId = studentId;
    }
}

// Global avatar manager instance
let avatarManager;

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    avatarManager = new EmotionAvatarManager();
    
    // Make it globally accessible
    window.BrainBuddyAvatar = avatarManager;
});

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = EmotionAvatarManager;
}