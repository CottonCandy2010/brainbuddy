"""
Avatar Service for Brain Buddy
Manages avatar customization, storage, and integration with the learning platform
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from app import db
from models import StudentProgress


class AvatarService:
    """Service for managing student avatars and customization"""
    
    DEFAULT_AVATAR = {
        'name': 'My Learning Buddy',
        'skinTone': '#fdbcb4',
        'hairColor': '#8B4513', 
        'eyeColor': '#333333',
        'shirtColor': '#4285f4',
        'accessory': 'none',
        'expression': 'happy',
        'created_at': None,
        'updated_at': None
    }
    
    AVATAR_TEMPLATES = [
        {
            'id': 'friendly_sam',
            'name': 'Happy Sam',
            'skinTone': '#fdbcb4',
            'hairColor': '#8B4513',
            'eyeColor': '#4682B4',
            'shirtColor': '#34a853',
            'accessory': 'none',
            'expression': 'happy',
            'personality': 'encouraging'
        },
        {
            'id': 'smart_alex',
            'name': 'Clever Alex',
            'skinTone': '#f1c27d',
            'hairColor': '#000000',
            'eyeColor': '#8B4513',
            'shirtColor': '#4285f4',
            'accessory': 'glasses',
            'expression': 'focused',
            'personality': 'analytical'
        },
        {
            'id': 'cool_maya',
            'name': 'Cool Maya',
            'skinTone': '#e0ac69',
            'hairColor': '#DC143C',
            'eyeColor': '#228B22',
            'shirtColor': '#9333ea',
            'accessory': 'bow',
            'expression': 'cool',
            'personality': 'confident'
        },
        {
            'id': 'happy_taylor',
            'name': 'Cheerful Taylor',
            'skinTone': '#c68642',
            'hairColor': '#FFD700',
            'eyeColor': '#9370DB',
            'shirtColor': '#ea4335',
            'accessory': 'hat',
            'expression': 'excited',
            'personality': 'enthusiastic'
        }
    ]
    
    @staticmethod
    def save_student_avatar(student_id: str, avatar_config: Dict[str, Any]) -> bool:
        """
        Save student's avatar configuration
        
        Args:
            student_id: Unique identifier for the student
            avatar_config: Dictionary containing avatar configuration
            
        Returns:
            bool: True if saved successfully, False otherwise
        """
        try:
            # Add timestamps
            avatar_config['updated_at'] = datetime.utcnow().isoformat()
            if 'created_at' not in avatar_config:
                avatar_config['created_at'] = datetime.utcnow().isoformat()
            
            # Validate avatar configuration
            if not AvatarService._validate_avatar_config(avatar_config):
                return False
            
            # In a real application, this would save to a database
            # For now, we'll use a simple storage mechanism
            # This could be extended to use Firebase, PostgreSQL, or other storage
            
            return True
            
        except Exception as e:
            print(f"Error saving avatar: {e}")
            return False
    
    @staticmethod
    def get_student_avatar(student_id: str) -> Dict[str, Any]:
        """
        Get student's avatar configuration
        
        Args:
            student_id: Unique identifier for the student
            
        Returns:
            Dict containing avatar configuration or default avatar
        """
        try:
            # In a real application, this would fetch from database
            # For now, return default avatar
            return AvatarService.DEFAULT_AVATAR.copy()
            
        except Exception as e:
            print(f"Error getting avatar: {e}")
            return AvatarService.DEFAULT_AVATAR.copy()
    
    @staticmethod
    def get_avatar_templates() -> List[Dict[str, Any]]:
        """
        Get available avatar templates
        
        Returns:
            List of avatar template dictionaries
        """
        return AvatarService.AVATAR_TEMPLATES.copy()
    
    @staticmethod
    def generate_avatar_svg(avatar_config: Dict[str, Any], size: int = 300) -> str:
        """
        Generate SVG representation of avatar
        
        Args:
            avatar_config: Avatar configuration dictionary
            size: Size of the SVG (width and height)
            
        Returns:
            String containing SVG markup
        """
        # Extract colors and properties
        skin_tone = avatar_config.get('skinTone', '#fdbcb4')
        hair_color = avatar_config.get('hairColor', '#8B4513')
        eye_color = avatar_config.get('eyeColor', '#333333')
        shirt_color = avatar_config.get('shirtColor', '#4285f4')
        accessory = avatar_config.get('accessory', 'none')
        expression = avatar_config.get('expression', 'happy')
        
        # Generate mouth path based on expression
        mouth_path = AvatarService._get_mouth_path(expression)
        
        # Generate accessories
        accessories_svg = AvatarService._get_accessories_svg(accessory)
        
        # Generate complete SVG
        svg = f'''
        <svg width="{size}" height="{size}" viewBox="0 0 300 300" xmlns="http://www.w3.org/2000/svg">
            <!-- Background circle -->
            <circle cx="150" cy="150" r="140" fill="#f0f8ff" stroke="#ddd" stroke-width="2"/>
            
            <!-- Face -->
            <circle cx="150" cy="140" r="80" fill="{skin_tone}"/>
            
            <!-- Hair -->
            <path d="M80 120 Q150 60 220 120 Q220 80 180 70 Q150 50 120 70 Q80 80 80 120" 
                  fill="{hair_color}"/>
            
            <!-- Eyes -->
            <circle cx="125" cy="125" r="8" fill="white"/>
            <circle cx="175" cy="125" r="8" fill="white"/>
            <circle cx="125" cy="125" r="4" fill="{eye_color}"/>
            <circle cx="175" cy="125" r="4" fill="{eye_color}"/>
            
            <!-- Nose -->
            <ellipse cx="150" cy="140" rx="3" ry="5" fill="#f4a792"/>
            
            <!-- Mouth -->
            <path d="{mouth_path}" stroke="#333" stroke-width="2" 
                  fill="none" stroke-linecap="round"/>
            
            <!-- Shirt -->
            <rect x="100" y="210" width="100" height="80" fill="{shirt_color}" 
                  rx="10"/>
            
            <!-- Accessories -->
            {accessories_svg}
        </svg>
        '''
        
        return svg.strip()
    
    @staticmethod
    def _validate_avatar_config(config: Dict[str, Any]) -> bool:
        """Validate avatar configuration"""
        required_fields = ['name', 'skinTone', 'hairColor', 'eyeColor', 'shirtColor']
        
        for field in required_fields:
            if field not in config:
                return False
                
        # Validate colors are hex format
        color_fields = ['skinTone', 'hairColor', 'eyeColor', 'shirtColor']
        for field in color_fields:
            if not config[field].startswith('#') or len(config[field]) != 7:
                return False
        
        return True
    
    @staticmethod
    def _get_mouth_path(expression: str) -> str:
        """Get SVG path for mouth based on expression"""
        mouth_paths = {
            'happy': 'M135 155 Q150 165 165 155',
            'excited': 'M130 155 Q150 170 170 155',
            'cool': 'M135 158 Q150 162 165 158',
            'focused': 'M140 160 L160 160'
        }
        return mouth_paths.get(expression, mouth_paths['happy'])
    
    @staticmethod
    def _get_accessories_svg(accessory: str) -> str:
        """Get SVG markup for accessories"""
        accessories = {
            'glasses': '''
                <rect x="115" y="120" width="25" height="15" fill="none" stroke="#333" stroke-width="2" rx="3"/>
                <rect x="160" y="120" width="25" height="15" fill="none" stroke="#333" stroke-width="2" rx="3"/>
                <line x1="140" y1="127" x2="160" y2="127" stroke="#333" stroke-width="2"/>
            ''',
            'hat': '''
                <ellipse cx="150" cy="85" rx="45" ry="8" fill="#2c3e50"/>
                <path d="M120 85 Q150 60 180 85 Q180 70 150 65 Q120 70 120 85" fill="#34495e"/>
            ''',
            'bow': '''
                <path d="M130 95 Q140 85 150 95 Q160 85 170 95 Q165 100 150 98 Q135 100 130 95" fill="#e74c3c"/>
                <circle cx="150" cy="95" r="3" fill="#c0392b"/>
            ''',
            'none': ''
        }
        return accessories.get(accessory, '')
    
    @staticmethod
    def get_avatar_reactions(mood: str = 'neutral') -> Dict[str, str]:
        """
        Get avatar reactions and messages based on student mood or performance
        
        Args:
            mood: Current mood or performance indicator
            
        Returns:
            Dictionary with reaction messages and expressions
        """
        reactions = {
            'success': {
                'message': "Wow! You're super awesome!",
                'expression': 'excited',
                'animation': 'bounce'
            },
            'encouragement': {
                'message': "You can do it! I believe in you!",
                'expression': 'happy',
                'animation': 'nod'
            },
            'challenge': {
                'message': "This is a fun puzzle! Let's figure it out together!",
                'expression': 'focused',
                'animation': 'think'
            },
            'celebration': {
                'message': "AMAZING! You're a learning superstar!",
                'expression': 'excited',
                'animation': 'jump'
            },
            'neutral': {
                'message': "Ready for our next fun adventure?",
                'expression': 'happy',
                'animation': 'idle'
            }
        }
        
        return reactions.get(mood, reactions['neutral'])
    
    @staticmethod
    def get_personalized_messages(student_id: str, context: str = 'general') -> List[str]:
        """
        Get personalized messages based on student's progress and avatar
        
        Args:
            student_id: Student identifier
            context: Context for the message (lesson_start, lesson_complete, etc.)
            
        Returns:
            List of personalized messages
        """
        # Get student's recent progress
        recent_progress = db.session.query(StudentProgress).filter_by(
            student_id=student_id
        ).order_by(StudentProgress.completed_at.desc()).limit(5).all()
        
        # Get avatar configuration
        avatar_config = AvatarService.get_student_avatar(student_id)
        avatar_name = avatar_config.get('name', 'Learning Buddy')
        
        # Generate context-specific messages
        messages = {
            'lesson_start': [
                f"Hi! I'm {avatar_name}, and I'm super excited to learn with you today!",
                f"Ready for another awesome adventure? {avatar_name} is here to help!",
                f"Let's explore something super cool together! {avatar_name} believes you're amazing!"
            ],
            'lesson_complete': [
                f"WOW! {avatar_name} is so proud of you - you're incredible!",
                f"You did fantastic! {avatar_name} knew you were awesome!",
                f"Amazing job! {avatar_name} is doing a happy dance with you!"
            ],
            'encouragement': [
                f"Don't worry, {avatar_name} is here to help you! We're a team!",
                f"Take your time! {avatar_name} knows you can do anything!",
                f"Every superhero was once learning too. {avatar_name} is cheering you on!"
            ],
            'general': [
                f"Hello! I'm {avatar_name}, your super fun learning friend!",
                f"{avatar_name} is here to make learning the best part of your day!",
                f"Ready to discover something incredible? {avatar_name} can't wait!"
            ]
        }
        
        return messages.get(context, messages['general'])


class AvatarAnimation:
    """Handle avatar animations and interactions"""
    
    @staticmethod
    def get_animation_css(animation_type: str) -> str:
        """Get CSS for avatar animations"""
        animations = {
            'bounce': '''
                @keyframes avatarBounce {
                    0%, 20%, 50%, 80%, 100% { transform: translateY(0); }
                    40% { transform: translateY(-10px); }
                    60% { transform: translateY(-5px); }
                }
                .avatar-bounce { animation: avatarBounce 2s infinite; }
            ''',
            'nod': '''
                @keyframes avatarNod {
                    0%, 100% { transform: rotateX(0deg); }
                    25%, 75% { transform: rotateX(-5deg); }
                    50% { transform: rotateX(5deg); }
                }
                .avatar-nod { animation: avatarNod 1s ease-in-out; }
            ''',
            'think': '''
                @keyframes avatarThink {
                    0%, 100% { transform: rotate(0deg); }
                    25% { transform: rotate(-2deg); }
                    75% { transform: rotate(2deg); }
                }
                .avatar-think { animation: avatarThink 2s ease-in-out infinite; }
            ''',
            'jump': '''
                @keyframes avatarJump {
                    0%, 100% { transform: translateY(0) scale(1); }
                    50% { transform: translateY(-20px) scale(1.1); }
                }
                .avatar-jump { animation: avatarJump 0.6s ease-in-out; }
            '''
        }
        
        return animations.get(animation_type, '')
    
    @staticmethod
    def create_interactive_avatar(avatar_config: Dict[str, Any], student_id: str) -> str:
        """Create an interactive avatar component with animations and reactions"""
        avatar_svg = AvatarService.generate_avatar_svg(avatar_config)
        avatar_name = avatar_config.get('name', 'Learning Buddy')
        
        return f'''
        <div class="interactive-avatar-container">
            <div class="avatar-display interactive" id="interactiveAvatar">
                {avatar_svg}
            </div>
            <div class="avatar-speech-bubble" id="avatarSpeech" style="display: none;">
                <p id="avatarMessage">Hi! I'm {avatar_name}!</p>
            </div>
            <div class="avatar-controls">
                <button class="btn btn-sm btn-outline-primary" onclick="avatarSpeak('encouragement')">
                    <i class="fas fa-thumbs-up"></i>
                </button>
                <button class="btn btn-sm btn-outline-info" onclick="avatarSpeak('hint')">
                    <i class="fas fa-lightbulb"></i>
                </button>
                <button class="btn btn-sm btn-outline-success" onclick="avatarCelebrate()">
                    <i class="fas fa-star"></i>
                </button>
            </div>
        </div>
        
        <style>
        .interactive-avatar-container {{
            position: relative;
            display: flex;
            flex-direction: column;
            align-items: center;
            margin: 20px 0;
        }}
        
        .avatar-display.interactive {{
            cursor: pointer;
            transition: transform 0.3s ease;
        }}
        
        .avatar-display.interactive:hover {{
            transform: scale(1.05);
        }}
        
        .avatar-speech-bubble {{
            background: #f0f8ff;
            border-radius: 20px;
            padding: 15px 20px;
            margin: 15px 0;
            position: relative;
            max-width: 250px;
            text-align: center;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }}
        
        .avatar-speech-bubble::before {{
            content: '';
            position: absolute;
            top: -10px;
            left: 50%;
            transform: translateX(-50%);
            width: 0;
            height: 0;
            border-left: 10px solid transparent;
            border-right: 10px solid transparent;
            border-bottom: 10px solid #f0f8ff;
        }}
        
        .avatar-controls {{
            display: flex;
            gap: 10px;
            margin-top: 10px;
        }}
        
        .avatar-controls .btn {{
            border-radius: 50%;
            width: 40px;
            height: 40px;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        
        {AvatarAnimation.get_animation_css('bounce')}
        {AvatarAnimation.get_animation_css('nod')}
        {AvatarAnimation.get_animation_css('jump')}
        </style>
        
        <script>
        // Avatar interaction functions
        function avatarSpeak(type) {{
            const messages = {{
                'encouragement': [
                    "You're doing great! Keep going!",
                    "I believe in you!",
                    "You've got this!",
                    "Don't give up - you're so close!"
                ],
                'hint': [
                    "Try thinking about it step by step!",
                    "What do you notice about the pattern?",
                    "Remember what we learned earlier!",
                    "Take your time and think it through!"
                ],
                'celebration': [
                    "Amazing work!",
                    "You're a superstar!",
                    "I'm so proud of you!",
                    "That was fantastic!"
                ]
            }};
            
            const messageList = messages[type] || messages['encouragement'];
            const randomMessage = messageList[Math.floor(Math.random() * messageList.length)];
            
            showAvatarMessage(randomMessage);
        }}
        
        function avatarCelebrate() {{
            const avatar = document.getElementById('interactiveAvatar');
            avatar.classList.add('avatar-jump');
            
            avatarSpeak('celebration');
            
            setTimeout(() => {{
                avatar.classList.remove('avatar-jump');
            }}, 600);
        }}
        
        function showAvatarMessage(message) {{
            const speechBubble = document.getElementById('avatarSpeech');
            const messageElement = document.getElementById('avatarMessage');
            
            messageElement.textContent = message;
            speechBubble.style.display = 'block';
            
            // Auto-hide after 4 seconds
            setTimeout(() => {{
                speechBubble.style.display = 'none';
            }}, 4000);
        }}
        
        // Auto-greeting when avatar loads
        document.addEventListener('DOMContentLoaded', function() {{
            setTimeout(() => {{
                showAvatarMessage("Hi! I'm {avatar_name}! Click the buttons to interact with me!");
            }}, 1000);
        }});
        </script>
        '''