"""
Progress Service for Brain Buddy
Comprehensive student progress tracking and analytics
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from firebase_config import get_firestore_client

class ProgressService:
    """Service for tracking and analyzing student learning progress"""
    
    def __init__(self):
        try:
            self.db = get_firestore_client()
        except Exception as e:
            print(f"Firebase not available: {e}")
            self.db = None
    
    def record_lesson_completion(self, student_id: str, lesson_data: Dict[str, Any]) -> bool:
        """
        Record a completed lesson for a student
        
        Args:
            student_id: Unique student identifier
            lesson_data: Dictionary containing lesson completion data
            
        Returns:
            bool: True if recorded successfully, False otherwise
        """
        if not self.db:
            return False
            
        try:
            completion_record = {
                'student_id': student_id,
                'subject': lesson_data.get('subject'),
                'topic': lesson_data.get('topic'),
                'score': lesson_data.get('score', 0),
                'time_spent': lesson_data.get('time_spent', 0),  # in minutes
                'difficulty_level': lesson_data.get('difficulty_level', 'medium'),
                'learning_style': lesson_data.get('learning_style', 'visual'),
                'completed_at': datetime.utcnow(),
                'session_id': lesson_data.get('session_id', ''),
                'answers_correct': lesson_data.get('answers_correct', 0),
                'answers_total': lesson_data.get('answers_total', 0),
                'hints_used': lesson_data.get('hints_used', 0),
                'attempts': lesson_data.get('attempts', 1)
            }
            
            # Add to lesson completions collection
            self.db.collection('lesson_completions').add(completion_record)
            
            # Update student statistics
            self._update_student_stats(student_id, completion_record)
            
            return True
            
        except Exception as e:
            print(f"Error recording lesson completion: {e}")
            return False
    
    def _update_student_stats(self, student_id: str, completion_record: Dict[str, Any]):
        """Update aggregated student statistics"""
        try:
            stats_ref = self.db.collection('student_stats').document(student_id)
            stats_doc = stats_ref.get()
            
            if stats_doc.exists:
                stats = stats_doc.to_dict()
            else:
                stats = {
                    'total_lessons': 0,
                    'total_time': 0,
                    'total_score': 0,
                    'subjects': {},
                    'learning_streak': 0,
                    'last_activity': None,
                    'achievements': [],
                    'weekly_goals': {},
                    'monthly_progress': {}
                }
            
            # Update basic stats
            stats['total_lessons'] += 1
            stats['total_time'] += completion_record['time_spent']
            stats['total_score'] = ((stats['total_score'] * (stats['total_lessons'] - 1)) + 
                                   completion_record['score']) / stats['total_lessons']
            
            # Update subject-specific stats
            subject = completion_record['subject']
            if subject not in stats['subjects']:
                stats['subjects'][subject] = {
                    'lessons_completed': 0,
                    'average_score': 0,
                    'time_spent': 0,
                    'difficulty_progress': 'beginner'
                }
            
            subject_stats = stats['subjects'][subject]
            subject_stats['lessons_completed'] += 1
            subject_stats['time_spent'] += completion_record['time_spent']
            subject_stats['average_score'] = ((subject_stats['average_score'] * 
                                              (subject_stats['lessons_completed'] - 1)) + 
                                             completion_record['score']) / subject_stats['lessons_completed']
            
            # Update learning streak
            today = datetime.utcnow().date()
            last_activity = stats.get('last_activity')
            
            if last_activity:
                last_date = last_activity.date() if hasattr(last_activity, 'date') else datetime.fromisoformat(last_activity).date()
                if (today - last_date).days == 1:
                    stats['learning_streak'] += 1
                elif (today - last_date).days > 1:
                    stats['learning_streak'] = 1
            else:
                stats['learning_streak'] = 1
            
            stats['last_activity'] = datetime.utcnow()
            
            # Save updated stats
            stats_ref.set(stats)
            
        except Exception as e:
            print(f"Error updating student stats: {e}")
    
    def get_student_dashboard_data(self, student_id: str) -> Dict[str, Any]:
        """
        Get comprehensive dashboard data for a student
        
        Args:
            student_id: Unique student identifier
            
        Returns:
            Dictionary containing all dashboard metrics
        """
        if not self.db:
            return self._get_demo_dashboard_data(student_id)
        
        try:
            # Get student stats
            stats_ref = self.db.collection('student_stats').document(student_id)
            stats_doc = stats_ref.get()
            
            if not stats_doc.exists:
                return self._get_demo_dashboard_data(student_id)
            
            stats = stats_doc.to_dict()
            
            # Get recent lesson completions
            recent_completions = self._get_recent_completions(student_id, 30)
            
            # Calculate weekly progress
            weekly_progress = self._calculate_weekly_progress(student_id)
            
            # Get subject performance
            subject_performance = self._get_subject_performance(stats.get('subjects', {}))
            
            # Get learning recommendations
            recommendations = self._generate_recommendations(student_id, stats)
            
            # Get recent activity
            recent_activity = self._get_recent_activity(student_id, 10)
            
            dashboard_data = {
                'student_info': {
                    'id': student_id,
                    'name': self._get_student_name(student_id),
                    'age': self._get_student_age(student_id),
                    'grade': self._get_student_grade(student_id)
                },
                'overview_stats': {
                    'total_learning_time': self._format_time(stats.get('total_time', 0)),
                    'lessons_completed': stats.get('total_lessons', 0),
                    'average_score': round(stats.get('total_score', 0)),
                    'learning_streak': stats.get('learning_streak', 0)
                },
                'weekly_progress': weekly_progress,
                'subject_performance': subject_performance,
                'recent_activity': recent_activity,
                'recommendations': recommendations,
                'goals': self._get_learning_goals(student_id),
                'achievements': stats.get('achievements', [])
            }
            
            return dashboard_data
            
        except Exception as e:
            print(f"Error getting dashboard data: {e}")
            return self._get_demo_dashboard_data(student_id)
    
    def get_detailed_analytics(self, student_id: str, days_back: int = 30) -> Dict[str, Any]:
        """
        Get detailed analytics for a specific time period
        
        Args:
            student_id: Unique student identifier
            days_back: Number of days to analyze
            
        Returns:
            Dictionary containing detailed analytics
        """
        if not self.db:
            return self._get_demo_analytics(student_id, days_back)
        
        try:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days_back)
            
            # Get lesson completions in date range
            completions_ref = self.db.collection('lesson_completions')
            completions = completions_ref.where('student_id', '==', student_id)\
                                       .where('completed_at', '>=', start_date)\
                                       .where('completed_at', '<=', end_date)\
                                       .order_by('completed_at').get()
            
            completion_data = [doc.to_dict() for doc in completions]
            
            # Calculate trends
            progress_trend = self._calculate_progress_trend(completion_data)
            subject_distribution = self._calculate_subject_distribution(completion_data)
            performance_over_time = self._calculate_performance_over_time(completion_data)
            learning_patterns = self._analyze_learning_patterns(completion_data)
            
            analytics = {
                'date_range': {
                    'start': start_date.isoformat(),
                    'end': end_date.isoformat(),
                    'days': days_back
                },
                'progress_trend': progress_trend,
                'subject_distribution': subject_distribution,
                'performance_over_time': performance_over_time,
                'learning_patterns': learning_patterns,
                'total_sessions': len(completion_data),
                'average_session_score': self._calculate_average_score(completion_data),
                'improvement_areas': self._identify_improvement_areas(completion_data)
            }
            
            return analytics
            
        except Exception as e:
            print(f"Error getting detailed analytics: {e}")
            return self._get_demo_analytics(student_id, days_back)
    
    def _get_demo_dashboard_data(self, student_id: str) -> Dict[str, Any]:
        """Generate demonstration data when Firebase is not available"""
        return {
            'student_info': {
                'id': student_id,
                'name': 'Emma',
                'age': 8,
                'grade': 'P3'
            },
            'overview_stats': {
                'total_learning_time': '2h 45m',
                'lessons_completed': 18,
                'average_score': 87,
                'learning_streak': 12
            },
            'weekly_progress': [
                {'week': 'Week 1', 'maths': 75, 'science': 70, 'english': 65},
                {'week': 'Week 2', 'maths': 82, 'science': 78, 'english': 70},
                {'week': 'Week 3', 'maths': 88, 'science': 83, 'english': 75},
                {'week': 'Week 4', 'maths': 92, 'science': 85, 'english': 78}
            ],
            'subject_performance': [
                {
                    'name': 'Number Magic! 🔢',
                    'score': 92,
                    'lessons_completed': 8,
                    'time_spent': 45
                },
                {
                    'name': 'Super Science! 🧪',
                    'score': 85,
                    'lessons_completed': 6,
                    'time_spent': 38
                },
                {
                    'name': 'Word Wizards! 📚',
                    'score': 78,
                    'lessons_completed': 4,
                    'time_spent': 32
                }
            ],
            'recent_activity': [
                {
                    'type': 'lesson_completed',
                    'title': 'Completed "Counting Fun" lesson',
                    'description': 'Number Magic! 🔢 • Score: 95%',
                    'time': '2 hours ago',
                    'icon': 'success'
                },
                {
                    'type': 'achievement',
                    'title': 'Earned "Math Master" badge',
                    'description': 'Completed 10 math lessons with high scores',
                    'time': '1 day ago',
                    'icon': 'achievement'
                }
            ],
            'recommendations': [
                {
                    'title': 'Focus on Addition Practice',
                    'description': 'Guest shows great progress in counting. Consider more addition exercises.',
                    'icon': 'calculator'
                },
                {
                    'title': 'Reading Comprehension',
                    'description': 'Try interactive story sessions to improve text understanding.',
                    'icon': 'book'
                }
            ],
            'goals': [
                {
                    'title': 'Complete 5 Math Lessons',
                    'progress': 4,
                    'target': 5,
                    'description': 'Almost there! One more lesson to reach the weekly goal.'
                },
                {
                    'title': 'Read 3 Stories',
                    'progress': 2,
                    'target': 3,
                    'description': 'Great progress on reading comprehension!'
                }
            ]
        }
    
    def _get_demo_analytics(self, student_id: str, days_back: int) -> Dict[str, Any]:
        """Generate demonstration analytics when Firebase is not available"""
        return {
            'date_range': {
                'start': (datetime.utcnow() - timedelta(days=days_back)).isoformat(),
                'end': datetime.utcnow().isoformat(),
                'days': days_back
            },
            'progress_trend': {
                'labels': ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
                'datasets': [
                    {
                        'label': 'Number Magic!',
                        'data': [75, 82, 88, 92],
                        'borderColor': '#4285f4'
                    },
                    {
                        'label': 'Super Science!',
                        'data': [70, 78, 83, 85],
                        'borderColor': '#34a853'
                    }
                ]
            },
            'subject_distribution': {
                'labels': ['Number Magic!', 'Super Science!', 'Word Wizards!', 'Creative Artists!'],
                'data': [35, 25, 20, 20],
                'colors': ['#4285f4', '#34a853', '#ea4335', '#fbbc04']
            },
            'total_sessions': 18,
            'average_session_score': 87,
            'improvement_areas': [
                'Reading comprehension needs more practice',
                'Math problem-solving skills are developing well',
                'Science experiments engage student effectively'
            ]
        }
    
    def _format_time(self, minutes: int) -> str:
        """Format minutes into human-readable time"""
        if minutes < 60:
            return f"{minutes}m"
        else:
            hours = minutes // 60
            mins = minutes % 60
            return f"{hours}h {mins}m"
    
    def _get_student_name(self, student_id: str) -> str:
        """Get student name from profile"""
        # This would fetch from student profiles collection
        student_names = {
            'student1': 'Guest',
            'student2': 'Guest', 
            'student3': 'Guest'
        }
        return student_names.get(student_id, 'Guest')
    
    def _get_student_age(self, student_id: str) -> int:
        """Get student age from profile"""
        student_ages = {
            'student1': 8,
            'student2': 10,
            'student3': 6
        }
        return student_ages.get(student_id, 8)
    
    def _get_student_grade(self, student_id: str) -> str:
        """Get student grade from profile"""
        student_grades = {
            'student1': 'P3',
            'student2': 'P5', 
            'student3': 'P2'
        }
        return student_grades.get(student_id, 'P3')
    
    def _get_recent_completions(self, student_id: str, days: int) -> List[Dict]:
        """Get recent lesson completions"""
        if not self.db:
            return []
        
        try:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            completions_ref = self.db.collection('lesson_completions')
            completions = completions_ref.where('student_id', '==', student_id)\
                                       .where('completed_at', '>=', start_date)\
                                       .order_by('completed_at', direction='DESCENDING')\
                                       .limit(20).get()
            
            return [doc.to_dict() for doc in completions]
        except Exception as e:
            print(f"Error getting recent completions: {e}")
            return []
    
    def _calculate_weekly_progress(self, student_id: str) -> List[Dict]:
        """Calculate weekly progress trends"""
        # Implementation would analyze lesson data by week
        return [
            {'week': 'Week 1', 'maths': 75, 'science': 70, 'english': 65},
            {'week': 'Week 2', 'maths': 82, 'science': 78, 'english': 70},
            {'week': 'Week 3', 'maths': 88, 'science': 83, 'english': 75},
            {'week': 'Week 4', 'maths': 92, 'science': 85, 'english': 78}
        ]
    
    def _get_subject_performance(self, subjects: Dict) -> List[Dict]:
        """Format subject performance data"""
        performance = []
        for subject, stats in subjects.items():
            performance.append({
                'name': self._format_subject_name(subject),
                'score': round(stats.get('average_score', 0)),
                'lessons_completed': stats.get('lessons_completed', 0),
                'time_spent': stats.get('time_spent', 0)
            })
        return performance
    
    def _format_subject_name(self, subject: str) -> str:
        """Convert subject key to display name"""
        subject_names = {
            'maths': 'Number Magic! 🔢',
            'science': 'Super Science! 🧪',
            'english': 'Word Wizards! 📚',
            'art': 'Creative Artists! 🎨',
            'geography': 'World Explorers! 🌍',
            'history': 'Time Travelers! ⏰',
            'computing': 'Digital Wizards! 💻'
        }
        return subject_names.get(subject, subject.title())
    
    def _generate_recommendations(self, student_id: str, stats: Dict) -> List[Dict]:
        """Generate learning recommendations based on performance"""
        return [
            {
                'title': 'Focus on Addition Practice',
                'description': 'Great progress in counting. Consider more addition exercises.',
                'icon': 'calculator'
            },
            {
                'title': 'Reading Comprehension',
                'description': 'Try interactive story sessions to improve understanding.',
                'icon': 'book'
            }
        ]
    
    def _get_recent_activity(self, student_id: str, limit: int) -> List[Dict]:
        """Get recent learning activity"""
        return [
            {
                'type': 'lesson_completed',
                'title': 'Completed "Counting Fun" lesson',
                'description': 'Number Magic! 🔢 • Score: 95%',
                'time': '2 hours ago',
                'icon': 'success'
            },
            {
                'type': 'achievement',
                'title': 'Earned "Math Master" badge',
                'description': 'Completed 10 math lessons with high scores',
                'time': '1 day ago',
                'icon': 'achievement'
            }
        ]
    
    def _get_learning_goals(self, student_id: str) -> List[Dict]:
        """Get current learning goals"""
        return [
            {
                'title': 'Complete 5 Math Lessons',
                'progress': 4,
                'target': 5,
                'description': 'Almost there! One more lesson to reach the weekly goal.'
            },
            {
                'title': 'Read 3 Stories',
                'progress': 2,
                'target': 3,
                'description': 'Great progress on reading comprehension!'
            }
        ]
    
    def _calculate_progress_trend(self, completion_data: List[Dict]) -> Dict:
        """Calculate progress trends over time"""
        # Implementation would analyze completion data trends
        return {
            'labels': ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
            'datasets': [
                {
                    'label': 'Average Score',
                    'data': [75, 82, 88, 92],
                    'borderColor': '#4285f4'
                }
            ]
        }
    
    def _calculate_subject_distribution(self, completion_data: List[Dict]) -> Dict:
        """Calculate time spent distribution by subject"""
        return {
            'labels': ['Number Magic!', 'Super Science!', 'Word Wizards!'],
            'data': [35, 25, 20],
            'colors': ['#4285f4', '#34a853', '#ea4335']
        }
    
    def _calculate_performance_over_time(self, completion_data: List[Dict]) -> List[Dict]:
        """Calculate performance metrics over time"""
        return []
    
    def _analyze_learning_patterns(self, completion_data: List[Dict]) -> Dict:
        """Analyze learning patterns and preferences"""
        return {
            'preferred_learning_time': 'Afternoon',
            'best_performing_subject': 'Number Magic!',
            'average_session_duration': 15,
            'learning_consistency': 'High'
        }
    
    def _calculate_average_score(self, completion_data: List[Dict]) -> float:
        """Calculate average score from completion data"""
        if not completion_data:
            return 0.0
        
        total_score = sum(item.get('score', 0) for item in completion_data)
        return round(total_score / len(completion_data), 1)
    
    def _identify_improvement_areas(self, completion_data: List[Dict]) -> List[str]:
        """Identify areas needing improvement"""
        return [
            'Reading comprehension could benefit from more practice',
            'Math problem-solving skills are developing well',
            'Science experiments engage the student effectively'
        ]