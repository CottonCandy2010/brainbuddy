"""
Achievement-Based Avatar Unlock System for Brain Buddy
Manages avatar unlocks, progression tracking, and achievement rewards
"""

from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from firebase_config import get_firestore_client

class AvatarUnlockSystem:
    """Manages avatar unlocks based on learning achievements"""
    
    # Define unlock requirements for special avatars
    UNLOCK_REQUIREMENTS = {
        'unlock_avatar1.jpeg': {
            'name': 'Math Master',
            'description': 'Complete 10 math lessons with 90% or higher score',
            'requirements': {
                'subject': 'maths',
                'lessons_completed': 10,
                'min_average_score': 90
            },
            'category': 'academic_excellence'
        },
        'unlock_avatar2.jpeg': {
            'name': 'Science Explorer',
            'description': 'Complete 8 science lessons and score 85% average',
            'requirements': {
                'subject': 'science',
                'lessons_completed': 8,
                'min_average_score': 85
            },
            'category': 'academic_excellence'
        },
        'unlock_avatar3.jpeg': {
            'name': 'Reading Champion',
            'description': 'Complete 12 English lessons with consistent progress',
            'requirements': {
                'subject': 'english',
                'lessons_completed': 12,
                'min_average_score': 80
            },
            'category': 'academic_excellence'
        },
        'unlock_avatar4.jpeg': {
            'name': 'History Explorer',
            'description': 'Complete 5 history lessons and explore ancient civilizations',
            'requirements': {
                'subject': 'history',
                'lessons_completed': 5,
                'special_activities': 3
            },
            'category': 'exploration'
        },
        'unlock_avatar5.jpeg': {
            'name': 'Learning Streak',
            'description': 'Maintain a 14-day learning streak',
            'requirements': {
                'learning_streak': 14
            },
            'category': 'consistency'
        },
        'unlock_avatar6.jpeg': {
            'name': 'Multi-Subject Star',
            'description': 'Complete lessons in all core subjects',
            'requirements': {
                'subjects_completed': ['maths', 'science', 'english', 'history'],
                'min_lessons_per_subject': 3
            },
            'category': 'well_rounded'
        },
        'unlock_avatar7.jpeg': {
            'name': 'Speed Learner',
            'description': 'Complete 5 lessons in a single day',
            'requirements': {
                'lessons_in_one_day': 5
            },
            'category': 'dedication'
        },
        'unlock_avatar8.jpeg': {
            'name': 'Perfect Score',
            'description': 'Achieve 100% score on any lesson',
            'requirements': {
                'perfect_score_achieved': True
            },
            'category': 'excellence'
        },
        'IMG_9299_1749128631869.jpeg': {
            'name': 'Geography Master',
            'description': 'Complete 8 geography lessons and explore 5 different countries',
            'requirements': {
                'subject': 'geography',
                'lessons_completed': 8,
                'special_activities': 5
            },
            'category': 'exploration'
        },
        'IMG_9300_1749128631869.jpeg': {
            'name': 'Language Champion',
            'description': 'Learn 20 new words in a foreign language',
            'requirements': {
                'subject': 'languages',
                'vocabulary_learned': 20,
                'min_average_score': 85
            },
            'category': 'linguistic'
        },
        'IMG_9304_1749128631869.jpeg': {
            'name': 'Computing Genius',
            'description': 'Complete 6 computing lessons and create a simple program',
            'requirements': {
                'subject': 'computing',
                'lessons_completed': 6,
                'special_activities': 1
            },
            'category': 'technical'
        },
        'IMG_9305_1749128631869.jpeg': {
            'name': 'Week Warrior',
            'description': 'Study for 7 consecutive days without missing a day',
            'requirements': {
                'consecutive_study_days': 7
            },
            'category': 'consistency'
        },
        'IMG_9306_1749128631869.jpeg': {
            'name': 'Question Master',
            'description': 'Answer 100 practice questions correctly across all subjects',
            'requirements': {
                'total_correct_answers': 100
            },
            'category': 'practice'
        },
        'IMG_9307_1749128631869.jpeg': {
            'name': 'History Detective',
            'description': 'Complete 10 history lessons and research 3 historical events',
            'requirements': {
                'subject': 'history',
                'lessons_completed': 10,
                'special_activities': 3
            },
            'category': 'discovery'
        },
        'IMG_9308_1749128631869.jpeg': {
            'name': 'Speed Scholar',
            'description': 'Complete any lesson in under 10 minutes with 90% score',
            'requirements': {
                'fast_completion': True,
                'min_score_in_time': 90,
                'time_limit_minutes': 10
            },
            'category': 'efficiency'
        },
        'IMG_9309_1749128631869.jpeg': {
            'name': 'Science Experimenter',
            'description': 'Complete 12 science lessons and conduct 5 virtual experiments',
            'requirements': {
                'subject': 'science',
                'lessons_completed': 12,
                'experiments_completed': 5
            },
            'category': 'scientific'
        },
        'IMG_9310_1749128631869.jpeg': {
            'name': 'Math Olympian',
            'description': 'Solve 50 advanced math problems with 95% accuracy',
            'requirements': {
                'subject': 'maths',
                'advanced_problems_solved': 50,
                'min_average_score': 95
            },
            'category': 'mathematical'
        },
        'IMG_9311_1749128631869.jpeg': {
            'name': 'Early Bird',
            'description': 'Complete lessons before 9 AM for 5 consecutive days',
            'requirements': {
                'early_morning_sessions': 5,
                'time_before': '09:00'
            },
            'category': 'discipline'
        },
        'IMG_9312_1749128631869.jpeg': {
            'name': 'Knowledge Explorer',
            'description': 'Complete at least 3 lessons in 6 different subjects',
            'requirements': {
                'subjects_explored': 6,
                'min_lessons_per_subject': 3
            },
            'category': 'versatility'
        },
        'IMG_9313_1749128631869.jpeg': {
            'name': 'Ultimate Scholar',
            'description': 'Achieve 30-day learning streak with 85% average score',
            'requirements': {
                'learning_streak': 30,
                'min_average_score': 85,
                'total_lessons_completed': 25
            },
            'category': 'mastery'
        }
    }
    
    def __init__(self):
        try:
            self.db = get_firestore_client()
        except Exception as e:
            print(f"Firebase not available: {e}")
            self.db = None
    
    def check_avatar_unlocks(self, student_id: str) -> List[str]:
        """
        Check which avatars should be unlocked for a student
        
        Args:
            student_id: Unique student identifier
            
        Returns:
            List of newly unlocked avatar filenames
        """
        if not self.db:
            return self._check_unlocks_offline(student_id)
        
        try:
            # Get student progress data
            progress_data = self._get_student_progress(student_id)
            unlocked_avatars = self._get_unlocked_avatars(student_id)
            
            newly_unlocked = []
            
            for avatar_file, requirements in self.UNLOCK_REQUIREMENTS.items():
                if avatar_file not in unlocked_avatars:
                    if self._check_requirements_met(progress_data, requirements['requirements']):
                        newly_unlocked.append(avatar_file)
                        self._unlock_avatar(student_id, avatar_file, requirements['name'])
            
            return newly_unlocked
            
        except Exception as e:
            print(f"Error checking avatar unlocks: {e}")
            return []
    
    def _check_requirements_met(self, progress_data: Dict, requirements: Dict) -> bool:
        """Check if specific requirements are met"""
        
        # Check subject-specific requirements
        if 'subject' in requirements:
            subject = requirements['subject']
            subject_data = progress_data.get('subjects', {}).get(subject, {})
            
            # Check lessons completed
            if 'lessons_completed' in requirements:
                if subject_data.get('lessons_completed', 0) < requirements['lessons_completed']:
                    return False
            
            # Check average score
            if 'min_average_score' in requirements:
                if subject_data.get('average_score', 0) < requirements['min_average_score']:
                    return False
            
            # Check special activities
            if 'special_activities' in requirements:
                if subject_data.get('special_activities', 0) < requirements['special_activities']:
                    return False
        
        # Check learning streak
        if 'learning_streak' in requirements:
            if progress_data.get('learning_streak', 0) < requirements['learning_streak']:
                return False
        
        # Check multi-subject completion
        if 'subjects_completed' in requirements:
            required_subjects = requirements['subjects_completed']
            min_lessons = requirements.get('min_lessons_per_subject', 1)
            
            for subject in required_subjects:
                subject_data = progress_data.get('subjects', {}).get(subject, {})
                if subject_data.get('lessons_completed', 0) < min_lessons:
                    return False
        
        # Check lessons in one day
        if 'lessons_in_one_day' in requirements:
            if not self._check_daily_lesson_count(progress_data, requirements['lessons_in_one_day']):
                return False
        
        # Check perfect score achievement
        if 'perfect_score_achieved' in requirements:
            if not progress_data.get('has_perfect_score', False):
                return False
        
        return True
    
    def _check_daily_lesson_count(self, progress_data: Dict, required_count: int) -> bool:
        """Check if student completed required lessons in a single day"""
        # This would check lesson completion timestamps
        # For now, return based on total lessons as approximation
        return progress_data.get('max_daily_lessons', 0) >= required_count
    
    def _get_student_progress(self, student_id: str) -> Dict:
        """Get comprehensive student progress data"""
        if not self.db:
            return {}
        
        try:
            stats_ref = self.db.collection('student_stats').document(student_id)
            stats_doc = stats_ref.get()
            
            if stats_doc.exists:
                return stats_doc.to_dict()
            else:
                return {}
        except Exception as e:
            print(f"Error getting student progress: {e}")
            return {}
    
    def _get_unlocked_avatars(self, student_id: str) -> List[str]:
        """Get list of already unlocked avatars for student"""
        if not self.db:
            return []
        
        try:
            unlocks_ref = self.db.collection('avatar_unlocks').document(student_id)
            unlocks_doc = unlocks_ref.get()
            
            if unlocks_doc.exists:
                return unlocks_doc.to_dict().get('unlocked_avatars', [])
            else:
                return []
        except Exception as e:
            print(f"Error getting unlocked avatars: {e}")
            return []
    
    def _unlock_avatar(self, student_id: str, avatar_file: str, avatar_name: str):
        """Record avatar unlock for student"""
        if not self.db:
            return
        
        try:
            unlocks_ref = self.db.collection('avatar_unlocks').document(student_id)
            unlocks_doc = unlocks_ref.get()
            
            if unlocks_doc.exists:
                data = unlocks_doc.to_dict()
                unlocked_avatars = data.get('unlocked_avatars', [])
            else:
                unlocked_avatars = []
            
            if avatar_file not in unlocked_avatars:
                unlocked_avatars.append(avatar_file)
                
                unlock_data = {
                    'unlocked_avatars': unlocked_avatars,
                    'unlock_history': data.get('unlock_history', []) + [{
                        'avatar_file': avatar_file,
                        'avatar_name': avatar_name,
                        'unlocked_at': datetime.utcnow(),
                        'student_id': student_id
                    }]
                }
                
                unlocks_ref.set(unlock_data)
                
        except Exception as e:
            print(f"Error unlocking avatar: {e}")
    
    def _check_unlocks_offline(self, student_id: str) -> List[str]:
        """Fallback unlock checking when Firebase unavailable"""
        # Simple offline logic - unlock based on basic criteria
        return []
    
    def get_avatar_progress(self, student_id: str) -> Dict[str, Any]:
        """
        Get progress towards unlocking each avatar
        
        Args:
            student_id: Unique student identifier
            
        Returns:
            Dictionary with progress information for each avatar
        """
        progress_data = self._get_student_progress(student_id)
        unlocked_avatars = self._get_unlocked_avatars(student_id)
        
        avatar_progress = {}
        
        for avatar_file, avatar_info in self.UNLOCK_REQUIREMENTS.items():
            requirements = avatar_info['requirements']
            is_unlocked = avatar_file in unlocked_avatars
            
            if is_unlocked:
                progress_percentage = 100
                status = 'unlocked'
            else:
                progress_percentage = self._calculate_progress_percentage(progress_data, requirements)
                status = 'locked' if progress_percentage < 100 else 'ready_to_unlock'
            
            avatar_progress[avatar_file] = {
                'name': avatar_info['name'],
                'description': avatar_info['description'],
                'category': avatar_info['category'],
                'progress_percentage': progress_percentage,
                'status': status,
                'is_unlocked': is_unlocked,
                'requirements_detail': self._get_requirements_detail(progress_data, requirements)
            }
        
        return avatar_progress
    
    def _calculate_progress_percentage(self, progress_data: Dict, requirements: Dict) -> int:
        """Calculate progress percentage towards unlocking an avatar"""
        total_requirements = len(requirements)
        met_requirements = 0
        
        for req_key, req_value in requirements.items():
            if req_key == 'subject':
                continue  # Subject is not a requirement itself
            elif req_key == 'lessons_completed' and 'subject' in requirements:
                subject = requirements['subject']
                completed = progress_data.get('subjects', {}).get(subject, {}).get('lessons_completed', 0)
                if completed >= req_value:
                    met_requirements += 1
            elif req_key == 'min_average_score' and 'subject' in requirements:
                subject = requirements['subject']
                score = progress_data.get('subjects', {}).get(subject, {}).get('average_score', 0)
                if score >= req_value:
                    met_requirements += 1
            elif req_key == 'learning_streak':
                if progress_data.get('learning_streak', 0) >= req_value:
                    met_requirements += 1
            elif req_key == 'perfect_score_achieved':
                if progress_data.get('has_perfect_score', False):
                    met_requirements += 1
            # Add more requirement checks as needed
        
        return int((met_requirements / total_requirements) * 100) if total_requirements > 0 else 0
    
    def _get_requirements_detail(self, progress_data: Dict, requirements: Dict) -> List[Dict]:
        """Get detailed breakdown of requirements and current progress"""
        details = []
        
        for req_key, req_value in requirements.items():
            if req_key == 'subject':
                continue
            elif req_key == 'lessons_completed' and 'subject' in requirements:
                subject = requirements['subject']
                current = progress_data.get('subjects', {}).get(subject, {}).get('lessons_completed', 0)
                details.append({
                    'description': f'Complete {req_value} {subject} lessons',
                    'current': current,
                    'required': req_value,
                    'completed': current >= req_value
                })
            elif req_key == 'min_average_score' and 'subject' in requirements:
                subject = requirements['subject']
                current = progress_data.get('subjects', {}).get(subject, {}).get('average_score', 0)
                details.append({
                    'description': f'Achieve {req_value}% average in {subject}',
                    'current': f'{current:.0f}%',
                    'required': f'{req_value}%',
                    'completed': current >= req_value
                })
            elif req_key == 'learning_streak':
                current = progress_data.get('learning_streak', 0)
                details.append({
                    'description': f'Maintain {req_value}-day learning streak',
                    'current': f'{current} days',
                    'required': f'{req_value} days',
                    'completed': current >= req_value
                })
            # Add more detailed breakdowns as needed
        
        return details

    def trigger_unlock_celebration(self, avatar_name: str) -> Dict[str, Any]:
        """Generate celebration data for avatar unlock"""
        return {
            'type': 'avatar_unlock',
            'title': f'🎉 New Avatar Unlocked!',
            'message': f'Congratulations! You\'ve unlocked the "{avatar_name}" avatar!',
            'confetti': True,
            'sound': 'celebration',
            'duration': 5000  # 5 seconds
        }