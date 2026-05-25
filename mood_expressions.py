"""
Mood and Emotion Expression System for Brain Buddy
Manages avatar emotional states and reactions during learning activities
"""

import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

class MoodExpressionEngine:
    """Engine for managing avatar mood expressions and emotional reactions"""
    
    # Define mood categories and their characteristics
    MOOD_CATEGORIES = {
        'positive': {
            'moods': ['happy', 'excited', 'confident', 'proud', 'cheerful'],
            'triggers': ['correct_answer', 'lesson_complete', 'streak_achievement', 'level_up'],
            'boost_factor': 1.2
        },
        'focused': {
            'moods': ['focused', 'concentrated', 'determined', 'curious', 'thoughtful'],
            'triggers': ['lesson_start', 'difficult_question', 'new_topic', 'challenge_mode'],
            'boost_factor': 1.1
        },
        'encouraging': {
            'moods': ['supportive', 'understanding', 'patient', 'motivating'],
            'triggers': ['wrong_answer', 'struggle_detected', 'low_confidence', 'multiple_attempts'],
            'boost_factor': 1.0
        },
        'celebratory': {
            'moods': ['amazing', 'fantastic', 'superstar', 'brilliant', 'outstanding'],
            'triggers': ['perfect_score', 'improvement', 'milestone_reached', 'breakthrough'],
            'boost_factor': 1.5
        },
        'restful': {
            'moods': ['calm', 'relaxed', 'peaceful', 'gentle', 'sleepy'],
            'triggers': ['break_time', 'end_session', 'fatigue_detected', 'quiet_time'],
            'boost_factor': 0.8
        }
    }
    
    # Emotional expressions for each mood
    MOOD_EXPRESSIONS = {
        'happy': {
            'face': 'big_smile',
            'eyes': 'bright_sparkle',
            'body_language': 'upright_confident',
            'colors': ['#FFD700', '#FF69B4', '#87CEEB'],
            'animations': ['gentle_bounce', 'sparkle_effect'],
            'sounds': ['cheerful_chime', 'happy_bell']
        },
        'excited': {
            'face': 'wide_smile',
            'eyes': 'star_sparkle',
            'body_language': 'jumping_joy',
            'colors': ['#FF6347', '#FFD700', '#FF1493'],
            'animations': ['bounce_high', 'confetti_effect'],
            'sounds': ['excitement_chime', 'celebration_sound']
        },
        'focused': {
            'face': 'determined_line',
            'eyes': 'concentrated_gaze',
            'body_language': 'leaning_forward',
            'colors': ['#4169E1', '#6A5ACD', '#2E8B57'],
            'animations': ['subtle_nod', 'thinking_aura'],
            'sounds': ['focus_tone', 'concentration_hum']
        },
        'curious': {
            'face': 'questioning_smile',
            'eyes': 'wide_wonder',
            'body_language': 'head_tilt',
            'colors': ['#FF8C00', '#32CD32', '#9370DB'],
            'animations': ['head_tilt', 'question_marks'],
            'sounds': ['curious_bell', 'wonder_chime']
        },
        'supportive': {
            'face': 'gentle_smile',
            'eyes': 'warm_gaze',
            'body_language': 'open_arms',
            'colors': ['#98FB98', '#F0E68C', '#DDA0DD'],
            'animations': ['gentle_sway', 'heart_effect'],
            'sounds': ['encouraging_tone', 'supportive_hum']
        },
        'proud': {
            'face': 'beaming_smile',
            'eyes': 'proud_sparkle',
            'body_language': 'chest_out',
            'colors': ['#FFD700', '#FF6347', '#40E0D0'],
            'animations': ['proud_pose', 'golden_glow'],
            'sounds': ['pride_fanfare', 'achievement_sound']
        },
        'sleepy': {
            'face': 'sleepy_yawn',
            'eyes': 'droopy_lids',
            'body_language': 'relaxed_slouch',
            'colors': ['#B0C4DE', '#E6E6FA', '#F5F5DC'],
            'animations': ['gentle_sway', 'sleep_particles'],
            'sounds': ['sleepy_yawn', 'peaceful_hum']
        }
    }
    
    # Contextual mood responses
    CONTEXT_RESPONSES = {
        'lesson_start': {
            'primary_moods': ['excited', 'focused', 'curious'],
            'messages': [
                "I'm so excited to learn with you today!",
                "Ready for an amazing learning adventure?",
                "Let's discover something wonderful together!",
                "I can't wait to see what we'll learn!"
            ]
        },
        'correct_answer': {
            'primary_moods': ['happy', 'proud', 'excited'],
            'messages': [
                "Fantastic! You got it right!",
                "Brilliant work! I'm so proud of you!",
                "Amazing! You're such a smart learner!",
                "Perfect! You're doing incredibly well!"
            ]
        },
        'wrong_answer': {
            'primary_moods': ['supportive', 'encouraging', 'patient'],
            'messages': [
                "That's okay! Learning is all about trying!",
                "No worries! Let's figure this out together!",
                "Great effort! Every mistake helps us learn!",
                "You're doing great! Let's try a different way!"
            ]
        },
        'struggle_detected': {
            'primary_moods': ['supportive', 'understanding', 'patient'],
            'messages': [
                "I believe in you! You can do this!",
                "It's okay to find things challenging!",
                "Every expert was once a beginner!",
                "You're braver than you believe!"
            ]
        },
        'lesson_complete': {
            'primary_moods': ['proud', 'happy', 'celebratory'],
            'messages': [
                "Wow! You completed the lesson! I'm so proud!",
                "Amazing work! You're such a dedicated learner!",
                "Fantastic job! You should feel proud!",
                "Incredible! You conquered that lesson!"
            ]
        },
        'break_time': {
            'primary_moods': ['calm', 'gentle', 'peaceful'],
            'messages': [
                "Great work! Time for a well-deserved break!",
                "Let's rest and recharge for more learning!",
                "You've earned this break! Relax and enjoy!",
                "Perfect time to rest those busy brain cells!"
            ]
        }
    }
    
    def __init__(self):
        self.current_mood = 'happy'
        self.mood_history = []
        self.emotion_intensity = 1.0
        self.context_awareness = {}
        
    def get_contextual_mood(self, context: str, student_performance: Dict = None) -> Tuple[str, Dict]:
        """
        Determine appropriate mood based on learning context and student performance
        
        Args:
            context: Current learning context (lesson_start, correct_answer, etc.)
            student_performance: Dictionary containing performance metrics
            
        Returns:
            Tuple of (mood_name, mood_expression_data)
        """
        if context not in self.CONTEXT_RESPONSES:
            context = 'lesson_start'
            
        context_data = self.CONTEXT_RESPONSES[context]
        
        # Consider student performance for mood selection
        if student_performance:
            accuracy = student_performance.get('accuracy', 0.5)
            engagement = student_performance.get('engagement', 0.5)
            confidence = student_performance.get('confidence', 0.5)
            
            # Adjust mood based on performance
            if accuracy > 0.8 and confidence > 0.7:
                mood_options = ['excited', 'proud', 'happy']
            elif accuracy < 0.4 or confidence < 0.3:
                mood_options = ['supportive', 'encouraging', 'patient']
            else:
                mood_options = context_data['primary_moods']
        else:
            mood_options = context_data['primary_moods']
        
        # Select mood with some randomness for variety
        selected_mood = random.choice(mood_options)
        
        # Get expression data for the selected mood
        expression_data = self.MOOD_EXPRESSIONS.get(selected_mood, self.MOOD_EXPRESSIONS['happy'])
        
        # Add contextual message
        expression_data['message'] = random.choice(context_data['messages'])
        expression_data['context'] = context
        
        # Update mood history
        self.mood_history.append({
            'mood': selected_mood,
            'context': context,
            'timestamp': datetime.now(),
            'performance': student_performance
        })
        
        # Keep only recent mood history
        if len(self.mood_history) > 20:
            self.mood_history = self.mood_history[-20:]
            
        self.current_mood = selected_mood
        return selected_mood, expression_data
    
    def get_adaptive_mood_response(self, student_id: str, learning_context: Dict) -> Dict:
        """
        Generate adaptive mood response based on student's learning journey
        
        Args:
            student_id: Unique identifier for student
            learning_context: Current learning situation data
            
        Returns:
            Dictionary containing complete mood response data
        """
        context = learning_context.get('situation', 'lesson_start')
        performance = learning_context.get('performance', {})
        time_of_day = learning_context.get('time_of_day', 'morning')
        session_duration = learning_context.get('session_duration', 0)
        
        # Adjust for time of day and session duration
        if time_of_day == 'evening' or session_duration > 45:
            if context in ['break_time', 'lesson_complete']:
                context = 'break_time'
        
        # Get base mood and expression
        mood, expression = self.get_contextual_mood(context, performance)
        
        # Add personalization based on student history
        expression['personalized_message'] = self._get_personalized_message(
            student_id, mood, context, performance
        )
        
        # Add interactive elements
        expression['interactive_actions'] = self._get_interactive_actions(mood, context)
        
        # Add learning insights
        expression['learning_insights'] = self._generate_learning_insights(
            performance, context, mood
        )
        
        return {
            'mood': mood,
            'expression': expression,
            'timestamp': datetime.now(),
            'context': context,
            'student_id': student_id
        }
    
    def _get_personalized_message(self, student_id: str, mood: str, context: str, performance: Dict) -> str:
        """Generate personalized message based on student's learning patterns"""
        # This would typically query student's learning history
        # For now, return contextually appropriate message
        
        base_messages = self.CONTEXT_RESPONSES.get(context, {}).get('messages', [])
        if base_messages:
            return random.choice(base_messages)
        
        return "You're doing amazing! Keep up the great work!"
    
    def _get_interactive_actions(self, mood: str, context: str) -> List[Dict]:
        """Generate interactive actions the avatar can perform"""
        actions = []
        
        if mood in ['excited', 'happy', 'proud']:
            actions.extend([
                {'type': 'animation', 'name': 'celebration_dance', 'duration': 3},
                {'type': 'sound', 'name': 'cheer_sound', 'volume': 0.7},
                {'type': 'particle_effect', 'name': 'confetti', 'duration': 2}
            ])
        
        if mood in ['supportive', 'encouraging']:
            actions.extend([
                {'type': 'animation', 'name': 'encouraging_gesture', 'duration': 2},
                {'type': 'sound', 'name': 'supportive_tone', 'volume': 0.5},
                {'type': 'visual_effect', 'name': 'warm_glow', 'duration': 3}
            ])
        
        if mood == 'focused':
            actions.extend([
                {'type': 'animation', 'name': 'thinking_pose', 'duration': 1},
                {'type': 'visual_effect', 'name': 'concentration_aura', 'duration': 5}
            ])
        
        return actions
    
    def _generate_learning_insights(self, performance: Dict, context: str, mood: str) -> Dict:
        """Generate insights about the student's learning progress"""
        insights = {}
        
        if performance:
            accuracy = performance.get('accuracy', 0)
            speed = performance.get('response_time', 0)
            
            if accuracy > 0.8:
                insights['strength'] = "You're showing excellent understanding!"
            elif accuracy > 0.6:
                insights['progress'] = "You're making steady progress!"
            else:
                insights['encouragement'] = "Every step forward counts!"
            
            if speed < 5:  # Fast response
                insights['speed'] = "Great quick thinking!"
            elif speed > 15:  # Slow but thorough
                insights['thoughtfulness'] = "I love how carefully you think!"
        
        return insights
    
    def get_mood_transition_animation(self, from_mood: str, to_mood: str) -> Dict:
        """Generate smooth transition animation between moods"""
        transitions = {
            ('focused', 'happy'): {
                'type': 'realization_to_joy',
                'duration': 2,
                'keyframes': ['surprise', 'understanding', 'smile', 'joy']
            },
            ('supportive', 'excited'): {
                'type': 'encouragement_to_celebration',
                'duration': 1.5,
                'keyframes': ['gentle_smile', 'growing_confidence', 'excitement']
            },
            ('sleepy', 'excited'): {
                'type': 'awakening_energy',
                'duration': 3,
                'keyframes': ['yawn', 'stretch', 'alertness', 'energy', 'excitement']
            }
        }
        
        return transitions.get((from_mood, to_mood), {
            'type': 'gentle_transition',
            'duration': 1,
            'keyframes': [from_mood, to_mood]
        })
    
    def get_mood_suggestions_for_context(self, context: str) -> List[Dict]:
        """Get suggested moods for teachers/parents to manually set"""
        suggestions = []
        
        if context in self.CONTEXT_RESPONSES:
            for mood in self.CONTEXT_RESPONSES[context]['primary_moods']:
                suggestions.append({
                    'mood': mood,
                    'description': self.MOOD_EXPRESSIONS[mood]['face'],
                    'appropriate_for': context,
                    'colors': self.MOOD_EXPRESSIONS[mood]['colors']
                })
        
        return suggestions
    
    def export_mood_analytics(self, student_id: str, days: int = 7) -> Dict:
        """Export mood and emotional engagement analytics"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        recent_moods = [
            entry for entry in self.mood_history 
            if entry['timestamp'] > cutoff_date
        ]
        
        mood_frequency = {}
        context_patterns = {}
        
        for entry in recent_moods:
            mood = entry['mood']
            context = entry['context']
            
            mood_frequency[mood] = mood_frequency.get(mood, 0) + 1
            context_patterns[context] = context_patterns.get(context, 0) + 1
        
        return {
            'student_id': student_id,
            'period_days': days,
            'total_interactions': len(recent_moods),
            'mood_distribution': mood_frequency,
            'context_patterns': context_patterns,
            'most_common_mood': max(mood_frequency.items(), key=lambda x: x[1])[0] if mood_frequency else 'happy',
            'emotional_engagement_score': self._calculate_engagement_score(recent_moods),
            'recommendations': self._generate_mood_recommendations(recent_moods)
        }
    
    def _calculate_engagement_score(self, mood_entries: List[Dict]) -> float:
        """Calculate emotional engagement score based on mood variety and context"""
        if not mood_entries:
            return 0.5
        
        # Variety of moods indicates good emotional range
        unique_moods = len(set(entry['mood'] for entry in mood_entries))
        mood_variety_score = min(unique_moods / 5.0, 1.0)  # Normalize to 0-1
        
        # Positive mood frequency
        positive_moods = ['happy', 'excited', 'proud', 'confident']
        positive_count = sum(1 for entry in mood_entries if entry['mood'] in positive_moods)
        positive_ratio = positive_count / len(mood_entries)
        
        # Combine scores
        engagement_score = (mood_variety_score * 0.4) + (positive_ratio * 0.6)
        return round(engagement_score, 2)
    
    def _generate_mood_recommendations(self, mood_entries: List[Dict]) -> List[str]:
        """Generate recommendations based on mood patterns"""
        recommendations = []
        
        if not mood_entries:
            return ["Continue engaging with learning activities to build emotional connection!"]
        
        # Analyze patterns
        moods = [entry['mood'] for entry in mood_entries]
        
        if 'supportive' in moods[-3:]:  # Recent struggles
            recommendations.append("Consider adjusting difficulty level or providing more encouragement")
        
        if moods.count('excited') > len(moods) * 0.7:  # Mostly excited
            recommendations.append("Great engagement! Consider introducing new challenges")
        
        if 'sleepy' in moods[-2:]:  # Recent tiredness
            recommendations.append("Student may benefit from a break or shorter learning sessions")
        
        return recommendations or ["Keep up the great work with emotional learning engagement!"]