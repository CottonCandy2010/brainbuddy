"""
Emotion and Mood Avatar Expression System for Brain Buddy
Dynamically changes avatar expressions based on student emotions and learning states
"""

import random
from datetime import datetime, timedelta
from typing import Dict, List, Any
from firebase_config import get_firestore_client

class EmotionAvatarSystem:
    """Manages dynamic avatar expressions based on student emotions and moods"""
    
    # Avatar expressions for different emotions
    AVATAR_EXPRESSIONS = {
        'happy': {
            'facial_expression': 'smile',
            'eyes': 'bright',
            'accessories': ['confetti', 'sparkles'],
            'animation': 'bounce',
            'colors': ['#FFD700', '#FF69B4', '#00BFFF'],
            'description': 'Happy and cheerful!'
        },
        'excited': {
            'facial_expression': 'wide_smile',
            'eyes': 'sparkling',
            'accessories': ['stars', 'fireworks'],
            'animation': 'jump',
            'colors': ['#FF4500', '#FFD700', '#32CD32'],
            'description': 'Super excited to learn!'
        },
        'focused': {
            'facial_expression': 'determined',
            'eyes': 'concentrated',
            'accessories': ['glasses', 'book'],
            'animation': 'steady',
            'colors': ['#4169E1', '#8A2BE2', '#2E8B57'],
            'description': 'Focused and ready!'
        },
        'curious': {
            'facial_expression': 'interested',
            'eyes': 'wide',
            'accessories': ['magnifying_glass', 'question_mark'],
            'animation': 'lean_forward',
            'colors': ['#FF6347', '#20B2AA', '#FFB6C1'],
            'description': 'Curious to discover!'
        },
        'confused': {
            'facial_expression': 'puzzled',
            'eyes': 'squinting',
            'accessories': ['thinking_bubble', 'scratch_head'],
            'animation': 'head_tilt',
            'colors': ['#DDA0DD', '#F0E68C', '#87CEEB'],
            'description': 'Thinking it through...'
        },
        'frustrated': {
            'facial_expression': 'frown',
            'eyes': 'concerned',
            'accessories': ['storm_cloud', 'helping_hand'],
            'animation': 'gentle_sway',
            'colors': ['#FFB6C1', '#DDA0DD', '#98FB98'],
            'description': 'Need some help?'
        },
        'proud': {
            'facial_expression': 'beaming',
            'eyes': 'confident',
            'accessories': ['trophy', 'medal', 'crown'],
            'animation': 'chest_out',
            'colors': ['#FFD700', '#FF1493', '#00FF00'],
            'description': 'Amazing work!'
        },
        'tired': {
            'facial_expression': 'sleepy',
            'eyes': 'droopy',
            'accessories': ['pillow', 'moon', 'zzz'],
            'animation': 'slow_blink',
            'colors': ['#708090', '#B0C4DE', '#E6E6FA'],
            'description': 'Time for a break?'
        },
        'determined': {
            'facial_expression': 'serious',
            'eyes': 'intense',
            'accessories': ['fire', 'lightning', 'mountain'],
            'animation': 'power_stance',
            'colors': ['#DC143C', '#FF4500', '#B22222'],
            'description': 'Ready for any challenge!'
        },
        'playful': {
            'facial_expression': 'grin',
            'eyes': 'mischievous',
            'accessories': ['toys', 'balloons', 'rainbow'],
            'animation': 'wiggle',
            'colors': ['#FF69B4', '#32CD32', '#FFD700'],
            'description': 'Let\'s have fun learning!'
        }
    }
    
    # Mood-based avatar themes
    MOOD_THEMES = {
        'morning_energy': {
            'time_range': ('06:00', '10:00'),
            'preferred_emotions': ['excited', 'happy', 'determined'],
            'background': 'sunrise',
            'special_effects': ['sunbeams', 'birds']
        },
        'focused_afternoon': {
            'time_range': ('10:00', '15:00'),
            'preferred_emotions': ['focused', 'curious', 'determined'],
            'background': 'study_room',
            'special_effects': ['bookshelf', 'desk_lamp']
        },
        'evening_calm': {
            'time_range': ('15:00', '19:00'),
            'preferred_emotions': ['happy', 'proud', 'playful'],
            'background': 'cozy_room',
            'special_effects': ['warm_light', 'plants']
        },
        'weekend_fun': {
            'day_types': ['saturday', 'sunday'],
            'preferred_emotions': ['playful', 'excited', 'curious'],
            'background': 'playground',
            'special_effects': ['games', 'toys', 'friends']
        }
    }
    
    # Learning context expressions
    LEARNING_EXPRESSIONS = {
        'lesson_start': {
            'emotion': 'excited',
            'message': "Let's start this amazing lesson!",
            'duration': 3000
        },
        'correct_answer': {
            'emotion': 'proud',
            'message': "Fantastic! You got it right!",
            'duration': 2000
        },
        'incorrect_answer': {
            'emotion': 'confused',
            'message': "Hmm, let's try that again together!",
            'duration': 2500
        },
        'lesson_complete': {
            'emotion': 'happy',
            'message': "Wonderful! You completed the lesson!",
            'duration': 4000
        },
        'struggle_detected': {
            'emotion': 'frustrated',
            'message': "I'm here to help you succeed!",
            'duration': 3000
        },
        'breakthrough_moment': {
            'emotion': 'excited',
            'message': "Yes! You figured it out!",
            'duration': 3500
        },
        'taking_break': {
            'emotion': 'tired',
            'message': "Great idea to take a break!",
            'duration': 2000
        },
        'return_from_break': {
            'emotion': 'determined',
            'message': "Ready to continue learning?",
            'duration': 2500
        }
    }
    
    def __init__(self):
        try:
            self.db = get_firestore_client()
        except Exception:
            self.db = None
    
    def get_current_avatar_expression(self, student_id: str, context: Dict = None) -> Dict[str, Any]:
        """Get the current avatar expression based on student's emotional state and context"""
        try:
            # Get student's current emotional state
            current_emotion = self._detect_student_emotion(student_id, context)
            
            # Get appropriate mood theme
            current_theme = self._get_current_mood_theme()
            
            # Generate avatar expression
            expression = self._generate_avatar_expression(current_emotion, current_theme, context)
            
            # Log emotion for learning
            self._log_emotion_data(student_id, current_emotion, context)
            
            return {
                'emotion': current_emotion,
                'expression': expression,
                'theme': current_theme,
                'timestamp': datetime.now().isoformat(),
                'context': context or {}
            }
            
        except Exception as e:
            return self._get_default_expression()
    
    def _detect_student_emotion(self, student_id: str, context: Dict = None) -> str:
        """Detect student's current emotion based on recent activity and context"""
        try:
            if context and context.get('learning_event'):
                # Use learning context to determine emotion
                event = context['learning_event']
                if event in self.LEARNING_EXPRESSIONS:
                    return self.LEARNING_EXPRESSIONS[event]['emotion']
            
            # Analyze recent learning performance
            recent_performance = self._get_recent_performance(student_id)
            
            if recent_performance['average_score'] >= 90:
                return 'proud'
            elif recent_performance['average_score'] >= 75:
                return 'happy'
            elif recent_performance['average_score'] >= 60:
                return 'focused'
            elif recent_performance['consecutive_wrong'] >= 3:
                return 'frustrated'
            elif recent_performance['time_spent'] > 30:
                return 'tired'
            elif recent_performance['questions_answered'] == 0:
                return 'curious'
            else:
                return 'determined'
                
        except Exception:
            return 'happy'  # Default emotion
    
    def _get_recent_performance(self, student_id: str) -> Dict:
        """Get student's recent learning performance data"""
        try:
            if not self.db:
                return self._get_mock_performance()
            
            # Get last 10 minutes of activity
            recent_time = datetime.now() - timedelta(minutes=10)
            
            activities = self.db.collection('student_activities')\
                .where('student_id', '==', student_id)\
                .where('timestamp', '>=', recent_time)\
                .order_by('timestamp', direction='DESCENDING')\
                .limit(20).stream()
            
            activity_list = [activity.to_dict() for activity in activities]
            
            if not activity_list:
                return self._get_mock_performance()
            
            # Calculate performance metrics
            scores = [a.get('score', 0) for a in activity_list if a.get('score') is not None]
            wrong_answers = [a for a in activity_list if a.get('correct') == False]
            total_time = sum(a.get('time_spent', 0) for a in activity_list)
            
            consecutive_wrong = 0
            for activity in activity_list:
                if activity.get('correct') == False:
                    consecutive_wrong += 1
                else:
                    break
            
            return {
                'average_score': sum(scores) / len(scores) if scores else 70,
                'consecutive_wrong': consecutive_wrong,
                'time_spent': total_time,
                'questions_answered': len(activity_list),
                'recent_activities': len(activity_list)
            }
            
        except Exception:
            return self._get_mock_performance()
    
    def _get_mock_performance(self) -> Dict:
        """Get mock performance data for offline mode"""
        return {
            'average_score': random.randint(60, 95),
            'consecutive_wrong': random.randint(0, 2),
            'time_spent': random.randint(5, 25),
            'questions_answered': random.randint(3, 15),
            'recent_activities': random.randint(5, 10)
        }
    
    def _get_current_mood_theme(self) -> Dict:
        """Get current mood theme based on time and day"""
        now = datetime.now()
        current_time = now.strftime('%H:%M')
        current_day = now.strftime('%A').lower()
        
        # Check for weekend theme
        if current_day in ['saturday', 'sunday']:
            return self.MOOD_THEMES['weekend_fun']
        
        # Check time-based themes
        for theme_name, theme_data in self.MOOD_THEMES.items():
            if 'time_range' in theme_data:
                start_time, end_time = theme_data['time_range']
                if start_time <= current_time <= end_time:
                    return theme_data
        
        # Default theme
        return self.MOOD_THEMES['focused_afternoon']
    
    def _generate_avatar_expression(self, emotion: str, theme: Dict, context: Dict = None) -> Dict:
        """Generate complete avatar expression data"""
        base_expression = self.AVATAR_EXPRESSIONS.get(emotion, self.AVATAR_EXPRESSIONS['happy'])
        
        # Customize expression based on theme
        expression = base_expression.copy()
        
        # Add theme-specific elements
        if theme.get('special_effects'):
            expression['background_effects'] = theme['special_effects']
        
        if theme.get('background'):
            expression['background'] = theme['background']
        
        # Add context-specific elements
        if context and context.get('subject'):
            expression['subject_elements'] = self._get_subject_elements(context['subject'])
        
        # Add random variation
        expression['variation_id'] = random.randint(1, 5)
        
        return expression
    
    def _get_subject_elements(self, subject: str) -> List[str]:
        """Get subject-specific visual elements"""
        subject_elements = {
            'maths': ['numbers', 'calculator', 'geometric_shapes'],
            'science': ['beaker', 'microscope', 'atoms'],
            'english': ['books', 'pencil', 'alphabet'],
            'history': ['scroll', 'ancient_items', 'timeline'],
            'geography': ['globe', 'map', 'compass'],
            'languages': ['speech_bubble', 'flags', 'dictionary'],
            'computing': ['computer', 'code', 'robot']
        }
        
        return subject_elements.get(subject, ['books', 'learning'])
    
    def _log_emotion_data(self, student_id: str, emotion: str, context: Dict = None):
        """Log emotion data for analysis and improvement"""
        try:
            if not self.db:
                return
            
            emotion_log = {
                'student_id': student_id,
                'emotion': emotion,
                'timestamp': datetime.now(),
                'context': context or {},
                'session_id': context.get('session_id') if context else None
            }
            
            self.db.collection('emotion_logs').add(emotion_log)
            
        except Exception:
            pass  # Fail silently for logging
    
    def _get_default_expression(self) -> Dict[str, Any]:
        """Get default avatar expression when errors occur"""
        return {
            'emotion': 'happy',
            'expression': self.AVATAR_EXPRESSIONS['happy'],
            'theme': self.MOOD_THEMES['focused_afternoon'],
            'timestamp': datetime.now().isoformat(),
            'context': {},
            'fallback': True
        }
    
    def trigger_expression_change(self, student_id: str, learning_event: str, additional_context: Dict = None) -> Dict[str, Any]:
        """Trigger an immediate avatar expression change based on learning event"""
        context = {'learning_event': learning_event}
        if additional_context:
            context.update(additional_context)
        
        expression_data = self.get_current_avatar_expression(student_id, context)
        
        # Add event-specific message
        if learning_event in self.LEARNING_EXPRESSIONS:
            event_data = self.LEARNING_EXPRESSIONS[learning_event]
            expression_data['message'] = event_data['message']
            expression_data['message_duration'] = event_data['duration']
        
        return expression_data
    
    def get_emotion_suggestions(self, student_id: str) -> List[Dict]:
        """Get suggestions for improving student's emotional state"""
        current_emotion = self._detect_student_emotion(student_id)
        
        suggestions = {
            'frustrated': [
                {'action': 'take_break', 'message': 'How about a quick 5-minute break?'},
                {'action': 'easier_question', 'message': 'Let\'s try an easier question first'},
                {'action': 'hint', 'message': 'Would you like a helpful hint?'}
            ],
            'tired': [
                {'action': 'long_break', 'message': 'Time for a longer break - you\'ve earned it!'},
                {'action': 'change_activity', 'message': 'Let\'s try a different type of activity'},
                {'action': 'end_session', 'message': 'Great work today! Ready to finish?'}
            ],
            'confused': [
                {'action': 'explanation', 'message': 'Let me explain this in a different way'},
                {'action': 'example', 'message': 'Here\'s a helpful example'},
                {'action': 'video', 'message': 'Would a video explanation help?'}
            ]
        }
        
        return suggestions.get(current_emotion, [])
    
    def get_celebration_expression(self, achievement_type: str) -> Dict[str, Any]:
        """Get special celebration expression for achievements"""
        celebrations = {
            'quest_complete': {
                'emotion': 'excited',
                'special_effects': ['fireworks', 'confetti', 'party_hat'],
                'animation': 'celebration_dance',
                'message': 'Quest completed! You\'re amazing!',
                'duration': 5000
            },
            'avatar_unlock': {
                'emotion': 'proud',
                'special_effects': ['golden_light', 'sparkles', 'new_avatar'],
                'animation': 'reveal_unlock',
                'message': 'New avatar unlocked! Fantastic achievement!',
                'duration': 4000
            },
            'perfect_score': {
                'emotion': 'excited',
                'special_effects': ['rainbow', 'stars', 'perfect_badge'],
                'animation': 'perfect_spin',
                'message': 'Perfect score! You\'re a superstar!',
                'duration': 4500
            },
            'streak_milestone': {
                'emotion': 'determined',
                'special_effects': ['fire', 'lightning', 'streak_counter'],
                'animation': 'power_surge',
                'message': 'Amazing learning streak! Keep it up!',
                'duration': 3500
            }
        }
        
        celebration = celebrations.get(achievement_type, celebrations['quest_complete'])
        
        return {
            'type': 'celebration',
            'achievement': achievement_type,
            'emotion': celebration['emotion'],
            'expression': {
                **self.AVATAR_EXPRESSIONS[celebration['emotion']],
                'special_effects': celebration['special_effects'],
                'animation': celebration['animation']
            },
            'message': celebration['message'],
            'duration': celebration['duration'],
            'timestamp': datetime.now().isoformat()
        }