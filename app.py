import os
import logging
from datetime import datetime, timedelta
from flask import Flask, render_template, request, session, redirect, url_for, jsonify, send_file, flash
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from sqlalchemy.orm import DeclarativeBase
from ai_content_generator import generate_lesson_content
from firebase_config import get_firestore_client
from audio_service import audio_service
from adaptive_difficulty import AdaptiveDifficultyEngine
from adaptive_difficulty_animations import AdaptiveDifficultyAnimations
from mood_expressions import MoodExpressionEngine
from quest_system import QuestSystem
from emotion_avatar_system import EmotionAvatarSystem
from error_reporting import error_reporter, handle_server_error

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Create the Flask application
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "brain-buddy-secret-key")

# Enable CORS for audio API calls
CORS(app)

# Configure database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///progress.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
db.init_app(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'parent_login'
login_manager.login_message = 'Please log in to access your family account.'

@login_manager.user_loader
def load_user(user_id):
    from models import Parent
    return Parent.query.get(int(user_id))

with app.app_context():
    # Import models after db is configured
    import models
    from progress_service import ProgressService
    from adaptive_difficulty import AdaptiveDifficultyEngine
    db.create_all()

# Add template filter for HTML unescaping
@app.template_filter('fix_encoding')
def fix_encoding_filter(text):
    import html
    if not text:
        return text
    # Repeatedly unescape to handle multiple encodings
    while '&amp;' in text:
        text = html.unescape(text)
    return text

# Initialize services
adaptive_engine = AdaptiveDifficultyEngine()
adaptive_animations = AdaptiveDifficultyAnimations()
mood_engine = MoodExpressionEngine()
quest_system = QuestSystem()
emotion_avatar_system = EmotionAvatarSystem()

# Define routes
@app.route('/')
def index():
    # Check if parent is logged in and has children
    if current_user.is_authenticated:
        return redirect(url_for('family_dashboard'))
    
    # Check if age is provided, if not show welcome page
    age = request.args.get('age')
    step = request.args.get('step')
    if age or step:
        return render_template('index.html', student_age=age, step=step)
    else:
        return render_template('index.html')

# Family Account Management Routes
@app.route('/parent-signup', methods=['GET', 'POST'])
def parent_signup():
    """Parent registration for family accounts"""
    if request.method == 'POST':
        try:
            from models import Parent
            
            email = request.form.get('email')
            password = request.form.get('password')
            first_name = request.form.get('first_name')
            last_name = request.form.get('last_name')
            phone = request.form.get('phone', '')
            
            # Check if parent already exists
            existing_parent = Parent.query.filter_by(email=email).first()
            if existing_parent:
                flash('An account with this email already exists.', 'error')
                return render_template('parent_signup.html')
            
            # Create new parent account
            parent = Parent(
                email=email,
                first_name=first_name,
                last_name=last_name,
                phone_number=phone
            )
            parent.set_password(password)
            
            db.session.add(parent)
            db.session.commit()
            
            login_user(parent)
            flash('Welcome! Your family account has been created successfully.', 'success')
            return redirect(url_for('add_child'))
            
        except Exception as e:
            flash(f'Registration failed: {str(e)}', 'error')
            return render_template('parent_signup.html')
    
    return render_template('parent_signup.html')

@app.route('/parent-login', methods=['GET', 'POST'])
def parent_login():
    """Parent login for family accounts"""
    if request.method == 'POST':
        try:
            from models import Parent
            
            email = request.form.get('email')
            password = request.form.get('password')
            
            parent = Parent.query.filter_by(email=email).first()
            
            if parent and parent.check_password(password):
                login_user(parent)
                flash('Welcome back!', 'success')
                return redirect(url_for('family_dashboard'))
            else:
                flash('Invalid email or password.', 'error')
                
        except Exception as e:
            flash(f'Login failed: {str(e)}', 'error')
    
    return render_template('parent_login.html')

@app.route('/logout')
@login_required
def logout():
    """Logout from family account"""
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('index'))

@app.route('/family-dashboard')
@login_required
def family_dashboard():
    """Main dashboard for family account management"""
    from models import Student
    
    children = Student.query.filter_by(parent_id=current_user.id, is_active=True).all()
    
    # Get progress summary for each child
    children_progress = []
    for child in children:
        progress = child.get_progress_summary()
        children_progress.append({
            'child': child,
            'progress': progress
        })
    
    return render_template('family_dashboard.html', 
                         children_progress=children_progress,
                         parent=current_user)

@app.route('/add-child', methods=['GET', 'POST'])
@login_required
def add_child():
    """Add a new child to the family account"""
    if request.method == 'POST':
        try:
            from models import Student
            
            student_name = request.form.get('student_name')
            age = int(request.form.get('age'))
            grade_level = request.form.get('grade_level')
            learning_style = request.form.get('learning_style', 'visual')
            avatar_image = request.form.get('avatar_image', 'avatar1.jpeg')
            
            # Create new student
            student = Student(
                parent_id=current_user.id,
                student_name=student_name,
                age=age,
                grade_level=grade_level,
                learning_style=learning_style,
                avatar_image=avatar_image
            )
            
            db.session.add(student)
            db.session.commit()
            
            flash(f'{student_name} has been added to your family account!', 'success')
            return redirect(url_for('family_dashboard'))
            
        except Exception as e:
            flash(f'Failed to add child: {str(e)}', 'error')
    
    return render_template('add_child.html')

@app.route('/edit-child/<int:child_id>', methods=['GET', 'POST'])
@login_required
def edit_child(child_id):
    """Edit child profile"""
    from models import Student
    
    child = Student.query.filter_by(id=child_id, parent_id=current_user.id).first_or_404()
    
    if request.method == 'POST':
        try:
            child.student_name = request.form.get('student_name')
            child.age = int(request.form.get('age'))
            child.grade_level = request.form.get('grade_level')
            child.learning_style = request.form.get('learning_style')
            child.avatar_image = request.form.get('avatar_image')
            
            db.session.commit()
            flash(f"{child.student_name}'s profile has been updated!", 'success')
            return redirect(url_for('family_dashboard'))
            
        except Exception as e:
            flash(f'Failed to update profile: {str(e)}', 'error')
    
    return render_template('edit_child.html', child=child)

@app.route('/child-login/<int:child_id>')
@login_required
def child_login(child_id):
    """Log in as a specific child for learning activities"""
    from models import Student
    
    child = Student.query.filter_by(id=child_id, parent_id=current_user.id).first_or_404()
    
    # Store child info in session for learning activities
    session['active_child_id'] = child.id
    session['active_child_name'] = child.student_name
    session['active_child_student_id'] = child.student_id
    session['active_child_age'] = child.age
    session['active_child_grade'] = child.grade_level
    
    flash(f"Now learning as {child.student_name}!", 'info')
    return redirect(url_for('select_subject'))

@app.route('/switch-child')
@login_required
def switch_child():
    """Switch between children for learning activities"""
    from models import Student
    
    children = Student.query.filter_by(parent_id=current_user.id, is_active=True).all()
    return render_template('switch_child.html', children=children)

@app.route('/age-setup')
def age_setup():
    return render_template('age_setup_new.html')

@app.route('/settings')
def settings():
    return render_template('settings.html')

@app.route('/study-buddy')
def study_buddy():
    return render_template('study_buddy.html')

@app.route('/study-buddy-ai', methods=['POST'])
def study_buddy_ai():
    """AI Study Buddy chat endpoint"""
    try:
        data = request.get_json()
        user_message = data.get('message', '')
        
        if not user_message:
            return jsonify({'response': "I didn't catch that! Could you ask me something?"})
        
        # Generate AI response using simple educational responses
        response = generate_study_buddy_response(user_message)
        
        return jsonify({'response': response})
        
    except Exception as e:
        app.logger.error(f"Error in study buddy chat: {e}")
        return jsonify({'response': "Sorry, I'm having trouble thinking right now. Could you try asking again?"})

@app.route('/mood-study')
def mood_study():
    return render_template('mood_study.html')

@app.route('/study-index')
def study_index():
    return render_template('study_index.html')

@app.route('/onboarding')
def onboarding():
    return render_template('onboarding.html')

@app.route('/quick-burst')
def quick_burst():
    return render_template('quick_burst.html')

@app.route('/subject-explorer')
def subject_explorer():
    subject = request.args.get('subject', 'maths')
    level = request.args.get('level', 'highschool')
    
    # Get resource counts and progress data
    resource_data = {
        'materials_count': get_materials_count(subject, level),
        'practice_count': get_practice_count(subject, level),
        'guides_count': get_guides_count(subject, level),
        'cheatsheets_count': get_cheatsheets_count(subject, level),
        'videos_count': get_videos_count(subject, level),
        'flashcards_count': get_flashcards_count(subject, level),
        'completion_percentage': get_completion_percentage(subject, level),
        'study_hours': get_study_hours(subject, level),
        'quiz_score': get_quiz_score(subject, level),
        'streak_days': get_streak_days(subject, level)
    }
    
    return render_template('subject_explorer.html', 
                         subject=subject, 
                         level=level,
                         **resource_data)

@app.route('/practice-questions')
def practice_questions():
    subject = request.args.get('subject', 'maths')
    level = request.args.get('level', 'highschool')
    
    # Generate practice question categories based on subject and level
    question_categories = get_practice_categories(subject, level)
    
    return render_template('practice_questions.html',
                         subject=subject,
                         level=level,
                         question_categories=question_categories)

@app.route('/soundtrack-generator')
def soundtrack_generator():
    """Interactive Learning Soundtrack Generator"""
    return render_template('soundtrack_generator.html')

@app.route('/cheat-sheets')
def cheat_sheets():
    subject = request.args.get('subject', 'maths')
    level = request.args.get('level', 'highschool')
    
    # Generate cheat sheets based on subject and level
    cheat_sheets_data = get_cheat_sheets(subject, level)
    
    return render_template('cheat_sheets.html',
                         subject=subject,
                         level=level,
                         cheat_sheets=cheat_sheets_data)

@app.route('/api/cheat-sheet/<sheet_id>')
def get_cheat_sheet_content(sheet_id):
    subject = request.args.get('subject', 'maths')
    level = request.args.get('level', 'highschool')
    
    # Generate full cheat sheet content using AI
    content = generate_cheat_sheet_content(sheet_id, subject, level)
    
    return jsonify(content)

@app.route('/subject-summary')
def subject_summary():
    subject = request.args.get('subject', 'maths')
    level = request.args.get('level', 'highschool')
    
    # Subject information for the template
    subject_info = {
        'maths': {'name': 'Mathematics', 'icon': 'fas fa-calculator', 'description': 'Develop logical thinking and problem-solving skills through numbers, patterns, and mathematical reasoning'},
        'science': {'name': 'Science', 'icon': 'fas fa-flask', 'description': 'Explore the natural world through observation, experimentation, and scientific inquiry'},
        'english': {'name': 'English', 'icon': 'fas fa-book', 'description': 'Master language arts, literature, and communication skills for effective expression'},
        'history': {'name': 'History', 'icon': 'fas fa-landmark', 'description': 'Understand past events, cultures, and civilizations to better comprehend the present'},
        'geography': {'name': 'Geography', 'icon': 'fas fa-globe-americas', 'description': 'Explore countries, landscapes, environments, and human-earth interactions'},
        'languages': {'name': 'Languages', 'icon': 'fas fa-language', 'description': 'Learn foreign languages and develop multicultural communication skills'},

        'art': {'name': 'Art', 'icon': 'fas fa-palette', 'description': 'Express creativity through visual arts, design, and artistic techniques'},

        'computing': {'name': 'Computing', 'icon': 'fas fa-laptop-code', 'description': 'Master digital literacy, programming, and computational thinking for the modern world'}
    }
    
    return render_template('subject_summary.html', 
                         subject=subject, 
                         level=level, 
                         subject_info=subject_info.get(subject, subject_info['maths']))

def get_curriculum_topics(subject, level):
    """Get curriculum topics based on subject and level"""
    
    curriculum_map = {
        'maths': {
            'primary': [
                {
                    'id': 'numbers-1-10',
                    'title': 'Numbers 1-10',
                    'icon': '🔢',
                    'description': 'Let\'s learn about numbers 1 to 10! We can count how many toys, fingers, or friends we have.',
                    'difficulty': 'easy',
                    'year': 'Year 1 (Ages 5-6)',
                    'lessons': [
                        'Count the Animals - How many puppies? (1-10)',
                        'Number Recognition - Match dots to numbers 1-10',
                        'Counting Fingers - Show 3 fingers, count them',
                        'Before, After, Between - What comes after 7?',
                        'Counting by 2s - 2, 4, 6, 8, 10',
                        'Number Line Fun - Numbers 1 to 10 in order',
                        'Grouping Objects - Make groups up to 10',
                        'Comparing Numbers - Which has more? (up to 10)',
                        'Ordering Numbers 1-10 - Smallest to largest',
                        'Simple Counting - Count objects up to 10',
                        'Writing Numbers 1-10 - Trace and write each number',
                        'Number Games - Fun activities with numbers 1-10'
                    ],
                    'activities': [
                        'Count colorful objects up to 10',
                        'Number matching games with pictures',
                        'Finger counting exercises',
                        'Simple number ordering puzzles'
                    ]
                },
                {
                    'id': 'simple-adding',
                    'title': 'Simple Adding (to 10)',
                    'icon': '➕',
                    'description': 'Learn to add numbers together! Start with small numbers and use your fingers or toys to help.',
                    'difficulty': 'easy',
                    'year': 'Year 1 (Ages 5-6)',
                    'lessons': [
                        'Adding with fingers - 2 + 3 = 5',
                        'Adding toys together - 4 blocks + 2 blocks',
                        'Number line adding - jump forward',
                        'Picture adding - count all the animals',
                        'Simple word problems - 3 apples + 2 apples'
                    ],
                    'activities': [
                        'Use finger counting for addition',
                        'Add colorful objects together',
                        'Simple addition with pictures',
                        'Number line jumping games'
                    ]
                },
                {
                    'id': 'adding-subtracting-to-10',
                    'title': 'Adding & Subtracting to 10',
                    'icon': '➕',
                    'description': 'Adding means putting things together to find the total. Subtracting means taking things away to find what\'s left.',
                    'difficulty': 'easy',
                    'year': 'Year 1 (Ages 5-6)',
                    'lessons': [
                        'Adding with fingers',
                        'Taking away objects',
                        '3 apples + 2 apples = 5 apples',
                        '5 birds - 2 birds flying away',
                        'Simple word problems'
                    ],
                    'activities': [
                        'Click on fingers to show addition',
                        'Interactive apple counting game',
                        'Birds flying away subtraction'
                    ]
                },
                {
                    'id': 'shapes-patterns',
                    'title': 'Shapes & Patterns',
                    'icon': '🔷',
                    'description': 'Shapes are all around us! Circles are round, squares have four equal sides.',
                    'difficulty': 'easy',
                    'year': 'Year 1 (Ages 5-6)',
                    'lessons': [
                        'Circle, square, triangle, rectangle',
                        'Finding shapes in pictures',
                        'Shape patterns',
                        'Drawing basic shapes',
                        'Shapes in the house'
                    ],
                    'activities': [
                        'Find the circles in the house picture',
                        'Shape matching games',
                        'Pattern completion puzzles'
                    ]
                },
                {
                    'id': 'time-oclock-half-past',
                    'title': 'Time (O\'clock & Half Past)',
                    'icon': '🕐',
                    'description': 'Clocks help us know when to play or eat! O\'clock is when the big hand points to 12.',
                    'difficulty': 'medium',
                    'year': 'Year 1 (Ages 5-6)',
                    'lessons': [
                        'Reading o\'clock times',
                        'Understanding half past',
                        'Clock faces with big and little hands',
                        'When we eat breakfast (morning)',
                        'When we go to bed (night)'
                    ],
                    'activities': [
                        'Match the clock to the time word',
                        'Interactive clock face games',
                        'Daily routine time matching'
                    ]
                },
                {
                    'id': 'numbers-to-100',
                    'title': 'Numbers to 100 & Place Value',
                    'icon': '💯',
                    'description': 'Numbers can be big! In 23, the \'2\' means 2 tens, and the \'3\' means 3 ones.',
                    'difficulty': 'medium',
                    'year': 'Year 2 (Ages 6-7)',
                    'lessons': [
                        'Counting to 100',
                        'Understanding tens and ones',
                        'Building numbers with blocks',
                        'What does each digit mean?',
                        'Comparing big numbers'
                    ],
                    'activities': [
                        'Build a number with tens and ones blocks',
                        'Place value sorting games',
                        'Number building challenges'
                    ]
                },
                {
                    'id': 'multiplication-division',
                    'title': 'Multiplication & Division (2s, 5s, 10s)',
                    'icon': '✖️',
                    'description': 'Multiplication is like adding groups quickly. Division is sharing things equally.',
                    'difficulty': 'medium',
                    'year': 'Year 2 (Ages 6-7)',
                    'lessons': [
                        '2 groups of 5 sweets = 10 sweets',
                        'Times tables for 2s, 5s, 10s',
                        'Sharing cookies equally',
                        'Arrays and groups',
                        'Division as sharing'
                    ],
                    'activities': [
                        'Times table pop-quiz games',
                        'Sharing objects equally',
                        'Visual multiplication arrays'
                    ]
                },
                {
                    'id': 'fractions-halves-quarters',
                    'title': 'Fractions (Halves, Quarters, Thirds)',
                    'icon': '🍕',
                    'description': 'Fractions are parts of a whole! Half means 1 out of 2 equal parts.',
                    'difficulty': 'medium',
                    'year': 'Year 2 (Ages 6-7)',
                    'lessons': [
                        'Pizza cut into halves',
                        'Quarters of a circle',
                        'Finding thirds of shapes',
                        'Colouring fractions',
                        'Real-life fractions'
                    ],
                    'activities': [
                        'Drag fractions to correct shapes',
                        'Pizza fraction games',
                        'Colour in fractions'
                    ]
                },
                {
                    'id': 'money-change',
                    'title': 'Money & Change',
                    'icon': '💰',
                    'description': 'We use money to buy things! Let\'s learn to count coins and work out change.',
                    'difficulty': 'medium',
                    'year': 'Year 2 (Ages 6-7)',
                    'lessons': [
                        'UK coins (1p, 2p, 5p, 10p, 20p, 50p)',
                        'Counting money',
                        'Shopping for toys',
                        'Working out change',
                        'Saving pocket money'
                    ],
                    'activities': [
                        'Shopping game with toy prices',
                        'Count coins to buy items',
                        'Change calculation games'
                    ]
                },
                {
                    'id': 'measuring-length-height',
                    'title': 'Measuring Length & Height',
                    'icon': '📏',
                    'description': 'How tall are you? How long is your desk? Let\'s learn to measure things!',
                    'difficulty': 'easy',
                    'year': 'Year 1 (Ages 5-6)',
                    'lessons': [
                        'Using rulers and measuring tapes',
                        'Centimetres and metres',
                        'Comparing lengths (longer, shorter)',
                        'Measuring body parts (hand, foot)',
                        'Measuring classroom objects'
                    ],
                    'activities': [
                        'Measure your pencil in centimetres',
                        'Compare heights of different objects',
                        'Interactive measuring games'
                    ]
                },
                {
                    'id': 'weight-capacity',
                    'title': 'Weight & Capacity',
                    'icon': '⚖️',
                    'description': 'Some things are heavy, some are light! Capacity tells us how much fits inside.',
                    'difficulty': 'easy',
                    'year': 'Year 1 (Ages 5-6)',
                    'lessons': [
                        'Heavy vs light objects',
                        'Using balance scales',
                        'Kilograms and grams',
                        'Full, empty, half full',
                        'Litres and millilitres'
                    ],
                    'activities': [
                        'Balance scale experiments',
                        'Sort objects by weight',
                        'Measuring water in containers'
                    ]
                },
                {
                    'id': 'position-direction',
                    'title': 'Position & Direction',
                    'icon': '🧭',
                    'description': 'Where is the treasure? Learn about left, right, forwards, backwards!',
                    'difficulty': 'easy',
                    'year': 'Year 1 (Ages 5-6)',
                    'lessons': [
                        'Left and right directions',
                        'Up, down, forwards, backwards',
                        'Following simple directions',
                        'Map reading basics',
                        'Position words (next to, behind, in front)'
                    ],
                    'activities': [
                        'Treasure hunt with directions',
                        'Robot programming games',
                        'Following map directions'
                    ]
                },
                {
                    'id': '2d-3d-shapes',
                    'title': '2D & 3D Shapes',
                    'icon': '🔶',
                    'description': 'Flat shapes and solid shapes are everywhere! Explore circles, cubes, and more.',
                    'difficulty': 'medium',
                    'year': 'Year 2 (Ages 6-7)',
                    'lessons': [
                        '2D shapes: circle, square, triangle, rectangle',
                        '3D shapes: cube, sphere, cylinder, cone',
                        'Faces, edges, and vertices',
                        'Shape properties',
                        'Shapes in real life'
                    ],
                    'activities': [
                        'Shape hunt around the house',
                        'Build 3D shapes with blocks',
                        'Count faces and edges'
                    ]
                },
                {
                    'id': 'symmetry',
                    'title': 'Symmetry',
                    'icon': '🦋',
                    'description': 'Butterflies have symmetry! One half looks exactly like the other half.',
                    'difficulty': 'medium',
                    'year': 'Year 2 (Ages 6-7)',
                    'lessons': [
                        'Lines of symmetry',
                        'Symmetrical patterns',
                        'Mirror images',
                        'Creating symmetrical art',
                        'Finding symmetry in nature'
                    ],
                    'activities': [
                        'Complete the butterfly wing',
                        'Mirror drawing activities',
                        'Symmetry in letters and numbers'
                    ]
                },
                {
                    'id': 'data-handling-graphs',
                    'title': 'Data Handling & Graphs',
                    'icon': '📊',
                    'description': 'Collect information and make it into colourful charts and graphs!',
                    'difficulty': 'medium',
                    'year': 'Year 2 (Ages 6-7)',
                    'lessons': [
                        'Collecting data about favourite colours',
                        'Making bar charts',
                        'Reading pictograms',
                        'Tally charts for counting',
                        'Asking questions about data'
                    ],
                    'activities': [
                        'Class favourite pet survey',
                        'Create your own bar chart',
                        'Read weather pictograms'
                    ]
                },
                {
                    'id': 'sequences-patterns',
                    'title': 'Sequences & Patterns',
                    'icon': '🎨',
                    'description': 'Patterns are everywhere! Red, blue, red, blue... what comes next?',
                    'difficulty': 'easy',
                    'year': 'Year 1 (Ages 5-6)',
                    'lessons': [
                        'Colour patterns (red, blue, red, blue)',
                        'Shape patterns (circle, square, circle)',
                        'Number patterns (2, 4, 6, 8)',
                        'Creating your own patterns',
                        'Patterns in nature'
                    ],
                    'activities': [
                        'Complete the pattern puzzles',
                        'Make patterns with blocks',
                        'Find patterns on clothing'
                    ]
                },
                {
                    'id': 'problem-solving',
                    'title': 'Problem Solving',
                    'icon': '🧩',
                    'description': 'Use your maths skills to solve real problems! Like sharing sweets fairly.',
                    'difficulty': 'medium',
                    'year': 'Year 2 (Ages 6-7)',
                    'lessons': [
                        'Reading word problems carefully',
                        'Deciding which operation to use',
                        'Drawing pictures to help solve',
                        'Checking if answers make sense',
                        'Multi-step problems'
                    ],
                    'activities': [
                        'Shopping problems with money',
                        'Party planning maths',
                        'Playground sharing problems'
                    ]
                },
                {
                    'id': 'mental-maths-strategies',
                    'title': 'Mental Maths Strategies',
                    'icon': '🧠',
                    'description': 'Quick ways to work out sums in your head! No pencil needed.',
                    'difficulty': 'medium',
                    'year': 'Year 2 (Ages 6-7)',
                    'lessons': [
                        'Counting on from bigger numbers',
                        'Making 10 first (7+5 = 7+3+2)',
                        'Doubling and halving',
                        'Number bonds to 20',
                        'Quick addition tricks'
                    ],
                    'activities': [
                        'Speed counting games',
                        'Mental maths challenges',
                        'Number bond practice'
                    ]
                },
                {
                    'id': 'telling-time-digital',
                    'title': 'Telling Time (Digital & Analogue)',
                    'icon': '⏰',
                    'description': 'Digital clocks show numbers, analogue clocks have hands. Learn both!',
                    'difficulty': 'medium',
                    'year': 'Year 2 (Ages 6-7)',
                    'lessons': [
                        'Quarter past and quarter to',
                        'Reading digital displays',
                        'Matching analogue to digital times',
                        'AM and PM times',
                        'Duration (how long things take)'
                    ],
                    'activities': [
                        'Set the clock game',
                        'Daily schedule timing',
                        'Time matching puzzles'
                    ]
                },
                {
                    'id': 'real-life-maths',
                    'title': 'Real Life Maths',
                    'icon': '🏠',
                    'description': 'Maths is everywhere! In cooking, shopping, building, and playing.',
                    'difficulty': 'easy',
                    'year': 'Year 1-2 (Ages 5-7)',
                    'lessons': [
                        'Cooking measurements',
                        'Birthday party planning',
                        'Building with blocks',
                        'Garden maths',
                        'Sports and maths'
                    ],
                    'activities': [
                        'Recipe following activities',
                        'Plan a party for 8 friends',
                        'Measure ingredients for baking'
                    ]
                },
                {
                    'id': 'early-algebra',
                    'title': 'Early Algebra (What\'s Missing?)',
                    'icon': '❓',
                    'description': 'Sometimes numbers hide! Can you find the missing number? 5 + ? = 8',
                    'difficulty': 'medium',
                    'year': 'Year 2 (Ages 6-7)',
                    'lessons': [
                        'Finding missing numbers in sums',
                        'Balancing both sides',
                        'Function machines',
                        'Number sentences',
                        'Inverse operations'
                    ],
                    'activities': [
                        'Missing number detective games',
                        'Balance scale equations',
                        'Function machine puzzles'
                    ]
                },
                {
                    'id': 'estimation-rounding',
                    'title': 'Estimation & Rounding',
                    'icon': '🎯',
                    'description': 'Sometimes we don\'t need exact answers! About how many sweets are in the jar?',
                    'difficulty': 'medium',
                    'year': 'Year 2 (Ages 6-7)',
                    'lessons': [
                        'Estimating quantities',
                        'Rounding to nearest 10',
                        'About how many?',
                        'Close enough answers',
                        'Checking estimates'
                    ],
                    'activities': [
                        'Guess the number of beans',
                        'Rounding number games',
                        'Estimation challenges'
                    ]
                }
            ],
            'science': [
                {
                    'id': 'living-things',
                    'title': 'Living Things',
                    'icon': '🌱',
                    'description': 'Living things grow, move, and need food. Non-living things don\'t do these things.',
                    'difficulty': 'easy',
                    'year': 'Year 1 (Ages 5-6)',
                    'lessons': [
                        'Is a bird a living thing?',
                        'Animals that grow and move',
                        'Plants that need water',
                        'Rocks and toys don\'t grow',
                        'What makes something alive?'
                    ],
                    'activities': [
                        'Sort into Living or Not Living',
                        'Animal movement games',
                        'Plant growing experiments'
                    ]
                },
                {
                    'id': 'animals-including-humans',
                    'title': 'Animals, Including Humans',
                    'icon': '🐾',
                    'description': 'Animals are different! Some have fur, some have feathers. We have body parts that help us.',
                    'difficulty': 'easy',
                    'year': 'Year 1 (Ages 5-6)',
                    'lessons': [
                        'Animals with wings can fly',
                        'Fish live in water',
                        'Our body parts (head, arms, legs)',
                        'What animals eat',
                        'Where animals live'
                    ],
                    'activities': [
                        'Match animals to their homes',
                        'Body parts labeling game',
                        'Animal sounds matching'
                    ]
                },
                {
                    'id': 'plants',
                    'title': 'Plants',
                    'icon': '🌿',
                    'description': 'Plants grow from seeds! They need light, water, and warmth to be healthy.',
                    'difficulty': 'medium',
                    'year': 'Year 2 (Ages 6-7)',
                    'lessons': [
                        'Parts of a plant (root, stem, leaf, flower)',
                        'What plants need to grow',
                        'From seed to flower',
                        'Caring for plants',
                        'Plants make food from sunlight'
                    ],
                    'activities': [
                        'Label plant parts game',
                        'Plant growing simulation',
                        'Seed planting project'
                    ]
                }
            ],
            'english': [
                {
                    'id': 'phonics-fun',
                    'title': 'Phonics Fun',
                    'icon': '🔤',
                    'description': 'Sounds help us read and write! Let\'s learn our letter sounds and put them together.',
                    'difficulty': 'easy',
                    'year': 'Year 1 (Ages 5-6)',
                    'lessons': [
                        'Letter \'s\' makes the \'sss\' sound',
                        'Letter \'a\' with apple',
                        'Blending sounds: c-a-t = cat',
                        'Words that start with \'s\'',
                        'Fun with letter sounds'
                    ],
                    'activities': [
                        'Listen and find \'s\' words',
                        'Blend sounds to read words',
                        'Letter sound matching games'
                    ]
                },
                {
                    'id': 'capital-letters-full-stops',
                    'title': 'Capital Letters & Full Stops',
                    'icon': '✏️',
                    'description': 'Every sentence starts with a capital letter! We use a full stop at the end.',
                    'difficulty': 'easy',
                    'year': 'Year 1 (Ages 5-6)',
                    'lessons': [
                        'Big letters at the start',
                        'Full stops at the end',
                        'Making sentences look right',
                        'Capital letters for names',
                        'Practice writing sentences'
                    ],
                    'activities': [
                        'Drag capital letters to sentence starts',
                        'Add full stops to sentences',
                        'Fix the sentence games'
                    ]
                },
                {
                    'id': 'spelling-power',
                    'title': 'Spelling Power',
                    'icon': '📝',
                    'description': 'Let\'s learn new spelling rules! Like adding \'-ing\' to words.',
                    'difficulty': 'medium',
                    'year': 'Year 2 (Ages 6-7)',
                    'lessons': [
                        'Adding \'-ing\' to words',
                        'Tricky words like \'because\'',
                        'Spelling \'friend\' correctly',
                        'Word families and patterns',
                        'Common spelling mistakes'
                    ],
                    'activities': [
                        'Type missing letters in words',
                        'Spelling bee games',
                        'Word building challenges'
                    ]
                }
            ],

            'computing': [
                {
                    'id': 'what-is-computer',
                    'title': 'What is a Computer?',
                    'icon': '💻',
                    'description': 'Computers are clever machines that help us learn and play! They can be big or small.',
                    'difficulty': 'easy',
                    'year': 'Year 1 (Ages 5-6)',
                    'lessons': [
                        'Laptops, tablets, and phones',
                        'Screen, keyboard, and mouse',
                        'What computers help us do',
                        'Computers at home and school',
                        'Being careful with computers'
                    ],
                    'activities': [
                        'Point to computer parts',
                        'Find computers in pictures',
                        'Computer safety games'
                    ]
                },
                {
                    'id': 'simple-programming',
                    'title': 'Simple Programming (Sequences)',
                    'icon': '🤖',
                    'description': 'We can tell computers what to do using code! Sequence means putting instructions in order.',
                    'difficulty': 'medium',
                    'year': 'Year 2 (Ages 6-7)',
                    'lessons': [
                        'Step-by-step instructions',
                        'Making a character move',
                        'Putting commands in order',
                        'If this, then that',
                        'Simple coding blocks'
                    ],
                    'activities': [
                        'Drag code blocks in order',
                        'Move robot across grid',
                        'Sequence building games'
                    ]
                }
            ]
        }
    }
    
    return curriculum_map.get(subject, {}).get(level, [])

@app.route('/curriculum-topics')
def curriculum_topics():
    level = request.args.get('level', 'highschool')
    subject = request.args.get('subject', 'maths')
    
    # Get curriculum topics based on level and subject
    curriculum_data = get_curriculum_topics(subject, level)
    
    return render_template('curriculum_topics.html', 
                         level=level, 
                         subject=subject,
                         curriculum_data=curriculum_data)



@app.route('/api/study-buddy-chat', methods=['POST'])
def study_buddy_chat():
    """AI Study Buddy chat endpoint"""
    try:
        data = request.get_json()
        user_message = data.get('message', '')
        context = data.get('context', [])
        
        if not user_message:
            return jsonify({'error': 'No message provided'}), 400
        
        # Generate AI response using Gemini
        from ai_content_generator import generate_study_buddy_response
        ai_response = generate_study_buddy_response(user_message, context)
        
        return jsonify({'response': ai_response})
        
    except Exception as e:
        app.logger.error(f"Error in study buddy chat: {e}")
        return jsonify({'error': 'Failed to generate response'}), 500

@app.route('/select_subject')
def select_subject():
    return render_template('index.html', step='subject')

@app.route('/select-style')
def select_style():
    subject = request.args.get('subject', 'maths')
    topic = request.args.get('topic', 'Numbers and Counting')
    
    # Ensure we have a valid subject
    if not subject:
        return redirect(url_for('index'))
    
    app.logger.info(f"Loading style selection for subject: {subject}, topic: {topic}")
    
    return render_template('index.html', 
                         step='style', 
                         subject=subject, 
                         topic=topic)

@app.route('/lesson')
def lesson():
    import html
    subject = request.args.get('subject')
    style = request.args.get('style')
    student_id = request.args.get('student_id', 'demo_student')
    topic = request.args.get('topic')
    
    # Fix URL encoding issues with topic parameter
    if topic:
        # Repeatedly unescape to handle multiple encodings
        while '&amp;' in topic:
            topic = html.unescape(topic)
    
    if not subject or not style:
        return redirect(url_for('index'))
    
    # Generate AI-powered content for all subjects including maths
    try:
        # For Primary 1 math "Numbers 1-10", use specialized content
        if subject == 'maths' and topic == 'Numbers 1-10':
            from ai_content_generator import create_primary1_math_content
            content = create_primary1_math_content(style, topic)
            app.logger.info(f"Generated Primary 1 content for {subject} - {style} - {topic}")
        else:
            content = generate_lesson_content(subject, style, topic or f'{subject.title()} Fundamentals')
            app.logger.info(f"Generated AI content for {subject} - {style} - {topic}")
            
        # Ensure content has all required learning styles
        if not content.get('visual'):
            content['visual'] = content.get(style, 'Visual content is being generated...')
        if not content.get('verbal'):
            content['verbal'] = content.get(style, 'Written content is being generated...')
        if not content.get('auditory'):
            content['auditory'] = content.get(style, 'Audio content is being generated...')
            
    except Exception as e:
        app.logger.error(f"Error generating AI content: {e}")
        # Fallback to basic content if AI fails
        content = {
            'title': f'Learning {subject.title()}: {topic or "General Topics"}',
            'visual': f'<h3>Visual Learning</h3><p>Educational content for {subject} is being prepared...</p>',
            'verbal': f'<h3>Verbal Learning</h3><p>Educational content for {subject} is being prepared...</p>',
            'auditory': f'<h3>Auditory Learning</h3><p>Educational content for {subject} is being prepared...</p>',
            'current_style': style
        }

    
    return render_template('lesson.html', 
                          subject=subject, 
                          style=style, 
                          content=content,
                          student_id=student_id)

def generate_math_topic_content(topic, style):
    """Generate specific content for each mathematics topic"""
    
    topic_content_map = {
        'numbers-to-20': {
            'title': f'Numbers to 20 ({style.title()} Style)',
            'examples': get_all_80_counting_examples()
        },
        'adding-subtracting-to-10': {
            'title': f'Adding & Subtracting to 10 ({style.title()} Style)',
            'examples': get_addition_subtraction_examples()
        },
        'shapes-patterns': {
            'title': f'Shapes & Patterns ({style.title()} Style)',
            'examples': get_shapes_patterns_examples()
        },
        'time-oclock-half-past': {
            'title': f'Time (O\'clock & Half Past) ({style.title()} Style)',
            'examples': get_time_examples()
        },
        'numbers-to-100': {
            'title': f'Numbers to 100 & Place Value ({style.title()} Style)',
            'examples': get_place_value_examples()
        },
        'multiplication-division': {
            'title': f'Multiplication & Division ({style.title()} Style)',
            'examples': get_multiplication_examples()
        },
        'fractions-halves-quarters': {
            'title': f'Fractions ({style.title()} Style)',
            'examples': get_fractions_examples()
        },
        'money-change': {
            'title': f'Money & Change ({style.title()} Style)',
            'examples': get_money_examples()
        },
        'measuring-length-height': {
            'title': f'Measuring Length & Height ({style.title()} Style)',
            'examples': get_measurement_examples()
        },
        'weight-capacity': {
            'title': f'Weight & Capacity ({style.title()} Style)',
            'examples': get_weight_capacity_examples()
        },
        'position-direction': {
            'title': f'Position & Direction ({style.title()} Style)',
            'examples': get_position_direction_examples()
        },
        '2d-3d-shapes': {
            'title': f'2D & 3D Shapes ({style.title()} Style)',
            'examples': get_2d_3d_shapes_examples()
        },
        'symmetry': {
            'title': f'Symmetry ({style.title()} Style)',
            'examples': get_symmetry_examples()
        },
        'data-handling-graphs': {
            'title': f'Data Handling & Graphs ({style.title()} Style)',
            'examples': get_data_graphs_examples()
        },
        'sequences-patterns': {
            'title': f'Sequences & Patterns ({style.title()} Style)',
            'examples': get_sequences_examples()
        },
        'problem-solving': {
            'title': f'Problem Solving ({style.title()} Style)',
            'examples': get_problem_solving_examples()
        },
        'mental-maths-strategies': {
            'title': f'Mental Maths Strategies ({style.title()} Style)',
            'examples': get_mental_maths_examples()
        },
        'telling-time-digital': {
            'title': f'Telling Time (Digital & Analogue) ({style.title()} Style)',
            'examples': get_digital_time_examples()
        },
        'real-life-maths': {
            'title': f'Real Life Maths ({style.title()} Style)',
            'examples': get_real_life_maths_examples()
        },
        'early-algebra': {
            'title': f'Early Algebra ({style.title()} Style)',
            'examples': get_early_algebra_examples()
        },
        'estimation-rounding': {
            'title': f'Estimation & Rounding ({style.title()} Style)',
            'examples': get_estimation_examples()
        }
    }
    
    content = topic_content_map.get(topic)
    if content:
        return {
            'title': content['title'],
            'subject': 'maths',
            'topic': topic,
            'style': style,
            'examples': content['examples'],
            'total_questions': len(content['examples']),
            'current_question': 1
        }
    return None

def get_addition_subtraction_examples():
    """Return addition and subtraction examples for ages 5-6"""
    return [
        {
            'id': 1,
            'title': 'Adding Apples',
            'instruction': 'Let\'s add apples together! Count all the apples.',
            'task': 'I have 3 red apples and 2 green apples. How many apples do I have altogether?',
            'visual_aid': 'Picture showing 3 red apples + 2 green apples.',
            'expected_answer': 'Student types 5 or taps 5.'
        },
        {
            'id': 2,
            'title': 'Taking Away Toys',
            'instruction': 'Sometimes we take toys away. Let\'s see how many are left.',
            'task': 'There were 6 toy cars. 2 cars drove away. How many cars are left?',
            'visual_aid': 'Picture of 6 cars, then 2 cars moving away.',
            'expected_answer': 'Student types 4.'
        },
        {
            'id': 3,
            'title': 'Adding with Fingers',
            'instruction': 'Use your fingers to help you add!',
            'task': 'Show 4 fingers on one hand and 3 fingers on the other. How many fingers altogether?',
            'visual_aid': 'Two hands showing 4 and 3 fingers.',
            'expected_answer': 'Student types 7.'
        },
        {
            'id': 4,
            'title': 'Subtracting Balloons',
            'instruction': 'Oh no! Some balloons flew away!',
            'task': 'There were 8 balloons. 3 balloons flew away. How many balloons are left?',
            'visual_aid': 'Picture of 8 balloons, then 3 flying away.',
            'expected_answer': 'Student types 5.'
        },
        {
            'id': 5,
            'title': 'Adding Animals on the Farm',
            'instruction': 'Let\'s count all the farm animals together!',
            'task': '2 cows + 4 sheep = ? animals',
            'visual_aid': 'Farm scene with 2 cows and 4 sheep.',
            'expected_answer': 'Student types 6.'
        }
    ]

def get_shapes_patterns_examples():
    """Return shapes and patterns examples"""
    return [
        {
            'id': 1,
            'title': 'Circle Hunt',
            'instruction': 'Circles are round! Let\'s find circles around us.',
            'task': 'Look at this picture. How many circles can you find?',
            'visual_aid': 'Picture with wheels, clock, and ball (3 circles).',
            'expected_answer': 'Student taps each circle and counts 3.'
        },
        {
            'id': 2,
            'title': 'Square Windows',
            'instruction': 'Squares have 4 equal sides!',
            'task': 'Count how many square windows you can see on this house.',
            'visual_aid': 'House drawing with 4 square windows.',
            'expected_answer': 'Student types 4.'
        },
        {
            'id': 3,
            'title': 'Triangle Roofs',
            'instruction': 'Triangles have 3 sides and look like roof tops!',
            'task': 'How many triangle roofs can you see?',
            'visual_aid': 'Row of houses with triangle roofs.',
            'expected_answer': 'Student counts the triangular roofs.'
        },
        {
            'id': 4,
            'title': 'Colour Pattern Fun',
            'instruction': 'Patterns repeat! Red, blue, red, blue...',
            'task': 'What colour comes next? Red, Blue, Red, Blue, ?',
            'visual_aid': 'Coloured blocks showing the pattern.',
            'expected_answer': 'Student taps Red.'
        },
        {
            'id': 5,
            'title': 'Shape Pattern Challenge',
            'instruction': 'Shapes can make patterns too!',
            'task': 'Circle, Square, Circle, Square, ?',
            'visual_aid': 'Shape sequence with one missing.',
            'expected_answer': 'Student taps Circle.'
        }
    ]

def get_time_examples():
    """Return time telling examples"""
    return [
        {
            'id': 1,
            'title': 'Breakfast Time',
            'instruction': 'We eat breakfast in the morning at 8 o\'clock!',
            'task': 'What time does this clock show?',
            'visual_aid': 'Clock showing 8:00 with breakfast picture.',
            'expected_answer': 'Student types 8 o\'clock.'
        },
        {
            'id': 2,
            'title': 'Lunch Time',
            'instruction': 'When the big hand points to 12 and little hand points to 12, it\'s 12 o\'clock!',
            'task': 'What time is lunch?',
            'visual_aid': 'Clock showing 12:00 with lunch picture.',
            'expected_answer': 'Student types 12 o\'clock.'
        },
        {
            'id': 3,
            'title': 'Half Past Playtime',
            'instruction': 'Half past means the big hand points to 6!',
            'task': 'What time does this clock show?',
            'visual_aid': 'Clock showing 3:30.',
            'expected_answer': 'Student types half past 3.'
        },
        {
            'id': 4,
            'title': 'Bedtime Story',
            'instruction': 'Bedtime is at 7 o\'clock in the evening!',
            'task': 'Draw the hands on the clock to show 7 o\'clock.',
            'visual_aid': 'Empty clock face for student to complete.',
            'expected_answer': 'Student draws hands correctly.'
        },
        {
            'id': 5,
            'title': 'School Time',
            'instruction': 'School starts at half past 8!',
            'task': 'Which clock shows half past 8?',
            'visual_aid': 'Three clocks - student picks the correct one.',
            'expected_answer': 'Student taps the clock showing 8:30.'
        }
    ]

def get_place_value_examples():
    """Return place value examples for larger numbers"""
    return [
        {
            'id': 1,
            'title': 'Tens and Ones with Blocks',
            'instruction': 'In the number 23, the 2 means 2 tens and the 3 means 3 ones.',
            'task': 'How many tens are in the number 35?',
            'visual_aid': '3 bundles of 10 blocks + 5 single blocks.',
            'expected_answer': 'Student types 3.'
        },
        {
            'id': 2,
            'title': 'Building Number 47',
            'instruction': 'Let\'s build numbers with tens and ones!',
            'task': 'Use blocks to build 47. How many tens do you need?',
            'visual_aid': 'Blocks showing 4 tens and 7 ones.',
            'expected_answer': 'Student types 4.'
        },
        {
            'id': 3,
            'title': 'Counting to 100',
            'instruction': 'Let\'s count all the way to 100!',
            'task': 'What number comes after 89?',
            'visual_aid': 'Number sequence: 87, 88, 89, ?',
            'expected_answer': 'Student types 90.'
        },
        {
            'id': 4,
            'title': 'Number Hunt to 50',
            'instruction': 'Find the number on the hundred square!',
            'task': 'Point to the number 34 on the grid.',
            'visual_aid': 'Hundred square grid.',
            'expected_answer': 'Student taps 34.'
        },
        {
            'id': 5,
            'title': 'Comparing Big Numbers',
            'instruction': 'Which number is bigger: 27 or 35?',
            'task': 'Circle the larger number.',
            'visual_aid': 'Two numbers displayed: 27 and 35.',
            'expected_answer': 'Student circles 35.'
        }
    ]

def get_multiplication_examples():
    """Return multiplication and division examples"""
    return [
        {
            'id': 1,
            'title': 'Groups of 2 Shoes',
            'instruction': 'Multiplication is like counting groups quickly!',
            'task': '3 groups of 2 shoes. How many shoes altogether?',
            'visual_aid': '3 pairs of shoes (6 shoes total).',
            'expected_answer': 'Student types 6.'
        },
        {
            'id': 2,
            'title': 'Times Tables for 5',
            'instruction': 'Let\'s learn the 5 times table!',
            'task': '2 × 5 = ?',
            'visual_aid': '2 hands showing 5 fingers each.',
            'expected_answer': 'Student types 10.'
        },
        {
            'id': 3,
            'title': 'Sharing Cookies Equally',
            'instruction': 'Division means sharing fairly!',
            'task': '12 cookies shared between 3 children. How many cookies does each child get?',
            'visual_aid': '12 cookies divided into 3 equal groups.',
            'expected_answer': 'Student types 4.'
        },
        {
            'id': 4,
            'title': 'Arrays of Sweets',
            'instruction': 'Sweets in rows help us multiply!',
            'task': '4 rows of 5 sweets. How many sweets in total?',
            'visual_aid': '4 × 5 array of sweets.',
            'expected_answer': 'Student types 20.'
        },
        {
            'id': 5,
            'title': 'Ten Times Table',
            'instruction': 'Multiplying by 10 is easy - just add a zero!',
            'task': '3 × 10 = ?',
            'visual_aid': '3 groups of 10 objects.',
            'expected_answer': 'Student types 30.'
        }
    ]

def get_fractions_examples():
    """Return fractions examples"""
    return [
        {
            'id': 1,
            'title': 'Half a Pizza',
            'instruction': 'Half means 1 out of 2 equal parts!',
            'task': 'Colour half of this pizza.',
            'visual_aid': 'Pizza divided into 2 equal parts.',
            'expected_answer': 'Student colours one half.'
        },
        {
            'id': 2,
            'title': 'Quarter of a Cake',
            'instruction': 'A quarter is 1 out of 4 equal parts!',
            'task': 'How many quarters make a whole cake?',
            'visual_aid': 'Cake divided into 4 equal parts.',
            'expected_answer': 'Student types 4.'
        },
        {
            'id': 3,
            'title': 'Third of a Chocolate Bar',
            'instruction': 'A third is 1 out of 3 equal parts!',
            'task': 'Shade one third of this chocolate bar.',
            'visual_aid': 'Chocolate bar with 3 equal sections.',
            'expected_answer': 'Student shades one section.'
        },
        {
            'id': 4,
            'title': 'Half of 8 Sweets',
            'instruction': 'Half of a group means divide by 2!',
            'task': 'What is half of 8 sweets?',
            'visual_aid': '8 sweets divided into 2 equal groups.',
            'expected_answer': 'Student types 4.'
        },
        {
            'id': 5,
            'title': 'Finding Halves and Quarters',
            'instruction': 'Can you spot the fractions?',
            'task': 'Which shape shows a quarter?',
            'visual_aid': 'Three shapes - one showing 1/2, one showing 1/4, one showing 1/3.',
            'expected_answer': 'Student taps the shape showing 1/4.'
        }
    ]

def get_money_examples():
    """Return money and change examples"""
    return [
        {
            'id': 1,
            'title': 'UK Coins Recognition',
            'instruction': 'Let\'s learn about British coins!',
            'task': 'Which coin is worth 10p?',
            'visual_aid': 'Pictures of 1p, 5p, 10p, 20p coins.',
            'expected_answer': 'Student taps the 10p coin.'
        },
        {
            'id': 2,
            'title': 'Counting Pennies',
            'instruction': 'Count your pennies to see how much money you have!',
            'task': 'How much money is this? 5p + 2p + 1p',
            'visual_aid': 'Three coins: 5p, 2p, 1p.',
            'expected_answer': 'Student types 8p.'
        },
        {
            'id': 3,
            'title': 'Shopping for Toys',
            'instruction': 'Let\'s go shopping! How much does it cost?',
            'task': 'A ball costs 15p. How many 5p coins do you need?',
            'visual_aid': 'Picture of ball with 15p price tag.',
            'expected_answer': 'Student types 3.'
        },
        {
            'id': 4,
            'title': 'Making 20p',
            'instruction': 'There are different ways to make 20p!',
            'task': 'Show me two 10p coins that make 20p.',
            'visual_aid': 'Collection of coins to choose from.',
            'expected_answer': 'Student selects two 10p coins.'
        },
        {
            'id': 5,
            'title': 'Pocket Money Saving',
            'instruction': 'Save your pocket money in your piggy bank!',
            'task': 'You have 25p and you spend 10p. How much money do you have left?',
            'visual_aid': 'Piggy bank and coins showing the calculation.',
            'expected_answer': 'Student types 15p.'
        }
    ]

def get_measurement_examples():
    """Return measurement examples"""
    return [
        {
            'id': 1,
            'title': 'Measuring Your Pencil',
            'instruction': 'Use a ruler to measure how long things are!',
            'task': 'This pencil is 12 cm long. How many centimetres is that?',
            'visual_aid': 'Picture of pencil next to ruler showing 12 cm.',
            'expected_answer': 'Student types 12.'
        },
        {
            'id': 2,
            'title': 'Comparing Heights',
            'instruction': 'Some things are taller, some are shorter!',
            'task': 'Which is taller: a chair or a table?',
            'visual_aid': 'Picture showing chair and table side by side.',
            'expected_answer': 'Student taps table.'
        },
        {
            'id': 3,
            'title': 'Hand Span Measuring',
            'instruction': 'Your hand can be a measuring tool too!',
            'task': 'How many hand spans wide is your desk?',
            'visual_aid': 'Picture showing hands measuring desk width.',
            'expected_answer': 'Student measures and records answer.'
        },
        {
            'id': 4,
            'title': 'Metres and Centimetres',
            'instruction': '100 centimetres make 1 metre!',
            'task': 'Is your classroom longer than 5 metres?',
            'visual_aid': 'Classroom with metre ruler for scale.',
            'expected_answer': 'Student observes and answers yes/no.'
        },
        {
            'id': 5,
            'title': 'Longest and Shortest',
            'instruction': 'Put these objects in order from shortest to longest!',
            'task': 'Order: crayon, book, ruler',
            'visual_aid': 'Three objects to arrange by length.',
            'expected_answer': 'Student drags: crayon, ruler, book.'
        }
    ]

def get_weight_capacity_examples():
    """Return weight and capacity examples"""
    return [
        {
            'id': 1,
            'title': 'Heavy or Light?',
            'instruction': 'Some things are heavy, some are light!',
            'task': 'Which is heavier: a feather or a book?',
            'visual_aid': 'Balance scale with feather and book.',
            'expected_answer': 'Student taps book.'
        },
        {
            'id': 2,
            'title': 'Balance Scale Fun',
            'instruction': 'Balance scales help us compare weights!',
            'task': 'If 3 apples balance with 1 orange, which weighs more?',
            'visual_aid': 'Balance scale showing 3 apples = 1 orange.',
            'expected_answer': 'Student taps orange.'
        },
        {
            'id': 3,
            'title': 'Full, Empty, Half Full',
            'instruction': 'Containers can hold different amounts!',
            'task': 'Which jar is half full?',
            'visual_aid': 'Three jars: empty, half full, completely full.',
            'expected_answer': 'Student taps the half-full jar.'
        },
        {
            'id': 4,
            'title': 'Water in Cups',
            'instruction': 'Let\'s measure how much water fits!',
            'task': 'How many small cups fill one big jug?',
            'visual_aid': 'Big jug with 4 small cups beside it.',
            'expected_answer': 'Student types 4.'
        },
        {
            'id': 5,
            'title': 'Sorting by Weight',
            'instruction': 'Put these items in order from lightest to heaviest!',
            'task': 'Order: balloon, apple, brick',
            'visual_aid': 'Three objects to sort by weight.',
            'expected_answer': 'Student arranges: balloon, apple, brick.'
        }
    ]

def get_position_direction_examples():
    """Return position and direction examples"""
    return [
        {
            'id': 1,
            'title': 'Left and Right Hands',
            'instruction': 'Your left hand is on the same side as your heart!',
            'task': 'Raise your right hand!',
            'visual_aid': 'Picture of child with hands clearly labeled.',
            'expected_answer': 'Student follows instruction.'
        },
        {
            'id': 2,
            'title': 'Treasure Map Directions',
            'instruction': 'Follow the directions to find the treasure!',
            'task': 'Go forward 3 steps, turn left, go forward 2 steps. Where is the treasure?',
            'visual_aid': 'Simple map with path marked.',
            'expected_answer': 'Student follows path and finds treasure.'
        },
        {
            'id': 3,
            'title': 'Position Words',
            'instruction': 'Where is the cat?',
            'task': 'The cat is _____ the box. (under, on, beside)',
            'visual_aid': 'Picture of cat in different positions relative to box.',
            'expected_answer': 'Student chooses correct position word.'
        },
        {
            'id': 4,
            'title': 'Robot Programming',
            'instruction': 'Program the robot to reach the star!',
            'task': 'Which directions: Forward, Right, Forward, Forward?',
            'visual_aid': 'Grid with robot and star, showing path.',
            'expected_answer': 'Student programs correct sequence.'
        },
        {
            'id': 5,
            'title': 'Classroom Map',
            'instruction': 'Where are different things in your classroom?',
            'task': 'The whiteboard is at the _____ of the classroom.',
            'visual_aid': 'Classroom layout diagram.',
            'expected_answer': 'Student identifies front/back/side.'
        }
    ]

def get_2d_3d_shapes_examples():
    """Return 2D and 3D shapes examples"""
    return [
        {
            'id': 1,
            'title': '2D Shape Detective',
            'instruction': '2D shapes are flat like paper!',
            'task': 'Find all the rectangles in this picture.',
            'visual_aid': 'Scene with various 2D shapes hidden in objects.',
            'expected_answer': 'Student taps all rectangles.'
        },
        {
            'id': 2,
            'title': '3D Shape Hunt',
            'instruction': '3D shapes are solid - you can hold them!',
            'task': 'Which objects are shaped like a cylinder?',
            'visual_aid': 'Collection of 3D objects including cans, boxes, balls.',
            'expected_answer': 'Student selects cylindrical objects.'
        },
        {
            'id': 3,
            'title': 'Counting Faces',
            'instruction': 'A face is a flat side of a 3D shape!',
            'task': 'How many faces does a cube have?',
            'visual_aid': 'Cube with faces highlighted and numbered.',
            'expected_answer': 'Student counts and types 6.'
        },
        {
            'id': 4,
            'title': 'Shape Building Challenge',
            'instruction': 'Build shapes using blocks!',
            'task': 'Use 6 blocks to build a rectangular prism.',
            'visual_aid': 'Virtual blocks to arrange into shape.',
            'expected_answer': 'Student builds correct shape.'
        },
        {
            'id': 5,
            'title': 'Real World Shapes',
            'instruction': 'Shapes are everywhere around us!',
            'task': 'What 3D shape is a ball?',
            'visual_aid': 'Various balls and spherical objects.',
            'expected_answer': 'Student identifies sphere.'
        }
    ]

def get_symmetry_examples():
    """Return symmetry examples"""
    return [
        {
            'id': 1,
            'title': 'Butterfly Wings',
            'instruction': 'Symmetry means both halves look exactly the same!',
            'task': 'Complete the other wing of the butterfly.',
            'visual_aid': 'Half butterfly for student to complete.',
            'expected_answer': 'Student draws matching wing pattern.'
        },
        {
            'id': 2,
            'title': 'Mirror Drawing',
            'instruction': 'Imagine there\'s a mirror down the middle!',
            'task': 'Draw the missing half of this face.',
            'visual_aid': 'Half face outline for completion.',
            'expected_answer': 'Student draws symmetrical features.'
        },
        {
            'id': 3,
            'title': 'Letter Symmetry',
            'instruction': 'Some letters have symmetry!',
            'task': 'Which letters look the same in a mirror: A, B, C?',
            'visual_aid': 'Letters A, B, C with mirror line.',
            'expected_answer': 'Student identifies A as symmetrical.'
        },
        {
            'id': 4,
            'title': 'Pattern Symmetry',
            'instruction': 'Patterns can be symmetrical too!',
            'task': 'Complete this symmetrical pattern.',
            'visual_aid': 'Half pattern of shapes and colours.',
            'expected_answer': 'Student completes matching pattern.'
        },
        {
            'id': 5,
            'title': 'Nature\'s Symmetry',
            'instruction': 'Find symmetry in nature!',
            'task': 'Is this leaf symmetrical?',
            'visual_aid': 'Various leaves, some symmetrical, some not.',
            'expected_answer': 'Student identifies symmetrical leaves.'
        }
    ]

def get_data_graphs_examples():
    """Return data and graphs examples"""
    return [
        {
            'id': 1,
            'title': 'Favourite Pet Survey',
            'instruction': 'Let\'s collect information about favourite pets!',
            'task': 'Count: 5 like dogs, 3 like cats, 2 like fish. Which pet is most popular?',
            'visual_aid': 'Simple bar chart showing pet preferences.',
            'expected_answer': 'Student identifies dogs as most popular.'
        },
        {
            'id': 2,
            'title': 'Weather Chart',
            'instruction': 'We can show weather information in pictures!',
            'task': 'How many sunny days were there this week?',
            'visual_aid': 'Pictogram with sun, cloud, and rain symbols.',
            'expected_answer': 'Student counts sunny day symbols.'
        },
        {
            'id': 3,
            'title': 'Tally Marks for Counting',
            'instruction': 'Tally marks help us count quickly!',
            'task': 'How many children chose pizza? IIII IIII II',
            'visual_aid': 'Tally marks grouped in fives.',
            'expected_answer': 'Student counts to get 12.'
        },
        {
            'id': 4,
            'title': 'Making Our Own Chart',
            'instruction': 'Let\'s create a chart about favourite colours!',
            'task': 'If 4 children like red and 6 like blue, draw the bars.',
            'visual_aid': 'Empty bar chart template.',
            'expected_answer': 'Student draws correct bar heights.'
        },
        {
            'id': 5,
            'title': 'Reading a Pictogram',
            'instruction': 'Each picture represents a certain number!',
            'task': 'If each apple = 2 children, how many children like apples? 🍎🍎🍎',
            'visual_aid': 'Pictogram with apple symbols.',
            'expected_answer': 'Student calculates 6 children.'
        }
    ]

def get_sequences_examples():
    """Return sequences and patterns examples"""
    return [
        {
            'id': 1,
            'title': 'Number Sequence Detective',
            'instruction': 'What number comes next in the pattern?',
            'task': '2, 4, 6, 8, ?',
            'visual_aid': 'Number sequence with missing number.',
            'expected_answer': 'Student types 10.'
        },
        {
            'id': 2,
            'title': 'Shape Pattern Train',
            'instruction': 'All aboard the pattern train!',
            'task': '🔴🔵🔴🔵? What shape comes next?',
            'visual_aid': 'Train carriages with alternating shape pattern.',
            'expected_answer': 'Student selects red circle.'
        },
        {
            'id': 3,
            'title': 'Growing Patterns',
            'instruction': 'Some patterns grow bigger each time!',
            'task': 'How many blocks in the next tower? ■, ■■, ■■■, ?',
            'visual_aid': 'Towers getting taller by one block each time.',
            'expected_answer': 'Student types 4.'
        },
        {
            'id': 4,
            'title': 'Clapping Patterns',
            'instruction': 'Patterns can be sounds too!',
            'task': 'Clap the pattern: loud, soft, loud, soft, ?',
            'visual_aid': 'Visual representation of loud and soft claps.',
            'expected_answer': 'Student claps loud.'
        },
        {
            'id': 5,
            'title': 'Nature Patterns',
            'instruction': 'Patterns are everywhere in nature!',
            'task': 'What pattern do you see on this zebra?',
            'visual_aid': 'Picture of zebra with black and white stripes.',
            'expected_answer': 'Student identifies stripe pattern.'
        }
    ]

def get_problem_solving_examples():
    """Return problem solving examples"""
    return [
        {
            'id': 1,
            'title': 'Birthday Party Planning',
            'instruction': 'Let\'s solve a real problem step by step!',
            'task': '8 children are coming to the party. Each needs 2 party hats. How many hats do we need?',
            'visual_aid': 'Picture of children and party hats.',
            'expected_answer': 'Student calculates 16 hats.'
        },
        {
            'id': 2,
            'title': 'Sharing Playground Equipment',
            'instruction': 'How can we share fairly?',
            'task': '15 children want to use 3 swings. How many children per swing?',
            'visual_aid': 'Playground scene with swings and children.',
            'expected_answer': 'Student divides: 15 ÷ 3 = 5.'
        },
        {
            'id': 3,
            'title': 'Shopping Money Problem',
            'instruction': 'Do we have enough money to buy what we want?',
            'task': 'A toy costs 25p. You have 30p. How much change will you get?',
            'visual_aid': 'Toy with price tag and coins.',
            'expected_answer': 'Student calculates 5p change.'
        },
        {
            'id': 4,
            'title': 'Garden Growing Problem',
            'instruction': 'Help plan the school garden!',
            'task': 'If we plant 4 rows with 6 flowers each, how many flowers in total?',
            'visual_aid': 'Garden plot divided into rows.',
            'expected_answer': 'Student calculates 24 flowers.'
        },
        {
            'id': 5,
            'title': 'Lunchtime Problem',
            'instruction': 'Make sure everyone gets fed!',
            'task': 'There are 20 sandwiches for 25 children. How many more sandwiches do we need?',
            'visual_aid': 'Sandwiches and children illustration.',
            'expected_answer': 'Student calculates 5 more needed.'
        }
    ]

def get_mental_maths_examples():
    """Return mental maths strategy examples"""
    return [
        {
            'id': 1,
            'title': 'Counting On Strategy',
            'instruction': 'Start with the bigger number and count on!',
            'task': 'To solve 7 + 3, start at 7 and count on: 8, 9, 10',
            'visual_aid': 'Number line showing jumps from 7 to 10.',
            'expected_answer': 'Student practices counting on strategy.'
        },
        {
            'id': 2,
            'title': 'Making 10 First',
            'instruction': 'Break numbers to make 10, then add the rest!',
            'task': '8 + 5 = ? Think: 8 + 2 = 10, then 10 + 3 = 13',
            'visual_aid': 'Visual showing 5 split into 2 + 3.',
            'expected_answer': 'Student applies make-10 strategy.'
        },
        {
            'id': 3,
            'title': 'Doubles Facts',
            'instruction': 'Use doubles you know to solve near doubles!',
            'task': 'What is 6 + 7? Think: 6 + 6 = 12, so 6 + 7 = 13',
            'visual_aid': 'Dominoes showing double 6 plus one more.',
            'expected_answer': 'Student uses doubles strategy.'
        },
        {
            'id': 4,
            'title': 'Number Bonds to 10',
            'instruction': 'Quick pairs that make 10!',
            'task': 'Fill in: 4 + ___ = 10, 7 + ___ = 10',
            'visual_aid': 'Ten frame showing different combinations.',
            'expected_answer': 'Student completes: 4 + 6 = 10, 7 + 3 = 10.'
        },
        {
            'id': 5,
            'title': 'Skip Counting by 2s',
            'instruction': 'Count by 2s to find totals quickly!',
            'task': 'Count these pairs of socks: 2, 4, 6, 8, 10',
            'visual_aid': '5 pairs of socks arranged in a row.',
            'expected_answer': 'Student skip counts to find total.'
        }
    ]

def get_digital_time_examples():
    """Return digital and analogue time examples"""
    return [
        {
            'id': 1,
            'title': 'Reading Digital Clocks',
            'instruction': 'Digital clocks show time with numbers!',
            'task': 'What time does this digital clock show: 9:30?',
            'visual_aid': 'Digital clock display showing 9:30.',
            'expected_answer': 'Student reads: nine thirty or half past nine.'
        },
        {
            'id': 2,
            'title': 'Quarter Past Times',
            'instruction': 'Quarter past means 15 minutes after the hour!',
            'task': 'Draw hands to show quarter past 2.',
            'visual_aid': 'Clock face for student to complete.',
            'expected_answer': 'Student draws hands at 2:15.'
        },
        {
            'id': 3,
            'title': 'Quarter To Times',
            'instruction': 'Quarter to means 15 minutes before the hour!',
            'task': 'What time is quarter to 5?',
            'visual_aid': 'Clock showing 4:45.',
            'expected_answer': 'Student identifies 4:45 or quarter to 5.'
        },
        {
            'id': 4,
            'title': 'AM and PM',
            'instruction': 'AM is morning, PM is afternoon and evening!',
            'task': 'Is 3:00 AM or 3:00 PM better for lunch?',
            'visual_aid': 'Pictures of morning and afternoon activities.',
            'expected_answer': 'Student chooses 3:00 PM.'
        },
        {
            'id': 5,
            'title': 'Duration - How Long?',
            'instruction': 'How much time passes between two times?',
            'task': 'From 2:00 to 4:00, how many hours pass?',
            'visual_aid': 'Two clocks showing start and end times.',
            'expected_answer': 'Student calculates 2 hours.'
        }
    ]

def get_real_life_maths_examples():
    """Return real life mathematics examples"""
    return [
        {
            'id': 1,
            'title': 'Cooking with Measurements',
            'instruction': 'Cooking uses lots of maths!',
            'task': 'Recipe needs 2 cups flour. We have 1 cup. How much more do we need?',
            'visual_aid': 'Measuring cups and flour.',
            'expected_answer': 'Student calculates 1 more cup needed.'
        },
        {
            'id': 2,
            'title': 'Party Planning Numbers',
            'instruction': 'Planning a party needs counting and adding!',
            'task': '8 friends coming to party. 3 cupcakes per person. How many cupcakes total?',
            'visual_aid': 'Party table with cupcakes and guests.',
            'expected_answer': 'Student calculates 24 cupcakes.'
        },
        {
            'id': 3,
            'title': 'Garden Maths',
            'instruction': 'Gardens are full of patterns and numbers!',
            'task': 'Plant flowers in 4 rows of 5. How many flowers total?',
            'visual_aid': 'Garden plot divided into rows.',
            'expected_answer': 'Student calculates 20 flowers.'
        },
        {
            'id': 4,
            'title': 'Shopping with Money',
            'instruction': 'Shopping teaches us about money and change!',
            'task': 'Toy costs 15p. You pay with 20p. How much change?',
            'visual_aid': 'Toy with price tag and coins.',
            'expected_answer': 'Student calculates 5p change.'
        },
        {
            'id': 5,
            'title': 'Sports Scores',
            'instruction': 'Sports involve lots of counting and adding!',
            'task': 'Team scored 3 goals in first half, 2 in second. Total goals?',
            'visual_aid': 'Football goals and scoreboard.',
            'expected_answer': 'Student adds to get 5 total goals.'
        }
    ]

def get_early_algebra_examples():
    """Return early algebra examples"""
    return [
        {
            'id': 1,
            'title': 'Missing Number Addition',
            'instruction': 'Find the mystery number!',
            'task': '5 + ? = 8. What number is missing?',
            'visual_aid': 'Balance scale with 5 + ? on one side, 8 on other.',
            'expected_answer': 'Student finds missing number is 3.'
        },
        {
            'id': 2,
            'title': 'Function Machine',
            'instruction': 'The machine follows a rule!',
            'task': 'Rule: Add 4. Input 3, Output ?',
            'visual_aid': 'Function machine showing +4 rule.',
            'expected_answer': 'Student calculates output is 7.'
        },
        {
            'id': 3,
            'title': 'Balance Equations',
            'instruction': 'Both sides must be equal!',
            'task': '6 = 2 + ? What makes both sides equal?',
            'visual_aid': 'Balance scales showing equation.',
            'expected_answer': 'Student finds ? = 4.'
        },
        {
            'id': 4,
            'title': 'Number Patterns',
            'instruction': 'Follow the pattern rule!',
            'task': '2, 4, 6, 8, ? What comes next?',
            'visual_aid': 'Number sequence with missing number.',
            'expected_answer': 'Student identifies pattern and answers 10.'
        },
        {
            'id': 5,
            'title': 'Inverse Operations',
            'instruction': 'Addition and subtraction are opposites!',
            'task': 'If 7 + 3 = 10, then 10 - 3 = ?',
            'visual_aid': 'Visual showing addition and subtraction relationship.',
            'expected_answer': 'Student applies inverse to get 7.'
        }
    ]

def get_estimation_examples():
    """Return estimation and rounding examples"""
    return [
        {
            'id': 1,
            'title': 'Estimate Quantities',
            'instruction': 'Make a good guess!',
            'task': 'About how many beans are in this jar? 10, 25, or 50?',
            'visual_aid': 'Jar filled with beans for estimation.',
            'expected_answer': 'Student makes reasonable estimate.'
        },
        {
            'id': 2,
            'title': 'Rounding to Nearest 10',
            'instruction': 'Round to the nearest 10!',
            'task': 'Round 27 to the nearest 10.',
            'visual_aid': 'Number line showing 20, 27, and 30.',
            'expected_answer': 'Student rounds to 30.'
        },
        {
            'id': 3,
            'title': 'About How Much?',
            'instruction': 'Sometimes "about" is good enough!',
            'task': 'About how much does this book cost? £2, £12, or £22?',
            'visual_aid': 'Book with £11.99 price tag.',
            'expected_answer': 'Student estimates about £12.'
        },
        {
            'id': 4,
            'title': 'Checking Estimates',
            'instruction': 'Check if your estimate was close!',
            'task': 'Estimated 20 sweets. Actually 23. Was estimate good?',
            'visual_aid': 'Estimated vs actual sweet counts.',
            'expected_answer': 'Student recognizes good estimate.'
        },
        {
            'id': 5,
            'title': 'Estimation Games',
            'instruction': 'Quick estimation is a useful skill!',
            'task': 'Estimate: About how many students in our class?',
            'visual_aid': 'Classroom scene for estimation.',
            'expected_answer': 'Student makes reasonable class size estimate.'
        }
    ]

def get_numbers_to_20_examples():
    """Return streamlined numbers to 20 examples"""
    return [
        {
            'id': 1,
            'title': 'Count the Farm Animals',
            'instruction': 'Look at the farm! How many animals can you count?',
            'task': 'Count all the cows in the picture.',
            'visual_aid': 'Picture showing 5 cartoon cows in a field.',
            'expected_answer': 'Student counts 5 cows.'
        },
        {
            'id': 2,
            'title': 'Number Recognition',
            'instruction': 'Match the dots to the correct number!',
            'task': 'How many dots do you see? Choose the right number.',
            'visual_aid': '7 colorful dots arranged in a pattern.',
            'expected_answer': 'Student identifies 7.'
        },
        {
            'id': 3,
            'title': 'Counting with Fingers',
            'instruction': 'Use your fingers to help you count!',
            'task': 'Show 8 fingers. How many fingers is that?',
            'visual_aid': 'Two hands showing 8 fingers clearly.',
            'expected_answer': 'Student shows 8 fingers and says 8.'
        },
        {
            'id': 4,
            'title': 'What Comes Next?',
            'instruction': 'Numbers go in order! What comes after this number?',
            'task': 'What number comes after 12?',
            'visual_aid': 'Number sequence: 10, 11, 12, ?',
            'expected_answer': 'Student answers 13.'
        },
        {
            'id': 5,
            'title': 'Counting Backwards',
            'instruction': 'Sometimes we count backwards! Like a rocket countdown!',
            'task': 'Count backwards from 15 to 10.',
            'visual_aid': 'Rocket with countdown numbers.',
            'expected_answer': 'Student counts: 15, 14, 13, 12, 11, 10.'
        }
    ]

def get_all_80_counting_examples():
    """Return all 80 counting and numbers examples - 30 original + 50 additional examples"""
    return [
        {
            'id': 1,
            'title': 'Count the Animals',
            'instruction': 'Look at the farm! How many animals can you count?',
            'task': 'Count all the cows in the picture.',
            'visual_aid': 'Image of 5 cartoon cows.',
            'expected_answer': "Student types '5' or taps a '5' button."
        },
        {
            'id': 2,
            'title': 'Number Recognition to 5',
            'instruction': 'Which number matches the dots?',
            'task': 'Tap the number that shows how many dots there are.',
            'visual_aid': 'Image of 3 dots and three number options: 2, 3, 4.',
            'expected_answer': "Student taps '3'."
        },
        {
            'id': 3,
            'title': 'Counting Fingers',
            'instruction': 'Use your fingers to help you count!',
            'task': 'Show 4 fingers. Now, how many fingers do you see in the picture?',
            'visual_aid': 'Image of a hand showing 4 fingers.',
            'expected_answer': "Student types '4'."
        },
        {
            'id': 4,
            'title': 'Counting Objects (Mixed)',
            'instruction': "Let's count all the different toys in the basket.",
            'task': 'Count how many toys are in the basket.',
            'visual_aid': 'Image of a basket with 6 mixed toys (e.g., ball, doll, car).',
            'expected_answer': "Student types '6'."
        },
        {
            'id': 5,
            'title': 'Number Before (to 10)',
            'instruction': 'What number comes just before this one?',
            'task': 'Type the number that comes before 7.',
            'visual_aid': "Large numeral '7'.",
            'expected_answer': "Student types '6'."
        },
        {
            'id': 6,
            'title': 'Number After (to 10)',
            'instruction': 'What number comes right after this one?',
            'task': 'Type the number that comes after 9.',
            'visual_aid': "Large numeral '9'.",
            'expected_answer': "Student types '10'."
        },
        {
            'id': 7,
            'title': 'Counting On from a Number',
            'instruction': 'Start at 5 and count on 3 more jumps!',
            'task': 'What number do you land on?',
            'visual_aid': 'Number line from 0-10 with an arrow starting at 5 and jumping 3 times.',
            'expected_answer': "Student types '8'."
        },
        {
            'id': 8,
            'title': 'Counting Backwards (from 10)',
            'instruction': "Let's count backwards like a rocket launch!",
            'task': 'What number comes before 5 when counting backwards from 10?',
            'visual_aid': 'Rocket countdown from 10.',
            'expected_answer': "Student types '4'."
        },
        {
            'id': 9,
            'title': 'Matching Number Words to Numerals (to 10)',
            'instruction': 'Draw a line from the word to the correct number.',
            'task': "Match 'four' to the numeral 4.",
            'visual_aid': 'Two columns: one with number words (one, two, three, four), one with numerals (4, 1, 3, 2).',
            'expected_answer': "Student drags 'four' to '4'."
        },
        {
            'id': 10,
            'title': 'Ordinal Numbers (First, Second, Third)',
            'instruction': 'Who finished first in the race?',
            'task': "Click on the animal that is in the 'second' position.",
            'visual_aid': "Image of 3 animals in a line, with '1st', '2nd', '3rd' labels.",
            'expected_answer': "Student taps the animal with '2nd' label."
        },
        {
            'id': 11,
            'title': 'Counting in 2s (Introduction)',
            'instruction': "Let's count the shoes! We can count them by 2s.",
            'task': 'Count in 2s: 2, 4, 6, ____, 10.',
            'visual_aid': 'Image of 5 pairs of shoes.',
            'expected_answer': "Student types '8'."
        },
        {
            'id': 12,
            'title': 'Counting in 5s (Introduction)',
            'instruction': 'Look at the stars on these flags. Each flag has 5 stars. Let\'s count them in 5s!',
            'task': 'Count in 5s: 5, 10, ____, 20.',
            'visual_aid': 'Image of 4 flags, each with 5 stars.',
            'expected_answer': "Student types '15'."
        },
        {
            'id': 13,
            'title': 'Counting in 10s (Introduction)',
            'instruction': 'These are bundles of 10 sticks. Let\'s count them in 10s!',
            'task': 'Count in 10s: 10, 20, 30, ____, 50.',
            'visual_aid': 'Image of 5 bundles of 10 sticks.',
            'expected_answer': "Student types '40'."
        },
        {
            'id': 14,
            'title': 'Number Line Missing Numbers (to 10)',
            'instruction': 'Some numbers are missing from this number line. Can you fill them in?',
            'task': 'Drag the correct numbers to fill the gaps: 1, 2, ___, 4, ___.',
            'visual_aid': 'Number line 1-5 with two blanks.',
            'expected_answer': "Student drags '3' and '5' to the correct spots."
        },
        {
            'id': 15,
            'title': 'Grouping Objects (Introduction to place value)',
            'instruction': 'Let\'s put these items into groups of ten.',
            'task': 'Count out 10 flowers and circle them. How many groups of 10 can you make?',
            'visual_aid': 'Image of 15 scattered flowers.',
            'expected_answer': "Student draws a circle around 10 flowers, then types '1' (group of 10)."
        },
        {
            'id': 16,
            'title': 'Comparing Numbers (More/Less to 10)',
            'instruction': 'Which group has more apples?',
            'task': 'Click on the basket with more apples.',
            'visual_aid': 'Image of two baskets: one with 7 apples, one with 4 apples.',
            'expected_answer': 'Student taps the basket with 7 apples.'
        },
        {
            'id': 17,
            'title': 'Ordering Numbers (Smallest to Largest to 10)',
            'instruction': 'Put these numbers in order, starting from the smallest.',
            'task': 'Drag the numbers 5, 2, 8 into the correct order.',
            'visual_aid': 'Three number blocks: 5, 2, 8.',
            'expected_answer': "Student drags blocks to form '2, 5, 8'."
        },
        {
            'id': 18,
            'title': 'Tally Marks (Introduction)',
            'instruction': 'Tally marks help us count quickly! Each group of four with a line through is 5.',
            'task': 'How many butterflies are shown with tally marks?',
            'visual_aid': 'Image of tally marks for 7 butterflies (IIII II).',
            'expected_answer': "Student types '7'."
        },
        {
            'id': 19,
            'title': 'Counting on from a Teen Number',
            'instruction': 'Let\'s count on from 14.',
            'task': 'What are the next two numbers after 14?',
            'visual_aid': "Numeral '14' and two empty boxes.",
            'expected_answer': "Student types '15, 16'."
        },
        {
            'id': 20,
            'title': 'Number Recognition to 20 (Mixed)',
            'instruction': 'Spot the numbers hiding in the picture!',
            'task': 'Click on the numbers 11, 16, and 20.',
            'visual_aid': 'A busy image with numbers 1-20 scattered within it.',
            'expected_answer': 'Student taps the correct numerals.'
        },
        {
            'id': 21,
            'title': 'Place Value (Tens and Ones to 50)',
            'instruction': 'Let\'s look at numbers bigger than 20. How many tens and ones are in 34?',
            'task': 'Fill in the blanks: 34 has ___ tens and ___ ones.',
            'visual_aid': 'Image of base ten blocks representing 34 (3 rods, 4 units).',
            'expected_answer': "Student types '3' and '4'."
        },
        {
            'id': 22,
            'title': 'Writing Numbers to 20',
            'instruction': 'Practice writing your numbers neatly!',
            'task': 'Trace the number 18, then write it by yourself.',
            'visual_aid': 'Dotted outline of the number 18 for tracing, then a blank space.',
            'expected_answer': "Student 'writes' 18 (e.g., using a touch screen or by typing)."
        },
        {
            'id': 23,
            'title': 'Even and Odd Numbers (Introduction)',
            'instruction': 'Even numbers can always be shared equally into two groups. Odd numbers always have one left over.',
            'task': 'Is the number 6 even or odd?',
            'visual_aid': 'Pairs of socks to illustrate even numbers (e.g., 6 socks as 3 pairs).',
            'expected_answer': "Student taps 'Even'."
        },
        {
            'id': 24,
            'title': 'Finding Missing Numbers in a Sequence (to 20)',
            'instruction': 'Help the number train get all its carriages!',
            'task': 'What number is missing from the train: 10, 11, ___, 13, 14?',
            'visual_aid': 'Image of a train with carriages showing numbers and one blank.',
            'expected_answer': "Student types '12'."
        },
        {
            'id': 25,
            'title': 'Counting up to 20 from any Number',
            'instruction': 'Start counting from 15. What are the next 3 numbers?',
            'task': 'Type the next three numbers in the sequence.',
            'visual_aid': "The number '15' displayed prominently.",
            'expected_answer': "Student types '16, 17, 18'."
        },
        {
            'id': 26,
            'title': 'Comparing Numbers (Greater Than/Less Than to 20)',
            'instruction': 'Use the hungry crocodile to pick the bigger number! The crocodile always eats the bigger number.',
            'task': 'Which number is greater: 12 or 17? Choose the correct crocodile sign (> or <).',
            'visual_aid': 'Two numbers (12 and 17) with the crocodile signs between them.',
            'expected_answer': "Student taps '<' (should tap '<' because 12 < 17)."
        },
        {
            'id': 27,
            'title': 'Ordering Numbers (Smallest to Largest to 20)',
            'instruction': 'Put these numbers in order from the smallest to the biggest.',
            'task': 'Drag the numbers 15, 8, 19, 11 into the correct order.',
            'visual_aid': 'Four number cards: 15, 8, 19, 11.',
            'expected_answer': "Student drags cards to form '8, 11, 15, 19'."
        },
        {
            'id': 28,
            'title': 'Number Bonds to 20 (Introduction)',
            'instruction': 'Can you find two numbers that add up to 20?',
            'task': 'If you have 15, how many more do you need to make 20?',
            'visual_aid': '20 frame with 15 dots filled.',
            'expected_answer': "Student types '5'."
        },
        {
            'id': 29,
            'title': 'Reading and Writing Number Words to 20',
            'instruction': 'Practice reading and writing the words for numbers.',
            'task': "Read the word 'sixteen' and then type the number.",
            'visual_aid': "The word 'sixteen' written clearly.",
            'expected_answer': "Student types '16'."
        },
        {
            'id': 30,
            'title': 'Counting Objects in Arrays (Basic)',
            'instruction': 'Sometimes objects are in neat rows. We can count them by rows or columns!',
            'task': 'How many cookies are there? (Image: 3 rows of 2 cookies)',
            'visual_aid': 'Image of 3 rows of 2 cookies.',
            'expected_answer': "Student types '6'."
        },
        # Additional 50 examples (31-80)
        {
            'id': 31,
            'title': 'Counting Fruit to 20',
            'instruction': 'The fruit basket is full! Can you count all the yummy fruits?',
            'task': 'Count the total number of fruits in the basket.',
            'visual_aid': 'A basket with 17 different fruits.',
            'expected_answer': 'Student types 17 or taps the number 17.'
        },
        {
            'id': 32,
            'title': 'Number Formation - Tracing 1-5',
            'instruction': 'Let us learn to write numbers neatly! Follow the dots to trace the number.',
            'task': 'Trace the number 3 using your finger or stylus.',
            'visual_aid': 'Large dotted outline of the numeral 3.',
            'expected_answer': 'Student successfully traces the number.'
        },
        {
            'id': 33,
            'title': 'Listen and Count',
            'instruction': 'Listen carefully to the sounds. How many sounds do you hear?',
            'task': 'Count the number of meows you hear.',
            'visual_aid': 'Play audio of 9 distinct meow sounds with a cute cat image.',
            'expected_answer': 'Student types 9 or taps the number 9.'
        },
        {
            'id': 34,
            'title': 'Number Between (to 20)',
            'instruction': 'A number is hiding between these two! Can you find it?',
            'task': 'Type the number that comes between 13 and 15.',
            'visual_aid': 'Number sequence: 13, blank box, 15.',
            'expected_answer': 'Student types 14.'
        },
        {
            'id': 35,
            'title': 'Place Value - Bundles of 10',
            'instruction': 'These are bundles of 10 sticks. How many tens and ones are there?',
            'task': 'Count the bundles of ten and the single sticks. How many sticks altogether?',
            'visual_aid': 'Image of 2 bundles of 10 sticks and 3 single sticks.',
            'expected_answer': 'Student types 23.'
        },
        {
            'id': 36,
            'title': 'Counting Steps',
            'instruction': 'Imagine you are walking. Each tap is one step!',
            'task': 'Tap the screen 12 times. What number did you get to?',
            'visual_aid': 'Screen shows a counter increasing with each tap, with footstep sounds.',
            'expected_answer': 'Student types 12.'
        },
        {
            'id': 37,
            'title': 'Missing Number in a Sequence (to 30)',
            'instruction': 'The number train has lost a carriage! Help fill the gap.',
            'task': 'What number is missing from the sequence: 25, 26, ___, 28?',
            'visual_aid': 'Train carriages with numbers 25, 26, blank, 28.',
            'expected_answer': 'Student types 27.'
        },
        {
            'id': 38,
            'title': 'Counting Backwards from 20',
            'instruction': 'Let us count backwards from 20 all the way to 10!',
            'task': 'Type the next number when counting backwards from 16.',
            'visual_aid': 'Audio of counting backwards from 20 with a descending number line.',
            'expected_answer': 'Student types 15.'
        },
        {
            'id': 39,
            'title': 'Grouping by 10s and 1s',
            'instruction': 'Look at these colourful beads. Group them into tens and ones.',
            'task': 'Drag the beads to form groups of 10, then count the ones left over.',
            'visual_aid': 'Scattered beads that snap into groups of 10 when dragged close.',
            'expected_answer': 'Student types 28.'
        },
        {
            'id': 40,
            'title': 'Number Recognition - Large Numbers to 50',
            'instruction': 'Which number is this? It is a bit bigger!',
            'task': 'Tap the correct number that is written.',
            'visual_aid': 'Large numeral 42 with voice saying Forty-two.',
            'expected_answer': 'Student taps 42 from multiple-choice options.'
        },
        {
            'id': 41,
            'title': 'Skip Counting Maze (2s)',
            'instruction': 'Help the bunny find the carrots by hopping on numbers that count by 2s!',
            'task': 'Tap the numbers in order, counting by 2s, to get the bunny to the carrot.',
            'visual_aid': 'A grid with numbers where tapping correct numbers moves the bunny.',
            'expected_answer': 'Student taps sequence: 2, 4, 6, 8, 10, 12.'
        },
        {
            'id': 42,
            'title': 'Comparing Numbers (More/Less to 20)',
            'instruction': 'Which jar has less sweets?',
            'task': 'Click on the jar that contains fewer sweets.',
            'visual_aid': 'Two jars, one with 18 sweets, one with 11 sweets.',
            'expected_answer': 'Student taps the jar with 11 sweets.'
        },
        {
            'id': 43,
            'title': 'Ordinal Numbers (Ordering Animals)',
            'instruction': 'The animals are lining up for a race! Who is third?',
            'task': 'Drag the animal that is in fifth place to the finish line.',
            'visual_aid': '7 cartoon animals in a line with starting points.',
            'expected_answer': 'Student drags the fifth animal.'
        },
        {
            'id': 44,
            'title': 'Counting Objects on a Tally Chart',
            'instruction': 'This tally chart shows how many favourite fruits people chose.',
            'task': 'Count the tally marks next to Apples and type the number.',
            'visual_aid': 'Tally chart with Apples (6 marks), Bananas (4 marks), Oranges (2 marks).',
            'expected_answer': 'Student types 6.'
        },
        {
            'id': 45,
            'title': 'Number Sentences (Fill the Blank)',
            'instruction': 'A number sentence has a missing part. Can you solve it?',
            'task': 'Fill in the missing number: 8, ___, 10, 11.',
            'visual_aid': 'Sequence with a blank box and voice reading the numbers.',
            'expected_answer': 'Student types 9.'
        },
        {
            'id': 46,
            'title': 'Counting Backwards from 30',
            'instruction': 'Imagine a countdown to a party! Count backwards from 30.',
            'task': 'What number comes just before 25 when counting backwards?',
            'visual_aid': 'Audio counting backwards from 30 with party scene.',
            'expected_answer': 'Student types 24.'
        },
        {
            'id': 47,
            'title': 'Even Numbers Discovery',
            'instruction': 'Even numbers are like pairs! You can always make two equal groups.',
            'task': 'Circle the even numbers from this list: 2, 5, 8, 11, 14.',
            'visual_aid': 'Numbers with small pairs of objects next to even numbers.',
            'expected_answer': 'Student taps 2, 8, 14.'
        },
        {
            'id': 48,
            'title': 'Odd Numbers Discovery',
            'instruction': 'Odd numbers always have one friend left over when you try to make pairs!',
            'task': 'Circle the odd numbers from this list: 3, 6, 9, 12, 17.',
            'visual_aid': 'Groups of objects with one left over for odd numbers.',
            'expected_answer': 'Student taps 3, 9, 17.'
        },
        {
            'id': 49,
            'title': 'Counting Dots on a Domino',
            'instruction': 'Dominoes have dots! Can you count the total number of dots?',
            'task': 'Count the dots on both sides of the domino.',
            'visual_aid': 'Image of a domino with 6 dots on one side and 5 on the other.',
            'expected_answer': 'Student types 11.'
        },
        {
            'id': 50,
            'title': 'Reading Number Words to 30',
            'instruction': 'Can you read this number word and find the correct number?',
            'task': 'Tap the number that matches the word twenty-four.',
            'visual_aid': 'The word twenty-four with multiple choice numbers 23, 24, 42.',
            'expected_answer': 'Student taps 24.'
        },
        {
            'id': 51,
            'title': 'Writing Number Words to 30',
            'instruction': 'You have seen the number, now write its word!',
            'task': 'Type the word for the number 18.',
            'visual_aid': 'Large numeral 18 with text input box.',
            'expected_answer': 'Student types eighteen.'
        },
        {
            'id': 52,
            'title': 'Counting Steps on a Game Board',
            'instruction': 'Imagine playing a board game. Count how many steps the character takes.',
            'task': 'The character moves 6 steps. What number does it land on if it starts at 10?',
            'visual_aid': 'Game board path with character at 10, drag 6 spaces forward.',
            'expected_answer': 'Student types 16.'
        },
        {
            'id': 53,
            'title': 'Number Line - Jumps of 10',
            'instruction': 'Let us make big jumps on the number line, counting by tens!',
            'task': 'Start at 0 and jump 4 times by 10s. Where do you land?',
            'visual_aid': 'Number line 0-50 with jumps of 10 marked.',
            'expected_answer': 'Student types 40.'
        },
        {
            'id': 54,
            'title': 'Estimating Quantities',
            'instruction': 'Without counting exactly, guess how many shiny gems are in the box.',
            'task': 'Make a guess. Is it more or less than 10? Then count to check.',
            'visual_aid': 'Box with approximately 8-12 scattered gems.',
            'expected_answer': 'Student types guess, then sees 11.'
        },
        {
            'id': 55,
            'title': 'Ordering Numbers (Largest to Smallest)',
            'instruction': 'Now, let us put numbers in order from the BIGGEST to the smallest!',
            'task': 'Drag the numbers 16, 9, 13, 20 into order from largest to smallest.',
            'visual_aid': 'Number cards that can be dragged into sequence.',
            'expected_answer': 'Student drags to form: 20, 16, 13, 9.'
        },
        {
            'id': 56,
            'title': 'Using a Hundred Square',
            'instruction': 'A hundred square helps us see numbers! Find a number and jump forwards.',
            'task': 'Start at 23. Jump forward 5 spaces. What number do you land on?',
            'visual_aid': 'Hundred square where students can tap/highlight cells.',
            'expected_answer': 'Student types 28.'
        },
        {
            'id': 57,
            'title': 'Number Recognition through Sound',
            'instruction': 'Listen carefully! What number is being spoken?',
            'task': 'Listen to the audio and tap the correct numeral.',
            'visual_aid': 'Audio voice saying seventeen with multiple choice 17, 7, 10.',
            'expected_answer': 'Student taps 17.'
        },
        {
            'id': 58,
            'title': 'Tally Marks - Making a Group of 5',
            'instruction': 'Remember, four tally marks with a line through it makes 5!',
            'task': 'Complete the tally marks to show a group of 5.',
            'visual_aid': 'Tally marks showing IIII with student dragging diagonal line.',
            'expected_answer': 'Student drags the line correctly.'
        },
        {
            'id': 59,
            'title': 'Counting Backwards from 50',
            'instruction': 'Let us count backwards from 50! Think of a giant step down.',
            'task': 'What are the numbers just before 40, 39, 38?',
            'visual_aid': 'Audio counting backwards from 50 with descending path.',
            'expected_answer': 'Student types 37.'
        },
        {
            'id': 60,
            'title': 'Place Value - How Many Tens?',
            'instruction': 'Look at the number. How many groups of ten are in it?',
            'task': 'In the number 40, how many tens are there?',
            'visual_aid': 'Numeral 40 with image of 4 bundles of 10 sticks.',
            'expected_answer': 'Student types 4.'
        },
        {
            'id': 61,
            'title': 'Counting Up to 50 (Mixed Objects)',
            'instruction': 'The shop has lots of different items! Count how many there are in total.',
            'task': 'Count all the items in the shop window.',
            'visual_aid': 'Shop window with 35 mixed items that highlight as counted.',
            'expected_answer': 'Student types 35.'
        },
        {
            'id': 62,
            'title': 'Number Before and After (to 50)',
            'instruction': 'What numbers are around this one on the number line?',
            'task': 'What number comes before 45? What number comes after 45?',
            'visual_aid': 'Number line showing 44, 45, 46 with fill-in blanks.',
            'expected_answer': 'Student types 44 and 46.'
        },
        {
            'id': 63,
            'title': 'Number Formation - Tracing 10-20',
            'instruction': 'Let us trace some bigger numbers now!',
            'task': 'Trace the number 16. What is the number?',
            'visual_aid': 'Dotted outline of 16 with voice saying Sixteen.',
            'expected_answer': 'Student traces successfully, then types 16.'
        },
        {
            'id': 64,
            'title': 'Counting in 3s (Introduction)',
            'instruction': 'These flowers grow in groups of 3! Let us count them by 3s.',
            'task': 'Count in 3s: 3, 6, 9, ___, 15.',
            'visual_aid': 'Groups of 3 flowers with audio counting in 3s.',
            'expected_answer': 'Student types 12.'
        },
        {
            'id': 65,
            'title': 'Identifying the Smallest Number (up to 50)',
            'instruction': 'Out of these numbers, which one is the very smallest?',
            'task': 'Tap the smallest number from the group.',
            'visual_aid': 'Four number cards: 32, 19, 45, 28.',
            'expected_answer': 'Student taps 19.'
        },
        {
            'id': 66,
            'title': 'Identifying the Largest Number (up to 50)',
            'instruction': 'And now, which number is the very biggest?',
            'task': 'Tap the largest number from the group.',
            'visual_aid': 'Four number cards: 21, 48, 30, 17.',
            'expected_answer': 'Student taps 48.'
        },
        {
            'id': 67,
            'title': 'Counting Around the Room',
            'instruction': 'Let us imagine counting things in your classroom or living room!',
            'task': 'If you were counting chairs, how many do you think there would be?',
            'visual_aid': 'Animated classroom scene with countable objects.',
            'expected_answer': 'Student types a number (example: 4).'
        },
        {
            'id': 68,
            'title': 'Number Line - Jumps of 5',
            'instruction': 'Let us count by 5s on the number line to find our way!',
            'task': 'Start at 0 and jump 6 times by 5s. Where do you land?',
            'visual_aid': 'Number line 0-50 with jumps of 5 marked.',
            'expected_answer': 'Student types 30.'
        },
        {
            'id': 69,
            'title': 'Number Formation - Writing Numbers 20-30',
            'instruction': 'Time to practice writing numbers between 20 and 30!',
            'task': 'Trace the number 25, then try writing it alone.',
            'visual_aid': 'Dotted outline of 25 with voice saying Twenty-five.',
            'expected_answer': 'Student successfully traces/writes the number.'
        },
        {
            'id': 70,
            'title': 'How Many in Each Hand? (Number Bonds to 10)',
            'instruction': 'You have 10 toys. If you put some in one hand, how many are in the other?',
            'task': 'If you have 6 toys in one hand, how many are in the other to make 10?',
            'visual_aid': 'Two hands, one showing 6 toys, other with question mark.',
            'expected_answer': 'Student types 4.'
        },
        {
            'id': 71,
            'title': 'Sequencing Numbers to 40',
            'instruction': 'Put these numbers in the right order from smallest to biggest.',
            'task': 'Arrange the numbers: 31, 28, 35, 29.',
            'visual_aid': 'Number cards that can be dragged into order.',
            'expected_answer': 'Student drags to form: 28, 29, 31, 35.'
        },
        {
            'id': 72,
            'title': 'Counting Groups (Beyond 10)',
            'instruction': 'Count these cute little penguins in groups of 2.',
            'task': 'How many penguins are there in total if you count in 2s?',
            'visual_aid': '14 penguins arranged in pairs that highlight as counted.',
            'expected_answer': 'Student types 14.'
        },
        {
            'id': 73,
            'title': 'Identifying Tally Marks to 20',
            'instruction': 'Count these tally marks! Remember the groups of 5.',
            'task': 'How many tally marks are shown?',
            'visual_aid': 'Tally marks representing 13.',
            'expected_answer': 'Student types 13.'
        },
        {
            'id': 74,
            'title': 'What Comes Next? (Counting by 1s to 50)',
            'instruction': 'The number sequence is growing! What number comes next?',
            'task': 'What comes next: 47, 48, 49, ___?',
            'visual_aid': 'Numbers in sequence with voice reading them.',
            'expected_answer': 'Student types 50.'
        },
        {
            'id': 75,
            'title': 'Number Line - Jumps of 2',
            'instruction': 'Make little hops on the number line, counting by 2s!',
            'task': 'Start at 10 and jump 4 times by 2s. What number do you land on?',
            'visual_aid': 'Number line 0-20 with animated frog jumps.',
            'expected_answer': 'Student types 18.'
        },
        {
            'id': 76,
            'title': 'Place Value - How Many Ones?',
            'instruction': 'In this number, how many single ones are there?',
            'task': 'In the number 37, how many ones are there?',
            'visual_aid': 'Numeral 37 with 3 bundles of 10 and 7 single blocks.',
            'expected_answer': 'Student types 7.'
        },
        {
            'id': 77,
            'title': 'Story Problem - Counting On',
            'instruction': 'Sarah had 15 stickers. She got 3 more. How many does she have now?',
            'task': 'Count on from 15 to find the total.',
            'visual_aid': 'Image of 15 stickers, then 3 more appearing.',
            'expected_answer': 'Student types 18.'
        },
        {
            'id': 78,
            'title': 'Ordinal Numbers - Who is Last?',
            'instruction': 'Look at the animals in the queue. Who is last?',
            'task': 'Click on the animal that is in the last position (8th).',
            'visual_aid': '8 cartoon animals in a line.',
            'expected_answer': 'Student taps the 8th animal.'
        },
        {
            'id': 79,
            'title': 'Number Match - Quantity to Numeral (to 50)',
            'instruction': 'How many stars are in the sky? Find the matching number.',
            'task': 'Count the stars and tap the correct numeral.',
            'visual_aid': 'Sky scene with 31 scattered stars.',
            'expected_answer': 'Student taps 31.'
        },
        {
            'id': 80,
            'title': 'Simple Addition with Pictures (to 10)',
            'instruction': 'Adding numbers means putting groups together!',
            'task': 'Count the red apples, count the green apples, then count them all together.',
            'visual_aid': '4 red apples and 3 green apples.',
            'expected_answer': 'Student types 7.'
        }
    ]

def generate_study_buddy_response(user_message):
    """Generate educational AI responses for Study Buddy"""
    
    message_lower = user_message.lower()
    
    # Counting and numbers help
    if any(word in message_lower for word in ['count', 'counting', 'number', 'numbers', '20']):
        return "Great question about counting! 🔢 Let's count together: 1, 2, 3, 4, 5... We can count all the way to 20! Try counting your fingers - how many do you have? Counting helps us know how many things we have. Would you like to practice counting objects like toys or animals?"
    
    # Addition help
    if any(word in message_lower for word in ['add', 'addition', 'plus', '+']):
        return "Addition is putting groups together! ➕ When we add, we combine things to find the total. For example: 2 apples + 3 apples = 5 apples! It's like having friends join your group. Try it with your toys - put 2 toys here and 3 toys there, then count them all together!"
    
    # Shapes help
    if any(word in message_lower for word in ['shape', 'shapes', 'circle', 'square', 'triangle', '2d']):
        return "Shapes are everywhere around us! 🔷 A circle is round like a ball ⚽, a square has 4 equal sides like a window 🪟, and a triangle has 3 sides like a slice of pizza 🍕! Look around your room - can you find something that's a circle? What about a square?"
    
    # Time help
    if any(word in message_lower for word in ['time', 'clock', 'hour', 'oclock', "o'clock"]):
        return "Time helps us know when things happen! 🕐 When the big hand points to 12 and the little hand points to a number, we say 'o'clock'. Like when it's 3 o'clock, the little hand points to 3! What time do you eat breakfast? What time do you go to bed?"
    
    # Study tips
    if any(word in message_lower for word in ['tip', 'tips', 'study', 'learn', 'learning']):
        return "Here's a super fun learning tip! 💡 Make learning into a game! When you're counting, use colorful objects like blocks or fruit. When learning shapes, go on a shape hunt around your house. Remember: it's okay to make mistakes - that's how we learn! Take breaks when you need them, and celebrate when you learn something new! 🌟"
    
    # Practice questions
    if any(word in message_lower for word in ['practice', 'question', 'quiz', 'test']):
        return "Let's practice together! 📝 Here's a fun question for you: If you have 3 red balloons and 2 blue balloons, how many balloons do you have altogether? Count them up! 🎈 Remember, you can use your fingers to help count. Take your time and think about it!"
    
    # General encouragement and default response
    return "That's a wonderful question! 🌟 I love helping you learn new things. Learning is like going on an adventure - there's always something exciting to discover! Remember, every expert was once a beginner, so keep asking questions and trying your best. You're doing great! What else would you like to explore together?"

@app.route('/admin/lessons')
def admin_lessons():
    """Admin interface for lesson management"""
    return render_template('admin_lessons.html')

@app.route('/api/test-firebase')
def test_firebase():
    """Test Firebase connection"""
    try:
        db = get_firestore_client()
        if db:
            # Try to read from Firestore
            test_ref = db.collection('test').limit(1)
            list(test_ref.stream())  # This will throw an error if connection fails
            return jsonify({'success': True, 'message': 'Firebase connection successful'})
        else:
            return jsonify({'success': False, 'error': 'Failed to initialize Firebase client'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/dashboard')
def dashboard():
    """Student progress dashboard with exciting quests"""
    student_id = request.args.get('student_id', 'demo_student')
    
    # Get quest progress for the student
    quest_progress = quest_system.get_quest_progress_summary(student_id)
    
    # Get dashboard data (keeping existing functionality)
    try:
        from progress_service import ProgressService
        dashboard_data = ProgressService.get_student_dashboard(student_id)
        leaderboard = ProgressService.get_leaderboard()
    except Exception:
        # Fallback dashboard data
        dashboard_data = {
            'lessons_completed': 0,
            'total_score': 0,
            'learning_streak': 0,
            'subject_stats': []
        }
        leaderboard = []
    
    return render_template('dashboard.html', 
                          student_id=student_id,
                          data=dashboard_data,
                          quest_progress=quest_progress,
                          leaderboard=leaderboard)

@app.route('/quests')
def quests():
    """Display exciting quests for kids"""
    student_id = request.args.get('student_id', 'demo_student')
    quest_progress = quest_system.get_quest_progress_summary(student_id)
    return render_template('quests.html', student_id=student_id, quest_progress=quest_progress)

@app.route('/quest/update', methods=['POST'])
def update_quest_progress():
    """Update quest progress when student completes activities"""
    try:
        data = request.get_json()
        student_id = data.get('student_id', 'demo_student')
        activity_data = data.get('activity_data', {})
        
        result = quest_system.update_quest_progress(student_id, activity_data)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/api/avatar-expression')
def get_avatar_expression():
    """Get current avatar expression based on student emotion and context"""
    try:
        student_id = request.args.get('student_id', 'demo_student')
        
        # Get context from query parameters
        context = {}
        if request.args.get('subject'):
            context['subject'] = request.args.get('subject')
        if request.args.get('learning_event'):
            context['learning_event'] = request.args.get('learning_event')
        if request.args.get('session_id'):
            context['session_id'] = request.args.get('session_id')
        
        expression_data = emotion_avatar_system.get_current_avatar_expression(student_id, context or None)
        return jsonify(expression_data)
        
    except Exception as e:
        return jsonify({'error': str(e), 'fallback': True})

@app.route('/api/avatar-expression/trigger', methods=['POST'])
def trigger_avatar_expression():
    """Trigger specific avatar expression based on learning event"""
    try:
        data = request.get_json()
        student_id = data.get('student_id', 'demo_student')
        learning_event = data.get('learning_event')
        additional_context = data.get('context', {})
        
        if not learning_event:
            return jsonify({'error': 'Learning event is required'}), 400
        
        expression_data = emotion_avatar_system.trigger_expression_change(
            student_id, learning_event, additional_context
        )
        
        return jsonify(expression_data)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/avatar-expression/celebration', methods=['POST'])
def trigger_celebration_expression():
    """Trigger celebration avatar expression for achievements"""
    try:
        data = request.get_json()
        achievement_type = data.get('achievement_type')
        
        if not achievement_type:
            return jsonify({'error': 'Achievement type is required'}), 400
        
        celebration_data = emotion_avatar_system.get_celebration_expression(achievement_type)
        return jsonify(celebration_data)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/current-child')
def get_current_child():
    """Get current active child profile"""
    try:
        # Check session for current child
        current_child_id = session.get('current_child_id')
        
        if current_child_id:
            child = Student.query.get(current_child_id)
            if child:
                return jsonify({
                    'child': {
                        'id': child.id,
                        'name': child.student_name,
                        'age': child.age,
                        'grade': child.grade_level,
                        'profile_picture': child.avatar_image
                    }
                })
        
        # Default to first child if no current child set
        parent_id = session.get('parent_id')
        if parent_id:
            child = Student.query.filter_by(parent_id=parent_id).first()
            if child:
                session['current_child_id'] = child.id
                return jsonify({
                    'child': {
                        'id': child.id,
                        'name': child.student_name,
                        'age': child.age,
                        'grade': child.grade_level,
                        'profile_picture': child.avatar_image
                    }
                })
        
        return jsonify({'error': 'No child found'}), 404
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/family-children')
def get_family_children():
    """Get all children in the family"""
    try:
        parent_id = session.get('parent_id')
        current_child_id = session.get('current_child_id')
        
        if not parent_id:
            return jsonify({'children': []})
        
        children = Student.query.filter_by(parent_id=parent_id).all()
        
        children_data = []
        for child in children:
            children_data.append({
                'id': child.id,
                'name': child.student_name,
                'age': child.age,
                'grade': child.grade_level,
                'profile_picture': child.avatar_image,
                'is_current': child.id == current_child_id
            })
        
        return jsonify({'children': children_data})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/switch-child-profile', methods=['POST'])
def switch_child_profile():
    """Switch to a different child profile"""
    try:
        data = request.get_json()
        child_id = data.get('child_id')
        
        if not child_id:
            return jsonify({'error': 'Child ID required'}), 400
        
        # Verify child belongs to current parent
        parent_id = session.get('parent_id')
        child = Student.query.filter_by(id=child_id, parent_id=parent_id).first()
        
        if not child:
            return jsonify({'error': 'Child not found'}), 404
        
        # Switch current child
        session['current_child_id'] = child.id
        
        return jsonify({
            'success': True,
            'child': {
                'id': child.id,
                'name': child.student_name,
                'age': child.age,
                'grade': child.grade_level,
                'profile_picture': child.avatar_image
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/auditory-numbers')
def auditory_numbers():
    """Interactive auditory learning for numbers and counting"""
    return render_template('auditory_content_clean.html')

@app.route('/api/generate-speech', methods=['POST'])
def api_generate_speech():
    """Generate speech audio using Gemini TTS"""
    try:
        from gemini_tts import GeminiTTSService
        
        data = request.get_json()
        text = data.get('text', '')
        voice_gender = data.get('voice_gender', 'female')
        
        if not text:
            return jsonify({'error': 'No text provided'}), 400
        
        tts_service = GeminiTTSService()
        audio_url = tts_service.create_audio_url(text, voice_gender)
        
        if audio_url:
            return jsonify({
                'success': True,
                'audio_url': audio_url
            })
        else:
            return jsonify({'error': 'Failed to generate audio'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/complete-lesson', methods=['POST'])
def api_complete_lesson():
    """Record lesson completion progress"""
    try:
        data = request.get_json()
        
        progress = ProgressService.record_lesson_progress(
            student_id=data.get('student_id', 'demo_student'),
            student_name=data.get('student_name', 'Demo Student'),
            subject=data['subject'],
            topic=data.get('topic', 'General Topic'),
            learning_style=data['learning_style'],
            completion_percentage=data.get('completion_percentage', 100),
            time_spent_minutes=data.get('time_spent_minutes', 5)
        )
        
        return jsonify({
            'success': True, 
            'points_earned': progress.points_earned,
            'message': f'Great job! You earned {progress.points_earned} points!'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/audio/voices')
def get_voices():
    """Get available voices for text-to-speech"""
    # Return standard web speech API voice options
    voices = [
        {'id': 'female-1', 'name': 'Female Voice 1', 'gender': 'female', 'lang': 'en-US'},
        {'id': 'female-2', 'name': 'Female Voice 2', 'gender': 'female', 'lang': 'en-GB'},
        {'id': 'male-1', 'name': 'Male Voice 1', 'gender': 'male', 'lang': 'en-US'},
        {'id': 'male-2', 'name': 'Male Voice 2', 'gender': 'male', 'lang': 'en-GB'},
    ]
    return jsonify({'voices': voices})

@app.route('/api/generate-lesson-content', methods=['POST'])
def api_generate_lesson_content():
    """Generate lesson content using AI"""
    try:
        data = request.get_json()
        subject = data.get('subject', 'maths')
        topic = data.get('topic', 'numbers-to-20')
        style = data.get('style', 'visual')
        
        # Generate content using AI
        content = generate_lesson_content(subject, style, topic)
        app.logger.info(f"Successfully generated content for {subject} - {topic}")
        
        # Format the AI content properly
        main_content = content.get(style, content.get('visual', content.get('verbal', 'Educational content for this lesson.')))
        
        # Clean up the formatting for better display
        if main_content:
            # Remove markdown formatting and organize content
            main_content = main_content.replace('##', '<h4>').replace('**', '<strong>').replace('**', '</strong>')
            main_content = main_content.replace('**(', '<p><strong>(').replace(')**', ')</strong></p>')
            main_content = main_content.replace('\n\n', '</p><p>').replace('\n', '<br>')
            main_content = f'<p>{main_content}</p>'
        
        # Create structured lesson content
        lesson_html = f"""
        <div class="lesson-content">
            <div class="lesson-overview">
                <h3>{content.get('title', topic.replace('-', ' ').title())}</h3>
                <p class="lesson-description">{content.get('description', 'Educational lesson for primary school students')}</p>
            </div>
            
            <div class="lesson-sections">
                <div class="lesson-section">
                    <h4>Learning Objectives</h4>
                    <div class="content-box">
                        <p>{content.get('objectives', 'Students will learn fundamental concepts through engaging activities.')}</p>
                    </div>
                </div>
                
                <div class="lesson-section">
                    <h4>Lesson Content</h4>
                    <div class="content-box lesson-main-content">
                        <div class="formatted-content">
                            {main_content}
                        </div>
                    </div>
                </div>
                
                <div class="lesson-section">
                    <h4>Activities & Practice</h4>
                    <div class="content-box">
                        <p>{content.get('activities', 'Interactive exercises and hands-on activities to reinforce learning.')}</p>
                    </div>
                </div>
            </div>
        </div>
        
        <style>
        .lesson-content {{ margin: 20px 0; }}
        .lesson-overview {{ background: #f8f9fa; padding: 20px; border-radius: 10px; margin-bottom: 20px; }}
        .lesson-section {{ margin-bottom: 25px; }}
        .lesson-section h4 {{ color: hsl(var(--primary)); margin-bottom: 15px; }}
        .content-box {{ 
            background: white; 
            padding: 20px; 
            border-radius: 10px; 
            border-left: 4px solid hsl(var(--primary));
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }}
        .counting-activity {{
            background: #e8f4fd;
            padding: 15px;
            border-radius: 8px;
            margin: 10px 0;
        }}
        </style>
        """
        
        return jsonify({'content': lesson_html})
        
    except Exception as e:
        app.logger.error(f"Error generating lesson content: {e}")
        return jsonify({
            'content': '<div class="alert alert-warning"><h4>Content Loading</h4><p>Educational content is being prepared. Please try refreshing the page.</p></div>'
        }), 500

@app.route('/api/generate-lessons', methods=['POST'])
def api_generate_lessons():
    """API endpoint to trigger lesson generation"""
    try:
        # Import here to avoid startup issues
        from lesson_generator import run_lesson_generation
        
        # Run lesson generation
        success = run_lesson_generation()
        
        if success:
            return jsonify({'success': True, 'message': 'Lessons generated successfully'})
        else:
            return jsonify({'success': False, 'error': 'Lesson generation failed'})
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

def get_placeholder_content(subject, style):
    """
    This function provides placeholder content based on subject and learning style.
    In the future, this would be replaced with actual API calls to OpenAI/Gemini.
    """
    content = {
        'title': '',
        'visual': '',
        'verbal': '',
        'auditory': '',
        'current_style': style
    }
    
    if subject == 'maths':
        content['title'] = 'Understanding Fractions'
        content['visual'] = """
        <div class="visual-content text-center">
            <h3>Visual Representation of Fractions</h3>
            <div class="fraction-visual my-4">
                <svg width="600" height="300" class="mx-auto">
                    <!-- Whole -->
                    <rect x="50" y="50" width="200" height="50" fill="#6c757d" stroke="#343a40" stroke-width="2"/>
                    <text x="150" y="80" text-anchor="middle" fill="white">1 Whole</text>
                    
                    <!-- Halves -->
                    <rect x="50" y="120" width="100" height="50" fill="#0d6efd" stroke="#343a40" stroke-width="2"/>
                    <rect x="150" y="120" width="100" height="50" fill="#6610f2" stroke="#343a40" stroke-width="2"/>
                    <text x="100" y="150" text-anchor="middle" fill="white">1/2</text>
                    <text x="200" y="150" text-anchor="middle" fill="white">1/2</text>
                    
                    <!-- Quarters -->
                    <rect x="50" y="190" width="50" height="50" fill="#dc3545" stroke="#343a40" stroke-width="2"/>
                    <rect x="100" y="190" width="50" height="50" fill="#fd7e14" stroke="#343a40" stroke-width="2"/>
                    <rect x="150" y="190" width="50" height="50" fill="#ffc107" stroke="#343a40" stroke-width="2"/>
                    <rect x="200" y="190" width="50" height="50" fill="#20c997" stroke="#343a40" stroke-width="2"/>
                    <text x="75" y="220" text-anchor="middle" fill="white">1/4</text>
                    <text x="125" y="220" text-anchor="middle" fill="white">1/4</text>
                    <text x="175" y="220" text-anchor="middle" fill="white">1/4</text>
                    <text x="225" y="220" text-anchor="middle" fill="white">1/4</text>
                    
                    <!-- Explanation -->
                    <text x="350" y="80" text-anchor="middle">A fraction represents a part of a whole</text>
                    <text x="350" y="150" text-anchor="middle">When we divide a whole into 2 equal parts,</text>
                    <text x="350" y="170" text-anchor="middle">each part is 1/2 of the whole</text>
                    <text x="350" y="220" text-anchor="middle">When we divide a whole into 4 equal parts,</text>
                    <text x="350" y="240" text-anchor="middle">each part is 1/4 of the whole</text>
                </svg>
            </div>
            <div class="my-4">
                <p>Notice how the size of each piece gets smaller as we divide the whole into more parts!</p>
            </div>
        </div>
        """
        content['verbal'] = """
        <div class="verbal-content">
            <h3>Understanding Fractions</h3>
            <p>A fraction represents a part of a whole, like a piece of a pizza or a segment of a chocolate bar.</p>
            <p>Fractions consist of two parts:</p>
            <ul>
                <li><strong>Numerator</strong>: The top number that shows how many parts we have</li>
                <li><strong>Denominator</strong>: The bottom number that shows how many equal parts the whole is divided into</li>
            </ul>
            <p>For example, in the fraction 3/4:</p>
            <ul>
                <li>The numerator is 3, meaning we have 3 parts</li>
                <li>The denominator is 4, meaning the whole is divided into 4 equal parts</li>
            </ul>
            <p>We can add fractions with the same denominator by simply adding the numerators and keeping the denominator the same.</p>
            <p>For example: 1/4 + 2/4 = 3/4</p>
            <p>When fractions have different denominators, we need to find a common denominator first. This is a number that both denominators can divide into evenly.</p>
            <p>Remember, fractions are all around us in everyday life, from cooking recipes to telling time!</p>
        </div>
        """
        content['auditory'] = """
        <div class="auditory-content">
            <h3>Listening to Fractions Explanation</h3>
            <p>Click the play button to listen to an explanation about fractions:</p>
            <div class="text-center my-4">
                <i class="fas fa-volume-up fa-3x"></i>
                <p class="mt-2">(Audio would play here in the full version)</p>
            </div>
            <div class="transcript-container border p-3 mt-4">
                <h4>Transcript:</h4>
                <p>"Hello there! Today we're learning about fractions. A fraction is simply a part of a whole.</p>
                <p>Think about a pizza cut into 8 equal slices. Each slice is 1/8 of the whole pizza. If you eat 3 slices, you've eaten 3/8 of the pizza.</p>
                <p>The bottom number of a fraction tells us how many equal parts the whole is divided into. We call this the denominator.</p>
                <p>The top number tells us how many of those parts we're talking about. This is called the numerator.</p>
                <p>So in 3/8, the denominator 8 tells us the whole is divided into 8 equal parts, and the numerator 3 tells us we're considering 3 of those parts.</p>
                <p>Remember, the larger the denominator, the smaller each individual part will be. For example, 1/10 is smaller than 1/5 because when we divide something into 10 parts, each part is smaller than when we divide it into only 5 parts.</p>
                <p>Fractions are used every day in cooking, construction, shopping, and many other activities. Understanding fractions helps us divide things fairly and measure precisely."</p>
            </div>
        </div>
        """
    elif subject == 'science':
        content['title'] = 'The Water Cycle'
        content['visual'] = """
        <div class="visual-content text-center">
            <h3>The Water Cycle Visualized</h3>
            <div class="water-cycle-visual my-4">
                <svg width="600" height="400" class="mx-auto">
                    <!-- Sky -->
                    <rect x="0" y="0" width="600" height="150" fill="#87CEEB"/>
                    
                    <!-- Sun -->
                    <circle cx="500" cy="70" r="40" fill="#FFD700"/>
                    <text x="500" y="75" text-anchor="middle" fill="#000">Sun</text>
                    
                    <!-- Clouds -->
                    <circle cx="150" cy="70" r="25" fill="#FFFFFF"/>
                    <circle cx="180" cy="70" r="30" fill="#FFFFFF"/>
                    <circle cx="210" cy="70" r="25" fill="#FFFFFF"/>
                    <text x="180" y="75" text-anchor="middle" fill="#000">Condensation</text>
                    
                    <!-- Rain -->
                    <line x1="140" y1="100" x2="130" y2="130" stroke="#1E90FF" stroke-width="2"/>
                    <line x1="160" y1="100" x2="150" y2="130" stroke="#1E90FF" stroke-width="2"/>
                    <line x1="180" y1="100" x2="170" y2="130" stroke="#1E90FF" stroke-width="2"/>
                    <line x1="200" y1="100" x2="190" y2="130" stroke="#1E90FF" stroke-width="2"/>
                    <line x1="220" y1="100" x2="210" y2="130" stroke="#1E90FF" stroke-width="2"/>
                    <text x="180" y="150" text-anchor="middle" fill="#000">Precipitation</text>
                    
                    <!-- Ground -->
                    <rect x="0" y="250" width="600" height="150" fill="#8B4513"/>
                    
                    <!-- Water Body -->
                    <rect x="350" y="200" width="200" height="50" fill="#0000CD"/>
                    <text x="450" y="230" text-anchor="middle" fill="#FFFFFF">Ocean/Lake</text>
                    
                    <!-- Evaporation -->
                    <path d="M 400 200 Q 410 180 420 200 Q 430 180 440 200 Q 450 180 460 200" stroke="#1E90FF" stroke-width="2" fill="none"/>
                    <text x="430" y="170" text-anchor="middle" fill="#000">Evaporation</text>
                    
                    <!-- Underground Water -->
                    <rect x="50" y="300" width="200" height="50" fill="#1E90FF" opacity="0.5"/>
                    <text x="150" y="330" text-anchor="middle" fill="#000">Groundwater</text>
                    
                    <!-- Runoff -->
                    <path d="M 170 250 L 350 250" stroke="#1E90FF" stroke-width="2" fill="none"/>
                    <text x="260" y="240" text-anchor="middle" fill="#000">Runoff</text>
                </svg>
            </div>
            <div class="my-4">
                <p>The water cycle is a continuous process of water movement on, above, and below Earth's surface!</p>
            </div>
        </div>
        """
        content['verbal'] = """
        <div class="verbal-content">
            <h3>Understanding The Water Cycle</h3>
            <p>The water cycle, also known as the hydrologic cycle, describes the continuous movement of water on, above, and below the surface of the Earth. Water is always changing states between liquid, vapor, and ice, with these processes happening in the blink of an eye and over millions of years.</p>
            <p>The water cycle consists of several key processes:</p>
            <ul>
                <li><strong>Evaporation</strong>: The process where water changes from a liquid to a gas or vapor. The sun heats up water in rivers, lakes, and oceans, turning it into vapor that rises into the air.</li>
                <li><strong>Transpiration</strong>: The process where plants release water vapor from their leaves.</li>
                <li><strong>Condensation</strong>: When water vapor in the air gets cold and changes back into liquid, forming clouds.</li>
                <li><strong>Precipitation</strong>: When water falls from clouds back to Earth as rain, snow, hail, or sleet.</li>
                <li><strong>Collection</strong>: Precipitation collects in oceans, lakes, rivers, and soils.</li>
                <li><strong>Runoff</strong>: Water flowing over land into bodies of water.</li>
                <li><strong>Infiltration</strong>: The process where water soaks into the soil and becomes groundwater.</li>
            </ul>
            <p>The water cycle is essential for all life on Earth. It purifies water, replenishes water resources, and helps maintain Earth's temperature. Without it, our planet would be uninhabitable.</p>
            <p>Interestingly, the water on Earth today is the same water that has been here for billions of years. The water that dinosaurs drank is the same water we drink today!</p>
        </div>
        """
        content['auditory'] = """
        <div class="auditory-content">
            <h3>Listening to The Water Cycle Explanation</h3>
            <p>Click the play button to listen to an explanation about the water cycle:</p>
            <div class="text-center my-4">
                <i class="fas fa-volume-up fa-3x"></i>
                <p class="mt-2">(Audio would play here in the full version)</p>
            </div>
            <div class="transcript-container border p-3 mt-4">
                <h4>Transcript:</h4>
                <p>"Hello science explorers! Today we're diving into the fascinating water cycle - the journey water takes as it moves around our planet.</p>
                <p>The water cycle begins with the sun heating up water in oceans, lakes, and rivers. This causes the water to evaporate, changing from a liquid into an invisible gas called water vapor that rises into the air. Plants also release water vapor through their leaves in a process called transpiration.</p>
                <p>As this water vapor rises higher into the atmosphere, it cools down and condenses back into tiny water droplets, forming clouds. This process is called condensation.</p>
                <p>When the water droplets in clouds become too heavy, they fall back to Earth as precipitation - rain, snow, sleet, or hail, depending on the temperature.</p>
                <p>Once water reaches Earth's surface, it can take many paths. Some of it may flow over the land as runoff, eventually collecting in oceans, lakes, and rivers. Some may soak into the ground through infiltration, becoming groundwater that can feed springs or be stored in aquifers deep underground.</p>
                <p>And then the cycle begins again! The same water molecules have been cycling around our planet for billions of years. The water you drink today might once have been drunk by a dinosaur, or been part of an ancient ocean, or fallen as rain in a land far away.</p>
                <p>The water cycle is nature's recycling system, ensuring that water - essential for all life - is constantly renewed and redistributed around our planet."</p>
            </div>
        </div>
        """
    elif subject == 'english':
        content['title'] = 'Types of Poetic Devices'
        content['visual'] = """
        <div class="visual-content text-center">
            <h3>Visual Guide to Poetic Devices</h3>
            <div class="poetic-devices-visual my-4">
                <svg width="600" height="500" class="mx-auto">
                    <!-- Title -->
                    <text x="300" y="30" text-anchor="middle" font-size="20" font-weight="bold">Common Poetic Devices</text>
                    
                    <!-- Alliteration -->
                    <rect x="50" y="50" width="200" height="100" fill="#f8d7da" stroke="#721c24" stroke-width="2" rx="10"/>
                    <text x="150" y="80" text-anchor="middle" font-weight="bold">Alliteration</text>
                    <text x="150" y="110" text-anchor="middle" font-size="14">Peter Piper picked a peck</text>
                    <text x="150" y="130" text-anchor="middle" font-size="14">of pickled peppers</text>
                    
                    <!-- Simile -->
                    <rect x="350" y="50" width="200" height="100" fill="#d1ecf1" stroke="#0c5460" stroke-width="2" rx="10"/>
                    <text x="450" y="80" text-anchor="middle" font-weight="bold">Simile</text>
                    <text x="450" y="110" text-anchor="middle" font-size="14">Her eyes were like stars</text>
                    <text x="450" y="130" text-anchor="middle" font-size="14">bright and twinkling</text>
                    
                    <!-- Metaphor -->
                    <rect x="50" y="180" width="200" height="100" fill="#d4edda" stroke="#155724" stroke-width="2" rx="10"/>
                    <text x="150" y="210" text-anchor="middle" font-weight="bold">Metaphor</text>
                    <text x="150" y="240" text-anchor="middle" font-size="14">Time is a thief</text>
                    <text x="150" y="260" text-anchor="middle" font-size="14">stealing our youth</text>
                    
                    <!-- Personification -->
                    <rect x="350" y="180" width="200" height="100" fill="#fff3cd" stroke="#856404" stroke-width="2" rx="10"/>
                    <text x="450" y="210" text-anchor="middle" font-weight="bold">Personification</text>
                    <text x="450" y="240" text-anchor="middle" font-size="14">The wind whispered</text>
                    <text x="450" y="260" text-anchor="middle" font-size="14">through the trees</text>
                    
                    <!-- Onomatopoeia -->
                    <rect x="50" y="310" width="200" height="100" fill="#e2e3e5" stroke="#383d41" stroke-width="2" rx="10"/>
                    <text x="150" y="340" text-anchor="middle" font-weight="bold">Onomatopoeia</text>
                    <text x="150" y="370" text-anchor="middle" font-size="14">Buzz, Crash, Pop</text>
                    <text x="150" y="390" text-anchor="middle" font-size="14">Splash, Bang, Hiss</text>
                    
                    <!-- Hyperbole -->
                    <rect x="350" y="310" width="200" height="100" fill="#cce5ff" stroke="#004085" stroke-width="2" rx="10"/>
                    <text x="450" y="340" text-anchor="middle" font-weight="bold">Hyperbole</text>
                    <text x="450" y="370" text-anchor="middle" font-size="14">I've told you a</text>
                    <text x="450" y="390" text-anchor="middle" font-size="14">million times</text>
                </svg>
            </div>
            <div class="my-4">
                <p>Poetic devices enhance the beauty and impact of language in poetry and prose!</p>
            </div>
        </div>
        """
        content['verbal'] = """
        <div class="verbal-content">
            <h3>Understanding Poetic Devices</h3>
            <p>Poetic devices are techniques that writers use to create special effects in their writing, especially in poetry. These devices help to convey meaning, create rhythm, and evoke emotions in readers.</p>
            <p>Here are some common poetic devices:</p>
            <ul>
                <li><strong>Alliteration</strong>: Repetition of the same consonant sound at the beginning of nearby words. Example: "She sells seashells by the seashore."</li>
                <li><strong>Simile</strong>: A comparison between two unlike things using 'like' or 'as'. Example: "Her smile was as bright as the sun."</li>
                <li><strong>Metaphor</strong>: A direct comparison between two unlike things without using 'like' or 'as'. Example: "Her eyes were diamonds, sparkling in the light."</li>
                <li><strong>Personification</strong>: Giving human characteristics to non-human objects or ideas. Example: "The wind whispered through the trees."</li>
                <li><strong>Onomatopoeia</strong>: Words that imitate the sound they describe. Example: "The bee buzzed loudly."</li>
                <li><strong>Hyperbole</strong>: An extreme exaggeration used for emphasis or humor. Example: "I'm so hungry I could eat a horse."</li>
                <li><strong>Rhyme</strong>: The repetition of similar sounds at the end of words. Example: "Roses are red, violets are blue."</li>
                <li><strong>Rhythm</strong>: The pattern of stressed and unstressed syllables in poetry.</li>
            </ul>
            <p>Poetic devices make writing more engaging, memorable, and impactful. They help poets and writers to express complex ideas and emotions in a concise and creative way. Next time you read a poem or a story, try to identify the poetic devices used and think about how they enhance the meaning and beauty of the text.</p>
        </div>
        """
        content['auditory'] = """
        <div class="auditory-content">
            <h3>Listening to Poetic Devices Explanation</h3>
            <p>Click the play button to listen to an explanation about poetic devices:</p>
            <div class="text-center my-4">
                <i class="fas fa-volume-up fa-3x"></i>
                <p class="mt-2">(Audio would play here in the full version)</p>
            </div>
            <div class="transcript-container border p-3 mt-4">
                <h4>Transcript:</h4>
                <p>"Welcome to our exploration of poetic devices! These are special techniques that writers use to make their writing more powerful, musical, and memorable.</p>
                <p>Let's start with alliteration. This is when several words beginning with the same sound are used close together. For example: 'The slithering snake slid silently across the sand.' Notice how all those 's' sounds create a smooth, flowing effect that actually mimics the movement of a snake!</p>
                <p>Next, we have similes and metaphors. Both compare one thing to another, but in different ways. A simile uses 'like' or 'as' - for example, 'Her voice was like a gentle stream.' A metaphor makes a direct comparison without these words - 'Her voice was a gentle stream.' Both help us understand something by comparing it to something else.</p>
                <p>Personification is when we give human qualities to non-human things. 'The stars danced in the night sky' gives the stars the human ability to dance, creating a vivid image.</p>
                <p>Onomatopoeia is a fun one - these are words that sound like what they describe. Words like 'buzz,' 'crash,' 'pop,' 'splash' are all examples. They add a sensory dimension to writing.</p>
                <p>Hyperbole is an extreme exaggeration used for emphasis or effect. If someone says 'I've told you a million times,' they don't literally mean a million - they're using hyperbole to emphasize how many times they've repeated themselves.</p>
                <p>These devices aren't just fancy techniques - they help writers communicate more effectively and creatively. They make language come alive and help us see, hear, and feel what the writer wants to convey. Next time you read a poem or story, see if you can spot these devices at work!"</p>
            </div>
        </div>
        """
    
    return content

# Helper functions for subject explorer
def get_materials_count(subject, level):
    """Get count of learning materials for subject and level"""
    base_counts = {'maths': 45, 'science': 38, 'english': 42, 'history': 35, 'geography': 28, 'languages': 32, 'computing': 48}
    multipliers = {'primary': 0.6, 'highschool': 1.0, 'college': 1.3, 'university': 1.6}
    return int(base_counts.get(subject, 30) * multipliers.get(level, 1.0))

def get_practice_count(subject, level):
    """Get count of practice questions for subject and level"""
    base_counts = {'maths': 120, 'science': 95, 'english': 85, 'history': 70, 'geography': 60, 'languages': 90, 'computing': 110}
    multipliers = {'primary': 0.5, 'highschool': 1.0, 'college': 1.4, 'university': 1.8}
    return int(base_counts.get(subject, 75) * multipliers.get(level, 1.0))

def get_guides_count(subject, level):
    """Get count of study guides for subject and level"""
    base_counts = {'maths': 15, 'science': 12, 'english': 18, 'history': 14, 'geography': 10, 'languages': 16, 'computing': 20}
    multipliers = {'primary': 0.7, 'highschool': 1.0, 'college': 1.2, 'university': 1.5}
    return int(base_counts.get(subject, 12) * multipliers.get(level, 1.0))

def get_cheatsheets_count(subject, level):
    """Get count of cheat sheets for subject and level"""
    base_counts = {'maths': 25, 'science': 20, 'english': 15, 'history': 12, 'geography': 10, 'languages': 18, 'computing': 28}
    multipliers = {'primary': 0.4, 'highschool': 1.0, 'college': 1.3, 'university': 1.6}
    return int(base_counts.get(subject, 15) * multipliers.get(level, 1.0))

def get_videos_count(subject, level):
    """Get count of video tutorials for subject and level"""
    base_counts = {'maths': 35, 'science': 30, 'english': 25, 'history': 22, 'geography': 18, 'languages': 28, 'computing': 42}
    multipliers = {'primary': 0.8, 'highschool': 1.0, 'college': 1.1, 'university': 1.3}
    return int(base_counts.get(subject, 25) * multipliers.get(level, 1.0))

def get_flashcards_count(subject, level):
    """Get count of flashcards for subject and level"""
    base_counts = {'maths': 80, 'science': 70, 'english': 100, 'history': 90, 'geography': 65, 'languages': 120, 'computing': 95}
    multipliers = {'primary': 0.6, 'highschool': 1.0, 'college': 1.2, 'university': 1.4}
    return int(base_counts.get(subject, 70) * multipliers.get(level, 1.0))

def get_completion_percentage(subject, level):
    """Get completion percentage for subject and level"""
    import random
    return random.randint(15, 85)

def get_study_hours(subject, level):
    """Get study hours for subject and level"""
    import random
    return random.randint(8, 45)

def get_quiz_score(subject, level):
    """Get average quiz score for subject and level"""
    import random
    return random.randint(65, 95)

def get_streak_days(subject, level):
    """Get learning streak days"""
    import random
    return random.randint(3, 28)

def get_practice_categories(subject, level):
    """Generate practice question categories based on subject and level"""
    categories_data = {
        'maths': {
            'primary': [
                {'id': 'counting', 'name': 'Counting & Numbers 1-100', 'description': 'Counting, number recognition, and number writing', 'icon': 'fas fa-calculator', 'question_count': 40, 'estimated_time': 15, 'difficulty': 'easy'},
                {'id': 'addition', 'name': 'Addition & Subtraction', 'description': 'Adding and subtracting within 20', 'icon': 'fas fa-plus', 'question_count': 35, 'estimated_time': 15, 'difficulty': 'easy'},
                {'id': 'shapes', 'name': 'Shapes & Patterns', 'description': 'Shapes, patterns, and basic geometry', 'icon': 'fas fa-shapes', 'question_count': 25, 'estimated_time': 10, 'difficulty': 'easy'},
                {'id': 'time-money', 'name': 'Time & Money', 'description': 'Reading clocks and counting money', 'icon': 'fas fa-clock', 'question_count': 30, 'estimated_time': 12, 'difficulty': 'easy'},
                {'id': 'measurement', 'name': 'Measurement Fun', 'description': 'Length, weight, and volume activities', 'icon': 'fas fa-ruler', 'question_count': 25, 'estimated_time': 10, 'difficulty': 'easy'}
            ],

            'college': [
                {'id': 'calculus1', 'name': 'Calculus I', 'description': 'Limits, derivatives, and basic integration', 'icon': 'fas fa-infinity', 'question_count': 60, 'estimated_time': 30, 'difficulty': 'hard'},
                {'id': 'linear-algebra', 'name': 'Linear Algebra', 'description': 'Matrices, vectors, and linear transformations', 'icon': 'fas fa-vector-square', 'question_count': 50, 'estimated_time': 25, 'difficulty': 'hard'}
            ]
        },
        'science': {
            'primary': [
                {'id': 'animals', 'name': 'Animals & Plants', 'description': 'Amazing animals, plants, and their homes', 'icon': 'fas fa-paw', 'question_count': 30, 'estimated_time': 12, 'difficulty': 'easy'},
                {'id': 'weather', 'name': 'Weather & Seasons', 'description': 'Weather patterns, seasons, and climate', 'icon': 'fas fa-cloud-sun', 'question_count': 25, 'estimated_time': 10, 'difficulty': 'easy'},
                {'id': 'body', 'name': 'My Amazing Body', 'description': 'Body parts, health, and staying strong', 'icon': 'fas fa-heart', 'question_count': 25, 'estimated_time': 10, 'difficulty': 'easy'},
                {'id': 'earth-space', 'name': 'Earth & Space', 'description': 'Our planet, sun, moon, and stars', 'icon': 'fas fa-globe', 'question_count': 20, 'estimated_time': 8, 'difficulty': 'easy'},
                {'id': 'materials', 'name': 'Materials & Changes', 'description': 'Different materials and how things change', 'icon': 'fas fa-cog', 'question_count': 20, 'estimated_time': 8, 'difficulty': 'easy'}
            ],

        },
        'english': {
            'primary': [
                {'id': 'phonics', 'name': 'Phonics & Sounds', 'description': 'Letter sounds and reading basics', 'icon': 'fas fa-volume-up', 'question_count': 35, 'estimated_time': 15, 'difficulty': 'easy'},
                {'id': 'reading', 'name': 'Reading Adventures', 'description': 'Story comprehension and reading fun', 'icon': 'fas fa-book', 'question_count': 30, 'estimated_time': 12, 'difficulty': 'easy'},
                {'id': 'writing', 'name': 'Creative Writing', 'description': 'Writing stories and expressing ideas', 'icon': 'fas fa-pen', 'question_count': 25, 'estimated_time': 10, 'difficulty': 'easy'},
                {'id': 'spelling', 'name': 'Spelling Games', 'description': 'Spelling words and patterns', 'icon': 'fas fa-spell-check', 'question_count': 30, 'estimated_time': 12, 'difficulty': 'easy'},
                {'id': 'vocabulary', 'name': 'Vocabulary Fun', 'description': 'Learning new words and meanings', 'icon': 'fas fa-lightbulb', 'question_count': 25, 'estimated_time': 10, 'difficulty': 'easy'}
            ]
        },
        'art': {
            'primary': [
                {'id': 'drawing', 'name': 'Drawing & Coloring', 'description': 'Basic drawing and coloring techniques', 'icon': 'fas fa-palette', 'question_count': 20, 'estimated_time': 8, 'difficulty': 'easy'},
                {'id': 'crafts', 'name': 'Crafts & Making', 'description': 'Fun craft projects and creating', 'icon': 'fas fa-cut', 'question_count': 15, 'estimated_time': 6, 'difficulty': 'easy'},
                {'id': 'famous-artists', 'name': 'Famous Artists', 'description': 'Learning about great artists', 'icon': 'fas fa-user-tie', 'question_count': 15, 'estimated_time': 6, 'difficulty': 'easy'},
                {'id': 'colors', 'name': 'Colors & Shapes', 'description': 'Understanding colors and artistic shapes', 'icon': 'fas fa-circle', 'question_count': 20, 'estimated_time': 8, 'difficulty': 'easy'}
            ]
        },

    }
    
    return categories_data.get(subject, {}).get(level, [])

def get_cheat_sheets(subject, level):
    """Generate cheat sheets based on subject and level"""
    cheat_sheets_data = {
        'maths': {
            'highschool': [
                {
                    'id': 'algebra-formulas',
                    'title': 'Algebra Formulas',
                    'description': 'Essential algebraic formulas and identities',
                    'icon': 'fas fa-square-root-alt',
                    'type': 'Formulas',
                    'preview_content': '<div class="formula-preview"><strong>Quadratic Formula:</strong><br>x = (-b ± √(b²-4ac)) / 2a<br><strong>Difference of Squares:</strong><br>a² - b² = (a+b)(a-b)</div>'
                },
                {
                    'id': 'geometry-formulas',
                    'title': 'Geometry Formulas',
                    'description': 'Area, perimeter, and volume formulas',
                    'icon': 'fas fa-ruler-combined',
                    'type': 'Reference',
                    'preview_content': '<div class="formula-preview"><strong>Circle Area:</strong><br>A = πr²<br><strong>Triangle Area:</strong><br>A = ½bh<br><strong>Sphere Volume:</strong><br>V = (4/3)πr³</div>'
                }
            ]
        }
    }
    
    return cheat_sheets_data.get(subject, {}).get(level, [])

def generate_cheat_sheet_content(sheet_id, subject, level):
    """Generate full cheat sheet content using AI"""
    from ai_content_generator import generate_lesson_content
    
    # Use AI to generate comprehensive cheat sheet content
    try:
        content = generate_lesson_content(subject, 'visual', f'cheat sheet for {sheet_id}')
        return {
            'title': f'{subject.title()} - {sheet_id.replace("-", " ").title()}',
            'content': content['content']
        }
    except Exception as e:
        return {
            'title': f'{subject.title()} Quick Reference',
            'content': '<div class="cheat-sheet-content"><h3>Quick Reference Guide</h3><p>Essential formulas and concepts for quick reference during study sessions.</p></div>'
        }



@app.route('/api/mood-response')
def api_mood_response():
    """Generate mood-based avatar response for learning context"""
    try:
        context = request.args.get('context', 'lesson_start')
        student_id = request.args.get('student_id', 'default_student')
        
        # Get student performance data (simplified for demo)
        performance = {
            'accuracy': float(request.args.get('accuracy', 0.8)),
            'engagement': float(request.args.get('engagement', 0.7)),
            'confidence': float(request.args.get('confidence', 0.6))
        }
        
        learning_context = {
            'situation': context,
            'performance': performance,
            'time_of_day': 'morning',
            'session_duration': int(request.args.get('session_duration', 15))
        }
        
        if mood_engine:
            mood_response = mood_engine.get_adaptive_mood_response(student_id, learning_context)
        else:
            # Fallback response
            mood_response = {
                'mood': 'happy',
                'expression': {'message': 'Ready to learn!'},
                'timestamp': datetime.now()
            }
        
        return jsonify({
            'success': True,
            'mood_data': mood_response
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/avatar-mood-update', methods=['POST'])
def api_avatar_mood_update():
    """Update avatar mood and get corresponding expression"""
    try:
        data = request.get_json()
        new_mood = data.get('mood', 'happy')
        context = data.get('context', 'general')
        student_id = data.get('student_id', 'default_student')
        
        # Get mood expression data
        if mood_engine:
            mood, expression = mood_engine.get_contextual_mood(context)
            
            # Get transition animation if previous mood provided
            previous_mood = data.get('previous_mood')
            transition_animation = None
            if previous_mood and previous_mood != new_mood:
                transition_animation = mood_engine.get_mood_transition_animation(previous_mood, new_mood)
        else:
            mood = new_mood
            expression = {'message': 'Looking good!'}
            transition_animation = None
        
        return jsonify({
            'success': True,
            'mood': mood,
            'expression': expression,
            'transition_animation': transition_animation,
            'timestamp': mood_response.get('timestamp').isoformat() if mood_response and mood_response.get('timestamp') else None
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/mood-analytics/<student_id>')
def api_mood_analytics(student_id):
    """Get mood and emotional engagement analytics for a student"""
    try:
        days = int(request.args.get('days', 7))
        if mood_engine:
            analytics = mood_engine.export_mood_analytics(student_id, days)
        else:
            analytics = {'message': 'Mood analytics not available'}
        
        return jsonify({
            'success': True,
            'analytics': analytics
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/mood-dashboard')
def mood_dashboard():
    """Dashboard for viewing mood and emotional engagement insights"""
    return render_template('mood_dashboard.html')

@app.route('/parent-dashboard')
def parent_dashboard():
    """Parent Dashboard with Progress Insights"""
    return render_template('parent_dashboard.html')

@app.route('/api/parent-dashboard/student/<student_id>')
def get_student_progress(student_id):
    """Get comprehensive student progress data"""
    from progress_service import ProgressService
    
    progress_service = ProgressService()
    data = progress_service.get_student_dashboard_data(student_id)
    
    return jsonify(data)

@app.route('/api/parent-dashboard/analytics/<student_id>')
def get_student_analytics(student_id):
    """Get detailed analytics for a specific student"""
    from progress_service import ProgressService
    
    date_range = request.args.get('range', '30')  # days
    
    progress_service = ProgressService()
    analytics = progress_service.get_detailed_analytics(student_id, int(date_range))
    
    return jsonify(analytics)

@app.route('/profile')
def profile():
    """Profile customization page"""
    return render_template('profile.html')

@app.route('/api/save-profile', methods=['POST'])
def save_profile():
    """Save user profile data"""
    try:
        profile_data = request.get_json()
        
        # Get user session or create default student ID
        student_id = session.get('student_id', 'default_student')
        
        # Add student ID and timestamp to profile data
        profile_data['student_id'] = student_id
        profile_data['updated_at'] = datetime.utcnow()
        
        # Try to save to Firebase if available
        try:
            db = get_firestore_client()
            if db:
                db.collection('student_profiles').document(student_id).set(profile_data)
                return jsonify({'success': True, 'message': 'Profile saved successfully'})
        except Exception as e:
            print(f"Firebase save failed: {e}")
        
        # Return success even if Firebase unavailable (data saved locally on client)
        return jsonify({'success': True, 'message': 'Profile saved locally'})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/get-profile')
def get_profile():
    """Get user profile data"""
    try:
        student_id = session.get('student_id', 'default_student')
        
        # Try to get from Firebase if available
        try:
            db = get_firestore_client()
            if db:
                doc = db.collection('student_profiles').document(student_id).get()
                if doc.exists:
                    return jsonify({'success': True, 'profile': doc.to_dict()})
        except Exception as e:
            print(f"Firebase get failed: {e}")
        
        # Return default profile if Firebase unavailable
        default_profile = {
            'name': 'Student',
            'age': '8',
            'grade': 'P3',
            'avatar': 'avatar1.jpeg',
            'favoriteSubject': 'maths'
        }
        return jsonify({'success': True, 'profile': default_profile})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/get-available-avatars')
def get_available_avatars():
    """Get list of available avatar images"""
    avatars = []
    for i in range(1, 19):  # avatar1.jpeg to avatar18.jpeg
        avatars.append({
            'id': f'avatar{i}',
            'filename': f'avatar{i}.jpeg',
            'url': url_for('static', filename=f'images/profile-pics/avatar{i}.jpeg')
        })
    
    return jsonify({'success': True, 'avatars': avatars})

@app.route('/api/check-avatar-unlocks/<student_id>')
def check_avatar_unlocks(student_id):
    """Check for newly unlocked achievement avatars"""
    try:
        from achievement_system import AvatarUnlockSystem
        
        unlock_system = AvatarUnlockSystem()
        newly_unlocked = unlock_system.check_avatar_unlocks(student_id)
        
        return jsonify({
            'success': True, 
            'newly_unlocked': newly_unlocked,
            'count': len(newly_unlocked)
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/avatar-progress/<student_id>')
def get_avatar_progress(student_id):
    """Get progress towards unlocking achievement avatars"""
    try:
        from achievement_system import AvatarUnlockSystem
        
        unlock_system = AvatarUnlockSystem()
        progress = unlock_system.get_avatar_progress(student_id)
        
        return jsonify({'success': True, 'progress': progress})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/trigger-unlock/<student_id>/<avatar_file>', methods=['POST'])
def trigger_avatar_unlock(student_id, avatar_file):
    """Manually trigger avatar unlock for testing"""
    try:
        from achievement_system import AvatarUnlockSystem
        
        unlock_system = AvatarUnlockSystem()
        celebration_data = unlock_system.trigger_unlock_celebration(avatar_file)
        
        return jsonify({
            'success': True,
            'celebration': celebration_data
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# Error Handlers for Automatic Error Reporting
@app.errorhandler(404)
def handle_404_error(error):
    """Handle 404 Not Found errors"""
    error_id = handle_server_error(error, {
        'error_type': '404_not_found',
        'requested_url': request.url,
        'referrer': request.referrer
    })
    return render_template('error.html', 
                         error_code=404,
                         error_message="Page not found",
                         error_id=error_id), 404

@app.errorhandler(500)
def handle_500_error(error):
    """Handle 500 Internal Server Error"""
    error_id = handle_server_error(error, {
        'error_type': '500_internal_error',
        'requested_url': request.url,
        'method': request.method
    })
    return render_template('error.html', 
                         error_code=500,
                         error_message="Internal server error occurred",
                         error_id=error_id), 500

@app.errorhandler(Exception)
def handle_general_exception(error):
    """Handle all uncaught exceptions"""
    error_id = handle_server_error(error, {
        'error_type': 'uncaught_exception',
        'requested_url': request.url,
        'method': request.method
    })
    return render_template('error.html', 
                         error_code=500,
                         error_message="An unexpected error occurred",
                         error_id=error_id), 500

# API endpoint for client-side error reporting
@app.route('/api/report-error', methods=['POST'])
def api_report_error():
    """Receive and process client-side error reports"""
    try:
        error_data = request.get_json()
        
        # Validate required fields
        if not error_data or 'message' not in error_data:
            return jsonify({
                'success': False,
                'error': 'Invalid error data provided'
            }), 400
        
        # Process the client error
        error_id = error_reporter.capture_client_error(error_data)
        
        return jsonify({
            'success': True,
            'error_id': error_id,
            'message': 'Error reported successfully'
        })
        
    except Exception as e:
        # Handle error reporting errors
        fallback_error_id = handle_server_error(e, {
            'context': 'error_reporting_failure'
        })
        
        return jsonify({
            'success': False,
            'error': 'Failed to process error report',
            'fallback_error_id': fallback_error_id
        }), 500

# API endpoint for error statistics (admin use)
@app.route('/api/error-stats')
def api_error_stats():
    """Get error statistics for monitoring"""
    try:
        days_back = int(request.args.get('days', 7))
        stats = error_reporter.get_error_statistics(days_back)
        
        return jsonify({
            'success': True,
            'statistics': stats
        })
        
    except Exception as e:
        error_id = handle_server_error(e, {
            'context': 'error_stats_retrieval'
        })
        
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve error statistics',
            'error_id': error_id
        }), 500

# Admin dashboard for error monitoring
@app.route('/admin/errors')
def admin_error_dashboard():
    """Admin dashboard for monitoring errors"""
    try:
        return render_template('admin_errors.html')
    except Exception as e:
        error_id = handle_server_error(e)
        return f"Error loading admin dashboard: {error_id}", 500

# Error reporting test page
@app.route('/test/errors')
def error_test_page():
    """Test page for error reporting system"""
    try:
        return render_template('error_test.html')
    except Exception as e:
        error_id = handle_server_error(e)
        return f"Error loading test page: {error_id}", 500

@app.route('/api/adaptive-difficulty/check-transition', methods=['POST'])
def check_difficulty_transition():
    """
    Check if difficulty level should change and generate transition animation
    """
    try:
        data = request.get_json()
        student_id = data.get('student_id', 'demo_student')
        current_performance = data.get('performance', {})
        current_level = data.get('current_level', 'easy')
        
        # Calculate performance metrics
        performance_data = adaptive_engine.calculate_student_performance(
            student_id, 
            current_performance.get('subject', 'maths')
        )
        
        # Determine if level should change
        recommended_level = adaptive_engine.get_recommended_difficulty_level(performance_data)
        
        if recommended_level != current_level:
            # Generate transition animation
            animation_data = adaptive_animations.generate_transition_animation(
                current_level, 
                recommended_level, 
                performance_data
            )
            
            return jsonify({
                "transition_needed": True,
                "old_level": current_level,
                "new_level": recommended_level,
                "animation_data": animation_data,
                "performance_summary": performance_data
            })
        else:
            return jsonify({
                "transition_needed": False,
                "current_level": current_level,
                "performance_summary": performance_data
            })
    
    except Exception as e:
        app.logger.error(f"Adaptive difficulty transition error: {str(e)}")
        return jsonify({"error": "Failed to check difficulty transition"}), 500

@app.route('/api/adaptive-difficulty/animations/css')
def get_animation_css():
    """
    Serve CSS styles for adaptive difficulty animations
    """
    try:
        css_content = adaptive_animations.generate_css_styles()
        return css_content, 200, {'Content-Type': 'text/css'}
    except Exception as e:
        app.logger.error(f"CSS generation error: {str(e)}")
        return "", 500

@app.route('/api/adaptive-difficulty/animations/js')
def get_animation_js():
    """
    Serve JavaScript functions for adaptive difficulty animations
    """
    try:
        js_content = adaptive_animations.generate_javascript_functions()
        return js_content, 200, {'Content-Type': 'application/javascript'}
    except Exception as e:
        app.logger.error(f"JavaScript generation error: {str(e)}")
        return "", 500

