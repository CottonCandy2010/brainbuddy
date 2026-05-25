"""
Adaptive Difficulty Scaling System for Brain Buddy
Dynamically adjusts lesson difficulty based on student performance
"""

from datetime import datetime, timedelta
import json

class AdaptiveDifficultyEngine:
    
    # Difficulty levels
    DIFFICULTY_LEVELS = {
        'beginner': 1,
        'easy': 2,
        'medium': 3,
        'hard': 4,
        'expert': 5
    }
    
    # Performance thresholds
    PERFORMANCE_THRESHOLDS = {
        'excellent': 90,    # 90%+ accuracy
        'good': 75,         # 75-89% accuracy
        'average': 60,      # 60-74% accuracy
        'struggling': 40,   # 40-59% accuracy
        'needs_help': 0     # Below 40% accuracy
    }
    
    def __init__(self):
        self.current_difficulty = 2  # Start at easy level
        
    def calculate_student_performance(self, student_id, subject, days_back=7):
        """
        Calculate student performance metrics over the last N days
        """
        try:
            from models import StudentProgress
            cutoff_date = datetime.utcnow() - timedelta(days=days_back)
            
            recent_progress = StudentProgress.query.filter(
                StudentProgress.student_id == student_id,
                StudentProgress.subject == subject,
                StudentProgress.updated_at >= cutoff_date
            ).all()
            
            if not recent_progress:
                return {
                    'average_completion': 50,
                    'average_time_per_lesson': 300,  # 5 minutes default
                    'total_lessons': 0,
                    'performance_trend': 'stable',
                    'recommended_difficulty': 2
                }
            
            # Calculate metrics
            total_accuracy = sum(p.accuracy_rate() for p in recent_progress)
            avg_accuracy = total_accuracy / len(recent_progress)
            
            total_time = sum(p.time_spent_minutes for p in recent_progress)
            avg_time = total_time / len(recent_progress)
            
            total_completion = sum(p.completion_percentage for p in recent_progress)
            avg_completion = total_completion / len(recent_progress)
            
            # Determine trend (simplified)
            if len(recent_progress) >= 3:
                recent_scores = [p.accuracy_rate() for p in recent_progress[-3:]]
                if recent_scores[-1] > recent_scores[0]:
                    trend = 'improving'
                elif recent_scores[-1] < recent_scores[0]:
                    trend = 'declining'
                else:
                    trend = 'stable'
            else:
                trend = 'stable'
            
            # Calculate recommended difficulty
            recommended_difficulty = self._calculate_difficulty_adjustment(avg_completion, trend)
            
            return {
                'average_completion': avg_completion,
                'average_accuracy': avg_accuracy,
                'average_time_per_lesson': avg_time,
                'total_lessons': len(recent_progress),
                'performance_trend': trend,
                'recommended_difficulty': recommended_difficulty
            }
        except Exception as e:
            # Return default values if database query fails
            return {
                'average_completion': 50,
                'average_accuracy': 50,
                'average_time_per_lesson': 300,
                'total_lessons': 0,
                'performance_trend': 'stable',
                'recommended_difficulty': 2
            }
    
    def get_recommended_difficulty_level(self, performance_data):
        """
        Get recommended difficulty level based on performance data
        
        Args:
            performance_data: Dictionary containing performance metrics
            
        Returns:
            String representing recommended difficulty level
        """
        try:
            # Extract key metrics
            avg_completion = performance_data.get('average_completion', 50)
            avg_accuracy = performance_data.get('average_accuracy', 60)
            total_lessons = performance_data.get('total_lessons', 0)
            trend = performance_data.get('performance_trend', 'stable')
            
            # Calculate combined score
            combined_score = (avg_completion * 0.4) + (avg_accuracy * 0.6)
            
            # Adjust based on trend
            if trend == 'improving':
                combined_score += 5
            elif trend == 'declining':
                combined_score -= 5
            
            # Adjust based on experience (total lessons)
            if total_lessons > 10:
                combined_score += 2
            elif total_lessons > 5:
                combined_score += 1
            
            # Determine difficulty level
            if combined_score >= 85:
                return 'expert'
            elif combined_score >= 70:
                return 'hard'
            elif combined_score >= 55:
                return 'medium'
            elif combined_score >= 40:
                return 'easy'
            else:
                return 'beginner'
                
        except Exception as e:
            print(f"Error determining difficulty level: {e}")
            return 'easy'  # Safe fallback

    
    def _calculate_difficulty_adjustment(self, completion_rate, trend):
        """
        Calculate the appropriate difficulty level based on performance
        """
        base_difficulty = 2  # Easy level
        
        # Adjust based on completion rate
        if completion_rate >= self.PERFORMANCE_THRESHOLDS['excellent']:
            base_difficulty = 4  # Hard
        elif completion_rate >= self.PERFORMANCE_THRESHOLDS['good']:
            base_difficulty = 3  # Medium
        elif completion_rate >= self.PERFORMANCE_THRESHOLDS['average']:
            base_difficulty = 2  # Easy
        else:
            base_difficulty = 1  # Beginner
        
        # Adjust based on trend
        if trend == 'improving':
            base_difficulty = min(5, base_difficulty + 1)
        elif trend == 'declining':
            base_difficulty = max(1, base_difficulty - 1)
        
        return base_difficulty
    
    def generate_adaptive_content(self, subject, topic, learning_style, difficulty_level, student_performance):
        """
        Generate content adapted to the student's current difficulty level
        """
        difficulty_name = self._get_difficulty_name(difficulty_level)
        
        # Adjust content complexity based on difficulty
        if difficulty_level <= 2:  # Beginner/Easy
            content_structure = {
                'examples_count': 3,
                'practice_questions': 5,
                'explanation_detail': 'detailed',
                'visual_aids': True,
                'step_by_step': True,
                'hints_available': True
            }
        elif difficulty_level == 3:  # Medium
            content_structure = {
                'examples_count': 2,
                'practice_questions': 7,
                'explanation_detail': 'moderate',
                'visual_aids': True,
                'step_by_step': False,
                'hints_available': True
            }
        else:  # Hard/Expert
            content_structure = {
                'examples_count': 1,
                'practice_questions': 10,
                'explanation_detail': 'brief',
                'visual_aids': False,
                'step_by_step': False,
                'hints_available': False
            }
        
        return {
            'difficulty_level': difficulty_level,
            'difficulty_name': difficulty_name,
            'content_structure': content_structure,
            'adaptive_features': self._get_adaptive_features(student_performance),
            'next_milestone': self._get_next_milestone(difficulty_level)
        }
    
    def _get_difficulty_name(self, level):
        """Get difficulty name from level number"""
        for name, num in self.DIFFICULTY_LEVELS.items():
            if num == level:
                return name
        return 'medium'
    
    def _get_adaptive_features(self, performance):
        """
        Generate adaptive features based on performance
        """
        features = []
        
        if performance['average_completion'] < 60:
            features.extend([
                'Extra practice exercises',
                'Simplified explanations',
                'Additional visual aids',
                'Slower pacing'
            ])
        elif performance['average_completion'] > 85:
            features.extend([
                'Challenge questions',
                'Advanced concepts',
                'Faster pacing',
                'Independent exploration'
            ])
        else:
            features.extend([
                'Balanced content',
                'Regular checkpoints',
                'Moderate pacing'
            ])
        
        if performance['performance_trend'] == 'improving':
            features.append('Progressive difficulty increase')
        elif performance['performance_trend'] == 'declining':
            features.append('Additional support and review')
        
        return features
    
    def _get_next_milestone(self, current_level):
        """
        Define what the student needs to achieve to progress
        """
        milestones = {
            1: "Complete 5 lessons with 70%+ accuracy to unlock Easy level",
            2: "Complete 7 lessons with 80%+ accuracy to unlock Medium level", 
            3: "Complete 10 lessons with 85%+ accuracy to unlock Hard level",
            4: "Complete 12 lessons with 90%+ accuracy to unlock Expert level",
            5: "Maintain expert level performance"
        }
        
        return milestones.get(current_level, "Continue learning!")
    
    def update_difficulty_based_on_lesson(self, student_id, subject, lesson_completion, time_spent):
        """
        Update difficulty recommendation after a lesson is completed
        """
        # Get current performance
        performance = self.calculate_student_performance(student_id, subject)
        
        # Calculate new suggested difficulty
        new_difficulty = self._calculate_difficulty_adjustment(
            performance['average_completion'], 
            performance['performance_trend']
        )
        
        # Store the difficulty recommendation
        difficulty_data = {
            'student_id': student_id,
            'subject': subject,
            'current_difficulty': new_difficulty,
            'performance_metrics': performance,
            'last_updated': datetime.utcnow().isoformat()
        }
        
        return difficulty_data
    
    def get_personalized_lesson_flow(self, student_id, subject, target_topic):
        """
        Create a personalized lesson flow based on student's current ability
        """
        performance = self.calculate_student_performance(student_id, subject)
        difficulty = performance['suggested_difficulty']
        
        # Define lesson progression based on difficulty
        if difficulty <= 2:  # Beginner/Easy
            lesson_flow = [
                {'type': 'introduction', 'duration': 5},
                {'type': 'guided_example', 'duration': 10},
                {'type': 'practice', 'duration': 15},
                {'type': 'review', 'duration': 5}
            ]
        elif difficulty == 3:  # Medium
            lesson_flow = [
                {'type': 'quick_review', 'duration': 3},
                {'type': 'new_concept', 'duration': 8},
                {'type': 'guided_practice', 'duration': 12},
                {'type': 'independent_practice', 'duration': 10},
                {'type': 'assessment', 'duration': 7}
            ]
        else:  # Hard/Expert
            lesson_flow = [
                {'type': 'concept_introduction', 'duration': 5},
                {'type': 'complex_examples', 'duration': 10},
                {'type': 'problem_solving', 'duration': 15},
                {'type': 'advanced_challenges', 'duration': 10}
            ]
        
        return {
            'lesson_flow': lesson_flow,
            'total_duration': sum(step['duration'] for step in lesson_flow),
            'difficulty_level': difficulty,
            'adaptive_notes': f"Customized for {self._get_difficulty_name(difficulty)} level learner"
        }