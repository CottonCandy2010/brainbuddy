import os
import json

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("Google Generative AI library not available")

# Import DeepSeek integration
try:
    from deepseek_integration import deepseek_api
    DEEPSEEK_AVAILABLE = True
    print("DeepSeek AI integration loaded successfully")
except ImportError:
    DEEPSEEK_AVAILABLE = False
    print("DeepSeek integration not available")

# Initialize Gemini client
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
if GEMINI_API_KEY and GEMINI_AVAILABLE:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        print("Gemini AI configured successfully")
    except Exception as e:
        print(f"Error configuring Gemini: {e}")
        GEMINI_AVAILABLE = False
else:
    print("Gemini API key not found or library unavailable")

def generate_lesson_content(subject, learning_style, topic=None):
    """
    Generate personalized lesson content using Google Gemini AI.
    
    Args:
        subject (str): The subject (maths, science, english)
        learning_style (str): The learning style (visual, verbal, auditory)
        topic (str): Optional specific topic for the lesson
    
    Returns:
        dict: Contains title and content for the lesson
    """
    
    # Use Gemini AI to generate authentic educational content
    if GEMINI_API_KEY and GEMINI_AVAILABLE:
        try:
            return generate_gemini_lesson_content(subject, learning_style, topic)
        except Exception as e:
            print(f"Error generating Gemini content: {e}")
    
    # If Gemini is not available, provide structured educational content
    return create_structured_lesson_content(subject, learning_style, topic)
    
def generate_gemini_lesson_content(subject, learning_style, topic=None):
    """Generate lesson content using Gemini AI"""
    
    # Define age-appropriate topics for primary school
    primary_topics = {
        'maths': 'Counting and Numbers 1-20',
        'science': 'Plants and Animals Around Us',
        'english': 'Reading Simple Stories and Basic Writing'
    }
    
    if not topic:
        topic = primary_topics.get(subject, 'Basic Introduction')
    
    # Create educational prompt for Gemini
    prompt = f"""
    Create a clear, well-structured educational lesson for primary school children (ages 5-7) on the topic: "{topic}" in {subject}.
    
    Format the lesson as follows:
    
    LESSON TITLE: [Clear title for the lesson]
    
    WHAT YOU'LL LEARN:
    - [3-4 simple learning objectives]
    
    LET'S START LEARNING:
    [Main content with simple explanations, examples, and engaging activities]
    
    PRACTICE TIME:
    [3-4 practice activities or exercises]
    
    QUICK CHECK:
    [2-3 simple questions to check understanding]
    
    Make the content:
    - Age-appropriate for 5-7 year olds
    - Use simple, clear language
    - Include practical examples from daily life
    - Encourage active participation
    - Organized in clear sections with headings
    
    Focus on {learning_style} learning approaches in the activities and explanations.
    
    IMPORTANT: For visual learners, include interactive elements like:
    - Clickable buttons and interactive games
    - Visual counting exercises with pictures
    - Shape recognition activities
    - Drag and drop exercises
    - Visual math problems with graphics
    
    For auditory learners, include:
    - Audio instructions and explanations
    - Songs and rhymes for learning
    - Speaking exercises
    - Listening activities
    
    For verbal learners, include:
    - Reading exercises
    - Written explanations
    - Text-based questions
    - Word problems
    """
    
    try:
        if GEMINI_AVAILABLE:
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(prompt)
            lesson_content = response.text
        else:
            lesson_content = f"Interactive {subject} lesson content for {topic}"
        
        # For visual learning, provide interactive content
        if learning_style == 'visual':
            try:
                with open('templates/visual_content.html', 'r') as f:
                    visual_content = f.read()
                content_to_use = visual_content
            except Exception as e:
                print(f"Error loading visual content: {e}")
                content_to_use = lesson_content
        # For verbal learning with maths fundamentals, provide numbers 1-100
        elif learning_style == 'verbal' and subject == 'maths' and ('fundamental' in (topic or '').lower() or topic is None):
            content_to_use = generate_verbal_math_content()
        else:
            content_to_use = lesson_content
        
        return {
            'title': f"{topic} - {learning_style.title()} Learning",
            'content': content_to_use,
            'visual': content_to_use if learning_style == 'visual' else f"<p>Switch to Visual tab for interactive visual learning about {topic}</p>",
            'verbal': content_to_use if learning_style == 'verbal' else f"<p>Switch to Verbal tab for written learning content about {topic}</p>",
            'auditory': lesson_content if learning_style == 'auditory' else f"<p>Switch to Auditory tab for audio learning content about {topic}</p>",
            'current_style': learning_style,
            'description': f"Interactive {subject} lesson for primary school students",
            'objectives': f"Students will learn fundamental concepts in {topic}",
            'activities': "Hands-on activities and practice exercises"
        }
        
    except Exception as e:
        print(f"Gemini API error: {e}")
        return create_structured_lesson_content(subject, learning_style, topic)

def create_structured_lesson_content(subject, learning_style, topic=None):
    """Create structured educational content when AI is not available"""
    
    if not topic:
        topic = f"Introduction to {subject.title()}"
    
    # Create authentic mathematics content for primary students
    if subject == 'maths' and 'numbers' in topic.lower():
        # Check if this is Primary 1 content (Numbers 1-10)
        if '1-10' in topic or 'Primary 1' in topic:
            content = """
            <h4>Learning About Numbers 1-10</h4>
            
            <h5>What You'll Learn Today:</h5>
            <ul>
                <li>Recognize and count numbers from 1 to 10</li>
                <li>Understand the order of numbers 1-10</li>
                <li>Practice writing numbers 1-10 correctly</li>
                <li>Count objects up to 10</li>
            </ul>
            
            <h5>Let's Start Counting!</h5>
            <p>Numbers help us count things around us. Let's practice with familiar objects:</p>
            
            <div class="counting-activity">
                <p><strong>Count with me:</strong></p>
                <p>🍎 1 apple, 🍎🍎 2 apples, 🍎🍎🍎 3 apples...</p>
                <p>Can you count to 10? Let's try: 1, 2, 3, 4, 5, 6, 7, 8, 9, 10!</p>
            </div>
            """
        else:
            content = """
            <h4>Learning About Numbers 1-20</h4>
            
            <h5>What You'll Learn Today:</h5>
            <ul>
                <li>Recognize and count numbers from 1 to 20</li>
                <li>Understand the order of numbers</li>
                <li>Practice writing numbers correctly</li>
            </ul>
            
            <h5>Let's Start Counting!</h5>
            <p>Numbers help us count things around us. Let's practice with familiar objects:</p>
            
            <div class="counting-activity">
                <p><strong>Count with me:</strong></p>
                <p>🍎 1 apple, 🍎🍎 2 apples, 🍎🍎🍎 3 apples...</p>
                <p>Can you count to 10? Let's try: 1, 2, 3, 4, 5, 6, 7, 8, 9, 10!</p>
            </div>
            """
        
        <h5>Practice Activities:</h5>
        <ol>
            <li>Point to objects around you and count them</li>
            <li>Practice writing numbers 1-10 on paper</li>
            <li>Count toys, books, or fingers</li>
        </ol>
        
        <h5>Quick Check:</h5>
        <p>What number comes after 5? What number comes before 8?</p>
        """
    else:
        content = f"""
        <h4>Learning About {topic}</h4>
        
        <h5>Learning Objectives:</h5>
        <p>In this lesson, students will explore fundamental concepts in {subject} through interactive activities designed for {learning_style} learners.</p>
        
        <h5>Main Content:</h5>
        <p>This lesson introduces key concepts that are age-appropriate for primary school students, encouraging active participation and hands-on learning.</p>
        
        <h5>Practice Activities:</h5>
        <p>Students will engage in structured activities that reinforce learning through practical application and guided practice.</p>
        """
    
    return {
        'title': f"{topic} - {learning_style.title()} Learning",
        'visual': content,
        'verbal': content,
        'auditory': content,
        'current_style': learning_style,
        'description': f"Educational lesson in {subject} for primary school students",
        'objectives': f"Students will learn fundamental concepts in {topic}",
        'activities': "Interactive exercises and hands-on activities"
    }
    
    # Create the prompt for generating content
    prompt = f"""
    You are an expert educational content creator for secondary school students aged 11-16. 
    Create engaging lesson content about "{topic}" for the subject "{subject}".
    
    Generate content optimized for SEVEN different learning styles:
    
    1. VISUAL learners: Create actual SVG diagrams, interactive visual elements, color wheels, charts, and step-by-step visual guides using HTML/SVG code
    2. VERBAL learners: Provide clear written explanations, definitions, examples, and structured text-based learning
    3. AUDITORY learners: Create content that would work well when read aloud, with rhythm, repetition, and conversational tone
    4. PHYSICAL learners: Include hands-on activities, experiments, movement-based learning, and tactile experiences
    5. LOGICAL learners: Provide step-by-step reasoning, patterns, cause-and-effect relationships, and systematic approaches
    6. SOCIAL learners: Include group activities, discussions, collaborative projects, and peer learning opportunities
    7. SOLITARY learners: Create self-reflection questions, independent study tasks, personal exploration, and individual challenges
    
    Make the content:
    - Age-appropriate for 11-16 year olds
    - Engaging and fun while educational
    - Clear and easy to understand
    - Interactive where possible
    - About 150-200 words per learning style
    
    Respond in JSON format with this exact structure:
    {{
        "title": "Lesson title",
        "visual": "HTML content for visual learners with descriptions of visual elements",
        "verbal": "HTML content for verbal learners with clear written explanations", 
        "auditory": "HTML content for auditory learners with conversational, rhythm-friendly text",
        "physical": "HTML content for physical learners with hands-on activities and experiments",
        "logical": "HTML content for logical learners with step-by-step reasoning and patterns",
        "social": "HTML content for social learners with group activities and discussions",
        "solitary": "HTML content for solitary learners with self-reflection and independent study"
    }}
    
    Use HTML tags like <h3>, <p>, <ul>, <li>, <strong>, <em> for formatting. Do not include <div> wrapper tags.
    
    IMPORTANT for VISUAL content: Create complete SVG diagrams and visual elements. For example:
    - Color wheels: Full SVG circles with color segments
    - Charts: SVG bar charts, pie charts with actual data
    - Diagrams: Complete SVG illustrations with labels
    - Math visuals: Geometric shapes, fraction bars, number lines
    - Science diagrams: Cell structures, water cycle illustrations
    Never use placeholder text. Always generate working SVG code.
    """
    
    try:
        # Use Google Gemini Pro model
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Create the full prompt with system instruction
        full_prompt = f"""You are an expert educational content creator specializing in personalized learning for secondary school students. Always respond with valid JSON in the exact format requested.

{prompt}"""
        
        response = model.generate_content(
            full_prompt,
            generation_config={
                'temperature': 0.7,
                'max_output_tokens': 2000,
            }
        )
        
        # Parse the JSON response
        response_content = response.text
        if response_content is None:
            raise ValueError("Empty response from Gemini")
        
        # Clean up the response to extract JSON
        response_content = response_content.strip()
        if response_content.startswith('```json'):
            response_content = response_content[7:-3]
        elif response_content.startswith('```'):
            response_content = response_content[3:-3]
        
        content = json.loads(response_content)
        
        # Ensure all required keys exist
        required_keys = ['title', 'visual', 'verbal', 'auditory', 'physical', 'logical', 'social', 'solitary']
        for key in required_keys:
            if key not in content:
                content[key] = f"Content for {key} learning style is being generated..."
        
        # Add the current learning style to the response
        content['current_style'] = learning_style
        
        return content
        
    except json.JSONDecodeError as e:
        print(f"JSON parsing error: {e}")
        return get_fallback_content(subject, learning_style, topic)
    except Exception as e:
        print(f"Gemini API error: {e}")
        return get_visual_enhanced_content(subject, learning_style, topic)

def get_fallback_content(subject, learning_style, topic):
    """
    Fallback content in case of API errors - this should rarely be used
    but provides a safety net for the application.
    """
    return {
        'title': f'{topic or "Introduction to " + subject.title()}',
        'visual': f'<h3>Visual Learning</h3><p>We are generating personalized visual content for {subject}. Please try refreshing the page.</p>',
        'verbal': f'<h3>Verbal Learning</h3><p>We are generating personalized written content for {subject}. Please try refreshing the page.</p>',
        'auditory': f'<h3>Auditory Learning</h3><p>We are generating personalized audio-friendly content for {subject}. Please try refreshing the page.</p>',
        'current_style': learning_style
    }

def get_visual_enhanced_content(subject, learning_style, topic):
    """
    Enhanced visual content with actual SVG diagrams and interactive elements
    """
    visual_content = create_visual_content(subject, topic)
    
    return {
        'title': topic or f'Learning {subject.title()}',
        'visual': visual_content,
        'verbal': f'<h3>Written Learning</h3><p>Comprehensive written explanations for {subject} - {topic}. This content covers key concepts with clear examples and detailed explanations to help you master the topic.</p>',
        'auditory': create_audio_content(subject, topic),
        'physical': f'<h3>Hands-On Learning</h3><p>Interactive activities for {subject} - {topic}. Try hands-on experiments and physical activities that help you learn through movement and touch.</p>',
        'logical': f'<h3>Step-by-Step Learning</h3><p>Logical breakdown of {subject} - {topic}. Follow systematic steps and logical patterns to understand how concepts connect and build upon each other.</p>',
        'social': f'<h3>Group Learning</h3><p>Collaborative activities for {subject} - {topic}. Work with others through discussions, group projects, and peer learning to explore concepts together.</p>',
        'solitary': f'<h3>Independent Learning</h3><p>Self-paced study for {subject} - {topic}. Reflect on concepts independently through personal exploration and individual challenges.</p>',
        'current_style': learning_style
    }

def create_visual_content(subject, topic):
    """
    Create actual SVG visual content based on subject and topic
    """
    if subject.lower() == 'art':
        return create_art_visual(topic)
    elif subject.lower() == 'maths':
        return create_math_visual(topic)
    elif subject.lower() == 'science':
        return create_science_visual(topic)
    elif subject.lower() == 'geography':
        return create_geography_visual(topic)
    else:
        return create_general_visual(subject, topic)

def create_art_visual(topic):
    """Create interactive art visuals"""
    return '''
    <h3>Visual Art Learning</h3>
    <div class="art-visual-container text-center">
        <h4>Interactive Color Wheel</h4>
        <svg width="300" height="300" viewBox="0 0 300 300" class="mx-auto mb-4">
            <!-- Color Wheel -->
            <circle cx="150" cy="150" r="120" fill="none" stroke="#333" stroke-width="2"/>
            
            <!-- Primary Colors -->
            <circle cx="150" cy="50" r="20" fill="#FF0000" stroke="#000" stroke-width="2"/>
            <text x="150" y="25" text-anchor="middle" font-size="12" font-weight="bold">Red</text>
            
            <circle cx="254" cy="200" r="20" fill="#0000FF" stroke="#000" stroke-width="2"/>
            <text x="280" y="205" text-anchor="middle" font-size="12" font-weight="bold">Blue</text>
            
            <circle cx="46" cy="200" r="20" fill="#FFFF00" stroke="#000" stroke-width="2"/>
            <text x="20" y="205" text-anchor="middle" font-size="12" font-weight="bold">Yellow</text>
            
            <!-- Secondary Colors -->
            <circle cx="202" cy="100" r="15" fill="#FF8000" stroke="#000" stroke-width="1"/>
            <text x="202" y="125" text-anchor="middle" font-size="10">Orange</text>
            
            <circle cx="202" cy="200" r="15" fill="#8000FF" stroke="#000" stroke-width="1"/>
            <text x="202" y="225" text-anchor="middle" font-size="10">Purple</text>
            
            <circle cx="98" cy="100" r="15" fill="#80FF00" stroke="#000" stroke-width="1"/>
            <text x="98" y="125" text-anchor="middle" font-size="10">Green</text>
            
            <!-- Center -->
            <circle cx="150" cy="150" r="10" fill="#808080" stroke="#000" stroke-width="2"/>
            <text x="150" y="175" text-anchor="middle" font-size="10">Neutral</text>
        </svg>
        
        <h4>Color Temperature Scale</h4>
        <svg width="400" height="80" class="mx-auto mb-4">
            <defs>
                <linearGradient id="tempGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                    <stop offset="0%" style="stop-color:#0066CC;stop-opacity:1" />
                    <stop offset="25%" style="stop-color:#00CCFF;stop-opacity:1" />
                    <stop offset="50%" style="stop-color:#FFFFFF;stop-opacity:1" />
                    <stop offset="75%" style="stop-color:#FFCC00;stop-opacity:1" />
                    <stop offset="100%" style="stop-color:#FF3300;stop-opacity:1" />
                </linearGradient>
            </defs>
            <rect x="50" y="20" width="300" height="40" fill="url(#tempGradient)" stroke="#000" stroke-width="2"/>
            <text x="50" y="15" font-size="12" font-weight="bold">Cool</text>
            <text x="325" y="15" font-size="12" font-weight="bold">Warm</text>
        </svg>
        
        <div class="art-concepts mt-4">
            <h5>Key Art Concepts:</h5>
            <ul class="text-start">
                <li><strong>Primary Colors:</strong> Red, Blue, Yellow - cannot be mixed from other colors</li>
                <li><strong>Secondary Colors:</strong> Created by mixing two primary colors</li>
                <li><strong>Color Temperature:</strong> Cool colors (blues, greens) vs Warm colors (reds, yellows)</li>
                <li><strong>Complementary Colors:</strong> Colors opposite each other on the color wheel</li>
            </ul>
        </div>
    </div>
    '''

def create_math_visual(topic):
    """Create interactive math visuals"""
    return '''
    <h3>Mathematical Visualization</h3>
    <div class="math-visual-container">
        <h4>Fraction Representation</h4>
        <svg width="500" height="250" class="mx-auto mb-4">
            <!-- Whole -->
            <rect x="50" y="20" width="120" height="40" fill="#6c757d" stroke="#000" stroke-width="2"/>
            <text x="110" y="45" text-anchor="middle" fill="white" font-weight="bold">1 Whole</text>
            
            <!-- Halves -->
            <rect x="200" y="20" width="60" height="40" fill="#007bff" stroke="#000" stroke-width="2"/>
            <text x="230" y="45" text-anchor="middle" fill="white" font-weight="bold">1/2</text>
            <rect x="260" y="20" width="60" height="40" fill="#28a745" stroke="#000" stroke-width="2"/>
            <text x="290" y="45" text-anchor="middle" fill="white" font-weight="bold">1/2</text>
            
            <!-- Quarters -->
            <rect x="50" y="80" width="30" height="40" fill="#dc3545" stroke="#000" stroke-width="2"/>
            <text x="65" y="105" text-anchor="middle" fill="white" font-weight="bold">1/4</text>
            <rect x="80" y="80" width="30" height="40" fill="#fd7e14" stroke="#000" stroke-width="2"/>
            <text x="95" y="105" text-anchor="middle" fill="white" font-weight="bold">1/4</text>
            <rect x="110" y="80" width="30" height="40" fill="#ffc107" stroke="#000" stroke-width="2"/>
            <text x="125" y="105" text-anchor="middle" fill="black" font-weight="bold">1/4</text>
            <rect x="140" y="80" width="30" height="40" fill="#20c997" stroke="#000" stroke-width="2"/>
            <text x="155" y="105" text-anchor="middle" fill="white" font-weight="bold">1/4</text>
            
            <!-- Eighths -->
            <rect x="200" y="80" width="15" height="40" fill="#e83e8c" stroke="#000" stroke-width="1"/>
            <text x="207" y="105" text-anchor="middle" fill="white" font-size="10">1/8</text>
            <rect x="215" y="80" width="15" height="40" fill="#6f42c1" stroke="#000" stroke-width="1"/>
            <text x="222" y="105" text-anchor="middle" fill="white" font-size="10">1/8</text>
            <rect x="230" y="80" width="15" height="40" fill="#007bff" stroke="#000" stroke-width="1"/>
            <text x="237" y="105" text-anchor="middle" fill="white" font-size="10">1/8</text>
            <rect x="245" y="80" width="15" height="40" fill="#28a745" stroke="#000" stroke-width="1"/>
            <text x="252" y="105" text-anchor="middle" fill="white" font-size="10">1/8</text>
            <rect x="260" y="80" width="15" height="40" fill="#dc3545" stroke="#000" stroke-width="1"/>
            <text x="267" y="105" text-anchor="middle" fill="white" font-size="10">1/8</text>
            <rect x="275" y="80" width="15" height="40" fill="#fd7e14" stroke="#000" stroke-width="1"/>
            <text x="282" y="105" text-anchor="middle" fill="white" font-size="10">1/8</text>
            <rect x="290" y="80" width="15" height="40" fill="#ffc107" stroke="#000" stroke-width="1"/>
            <text x="297" y="105" text-anchor="middle" fill="black" font-size="10">1/8</text>
            <rect x="305" y="80" width="15" height="40" fill="#20c997" stroke="#000" stroke-width="1"/>
            <text x="312" y="105" text-anchor="middle" fill="white" font-size="10">1/8</text>
            
            <!-- Number Line -->
            <line x1="50" y1="180" x2="350" y2="180" stroke="#000" stroke-width="3"/>
            <text x="50" y="200" text-anchor="middle" font-weight="bold">0</text>
            <text x="125" y="200" text-anchor="middle" font-weight="bold">1/4</text>
            <text x="200" y="200" text-anchor="middle" font-weight="bold">1/2</text>
            <text x="275" y="200" text-anchor="middle" font-weight="bold">3/4</text>
            <text x="350" y="200" text-anchor="middle" font-weight="bold">1</text>
            
            <!-- Tick marks -->
            <line x1="50" y1="175" x2="50" y2="185" stroke="#000" stroke-width="2"/>
            <line x1="125" y1="175" x2="125" y2="185" stroke="#000" stroke-width="2"/>
            <line x1="200" y1="175" x2="200" y2="185" stroke="#000" stroke-width="2"/>
            <line x1="275" y1="175" x2="275" y2="185" stroke="#000" stroke-width="2"/>
            <line x1="350" y1="175" x2="350" y2="185" stroke="#000" stroke-width="2"/>
        </svg>
        
        <div class="math-concepts mt-4">
            <h5>Understanding Fractions:</h5>
            <ul>
                <li><strong>Numerator:</strong> Top number - shows how many parts we have</li>
                <li><strong>Denominator:</strong> Bottom number - shows total equal parts</li>
                <li><strong>Equivalent Fractions:</strong> Different fractions representing the same amount (1/2 = 2/4 = 4/8)</li>
                <li><strong>Comparing:</strong> Use the number line to see which fractions are larger or smaller</li>
            </ul>
        </div>
    </div>
    '''

def create_science_visual(topic):
    """Create interactive science visuals"""
    return '''
    <h3>Scientific Visualization</h3>
    <div class="science-visual-container">
        <h4>The Water Cycle</h4>
        <svg width="600" height="400" class="mx-auto mb-4">
            <!-- Sky background -->
            <rect x="0" y="0" width="600" height="200" fill="#87CEEB"/>
            
            <!-- Sun -->
            <circle cx="500" cy="60" r="30" fill="#FFD700" stroke="#FFA500" stroke-width="2"/>
            <path d="M 470 60 L 450 60" stroke="#FFD700" stroke-width="3"/>
            <path d="M 530 60 L 550 60" stroke="#FFD700" stroke-width="3"/>
            <path d="M 500 30 L 500 10" stroke="#FFD700" stroke-width="3"/>
            <path d="M 500 90 L 500 110" stroke="#FFD700" stroke-width="3"/>
            
            <!-- Clouds -->
            <ellipse cx="150" cy="80" rx="40" ry="25" fill="#FFFFFF" stroke="#CCCCCC"/>
            <ellipse cx="180" cy="75" rx="35" ry="20" fill="#FFFFFF" stroke="#CCCCCC"/>
            <ellipse cx="120" cy="85" rx="30" ry="18" fill="#FFFFFF" stroke="#CCCCCC"/>
            
            <!-- Rain drops -->
            <path d="M 140 110 L 135 140" stroke="#4169E1" stroke-width="2"/>
            <path d="M 160 115 L 155 145" stroke="#4169E1" stroke-width="2"/>
            <path d="M 180 112 L 175 142" stroke="#4169E1" stroke-width="2"/>
            <path d="M 120 118 L 115 148" stroke="#4169E1" stroke-width="2"/>
            
            <!-- Ground -->
            <rect x="0" y="250" width="600" height="150" fill="#8B4513"/>
            
            <!-- Ocean -->
            <ellipse cx="450" cy="275" rx="120" ry="40" fill="#006994" stroke="#004B73"/>
            <path d="M 350 265 Q 400 255 450 265 Q 500 255 550 265" stroke="#87CEEB" stroke-width="2" fill="none"/>
            
            <!-- Mountains -->
            <path d="M 0 250 L 80 180 L 160 250 Z" fill="#696969" stroke="#2F4F4F"/>
            <path d="M 100 250 L 200 160 L 300 250 Z" fill="#708090" stroke="#2F4F4F"/>
            
            <!-- Trees -->
            <rect x="85" y="220" width="10" height="30" fill="#8B4513"/>
            <ellipse cx="90" cy="210" rx="15" ry="20" fill="#228B22"/>
            
            <rect x="250" y="225" width="8" height="25" fill="#8B4513"/>
            <ellipse cx="254" cy="218" rx="12" ry="15" fill="#32CD32"/>
            
            <!-- Evaporation arrows -->
            <path d="M 420 260 Q 430 220 440 180" stroke="#FF6347" stroke-width="2" fill="none" marker-end="url(#arrowhead)"/>
            <path d="M 460 265 Q 470 230 480 190" stroke="#FF6347" stroke-width="2" fill="none" marker-end="url(#arrowhead)"/>
            
            <!-- Condensation arrow -->
            <path d="M 200 120 Q 250 140 300 160" stroke="#4169E1" stroke-width="2" fill="none" marker-end="url(#arrowhead)"/>
            
            <!-- Define arrow marker -->
            <defs>
                <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="10" refY="3.5" orient="auto">
                    <polygon points="0 0, 10 3.5, 0 7" fill="#FF6347"/>
                </marker>
            </defs>
            
            <!-- Labels -->
            <text x="500" y="45" text-anchor="middle" font-size="12" font-weight="bold">SUN</text>
            <text x="150" y="65" text-anchor="middle" font-size="12" font-weight="bold">CLOUDS</text>
            <text x="150" y="160" text-anchor="middle" font-size="10">Precipitation</text>
            <text x="450" y="290" text-anchor="middle" font-size="12" fill="white" font-weight="bold">OCEAN</text>
            <text x="480" y="220" font-size="10" fill="#FF6347">Evaporation</text>
            <text x="250" y="155" font-size="10" fill="#4169E1">Condensation</text>
        </svg>
        
        <div class="science-concepts mt-4">
            <h5>Water Cycle Process:</h5>
            <ol>
                <li><strong>Evaporation:</strong> Sun heats water, turning it into water vapor</li>
                <li><strong>Condensation:</strong> Water vapor cools and forms clouds</li>
                <li><strong>Precipitation:</strong> Water falls as rain, snow, or hail</li>
                <li><strong>Collection:</strong> Water collects in oceans, lakes, and rivers</li>
            </ol>
        </div>
    </div>
    '''

def create_geography_visual(topic):
    """Create interactive geography visuals"""
    return '''
    <h3>Geographic Visualization</h3>
    <div class="geography-visual-container">
        <h4>Climate Zones</h4>
        <svg width="500" height="300" class="mx-auto mb-4">
            <!-- Earth outline -->
            <ellipse cx="250" cy="150" rx="200" ry="120" fill="#87CEEB" stroke="#000" stroke-width="2"/>
            
            <!-- Climate zones -->
            <ellipse cx="250" cy="80" rx="180" ry="25" fill="#FFFFFF" opacity="0.8"/>
            <text x="250" y="85" text-anchor="middle" font-size="12" font-weight="bold">Arctic Zone</text>
            
            <ellipse cx="250" cy="120" rx="190" ry="35" fill="#90EE90" opacity="0.7"/>
            <text x="250" y="125" text-anchor="middle" font-size="12" font-weight="bold">Temperate Zone</text>
            
            <ellipse cx="250" cy="150" rx="195" ry="25" fill="#FFD700" opacity="0.7"/>
            <text x="250" y="155" text-anchor="middle" font-size="12" font-weight="bold">Tropical Zone</text>
            
            <ellipse cx="250" cy="180" rx="190" ry="35" fill="#90EE90" opacity="0.7"/>
            <text x="250" y="185" text-anchor="middle" font-size="12" font-weight="bold">Temperate Zone</text>
            
            <ellipse cx="250" cy="220" rx="180" ry="25" fill="#FFFFFF" opacity="0.8"/>
            <text x="250" y="225" text-anchor="middle" font-size="12" font-weight="bold">Antarctic Zone</text>
            
            <!-- Latitude lines -->
            <line x1="50" y1="80" x2="450" y2="80" stroke="#000" stroke-width="1" stroke-dasharray="5,5"/>
            <line x1="60" y1="120" x2="440" y2="120" stroke="#000" stroke-width="1" stroke-dasharray="5,5"/>
            <line x1="55" y1="150" x2="445" y2="150" stroke="#000" stroke-width="2"/>
            <line x1="60" y1="180" x2="440" y2="180" stroke="#000" stroke-width="1" stroke-dasharray="5,5"/>
            <line x1="50" y1="220" x2="450" y2="220" stroke="#000" stroke-width="1" stroke-dasharray="5,5"/>
        </svg>
        
        <div class="geography-concepts mt-4">
            <h5>Climate Zone Characteristics:</h5>
            <ul>
                <li><strong>Tropical Zone:</strong> Hot temperatures year-round, high rainfall</li>
                <li><strong>Temperate Zones:</strong> Moderate temperatures, four distinct seasons</li>
                <li><strong>Polar Zones:</strong> Cold temperatures, ice and snow</li>
                <li><strong>Equator:</strong> Imaginary line at 0° latitude, hottest region</li>
            </ul>
        </div>
    </div>
    '''

def create_general_visual(subject, topic):
    """Create general visual content for other subjects"""
    return f'''
    <h3>Visual Learning for {subject.title()}</h3>
    <div class="general-visual-container text-center">
        <svg width="400" height="200" class="mx-auto mb-4">
            <rect x="50" y="50" width="300" height="100" fill="#f8f9fa" stroke="#007bff" stroke-width="3" rx="10"/>
            <text x="200" y="90" text-anchor="middle" font-size="16" font-weight="bold" fill="#007bff">{topic}</text>
            <text x="200" y="110" text-anchor="middle" font-size="14" fill="#6c757d">Interactive Visual Learning</text>
            <circle cx="80" cy="100" r="15" fill="#28a745"/>
            <circle cx="320" cy="100" r="15" fill="#dc3545"/>
            <path d="M 95 100 L 305 100" stroke="#ffc107" stroke-width="4"/>
        </svg>
        <div class="concept-explanation">
            <h5>Key Visual Concepts:</h5>
            <p>This interactive diagram helps you understand {topic} through visual representation. 
            Visual learning engages your spatial intelligence and helps you see patterns and connections.</p>
        </div>
    </div>
    '''

def create_audio_content(subject, topic):
    """Create interactive audio content with voice selection and volume controls"""
    
    # Generate engaging audio-friendly content based on subject
    audio_content = {
        'maths': f"Welcome to your audio math lesson on {topic}! Let's explore mathematical concepts through clear explanations and step-by-step examples. Mathematics is all about patterns and logical thinking. Listen carefully as we break down complex ideas into simple, understandable parts.",
        'science': f"Discover the wonders of science with this audio lesson on {topic}! Science helps us understand how the world works through observation and experimentation. Let's explore fascinating scientific concepts together through engaging explanations.",
        'english': f"Enhance your English skills with this audio lesson on {topic}! Language is a powerful tool for communication and expression. Listen as we explore grammar, vocabulary, and reading comprehension in an engaging way.",
        'art': f"Express your creativity with this audio art lesson on {topic}! Art is about imagination, color, and visual expression. Listen to learn about artistic techniques, famous artists, and how to create beautiful works of art.",
        'geography': f"Explore our amazing world with this audio geography lesson on {topic}! Geography teaches us about places, people, and environments around the globe. Let's discover interesting facts about our planet together.",
        'history': f"Travel through time with this audio history lesson on {topic}! History tells the story of human civilization and helps us understand how we got to where we are today. Listen to fascinating stories from the past."
    }.get(subject.lower(), f"Welcome to your audio lesson on {topic}! Learning through listening helps reinforce concepts and improves comprehension. Let's explore this topic together through engaging audio content.")
    
    return f'''
    <div class="audio-learning-section">
        <div class="audio-controls-header">
            <h3>🎧 Audio Learning</h3>
            <p>Listen to your personalized lesson with AI voice narration</p>
        </div>
        
        <div class="audio-content-box">
            <div class="audio-text" id="audioText" data-subject="{subject}" data-topic="{topic}">
                {audio_content}
            </div>
            
            <div class="audio-controls">
                <div class="voice-selection">
                    <label for="voiceSelect">Choose Voice:</label>
                    <select id="voiceSelect" class="voice-selector">
                        <option value="female-1">Female Voice 1</option>
                        <option value="female-2">Female Voice 2</option>
                        <option value="male-1">Male Voice 1</option>
                        <option value="male-2">Male Voice 2</option>
                    </select>
                </div>
                
                <div class="volume-control">
                    <label for="volumeSlider">Volume:</label>
                    <input type="range" id="volumeSlider" min="0" max="100" value="80" class="volume-slider">
                    <span id="volumeValue">80%</span>
                </div>
                
                <div class="audio-buttons">
                    <button id="playAudioBtn" class="audio-btn play-btn">
                        <span class="btn-icon">▶️</span>
                        Play Audio
                    </button>
                    <button id="pauseAudioBtn" class="audio-btn pause-btn" style="display: none;">
                        <span class="btn-icon">⏸️</span>
                        Pause
                    </button>
                    <button id="stopAudioBtn" class="audio-btn stop-btn" style="display: none;">
                        <span class="btn-icon">⏹️</span>
                        Stop
                    </button>
                </div>
                
                <div class="audio-status" id="audioStatus">
                    Ready to play
                </div>
            </div>
        </div>
        
        <div class="audio-tips">
            <h4>📚 Audio Learning Tips</h4>
            <ul>
                <li>Find a quiet space to focus on the audio content</li>
                <li>Take notes while listening to reinforce learning</li>
                <li>Replay sections if you need to hear them again</li>
                <li>Try different voices to find your preferred learning style</li>
            </ul>
        </div>
    </div>
    '''

def generate_custom_topic_content(subject, learning_style, custom_topic):
    """
    Generate content for a custom topic specified by the user.
    """
    return generate_lesson_content(subject, learning_style, custom_topic)

def generate_study_buddy_response(user_message, context=None):
    """
    Generate Study Buddy AI responses using Gemini
    """
    try:
        # Use Gemini to generate study buddy responses
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Create context-aware prompt
        context_text = ""
        if context and len(context) > 0:
            context_text = "\n\nPrevious conversation:\n" + "\n".join([f"User: {msg.get('user', '')}\nBuddy: {msg.get('buddy', '')}" for msg in context[-3:]])
        
        prompt = f"""You are Study Buddy AI, a friendly and encouraging AI tutor for students aged 11-18. You help with homework, explain concepts, provide study tips, and keep students motivated.

Key personality traits:
- Enthusiastic and supportive
- Use age-appropriate language
- Include relevant emojis
- Break down complex topics into simple steps
- Provide practical examples
- Encourage learning and growth
- Be patient and understanding

Student's message: "{user_message}"
{context_text}

Respond as Study Buddy AI with helpful, engaging advice. Keep responses concise but informative (2-4 sentences max)."""

        response = model.generate_content(
            prompt,
            generation_config={
                'temperature': 0.8,
                'max_output_tokens': 300,
            }
        )
        
        return response.text.strip()
        
    except Exception as e:
        print(f"Error generating Study Buddy response: {e}")
        return get_fallback_study_response(user_message)

def get_fallback_study_response(user_message):
    """Fallback responses when AI is unavailable"""
    message_lower = user_message.lower()
    
    if any(word in message_lower for word in ['math', 'maths', 'calculate', 'number']):
        return "Math can be tricky, but let's break it down step by step! 📊 What specific math topic are you working on? I'm here to help make it clearer!"
    
    elif any(word in message_lower for word in ['science', 'experiment', 'biology', 'chemistry', 'physics']):
        return "Science is fascinating! 🔬 Let's explore this topic together. Can you tell me more about what you're studying? I love helping with scientific concepts!"
    
    elif any(word in message_lower for word in ['english', 'writing', 'essay', 'grammar', 'reading']):
        return "Great question about English! 📝 Reading and writing are such important skills. What specific area would you like help with? I'm excited to assist!"
    
    elif any(word in message_lower for word in ['study', 'tips', 'help', 'learn']):
        return "I'm so glad you're focused on learning! 🌟 Here's a great tip: break your study time into 25-minute chunks with 5-minute breaks. What subject are you studying today?"
    
    elif any(word in message_lower for word in ['motivation', 'tired', 'difficult', 'hard']):
        return "I believe in you! 💪 Learning can be challenging, but every small step counts. Remember, even the smartest people started as beginners. What's one small thing we can tackle together right now?"
    
    else:
        return "That's a great question! 🤔 I'm here to help you learn and grow. Could you tell me a bit more about what you're working on? I want to give you the best possible help!"

def generate_verbal_math_content():
    """Generate comprehensive verbal content for maths fundamentals including numbers 1-100"""
    
    # Number to word mapping for 1-100
    number_words = {}
    
    # Basic numbers 1-19
    basic = ["", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", 
             "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen", 
             "seventeen", "eighteen", "nineteen"]
    
    # Tens
    tens = ["", "", "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety"]
    
    # Generate all numbers 1-100
    for i in range(1, 101):
        if i == 100:
            number_words[i] = "one hundred"
        elif i < 20:
            number_words[i] = basic[i]
        else:
            ten_digit = i // 10
            unit_digit = i % 10
            if unit_digit == 0:
                number_words[i] = tens[ten_digit]
            else:
                number_words[i] = tens[ten_digit] + "-" + basic[unit_digit]
    
    content = """<div class="verbal-math-content">
        <h2>Maths Fundamentals - Verbal Learning</h2>
        <p class="lesson-intro">Learn to read and write numbers from 1 to 100 with their written spellings.</p>
        
        <div class="number-section">
            <h3>Numbers 1-100 with Written Spellings</h3>
            <div class="numbers-list">"""
    
    # Add all numbers 1-100 with their written forms
    for num in range(1, 101):
        word = number_words[num]
        content += f'<div class="number-line">{num} - {word}</div>'
    
    content += """</div>
        </div>
        
        <style>
        .verbal-math-content {
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            font-family: 'Nunito', sans-serif;
        }
        
        .numbers-list {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 8px;
            margin: 20px 0;
            max-height: 400px;
            overflow-y: auto;
            padding: 15px;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            background: #f8f9fa;
        }
        
        .number-line {
            padding: 8px 12px;
            background: white;
            border: 1px solid #ddd;
            border-radius: 5px;
            font-size: 16px;
            font-weight: 500;
        }
        
        .lesson-intro {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px;
            border-radius: 10px;
            text-align: center;
            margin: 20px 0;
        }
        </style>
    </div>"""
    
    return content