"""
Adaptive Difficulty Transition Animations System for Brain Buddy
Creates smooth visual transitions when difficulty levels change
"""

import json
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

class AdaptiveDifficultyAnimations:
    """
    Manages smooth visual transitions when student difficulty levels change
    """
    
    ANIMATION_TYPES = {
        'level_up': {
            'name': 'Level Up',
            'duration': 2000,  # milliseconds
            'effects': ['sparkle', 'scale_up', 'glow'],
            'colors': ['#4caf50', '#8bc34a', '#ffeb3b'],
            'sound': 'success_chime'
        },
        'level_down': {
            'name': 'Gentle Support',
            'duration': 1500,
            'effects': ['fade', 'gentle_bounce', 'warm_glow'],
            'colors': ['#ff9800', '#ffc107', '#ffeb3b'],
            'sound': 'gentle_chime'
        },
        'mastery_unlock': {
            'name': 'Mastery Achieved',
            'duration': 3000,
            'effects': ['fireworks', 'rainbow', 'celebration'],
            'colors': ['#e91e63', '#9c27b0', '#673ab7', '#3f51b5'],
            'sound': 'celebration_fanfare'
        },
        'skill_unlock': {
            'name': 'New Skill Unlocked',
            'duration': 2500,
            'effects': ['unlock_animation', 'sparkle_trail', 'glow_pulse'],
            'colors': ['#00bcd4', '#4caf50', '#ffeb3b'],
            'sound': 'unlock_chime'
        },
        'gentle_encouragement': {
            'name': 'Keep Going',
            'duration': 1200,
            'effects': ['pulse', 'warm_glow', 'gentle_bounce'],
            'colors': ['#ff9800', '#ffc107'],
            'sound': 'encouraging_tone'
        }
    }
    
    DIFFICULTY_TRANSITIONS = {
        'beginner_to_easy': {
            'animation': 'level_up',
            'message': "Amazing progress! You're ready for more challenges!",
            'icon': '🌟',
            'badge': 'Rising Star'
        },
        'easy_to_medium': {
            'animation': 'level_up',
            'message': "Fantastic! You're becoming a real expert!",
            'icon': '🚀',
            'badge': 'Smart Learner'
        },
        'medium_to_hard': {
            'animation': 'skill_unlock',
            'message': "Incredible! You've unlocked advanced challenges!",
            'icon': '⭐',
            'badge': 'Challenge Master'
        },
        'hard_to_expert': {
            'animation': 'mastery_unlock',
            'message': "Outstanding! You've achieved expert level!",
            'icon': '🏆',
            'badge': 'Expert Scholar'
        },
        'expert_to_hard': {
            'animation': 'gentle_encouragement',
            'message': "Taking a step back helps strengthen your skills!",
            'icon': '💪',
            'badge': 'Steady Learner'
        },
        'hard_to_medium': {
            'animation': 'gentle_encouragement',
            'message': "Perfect! Let's build confidence at this level!",
            'icon': '🎯',
            'badge': 'Focused Learner'
        },
        'medium_to_easy': {
            'animation': 'gentle_encouragement',
            'message': "Great choice! Mastering basics makes you stronger!",
            'icon': '🌱',
            'badge': 'Foundation Builder'
        },
        'easy_to_beginner': {
            'animation': 'gentle_encouragement',
            'message': "Let's practice more and build your confidence!",
            'icon': '🤗',
            'badge': 'Persistent Learner'
        }
    }
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def generate_transition_animation(self, old_level: str, new_level: str, 
                                    student_performance: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate animation data for difficulty level transition
        
        Args:
            old_level: Previous difficulty level
            new_level: New difficulty level
            student_performance: Current student performance metrics
            
        Returns:
            Animation configuration dictionary
        """
        transition_key = f"{old_level}_to_{new_level}"
        
        # Get transition config or use default
        transition_config = self.DIFFICULTY_TRANSITIONS.get(
            transition_key, 
            self._get_default_transition(old_level, new_level)
        )
        
        animation_type = transition_config['animation']
        animation_config = self.ANIMATION_TYPES[animation_type]
        
        # Generate personalized animation
        return {
            'id': f"difficulty_transition_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'type': animation_type,
            'transition': transition_key,
            'old_level': old_level,
            'new_level': new_level,
            'duration': animation_config['duration'],
            'effects': animation_config['effects'],
            'colors': animation_config['colors'],
            'sound': animation_config['sound'],
            'message': transition_config['message'],
            'icon': transition_config['icon'],
            'badge': transition_config['badge'],
            'performance_context': {
                'accuracy': student_performance.get('average_accuracy', 0),
                'completion_rate': student_performance.get('completion_rate', 0),
                'lessons_completed': student_performance.get('lessons_completed', 0),
                'time_spent': student_performance.get('time_spent', 0)
            },
            'animation_sequence': self._generate_animation_sequence(animation_type, transition_config),
            'css_classes': self._generate_css_classes(animation_type),
            'javascript_functions': self._generate_javascript_functions(animation_type)
        }
    
    def _get_default_transition(self, old_level: str, new_level: str) -> Dict[str, Any]:
        """Generate default transition when specific transition not found"""
        level_order = ['beginner', 'easy', 'medium', 'hard', 'expert']
        
        try:
            old_index = level_order.index(old_level)
            new_index = level_order.index(new_level)
            
            if new_index > old_index:
                # Level up
                return {
                    'animation': 'level_up',
                    'message': f"Great progress! Moving from {old_level} to {new_level}!",
                    'icon': '🌟',
                    'badge': 'Progress Maker'
                }
            else:
                # Level down or same
                return {
                    'animation': 'gentle_encouragement',
                    'message': f"Perfect! Let's strengthen your skills at {new_level} level!",
                    'icon': '💪',
                    'badge': 'Steady Learner'
                }
        except ValueError:
            return {
                'animation': 'gentle_encouragement',
                'message': "Keep learning and growing!",
                'icon': '📚',
                'badge': 'Dedicated Learner'
            }
    
    def _generate_animation_sequence(self, animation_type: str, transition_config: Dict) -> List[Dict]:
        """Generate step-by-step animation sequence"""
        
        sequences = {
            'level_up': [
                {'step': 1, 'delay': 0, 'action': 'show_message', 'data': transition_config['message']},
                {'step': 2, 'delay': 500, 'action': 'sparkle_effect', 'data': 'multiple_sparkles'},
                {'step': 3, 'delay': 1000, 'action': 'scale_animation', 'data': 'scale_up_bounce'},
                {'step': 4, 'delay': 1500, 'action': 'show_badge', 'data': transition_config['badge']},
                {'step': 5, 'delay': 2000, 'action': 'fade_out', 'data': 'gentle_fade'}
            ],
            'level_down': [
                {'step': 1, 'delay': 0, 'action': 'show_message', 'data': transition_config['message']},
                {'step': 2, 'delay': 300, 'action': 'warm_glow', 'data': 'gentle_glow'},
                {'step': 3, 'delay': 800, 'action': 'bounce_effect', 'data': 'gentle_bounce'},
                {'step': 4, 'delay': 1200, 'action': 'show_badge', 'data': transition_config['badge']},
                {'step': 5, 'delay': 1500, 'action': 'fade_out', 'data': 'gentle_fade'}
            ],
            'mastery_unlock': [
                {'step': 1, 'delay': 0, 'action': 'show_message', 'data': transition_config['message']},
                {'step': 2, 'delay': 300, 'action': 'fireworks', 'data': 'celebration_fireworks'},
                {'step': 3, 'delay': 800, 'action': 'rainbow_effect', 'data': 'rainbow_colors'},
                {'step': 4, 'delay': 1500, 'action': 'trophy_animation', 'data': 'golden_trophy'},
                {'step': 5, 'delay': 2000, 'action': 'show_badge', 'data': transition_config['badge']},
                {'step': 6, 'delay': 2500, 'action': 'confetti', 'data': 'celebration_confetti'},
                {'step': 7, 'delay': 3000, 'action': 'fade_out', 'data': 'gentle_fade'}
            ],
            'skill_unlock': [
                {'step': 1, 'delay': 0, 'action': 'show_message', 'data': transition_config['message']},
                {'step': 2, 'delay': 400, 'action': 'unlock_animation', 'data': 'key_unlock'},
                {'step': 3, 'delay': 1000, 'action': 'sparkle_trail', 'data': 'trailing_sparkles'},
                {'step': 4, 'delay': 1800, 'action': 'glow_pulse', 'data': 'pulsing_glow'},
                {'step': 5, 'delay': 2200, 'action': 'show_badge', 'data': transition_config['badge']},
                {'step': 6, 'delay': 2500, 'action': 'fade_out', 'data': 'gentle_fade'}
            ],
            'gentle_encouragement': [
                {'step': 1, 'delay': 0, 'action': 'show_message', 'data': transition_config['message']},
                {'step': 2, 'delay': 200, 'action': 'pulse_effect', 'data': 'gentle_pulse'},
                {'step': 3, 'delay': 600, 'action': 'warm_glow', 'data': 'encouraging_glow'},
                {'step': 4, 'delay': 1000, 'action': 'show_badge', 'data': transition_config['badge']},
                {'step': 5, 'delay': 1200, 'action': 'fade_out', 'data': 'gentle_fade'}
            ]
        }
        
        return sequences.get(animation_type, sequences['gentle_encouragement'])
    
    def _generate_css_classes(self, animation_type: str) -> List[str]:
        """Generate CSS classes for animation"""
        base_classes = ['adaptive-difficulty-animation', 'animated']
        
        type_classes = {
            'level_up': ['level-up-animation', 'sparkle-effect', 'scale-animation'],
            'level_down': ['level-down-animation', 'gentle-fade', 'warm-glow'],
            'mastery_unlock': ['mastery-animation', 'fireworks-effect', 'rainbow-effect'],
            'skill_unlock': ['skill-unlock-animation', 'unlock-effect', 'sparkle-trail'],
            'gentle_encouragement': ['encouragement-animation', 'pulse-effect', 'warm-glow']
        }
        
        return base_classes + type_classes.get(animation_type, [])
    
    def _generate_javascript_functions(self, animation_type: str) -> List[str]:
        """Generate JavaScript function names for animation"""
        return [
            'initializeAdaptiveDifficultyAnimation',
            'startAnimationSequence',
            'playAnimationStep',
            'cleanupAnimation',
            f'play{animation_type.replace("_", "").title()}Animation'
        ]
    
    def generate_css_styles(self) -> str:
        """Generate CSS styles for difficulty transition animations"""
        return """
/* Adaptive Difficulty Transition Animations */
.adaptive-difficulty-animation {
    position: fixed;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    z-index: 10000;
    max-width: 90vw;
    max-height: 90vh;
    pointer-events: none;
}

.difficulty-transition-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.3);
    z-index: 9999;
    display: flex;
    align-items: center;
    justify-content: center;
    animation: fadeIn 0.3s ease-out;
}

.difficulty-message-container {
    background: white;
    padding: 30px;
    border-radius: 20px;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
    text-align: center;
    max-width: 400px;
    position: relative;
    overflow: hidden;
}

.difficulty-icon {
    font-size: 3rem;
    margin-bottom: 15px;
    display: block;
}

.difficulty-message {
    font-size: 1.2rem;
    font-weight: bold;
    color: #333;
    margin-bottom: 20px;
    line-height: 1.4;
}

.difficulty-badge {
    background: linear-gradient(135deg, #ff6b6b, #ffd93d);
    color: white;
    padding: 8px 20px;
    border-radius: 25px;
    font-size: 0.9rem;
    font-weight: bold;
    display: inline-block;
    margin-top: 10px;
}

/* Level Up Animation */
@keyframes levelUpSparkle {
    0% { opacity: 0; transform: scale(0) rotate(0deg); }
    50% { opacity: 1; transform: scale(1.2) rotate(180deg); }
    100% { opacity: 0; transform: scale(0) rotate(360deg); }
}

@keyframes levelUpScale {
    0% { transform: scale(1); }
    50% { transform: scale(1.1); }
    100% { transform: scale(1); }
}

@keyframes levelUpGlow {
    0% { box-shadow: 0 0 5px rgba(76, 175, 80, 0.3); }
    50% { box-shadow: 0 0 20px rgba(76, 175, 80, 0.6); }
    100% { box-shadow: 0 0 5px rgba(76, 175, 80, 0.3); }
}

.level-up-animation {
    animation: levelUpScale 2s ease-in-out;
}

.level-up-animation::before {
    content: '';
    position: absolute;
    top: -5px;
    left: -5px;
    right: -5px;
    bottom: -5px;
    background: linear-gradient(45deg, #4caf50, #8bc34a, #ffeb3b);
    border-radius: 25px;
    z-index: -1;
    animation: levelUpGlow 2s ease-in-out;
}

/* Sparkle Effect */
.sparkle-effect {
    position: relative;
}

.sparkle-effect::after {
    content: '✨';
    position: absolute;
    top: 10%;
    left: 10%;
    font-size: 1.5rem;
    animation: levelUpSparkle 1s ease-in-out infinite;
}

/* Mastery Animation */
@keyframes masteryFireworks {
    0% { opacity: 0; transform: translateY(0) scale(0); }
    50% { opacity: 1; transform: translateY(-30px) scale(1.2); }
    100% { opacity: 0; transform: translateY(-60px) scale(0); }
}

@keyframes masteryRainbow {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

.mastery-animation {
    background: linear-gradient(45deg, #e91e63, #9c27b0, #673ab7, #3f51b5);
    background-size: 300% 300%;
    animation: masteryRainbow 3s ease-in-out;
}

.fireworks-effect::before {
    content: '🎆';
    position: absolute;
    top: 0;
    left: 50%;
    transform: translateX(-50%);
    font-size: 2rem;
    animation: masteryFireworks 2s ease-in-out;
}

/* Gentle Encouragement */
@keyframes gentlePulse {
    0% { transform: scale(1); opacity: 0.8; }
    50% { transform: scale(1.05); opacity: 1; }
    100% { transform: scale(1); opacity: 0.8; }
}

@keyframes warmGlow {
    0% { box-shadow: 0 0 10px rgba(255, 152, 0, 0.3); }
    50% { box-shadow: 0 0 25px rgba(255, 152, 0, 0.6); }
    100% { box-shadow: 0 0 10px rgba(255, 152, 0, 0.3); }
}

.encouragement-animation {
    animation: gentlePulse 1.5s ease-in-out;
}

.warm-glow {
    animation: warmGlow 2s ease-in-out;
}

/* Skill Unlock Animation */
@keyframes unlockKey {
    0% { transform: rotate(0deg); }
    25% { transform: rotate(-10deg); }
    50% { transform: rotate(10deg); }
    75% { transform: rotate(-5deg); }
    100% { transform: rotate(0deg); }
}

.skill-unlock-animation::before {
    content: '🔓';
    position: absolute;
    top: -30px;
    left: 50%;
    transform: translateX(-50%);
    font-size: 2rem;
    animation: unlockKey 2s ease-in-out;
}

/* Fade animations */
@keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
}

@keyframes fadeOut {
    from { opacity: 1; }
    to { opacity: 0; }
}

.fade-in {
    animation: fadeIn 0.5s ease-out;
}

.fade-out {
    animation: fadeOut 0.5s ease-out;
}

/* Responsive Design */
@media (max-width: 768px) {
    .difficulty-message-container {
        padding: 20px;
        max-width: 320px;
    }
    
    .difficulty-icon {
        font-size: 2.5rem;
    }
    
    .difficulty-message {
        font-size: 1rem;
    }
    
    .difficulty-badge {
        font-size: 0.8rem;
        padding: 6px 16px;
    }
}
"""
    
    def generate_javascript_functions(self) -> str:
        """Generate JavaScript functions for difficulty transition animations"""
        return """
// Adaptive Difficulty Transition Animations JavaScript

class AdaptiveDifficultyAnimations {
    constructor() {
        this.currentAnimation = null;
        this.animationQueue = [];
        this.isAnimating = false;
    }

    // Initialize animation system
    init() {
        this.injectCSS();
        this.setupEventListeners();
        console.log('Adaptive Difficulty Animations initialized');
    }

    // Inject CSS styles
    injectCSS() {
        const styleId = 'adaptive-difficulty-animations-css';
        if (!document.getElementById(styleId)) {
            const style = document.createElement('style');
            style.id = styleId;
            style.textContent = `""" + self.generate_css_styles() + """`;
            document.head.appendChild(style);
        }
    }

    // Setup event listeners
    setupEventListeners() {
        // Listen for difficulty change events
        document.addEventListener('difficultyLevelChanged', (event) => {
            this.handleDifficultyChange(event.detail);
        });

        // Listen for animation cleanup
        document.addEventListener('animationend', (event) => {
            if (event.target.classList.contains('adaptive-difficulty-animation')) {
                this.cleanupAnimation();
            }
        });
    }

    // Handle difficulty level changes
    handleDifficultyChange(difficultyData) {
        if (this.isAnimating) {
            this.animationQueue.push(difficultyData);
            return;
        }

        this.startTransitionAnimation(difficultyData);
    }

    // Start transition animation
    startTransitionAnimation(animationData) {
        this.isAnimating = true;
        this.currentAnimation = animationData;

        // Create animation overlay
        const overlay = this.createAnimationOverlay(animationData);
        document.body.appendChild(overlay);

        // Start animation sequence
        this.playAnimationSequence(animationData, overlay);

        // Play sound effect
        this.playAudioEffect(animationData.sound);
    }

    // Create animation overlay
    createAnimationOverlay(animationData) {
        const overlay = document.createElement('div');
        overlay.className = 'difficulty-transition-overlay fade-in';
        overlay.innerHTML = `
            <div class="difficulty-message-container ${animationData.css_classes.join(' ')}">
                <span class="difficulty-icon">${animationData.icon}</span>
                <div class="difficulty-message">${animationData.message}</div>
                <div class="difficulty-badge">${animationData.badge}</div>
            </div>
        `;
        return overlay;
    }

    // Play animation sequence
    playAnimationSequence(animationData, overlay) {
        const sequence = animationData.animation_sequence;
        let currentStep = 0;

        const playNextStep = () => {
            if (currentStep >= sequence.length) {
                this.finishAnimation(overlay);
                return;
            }

            const step = sequence[currentStep];
            setTimeout(() => {
                this.executeAnimationStep(step, overlay);
                currentStep++;
                playNextStep();
            }, step.delay);
        };

        playNextStep();
    }

    // Execute individual animation step
    executeAnimationStep(step, overlay) {
        const container = overlay.querySelector('.difficulty-message-container');
        
        switch (step.action) {
            case 'show_message':
                container.style.opacity = '1';
                break;
            case 'sparkle_effect':
                this.addSparkleEffect(container);
                break;
            case 'scale_animation':
                container.classList.add('level-up-animation');
                break;
            case 'warm_glow':
                container.classList.add('warm-glow');
                break;
            case 'bounce_effect':
                container.style.animation = 'gentlePulse 0.6s ease-in-out';
                break;
            case 'fireworks':
                this.addFireworksEffect(container);
                break;
            case 'rainbow_effect':
                container.classList.add('mastery-animation');
                break;
            case 'unlock_animation':
                container.classList.add('skill-unlock-animation');
                break;
            case 'pulse_effect':
                container.classList.add('encouragement-animation');
                break;
            case 'fade_out':
                overlay.classList.add('fade-out');
                break;
        }
    }

    // Add sparkle effect
    addSparkleEffect(container) {
        const sparkles = ['✨', '⭐', '🌟', '💫'];
        for (let i = 0; i < 6; i++) {
            const sparkle = document.createElement('div');
            sparkle.textContent = sparkles[Math.floor(Math.random() * sparkles.length)];
            sparkle.style.position = 'absolute';
            sparkle.style.fontSize = '1.5rem';
            sparkle.style.left = Math.random() * 100 + '%';
            sparkle.style.top = Math.random() * 100 + '%';
            sparkle.style.animation = 'levelUpSparkle 1s ease-in-out';
            sparkle.style.pointerEvents = 'none';
            container.appendChild(sparkle);

            setTimeout(() => sparkle.remove(), 1000);
        }
    }

    // Add fireworks effect
    addFireworksEffect(container) {
        const fireworks = ['🎆', '🎇', '✨', '🎊'];
        for (let i = 0; i < 4; i++) {
            const firework = document.createElement('div');
            firework.textContent = fireworks[Math.floor(Math.random() * fireworks.length)];
            firework.style.position = 'absolute';
            firework.style.fontSize = '2rem';
            firework.style.left = Math.random() * 100 + '%';
            firework.style.top = Math.random() * 50 + '%';
            firework.style.animation = 'masteryFireworks 2s ease-in-out';
            firework.style.pointerEvents = 'none';
            container.appendChild(firework);

            setTimeout(() => firework.remove(), 2000);
        }
    }

    // Play audio effect
    playAudioEffect(soundType) {
        // Use Web Audio API or simple audio
        try {
            const audio = new Audio();
            const soundMap = {
                'success_chime': 'data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEA...',
                'gentle_chime': 'data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEA...',
                'celebration_fanfare': 'data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEA...',
                'unlock_chime': 'data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEA...',
                'encouraging_tone': 'data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEA...'
            };

            // For now, use a simple beep or leave silent
            console.log(`Playing audio effect: ${soundType}`);
        } catch (error) {
            console.warn('Audio playback not supported:', error);
        }
    }

    // Finish animation
    finishAnimation(overlay) {
        setTimeout(() => {
            overlay.remove();
            this.isAnimating = false;
            this.currentAnimation = null;

            // Process next animation in queue
            if (this.animationQueue.length > 0) {
                const nextAnimation = this.animationQueue.shift();
                this.startTransitionAnimation(nextAnimation);
            }
        }, 500);
    }

    // Cleanup animation
    cleanupAnimation() {
        const overlays = document.querySelectorAll('.difficulty-transition-overlay');
        overlays.forEach(overlay => overlay.remove());
        this.isAnimating = false;
        this.currentAnimation = null;
    }

    // Trigger difficulty level change
    triggerDifficultyChange(oldLevel, newLevel, performanceData) {
        const event = new CustomEvent('difficultyLevelChanged', {
            detail: {
                oldLevel,
                newLevel,
                performanceData,
                timestamp: new Date().toISOString()
            }
        });
        document.dispatchEvent(event);
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.adaptiveDifficultyAnimations = new AdaptiveDifficultyAnimations();
    window.adaptiveDifficultyAnimations.init();
});

// Expose global functions
window.triggerDifficultyChange = (oldLevel, newLevel, performanceData) => {
    if (window.adaptiveDifficultyAnimations) {
        window.adaptiveDifficultyAnimations.triggerDifficultyChange(oldLevel, newLevel, performanceData);
    }
};
"""
    
    def integrate_with_adaptive_difficulty(self, adaptive_engine) -> str:
        """
        Generate integration code for adaptive difficulty engine
        
        Args:
            adaptive_engine: Instance of AdaptiveDifficultyEngine
            
        Returns:
            Integration JavaScript code
        """
        return f"""
// Integration with Adaptive Difficulty Engine
class AdaptiveDifficultyIntegration {{
    constructor() {{
        this.currentLevel = 'easy';
        this.animations = window.adaptiveDifficultyAnimations;
    }}

    // Monitor performance and trigger animations
    onPerformanceUpdate(studentId, performanceData) {{
        const newLevel = this.calculateNewDifficultyLevel(performanceData);
        
        if (newLevel !== this.currentLevel) {{
            this.triggerLevelChange(this.currentLevel, newLevel, performanceData);
            this.currentLevel = newLevel;
        }}
    }}

    // Calculate new difficulty level
    calculateNewDifficultyLevel(performanceData) {{
        const accuracy = performanceData.accuracy || 0;
        const completionRate = performanceData.completionRate || 0;
        const timeEfficiency = performanceData.timeEfficiency || 0;
        
        // Simple level calculation
        const score = (accuracy * 0.5) + (completionRate * 0.3) + (timeEfficiency * 0.2);
        
        if (score >= 90) return 'expert';
        if (score >= 75) return 'hard';
        if (score >= 60) return 'medium';
        if (score >= 45) return 'easy';
        return 'beginner';
    }}

    // Trigger level change with animation
    triggerLevelChange(oldLevel, newLevel, performanceData) {{
        if (this.animations) {{
            this.animations.triggerDifficultyChange(oldLevel, newLevel, performanceData);
        }}
        
        // Update UI elements
        this.updateDifficultyIndicators(newLevel);
        this.logDifficultyChange(oldLevel, newLevel, performanceData);
    }}

    // Update difficulty indicators in UI
    updateDifficultyIndicators(newLevel) {{
        const indicators = document.querySelectorAll('.difficulty-indicator');
        indicators.forEach(indicator => {{
            indicator.textContent = newLevel.charAt(0).toUpperCase() + newLevel.slice(1);
            indicator.className = `difficulty-indicator difficulty-${{newLevel}}`;
        }});
    }}

    // Log difficulty changes
    logDifficultyChange(oldLevel, newLevel, performanceData) {{
        const logData = {{
            timestamp: new Date().toISOString(),
            transition: `${{oldLevel}}_to_${{newLevel}}`,
            performance: performanceData,
            studentId: performanceData.studentId || 'unknown'
        }};
        
        console.log('Difficulty level changed:', logData);
        
        // Send to analytics if available
        if (window.analytics) {{
            window.analytics.track('difficulty_level_changed', logData);
        }}
    }}
}}

// Initialize integration
document.addEventListener('DOMContentLoaded', () => {{
    window.adaptiveDifficultyIntegration = new AdaptiveDifficultyIntegration();
}});
"""