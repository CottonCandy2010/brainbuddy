from app import db
from datetime import datetime
from sqlalchemy import func
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class Parent(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.String(20), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationship to children
    children = db.relationship('Student', backref='parent', lazy='dynamic', cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def __repr__(self):
        return f'<Parent {self.email}>'

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('parent.id'), nullable=False, index=True)
    student_name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    grade_level = db.Column(db.String(10), nullable=False)  # P1, P2, P3, etc.
    learning_style = db.Column(db.String(50), nullable=True)  # visual, auditory, verbal
    avatar_image = db.Column(db.String(100), default='avatar1.jpeg')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    total_points = db.Column(db.Integer, default=0)
    
    # Unique student identifier for tracking progress
    student_id = db.Column(db.String(100), unique=True, nullable=False, index=True)
    
    def __init__(self, **kwargs):
        super(Student, self).__init__(**kwargs)
        if not self.student_id:
            # Generate unique student ID
            import uuid
            self.student_id = f"student_{uuid.uuid4().hex[:12]}"
    
    def get_display_name(self):
        return f"{self.student_name} (Age {self.age})"
    
    def get_progress_summary(self):
        """Get basic progress summary for this student"""
        progress_entries = StudentProgress.query.filter_by(student_id=self.student_id).all()
        if not progress_entries:
            return {'total_lessons': 0, 'avg_completion': 0, 'total_time': 0}
        
        total_lessons = len(progress_entries)
        avg_completion = sum(p.completion_percentage for p in progress_entries) / total_lessons
        total_time = sum(p.time_spent_minutes for p in progress_entries)
        
        return {
            'total_lessons': total_lessons,
            'avg_completion': round(avg_completion, 1),
            'total_time': total_time
        }
    
    def __repr__(self):
        return f'<Student {self.student_name} (Parent: {self.parent_id})>'

class StudentProgress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String(100), nullable=False, index=True)
    student_name = db.Column(db.String(100), nullable=False)
    subject = db.Column(db.String(50), nullable=False)
    topic = db.Column(db.String(200), nullable=False)
    learning_style = db.Column(db.String(50), nullable=False)
    completion_percentage = db.Column(db.Integer, default=0)
    time_spent_minutes = db.Column(db.Integer, default=0)
    completed_at = db.Column(db.DateTime, default=datetime.utcnow)
    points_earned = db.Column(db.Integer, default=0)
    
    def __repr__(self):
        return f'<StudentProgress {self.student_name}: {self.subject} - {self.completion_percentage}%>'

class Achievement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String(100), nullable=False, index=True)
    badge_name = db.Column(db.String(100), nullable=False)
    badge_icon = db.Column(db.String(50), nullable=False)
    badge_color = db.Column(db.String(20), nullable=False)
    description = db.Column(db.Text, nullable=False)
    earned_at = db.Column(db.DateTime, default=datetime.utcnow)
    points_value = db.Column(db.Integer, default=100)
    
    def __repr__(self):
        return f'<Achievement {self.student_id}: {self.badge_name}>'

class LearningStreak(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String(100), nullable=False, unique=True, index=True)
    current_streak = db.Column(db.Integer, default=0)
    longest_streak = db.Column(db.Integer, default=0)
    last_activity_date = db.Column(db.Date, default=datetime.utcnow().date)
    total_points = db.Column(db.Integer, default=0)
    
    def __repr__(self):
        return f'<LearningStreak {self.student_id}: {self.current_streak} days>'

class StudentChallenge(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String(100), nullable=False, index=True)
    challenge_name = db.Column(db.String(100), nullable=False)
    challenge_type = db.Column(db.String(50), nullable=False)  # 'daily', 'weekly', 'subject_mastery'
    target_value = db.Column(db.Integer, nullable=False)
    current_progress = db.Column(db.Integer, default=0)
    is_completed = db.Column(db.Boolean, default=False)
    reward_points = db.Column(db.Integer, default=50)
    expires_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<StudentChallenge {self.student_id}: {self.challenge_name}>'