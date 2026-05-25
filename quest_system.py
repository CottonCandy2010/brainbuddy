"""
Brain Buddy Quest System - Exciting Challenges for Kids
Creates daily, weekly, and special quests to keep children engaged and motivated
"""

import random
from datetime import datetime, timedelta
from typing import Dict, List, Any
from firebase_config import get_firestore_client

class QuestSystem:
    """Manages exciting quests and challenges for young learners"""
    
    DAILY_QUESTS = [
        {
            'id': 'math_mystery',
            'title': 'Math Mystery Detective',
            'description': 'Solve 5 number puzzles to crack the mystery case!',
            'subject': 'maths',
            'requirements': {'questions_correct': 5, 'subject': 'maths'},
            'reward': {'points': 50, 'badge': 'Detective Badge'},
            'emoji': '🔍',
            'difficulty': 'easy'
        },
        {
            'id': 'science_explorer',
            'title': 'Science Lab Explorer',
            'description': 'Discover 3 amazing science facts today!',
            'subject': 'science',
            'requirements': {'lessons_completed': 1, 'subject': 'science'},
            'reward': {'points': 60, 'badge': 'Explorer Badge'},
            'emoji': '🧪',
            'difficulty': 'easy'
        },
        {
            'id': 'word_wizard',
            'title': 'Word Wizard Challenge',
            'description': 'Learn 8 new words and become a word wizard!',
            'subject': 'english',
            'requirements': {'vocabulary_learned': 8, 'subject': 'english'},
            'reward': {'points': 55, 'badge': 'Wizard Badge'},
            'emoji': '📚',
            'difficulty': 'medium'
        },
        {
            'id': 'time_traveler',
            'title': 'Time Traveler Mission',
            'description': 'Journey through history and learn about ancient times!',
            'subject': 'history',
            'requirements': {'lessons_completed': 1, 'subject': 'history'},
            'reward': {'points': 65, 'badge': 'Time Traveler Badge'},
            'emoji': '⏰',
            'difficulty': 'medium'
        },
        {
            'id': 'geography_adventurer',
            'title': 'Geography Adventure',
            'description': 'Explore 2 new countries and their amazing features!',
            'subject': 'geography',
            'requirements': {'countries_explored': 2, 'subject': 'geography'},
            'reward': {'points': 70, 'badge': 'Adventurer Badge'},
            'emoji': '🌍',
            'difficulty': 'medium'
        },
        {
            'id': 'language_star',
            'title': 'Language Star Quest',
            'description': 'Practice speaking and learn 5 new phrases!',
            'subject': 'languages',
            'requirements': {'phrases_learned': 5, 'subject': 'languages'},
            'reward': {'points': 45, 'badge': 'Star Speaker Badge'},
            'emoji': '⭐',
            'difficulty': 'easy'
        },
        {
            'id': 'tech_builder',
            'title': 'Tech Builder Challenge',
            'description': 'Create something cool with technology today!',
            'subject': 'computing',
            'requirements': {'projects_created': 1, 'subject': 'computing'},
            'reward': {'points': 80, 'badge': 'Builder Badge'},
            'emoji': '💻',
            'difficulty': 'hard'
        },
        {
            'id': 'speed_racer',
            'title': 'Speed Learning Racer',
            'description': 'Complete any lesson in under 15 minutes!',
            'subject': 'any',
            'requirements': {'fast_completion': True, 'time_limit': 15},
            'reward': {'points': 75, 'badge': 'Speed Racer Badge'},
            'emoji': '🏎️',
            'difficulty': 'hard'
        },
        {
            'id': 'perfect_student',
            'title': 'Perfect Student Challenge',
            'description': 'Get 100% on any quiz or activity!',
            'subject': 'any',
            'requirements': {'perfect_score': True},
            'reward': {'points': 100, 'badge': 'Perfect Student Badge'},
            'emoji': '💯',
            'difficulty': 'hard'
        },
        {
            'id': 'curious_mind',
            'title': 'Curious Mind Quest',
            'description': 'Ask 3 questions to Study Buddy AI today!',
            'subject': 'any',
            'requirements': {'ai_questions_asked': 3},
            'reward': {'points': 40, 'badge': 'Curious Mind Badge'},
            'emoji': '🤔',
            'difficulty': 'easy'
        }
    ]
    
    WEEKLY_QUESTS = [
        {
            'id': 'learning_champion',
            'title': 'Learning Champion of the Week',
            'description': 'Study every day this week without missing a single day!',
            'requirements': {'consecutive_days': 7},
            'reward': {'points': 300, 'special_avatar': True, 'badge': 'Weekly Champion'},
            'emoji': '🏆',
            'difficulty': 'hard'
        },
        {
            'id': 'subject_master',
            'title': 'Subject Master Challenge',
            'description': 'Complete 10 lessons in your favorite subject this week!',
            'requirements': {'lessons_in_subject': 10},
            'reward': {'points': 250, 'badge': 'Subject Master'},
            'emoji': '🎯',
            'difficulty': 'medium'
        },
        {
            'id': 'explorer_badge',
            'title': 'Knowledge Explorer',
            'description': 'Try lessons in 4 different subjects this week!',
            'requirements': {'different_subjects': 4},
            'reward': {'points': 200, 'badge': 'Explorer Badge'},
            'emoji': '🗺️',
            'difficulty': 'medium'
        },
        {
            'id': 'helping_hand',
            'title': 'Helping Hand Hero',
            'description': 'Help a friend or sibling with their studies 3 times!',
            'requirements': {'helped_others': 3},
            'reward': {'points': 150, 'badge': 'Helper Badge'},
            'emoji': '🤝',
            'difficulty': 'easy'
        },
        {
            'id': 'creative_thinker',
            'title': 'Creative Thinker Quest',
            'description': 'Create 2 projects using different subjects!',
            'requirements': {'creative_projects': 2},
            'reward': {'points': 180, 'badge': 'Creative Badge'},
            'emoji': '🎨',
            'difficulty': 'medium'
        }
    ]
    
    SPECIAL_QUESTS = [
        {
            'id': 'birthday_scholar',
            'title': 'Birthday Scholar Special',
            'description': 'Complete extra lessons on your birthday month!',
            'requirements': {'birthday_month_lessons': 5},
            'reward': {'points': 500, 'special_avatar': True, 'birthday_badge': True},
            'emoji': '🎂',
            'difficulty': 'special'
        },
        {
            'id': 'holiday_learner',
            'title': 'Holiday Learning Adventure',
            'description': 'Learn something new during school holidays!',
            'requirements': {'holiday_lessons': 3},
            'reward': {'points': 200, 'holiday_badge': True},
            'emoji': '🎄',
            'difficulty': 'special'
        },
        {
            'id': 'family_challenge',
            'title': 'Family Learning Challenge',
            'description': 'Complete lessons with family members watching!',
            'requirements': {'family_sessions': 2},
            'reward': {'points': 150, 'family_badge': True},
            'emoji': '👨‍👩‍👧‍👦',
            'difficulty': 'special'
        },
        {
            'id': 'weekend_warrior',
            'title': 'Weekend Warrior Quest',
            'description': 'Study during the weekend when others are playing!',
            'requirements': {'weekend_sessions': 2},
            'reward': {'points': 120, 'warrior_badge': True},
            'emoji': '⚔️',
            'difficulty': 'medium'
        },
        {
            'id': 'early_bird',
            'title': 'Early Bird Special',
            'description': 'Complete lessons before 9 AM for 3 days!',
            'requirements': {'early_sessions': 3, 'time_before': '09:00'},
            'reward': {'points': 200, 'early_bird_badge': True},
            'emoji': '🐦',
            'difficulty': 'hard'
        }
    ]
    
    def __init__(self):
        try:
            self.db = get_firestore_client()
        except Exception:
            self.db = None
    
    def get_daily_quest(self, student_id: str) -> Dict[str, Any]:
        """Get today's quest for a student"""
        try:
            today = datetime.now().strftime('%Y-%m-%d')
            
            # Check if student already has a quest for today
            if self.db:
                existing_quest = self.db.collection('daily_quests').document(f"{student_id}_{today}").get()
                if existing_quest.exists:
                    return existing_quest.to_dict()
            
            # Generate new quest for today
            quest = self._generate_daily_quest(student_id)
            quest['date'] = today
            quest['student_id'] = student_id
            quest['status'] = 'active'
            quest['progress'] = {}
            
            # Save to database
            if self.db:
                self.db.collection('daily_quests').document(f"{student_id}_{today}").set(quest)
            
            return quest
            
        except Exception as e:
            # Return offline quest
            return self._get_offline_daily_quest()
    
    def _generate_daily_quest(self, student_id: str) -> Dict[str, Any]:
        """Generate a personalized daily quest"""
        # Get student's recent activity to personalize quest
        student_progress = self._get_student_recent_activity(student_id)
        
        # Filter quests based on student's level and preferences
        suitable_quests = self._filter_quests_by_level(student_progress)
        
        # Select random quest
        quest = random.choice(suitable_quests)
        return quest.copy()
    
    def _filter_quests_by_level(self, student_progress: Dict) -> List[Dict]:
        """Filter quests based on student's ability level"""
        if not student_progress:
            return [q for q in self.DAILY_QUESTS if q['difficulty'] == 'easy']
        
        avg_score = student_progress.get('average_score', 70)
        
        if avg_score >= 90:
            return [q for q in self.DAILY_QUESTS if q['difficulty'] in ['medium', 'hard']]
        elif avg_score >= 75:
            return [q for q in self.DAILY_QUESTS if q['difficulty'] in ['easy', 'medium']]
        else:
            return [q for q in self.DAILY_QUESTS if q['difficulty'] == 'easy']
    
    def _get_student_recent_activity(self, student_id: str) -> Dict:
        """Get student's recent learning activity"""
        try:
            if not self.db:
                return {}
                
            # Get last 7 days of activity
            week_ago = datetime.now() - timedelta(days=7)
            
            progress_docs = self.db.collection('student_progress')\
                .where('student_id', '==', student_id)\
                .where('timestamp', '>=', week_ago)\
                .limit(20).stream()
            
            activities = [doc.to_dict() for doc in progress_docs]
            
            if not activities:
                return {}
            
            # Calculate averages
            total_score = sum(a.get('score', 0) for a in activities)
            avg_score = total_score / len(activities) if activities else 0
            
            subjects_studied = list(set(a.get('subject') for a in activities if a.get('subject')))
            
            return {
                'average_score': avg_score,
                'subjects_studied': subjects_studied,
                'total_lessons': len(activities),
                'recent_activity': True
            }
            
        except Exception:
            return {}
    
    def _get_offline_daily_quest(self) -> Dict[str, Any]:
        """Return a simple quest when offline"""
        quest = random.choice([
            q for q in self.DAILY_QUESTS 
            if q['difficulty'] == 'easy'
        ])
        
        quest = quest.copy()
        quest['date'] = datetime.now().strftime('%Y-%m-%d')
        quest['status'] = 'active'
        quest['progress'] = {}
        quest['offline_mode'] = True
        
        return quest
    
    def update_quest_progress(self, student_id: str, activity_data: Dict) -> Dict[str, Any]:
        """Update progress on current quest"""
        try:
            today = datetime.now().strftime('%Y-%m-%d')
            quest_id = f"{student_id}_{today}"
            
            if not self.db:
                return {'status': 'offline', 'message': 'Progress tracked locally'}
            
            quest_doc = self.db.collection('daily_quests').document(quest_id)
            quest = quest_doc.get()
            
            if not quest.exists:
                return {'status': 'no_quest', 'message': 'No active quest found'}
            
            quest_data = quest.to_dict()
            requirements = quest_data.get('requirements', {})
            progress = quest_data.get('progress', {})
            
            # Update progress based on activity
            updated = self._update_progress_values(progress, requirements, activity_data)
            
            if updated:
                quest_data['progress'] = progress
                
                # Check if quest is completed
                if self._is_quest_completed(requirements, progress):
                    quest_data['status'] = 'completed'
                    quest_data['completed_at'] = datetime.now()
                    
                    # Award rewards
                    reward_result = self._award_quest_rewards(student_id, quest_data['reward'])
                    quest_data['reward_awarded'] = reward_result
                
                quest_doc.set(quest_data)
                
                return {
                    'status': 'updated',
                    'quest': quest_data,
                    'completed': quest_data.get('status') == 'completed'
                }
            
            return {'status': 'no_update', 'message': 'No relevant progress made'}
            
        except Exception as e:
            return {'status': 'error', 'message': f'Failed to update quest: {str(e)}'}
    
    def _update_progress_values(self, progress: Dict, requirements: Dict, activity: Dict) -> bool:
        """Update progress values based on activity"""
        updated = False
        
        # Check each requirement type
        for req_key, req_value in requirements.items():
            if req_key == 'subject' and activity.get('subject') != req_value:
                continue
                
            if req_key == 'questions_correct':
                if activity.get('questions_correct'):
                    progress[req_key] = progress.get(req_key, 0) + activity['questions_correct']
                    updated = True
                    
            elif req_key == 'lessons_completed':
                if activity.get('lesson_completed'):
                    progress[req_key] = progress.get(req_key, 0) + 1
                    updated = True
                    
            elif req_key == 'vocabulary_learned':
                if activity.get('vocabulary_learned'):
                    progress[req_key] = progress.get(req_key, 0) + activity['vocabulary_learned']
                    updated = True
                    
            elif req_key == 'perfect_score':
                if activity.get('score') == 100:
                    progress[req_key] = True
                    updated = True
                    
            elif req_key == 'fast_completion':
                if activity.get('completion_time') and activity['completion_time'] <= requirements.get('time_limit', 15):
                    progress[req_key] = True
                    updated = True
                    
            elif req_key == 'ai_questions_asked':
                if activity.get('ai_question_asked'):
                    progress[req_key] = progress.get(req_key, 0) + 1
                    updated = True
        
        return updated
    
    def _is_quest_completed(self, requirements: Dict, progress: Dict) -> bool:
        """Check if quest requirements are met"""
        for req_key, req_value in requirements.items():
            if req_key == 'subject':
                continue  # Subject is a filter, not a completion requirement
                
            progress_value = progress.get(req_key, 0)
            
            if isinstance(req_value, bool):
                if not progress_value:
                    return False
            elif isinstance(req_value, (int, float)):
                if progress_value < req_value:
                    return False
        
        return True
    
    def _award_quest_rewards(self, student_id: str, reward: Dict) -> Dict:
        """Award quest completion rewards"""
        try:
            if not self.db:
                return {'status': 'offline', 'points': reward.get('points', 0)}
            
            # Update student points
            student_doc = self.db.collection('students').document(student_id)
            student_data = student_doc.get()
            
            if student_data.exists:
                current_points = student_data.to_dict().get('total_points', 0)
                new_points = current_points + reward.get('points', 0)
                
                student_doc.update({
                    'total_points': new_points,
                    'last_reward_date': datetime.now()
                })
            
            # Award badges if any
            if reward.get('badge'):
                self._award_badge(student_id, reward['badge'])
            
            return {
                'status': 'success',
                'points_awarded': reward.get('points', 0),
                'badge_awarded': reward.get('badge')
            }
            
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def _award_badge(self, student_id: str, badge_name: str):
        """Award a badge to student"""
        try:
            if not self.db:
                return
                
            badge_data = {
                'student_id': student_id,
                'badge_name': badge_name,
                'earned_date': datetime.now(),
                'quest_earned': True
            }
            
            self.db.collection('student_badges').add(badge_data)
            
        except Exception:
            pass
    
    def get_weekly_quests(self, student_id: str) -> List[Dict]:
        """Get available weekly quests"""
        try:
            week_start = datetime.now().strftime('%Y-W%U')
            
            active_quests = []
            for quest in self.WEEKLY_QUESTS:
                quest_copy = quest.copy()
                quest_copy['week'] = week_start
                quest_copy['student_id'] = student_id
                quest_copy['status'] = 'active'
                
                # Check if already completed this week
                if self.db:
                    existing = self.db.collection('weekly_quests')\
                        .where('student_id', '==', student_id)\
                        .where('quest_id', '==', quest['id'])\
                        .where('week', '==', week_start)\
                        .limit(1).get()
                    
                    if existing:
                        quest_copy = existing[0].to_dict()
                
                active_quests.append(quest_copy)
            
            return active_quests
            
        except Exception:
            return self.WEEKLY_QUESTS.copy()
    
    def get_quest_progress_summary(self, student_id: str) -> Dict[str, Any]:
        """Get overall quest progress summary"""
        try:
            summary = {
                'daily_quest': self.get_daily_quest(student_id),
                'weekly_quests': self.get_weekly_quests(student_id),
                'total_points': 0,
                'badges_earned': 0,
                'quests_completed_today': 0,
                'quests_completed_this_week': 0
            }
            
            if self.db:
                # Get total points
                student_doc = self.db.collection('students').document(student_id).get()
                if student_doc.exists:
                    summary['total_points'] = student_doc.to_dict().get('total_points', 0)
                
                # Get badges count
                badges = self.db.collection('student_badges')\
                    .where('student_id', '==', student_id).get()
                summary['badges_earned'] = len(badges)
            
            return summary
            
        except Exception:
            return {
                'daily_quest': self._get_offline_daily_quest(),
                'weekly_quests': [],
                'total_points': 0,
                'badges_earned': 0,
                'offline_mode': True
            }