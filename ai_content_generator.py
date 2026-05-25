"""
AI Content Generator for Brain Buddy
Generates personalized lesson content using Claude AI
"""

import anthropic
import os

# Initialize Anthropic client (reads ANTHROPIC_API_KEY from environment)
anthropic_client = anthropic.Anthropic()

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
    try:
        return generate_gemini_lesson_content(subject, learning_style, topic)
    except Exception as e:
        print(f"Gemini API error: {e}")
        return create_structured_lesson_content(subject, learning_style, topic)

def generate_gemini_lesson_content(subject, learning_style, topic=None):
    """Generate lesson content using Claude AI"""

    if not topic:
        topic = f"Introduction to {subject.title()}"

    # Check if this is Primary 1 Numbers 1-10 content
    if subject == 'maths' and ('1-10' in topic or 'Numbers 1-10' in topic):
        return create_primary1_math_content(learning_style, topic)

    # Check if this is Primary 1 Big & Small content
    if subject == 'maths' and ('Big & Small' in topic or 'big and small' in topic.lower()):
        return create_primary1_size_content(learning_style, topic)

    # Create the prompt for generating content
    prompt = f"""
    Create an engaging educational lesson for primary school children aged 5-11 about {topic} in {subject}.

    Learning Style: {learning_style}
    Subject: {subject}
    Topic: {topic}

    Please create content that is:
    - Age-appropriate for children aged 5-11
    - Interactive and engaging
    - Includes simple examples
    - Uses child-friendly language
    - Incorporates hands-on activities

    Format the response as HTML with proper headings and structure.
    """

    try:
        with anthropic_client.messages.stream(
            model="claude-opus-4-7",
            max_tokens=2048,
            messages=[{"role": "user", "content": prompt}]
        ) as stream:
            lesson_content = stream.get_final_message().content[0].text
    except Exception as e:
        print(f"Claude API error: {e}")
        lesson_content = f"Interactive {subject} lesson content for {topic}"
    
    return {
        'title': f"{topic} - {learning_style.title()} Learning",
        'content': lesson_content,
        'visual': lesson_content if learning_style == 'visual' else f"<p>Switch to Visual tab for interactive visual learning about {topic}</p>",
        'verbal': lesson_content if learning_style == 'verbal' else f"<p>Switch to Verbal tab for written learning content about {topic}</p>",
        'auditory': lesson_content if learning_style == 'auditory' else f"<p>Switch to Auditory tab for audio learning content about {topic}</p>",
        'current_style': learning_style,
        'description': f"Interactive {subject} lesson for primary school students",
        'objectives': f"Students will learn fundamental concepts in {topic}",
        'activities': "Hands-on activities and practice exercises"
    }

def create_primary1_math_content(learning_style, topic):
    """Create Primary 1 math content for numbers 1-10"""
    
    # Visual learning content with images and colors
    visual_content = """
    <h4>🎨 Visual Learning: Numbers 1-10</h4>
    
    <h5>🔢 Number Recognition:</h5>
    <div class="visual-numbers">
        <p style="font-size: 24px; color: #ff4757; margin: 10px 0;"><strong>1</strong> 🍎</p>
        <p style="font-size: 24px; color: #ff6348; margin: 10px 0;"><strong>2</strong> 🍎🍎</p>
        <p style="font-size: 24px; color: #ff7675; margin: 10px 0;"><strong>3</strong> 🍎🍎🍎</p>
        <p style="font-size: 24px; color: #fdcb6e; margin: 10px 0;"><strong>4</strong> ⭐⭐⭐⭐</p>
        <p style="font-size: 24px; color: #f1c40f; margin: 10px 0;"><strong>5</strong> ⭐⭐⭐⭐⭐</p>
        <p style="font-size: 24px; color: #00b894; margin: 10px 0;"><strong>6</strong> 🟢🟢🟢🟢🟢🟢</p>
        <p style="font-size: 24px; color: #fdcb6e; margin: 10px 0;"><strong>7</strong> 🟡🟡🟡🟡🟡🟡🟡</p>
        <p style="font-size: 24px; color: #74b9ff; margin: 10px 0;"><strong>8</strong> 🔵🔵🔵🔵🔵🔵🔵🔵</p>
        <p style="font-size: 24px; color: #e84393; margin: 10px 0;"><strong>9</strong> 🔴🔴🔴🔴🔴🔴🔴🔴🔴</p>
        <p style="font-size: 24px; color: #ffeaa7; margin: 10px 0;"><strong>10</strong> 🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟</p>
    </div>
    
    <h5>📊 Number Line:</h5>
    <div style="background: #ecf0f1; padding: 15px; border-radius: 8px; margin: 15px 0;">
        <p style="font-size: 20px; text-align: center;">
            <span style="color: #ff4757; font-weight: bold;">1</span> — 
            <span style="color: #ff6348; font-weight: bold;">2</span> — 
            <span style="color: #ff7675; font-weight: bold;">3</span> — 
            <span style="color: #fdcb6e; font-weight: bold;">4</span> — 
            <span style="color: #f1c40f; font-weight: bold;">5</span> — 
            <span style="color: #00b894; font-weight: bold;">6</span> — 
            <span style="color: #fdcb6e; font-weight: bold;">7</span> — 
            <span style="color: #74b9ff; font-weight: bold;">8</span> — 
            <span style="color: #e84393; font-weight: bold;">9</span> — 
            <span style="color: #ffeaa7; font-weight: bold;">10</span>
        </p>
    </div>
    
    <h5>🎯 Visual Activities:</h5>
    <ul>
        <li>🖍️ Color the numbers 1-10 in rainbow colors</li>
        <li>👆 Count objects in pictures and match to numbers</li>
        <li>🧩 Complete number puzzles with missing pieces</li>
        <li>📐 Trace dotted number outlines</li>
    </ul>
    
    <h5>🎮 Interactive Counting Game:</h5>
    <div style="background: #f0f8ff; padding: 20px; border-radius: 10px; margin: 20px 0; border: 2px solid #3498db;">
        <h6>Count the Animals!</h6>
        <div id="counting-game" style="text-align: center;">
            <div id="animal-display" style="font-size: 48px; margin: 20px 0;">
                🐶🐶🐶
            </div>
            <p id="question-text" style="font-size: 18px; margin: 15px 0;">How many dogs can you see?</p>
            <div id="answer-buttons" style="margin: 15px 0; text-align: center;">
                <!-- First row: Numbers 1-5 -->
                <div style="margin-bottom: 10px;">
                    <button onclick="checkAnswer(1)" style="font-size: 20px; margin: 5px; padding: 10px 20px; background: #ff4757; color: white; border: none; border-radius: 5px; cursor: pointer;">1</button>
                    <button onclick="checkAnswer(2)" style="font-size: 20px; margin: 5px; padding: 10px 20px; background: #ff8c42; color: white; border: none; border-radius: 5px; cursor: pointer;">2</button>
                    <button onclick="checkAnswer(3)" style="font-size: 20px; margin: 5px; padding: 10px 20px; background: #ffa726; color: white; border: none; border-radius: 5px; cursor: pointer;">3</button>
                    <button onclick="checkAnswer(4)" style="font-size: 20px; margin: 5px; padding: 10px 20px; background: #ffeb3b; color: black; border: none; border-radius: 5px; cursor: pointer;">4</button>
                    <button onclick="checkAnswer(5)" style="font-size: 20px; margin: 5px; padding: 10px 20px; background: #cddc39; color: black; border: none; border-radius: 5px; cursor: pointer;">5</button>
                </div>
                <!-- Second row: Numbers 6-10 -->
                <div>
                    <button onclick="checkAnswer(6)" style="font-size: 20px; margin: 5px; padding: 10px 20px; background: #4caf50; color: white; border: none; border-radius: 5px; cursor: pointer;">6</button>
                    <button onclick="checkAnswer(7)" style="font-size: 20px; margin: 5px; padding: 10px 20px; background: #2196f3; color: white; border: none; border-radius: 5px; cursor: pointer;">7</button>
                    <button onclick="checkAnswer(8)" style="font-size: 20px; margin: 5px; padding: 10px 20px; background: #3f51b5; color: white; border: none; border-radius: 5px; cursor: pointer;">8</button>
                    <button onclick="checkAnswer(9)" style="font-size: 20px; margin: 5px; padding: 10px 20px; background: #9c27b0; color: white; border: none; border-radius: 5px; cursor: pointer;">9</button>
                    <button onclick="checkAnswer(10)" style="font-size: 20px; margin: 5px; padding: 10px 20px; background: #e91e63; color: white; border: none; border-radius: 5px; cursor: pointer;">10</button>
                </div>
            </div>
            <div id="game-feedback" style="font-size: 16px; margin: 15px 0; font-weight: bold;"></div>
            <button onclick="nextQuestion()" id="next-btn" style="display: none; font-size: 16px; padding: 10px 20px; background: #27ae60; color: white; border: none; border-radius: 5px; cursor: pointer;">Next Question</button>
        </div>
    </div>
    
    <script>
    let currentAnswer = 3;
    let gameQuestions = [
        {animals: '🐶🐶🐶', question: 'How many dogs can you see?', answer: 3},
        {animals: '🐱🐱🐱🐱🐱', question: 'How many cats can you see?', answer: 5},
        {animals: '🐸🐸', question: 'How many frogs can you see?', answer: 2},
        {animals: '🦋🦋🦋🦋', question: 'How many butterflies can you see?', answer: 4},
        {animals: '🐰', question: 'How many rabbits can you see?', answer: 1},
        {animals: '🐧🐧🐧🐧🐧🐧', question: 'How many penguins can you see?', answer: 6}
    ];
    let currentQuestionIndex = 0;
    
    function checkAnswer(selectedAnswer) {
        const feedback = document.getElementById('game-feedback');
        const nextBtn = document.getElementById('next-btn');
        
        if (selectedAnswer === currentAnswer) {
            feedback.innerHTML = '🎉 Correct! Well done!';
            feedback.style.color = '#27ae60';
            nextBtn.style.display = 'inline-block';
        } else {
            feedback.innerHTML = '💭 Try again! Count carefully.';
            feedback.style.color = '#e74c3c';
        }
    }
    
    function nextQuestion() {
        currentQuestionIndex = (currentQuestionIndex + 1) % gameQuestions.length;
        const question = gameQuestions[currentQuestionIndex];
        
        document.getElementById('animal-display').innerHTML = question.animals;
        document.getElementById('question-text').innerHTML = question.question;
        currentAnswer = question.answer;
        
        document.getElementById('game-feedback').innerHTML = '';
        document.getElementById('next-btn').style.display = 'none';
    }
    </script>
    """
    
    # Verbal learning content with reading and writing
    verbal_content = """
    <h4>📚 Verbal Learning: Numbers 1-10</h4>
    
    <h5>📖 Number Words & Sounds:</h5>
    <div style="background: #e8f4fd; padding: 25px; border-radius: 12px; margin: 20px 0; border: 2px solid #4a90e2;">
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px;">
            <div style="background: white; padding: 20px; border-radius: 10px; border-left: 4px solid #2196f3;">
                <h6 style="color: #1976d2; margin-bottom: 15px;">🔢 Numbers 1-5</h6>
                <div style="font-size: 16px; line-height: 1.8;">
                    <p><strong style="color: #e74c3c; font-size: 18px;">1 = ONE</strong> <span style="color: #666;">(sounds like "wun")</span></p>
                    <p><strong style="color: #e74c3c; font-size: 18px;">2 = TWO</strong> <span style="color: #666;">(sounds like "too")</span></p>
                    <p><strong style="color: #e74c3c; font-size: 18px;">3 = THREE</strong> <span style="color: #666;">(sounds like "tree")</span></p>
                    <p><strong style="color: #e74c3c; font-size: 18px;">4 = FOUR</strong> <span style="color: #666;">(sounds like "for")</span></p>
                    <p><strong style="color: #e74c3c; font-size: 18px;">5 = FIVE</strong> <span style="color: #666;">(sounds like "hive")</span></p>
                </div>
            </div>
            
            <div style="background: white; padding: 20px; border-radius: 10px; border-left: 4px solid #ff9800;">
                <h6 style="color: #f57c00; margin-bottom: 15px;">🔢 Numbers 6-10</h6>
                <div style="font-size: 16px; line-height: 1.8;">
                    <p><strong style="color: #e74c3c; font-size: 18px;">6 = SIX</strong> <span style="color: #666;">(sounds like "sticks")</span></p>
                    <p><strong style="color: #e74c3c; font-size: 18px;">7 = SEVEN</strong> <span style="color: #666;">(sounds like "heaven")</span></p>
                    <p><strong style="color: #e74c3c; font-size: 18px;">8 = EIGHT</strong> <span style="color: #666;">(sounds like "ate")</span></p>
                    <p><strong style="color: #e74c3c; font-size: 18px;">9 = NINE</strong> <span style="color: #666;">(sounds like "mine")</span></p>
                    <p><strong style="color: #e74c3c; font-size: 18px;">10 = TEN</strong> <span style="color: #666;">(sounds like "hen")</span></p>
                </div>
            </div>
        </div>
    </div>
    
    <h5>📚 Number Stories & Reading:</h5>
    <div style="background: #f3e5f5; padding: 25px; border-radius: 12px; margin: 20px 0; border: 2px solid #9c27b0;">
        <div style="background: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; border-left: 4px solid #9c27b0;">
            <h6 style="color: #7b1fa2; margin-bottom: 15px;">📖 Count-Along Story</h6>
            <div style="font-size: 16px; line-height: 1.8; color: #333;">
                <p style="margin: 10px 0; padding: 15px; background: #fce4ec; border-radius: 8px;">
                    🌟 <em>"I can count to ten: <strong>One</strong>, <strong>two</strong>, <strong>three</strong>, <strong>four</strong>, <strong>five</strong>, <strong>six</strong>, <strong>seven</strong>, <strong>eight</strong>, <strong>nine</strong>, <strong>ten</strong>!"</em>
                </p>
                <p style="margin: 10px 0; padding: 15px; background: #f3e5f5; border-radius: 8px;">
                    ✋ <em>"There are <strong style="color: #e74c3c;">FIVE</strong> fingers on my hand."</em>
                </p>
                <p style="margin: 10px 0; padding: 15px; background: #fce4ec; border-radius: 8px;">
                    🐦 <em>"I see <strong style="color: #e74c3c;">THREE</strong> birds in the tree."</em>
                </p>
                <p style="margin: 10px 0; padding: 15px; background: #f3e5f5; border-radius: 8px;">
                    🎂 <em>"My birthday is when I turn <strong style="color: #e74c3c;">SIX</strong> years old."</em>
                </p>
            </div>
        </div>
    </div>
    
    <h5>📝 Interactive Writing Activities:</h5>
    <div style="background: #e8f5e8; padding: 25px; border-radius: 12px; margin: 20px 0; border: 2px solid #4caf50;">
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 20px;">
            <div style="background: white; padding: 20px; border-radius: 10px; border-left: 4px solid #4caf50;">
                <h6 style="color: #2e7d32; margin-bottom: 15px;">✏️ Number Writing</h6>
                <ul style="list-style: none; padding: 0;">
                    <li style="padding: 8px; background: #f1f8e9; margin: 5px 0; border-radius: 5px;">📝 Write number words: one, two, three...</li>
                    <li style="padding: 8px; background: #e8f5e8; margin: 5px 0; border-radius: 5px;">🔢 Practice writing digits: 1, 2, 3...</li>
                    <li style="padding: 8px; background: #f1f8e9; margin: 5px 0; border-radius: 5px;">📋 Fill in missing numbers: 1, 2, __, 4, 5</li>
                </ul>
            </div>
            
            <div style="background: white; padding: 20px; border-radius: 10px; border-left: 4px solid #ff9800;">
                <h6 style="color: #f57c00; margin-bottom: 15px;">📖 Reading Practice</h6>
                <ul style="list-style: none; padding: 0;">
                    <li style="padding: 8px; background: #fff3e0; margin: 5px 0; border-radius: 5px;">📚 Read simple counting books</li>
                    <li style="padding: 8px; background: #ffe0b2; margin: 5px 0; border-radius: 5px;">💭 Describe how many objects you see</li>
                    <li style="padding: 8px; background: #fff3e0; margin: 5px 0; border-radius: 5px;">🗣️ Say number words out loud</li>
                </ul>
            </div>
        </div>
    </div>
    
    <h5>🧠 Quick Questions Challenge:</h5>
    <div style="background: #fff3cd; padding: 25px; border-radius: 12px; margin: 20px 0; border: 2px solid #ffc107;">
        <div style="display: grid; gap: 20px;">
            <div style="background: white; padding: 20px; border-radius: 10px; border-left: 4px solid #ffc107;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                    <h6 style="color: #f57c00; margin: 0;">❓ Question 1</h6>
                    <button onclick="revealAnswer(1)" id="revealBtn1" style="background: #ff9800; color: white; border: none; padding: 8px 16px; border-radius: 20px; cursor: pointer; font-size: 14px;">🤔 Think First!</button>
                </div>
                <p style="font-size: 16px; margin-bottom: 15px;"><strong>What number comes after FIVE?</strong></p>
                <div id="answer1" style="display: none; background: #e8f5e8; padding: 15px; border-radius: 8px; border-left: 4px solid #4caf50;">
                    <p style="margin: 0; color: #2e7d32; font-weight: bold;">✅ Answer: SIX</p>
                    <p style="margin: 5px 0 0 0; color: #666; font-size: 14px;">The counting sequence is: ...four, five, <strong>six</strong>, seven...</p>
                </div>
            </div>
            
            <div style="background: white; padding: 20px; border-radius: 10px; border-left: 4px solid #ffc107;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                    <h6 style="color: #f57c00; margin: 0;">❓ Question 2</h6>
                    <button onclick="revealAnswer(2)" id="revealBtn2" style="background: #ff9800; color: white; border: none; padding: 8px 16px; border-radius: 20px; cursor: pointer; font-size: 14px;">🤔 Think First!</button>
                </div>
                <p style="font-size: 16px; margin-bottom: 15px;"><strong>What number comes before EIGHT?</strong></p>
                <div id="answer2" style="display: none; background: #e8f5e8; padding: 15px; border-radius: 8px; border-left: 4px solid #4caf50;">
                    <p style="margin: 0; color: #2e7d32; font-weight: bold;">✅ Answer: SEVEN</p>
                    <p style="margin: 5px 0 0 0; color: #666; font-size: 14px;">The counting sequence is: ...six, <strong>seven</strong>, eight, nine...</p>
                </div>
            </div>
            
            <div style="background: white; padding: 20px; border-radius: 10px; border-left: 4px solid #ffc107;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                    <h6 style="color: #f57c00; margin: 0;">❓ Question 3</h6>
                    <button onclick="revealAnswer(3)" id="revealBtn3" style="background: #ff9800; color: white; border: none; padding: 8px 16px; border-radius: 20px; cursor: pointer; font-size: 14px;">🤔 Think First!</button>
                </div>
                <p style="font-size: 16px; margin-bottom: 15px;"><strong>How do you spell the number 3?</strong></p>
                <div id="answer3" style="display: none; background: #e8f5e8; padding: 15px; border-radius: 8px; border-left: 4px solid #4caf50;">
                    <p style="margin: 0; color: #2e7d32; font-weight: bold;">✅ Answer: T-H-R-E-E</p>
                    <p style="margin: 5px 0 0 0; color: #666; font-size: 14px;">The word "three" sounds like "tree" and has 5 letters!</p>
                </div>
            </div>
            
            <div style="background: white; padding: 20px; border-radius: 10px; border-left: 4px solid #ffc107;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                    <h6 style="color: #f57c00; margin: 0;">❓ Question 4</h6>
                    <button onclick="revealAnswer(4)" id="revealBtn4" style="background: #ff9800; color: white; border: none; padding: 8px 16px; border-radius: 20px; cursor: pointer; font-size: 14px;">🤔 Think First!</button>
                </div>
                <p style="font-size: 16px; margin-bottom: 15px;"><strong>Which number word rhymes with "mine"?</strong></p>
                <div id="answer4" style="display: none; background: #e8f5e8; padding: 15px; border-radius: 8px; border-left: 4px solid #4caf50;">
                    <p style="margin: 0; color: #2e7d32; font-weight: bold;">✅ Answer: NINE</p>
                    <p style="margin: 5px 0 0 0; color: #666; font-size: 14px;">"Nine" and "mine" both end with the same sound!</p>
                </div>
            </div>
        </div>
    </div>
    
    <script>
    function revealAnswer(questionNumber) {
        const answer = document.getElementById('answer' + questionNumber);
        const button = document.getElementById('revealBtn' + questionNumber);
        
        if (answer.style.display === 'none') {
            answer.style.display = 'block';
            button.innerHTML = '🎉 Great thinking!';
            button.style.background = '#4caf50';
            button.disabled = true;
            button.style.cursor = 'default';
        }
    }
    </script>
    """
    
    # Auditory learning content with sounds and rhythm
    auditory_content = """
    <h4>🎵 Auditory Learning: Numbers 1-10</h4>
    
    <!-- Audio Controls Panel -->
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 25px; border-radius: 15px; margin: 20px 0; box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);">
        <h5 style="margin-bottom: 20px; color: white;">🎧 Audio Learning Controls</h5>
        
        <div style="display: flex; flex-wrap: wrap; gap: 20px; align-items: center; justify-content: center;">
            <div style="display: flex; align-items: center; gap: 10px;">
                <label for="voiceSelect" style="font-weight: 600;">Voice:</label>
                <select id="voiceSelect" style="padding: 8px 12px; border-radius: 8px; border: none; background: white; color: #333;">
                    <option value="0">Child-Friendly Voice</option>
                </select>
            </div>
            
            <div style="display: flex; align-items: center; gap: 10px;">
                <label for="speedRange" style="font-weight: 600;">Speed:</label>
                <input type="range" id="speedRange" min="0.5" max="1.5" step="0.1" value="0.8" style="width: 100px;">
                <span id="speedValue">0.8x</span>
            </div>
            
            <div style="display: flex; align-items: center; gap: 10px;">
                <label for="volumeRange" style="font-weight: 600;">Volume:</label>
                <input type="range" id="volumeRange" min="0" max="1" step="0.1" value="0.9" style="width: 100px;">
                <span id="volumeValue">90%</span>
            </div>
        </div>
    </div>
    
    <!-- Interactive Number Lessons -->
    <div style="background: #f8f9fa; padding: 25px; border-radius: 12px; margin: 20px 0; border: 2px solid #e9ecef;">
        <h5>🔢 Interactive Number Lessons</h5>
        
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 20px; margin: 20px 0;">
            <div style="background: white; padding: 20px; border-radius: 10px; border-left: 4px solid #e74c3c; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                <h6 style="color: #e74c3c; margin-bottom: 15px;">🎵 Counting Song</h6>
                <div id="countingSongText" style="display: none;">
                    Let's count together from one to ten! One, two, buckle my shoe. Three, four, knock at the door. Five, six, pick up sticks. Seven, eight, lay them straight. Nine, ten, a big fat hen! Now you know how to count to ten!
                </div>
                <button onclick="playAudio('countingSong')" class="audio-btn" style="background: #e74c3c; color: white; border: none; padding: 12px 20px; border-radius: 25px; cursor: pointer; font-weight: 600; margin: 5px;">
                    🎵 Play Counting Song
                </button>
            </div>
            

            
            <div style="background: white; padding: 20px; border-radius: 10px; border-left: 4px solid #27ae60; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                <h6 style="color: #27ae60; margin-bottom: 15px;">👏 Clapping Game</h6>
                <div id="clappingGameText" style="display: none;">
                    Let's play the clapping game! Clap your hands once for number one! ... ... Now clap your hands twice for number two! ... ... Now clap your hands three times for number three! ... ... Now clap your hands four times for number four! ... ... Now clap your hands five times for number five! ... ... Great job clapping and counting!
                </div>
                <button onclick="playAudio('clappingGame')" class="audio-btn" style="background: #27ae60; color: white; border: none; padding: 12px 20px; border-radius: 25px; cursor: pointer; font-weight: 600; margin: 5px;">
                    👏 Clapping Game
                </button>
            </div>
            
            <div style="background: white; padding: 20px; border-radius: 10px; border-left: 4px solid #f39c12; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                <h6 style="color: #f39c12; margin-bottom: 15px;">🎭 Echo Practice</h6>
                <div id="echoPracticeText" style="display: none;">
                    Echo practice time! I'll say a number, then you repeat it! Ready? One! Now you say one! Two! Now you say two! Three! Now you say three! Four! Now you say four! Five! Now you say five! Six! Now you say six! Seven! Now you say seven! Eight! Now you say eight! Nine! Now you say nine! Ten! Now you say ten! Excellent echoing!
                </div>
                <button onclick="playAudio('echoPractice')" class="audio-btn" style="background: #f39c12; color: white; border: none; padding: 12px 20px; border-radius: 25px; cursor: pointer; font-weight: 600; margin: 5px;">
                    🎭 Echo Practice
                </button>
            </div>
        </div>
        
        <!-- Main Audio Controls -->
        <div style="text-align: center; margin: 25px 0; padding: 20px; background: white; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
            <h6 style="margin-bottom: 15px;">🎮 Audio Controls</h6>
            <div style="display: flex; justify-content: center; gap: 15px; flex-wrap: wrap;">
                <button onclick="pauseAudio()" id="pauseBtn" style="background: #ff6b6b; color: white; border: none; padding: 12px 20px; border-radius: 25px; cursor: pointer; font-weight: 600;">
                    ⏸️ Pause
                </button>
                <button onclick="playLastAudio()" id="playBtn" style="background: #28a745; color: white; border: none; padding: 12px 20px; border-radius: 25px; cursor: pointer; font-weight: 600;">
                    ▶️ Play
                </button>
                <button onclick="playAllNumbers()" style="background: #17a2b8; color: white; border: none; padding: 12px 20px; border-radius: 25px; cursor: pointer; font-weight: 600;">
                    🔢 Count 1-10
                </button>
            </div>
            <div id="audioStatus" style="margin-top: 15px; font-weight: 600; color: #667eea;">Ready to start learning!</div>
        </div>
    </div>
    
    <h5>🎯 Additional Listening Activities:</h5>
    <div style="background: #fff3cd; padding: 20px; border-radius: 10px; margin: 15px 0; border-left: 4px solid #ffc107;">
        <ul style="margin: 0; padding-left: 20px;">
            <li>🎧 Listen to each number lesson above</li>
            <li>👏 Practice the clapping game</li>
            <li>🎤 Use the echo practice to improve pronunciation</li>
            <li>🗣️ Try saying numbers in different voices (high, low, fast, slow)</li>
            <li>🔔 Listen for number words in stories and songs</li>
        </ul>
    </div>
    

    

    
    <script>
    let synthesis = window.speechSynthesis;
    let currentUtterance = null;
    let voices = [];
    let isPlaying = false;
    let isPaused = false;
    
    // Initialize audio system when page loads
    document.addEventListener('DOMContentLoaded', function() {
        loadVoices();
        initializeControls();
        
        // Load voices again after a delay (some browsers need this)
        setTimeout(loadVoices, 100);
    });
    
    // Load voices
    function loadVoices() {
        voices = synthesis.getVoices();
        populateVoiceSelect();
    }
    
    function populateVoiceSelect() {
        const voiceSelect = document.getElementById('voiceSelect');
        if (!voiceSelect) return;
        
        voiceSelect.innerHTML = '';
        
        // Filter for English voices and categorize by gender
        const englishVoices = voices.filter(voice => voice.lang.includes('en'));
        
        const femaleVoices = englishVoices.filter(voice => 
            voice.name.includes('Female') || voice.name.includes('female') || 
            voice.name.includes('Samantha') || voice.name.includes('Karen') ||
            voice.name.includes('Moira') || voice.name.includes('Fiona') ||
            voice.name.includes('Google UK English Female') || 
            voice.name.includes('Microsoft Zira') || voice.name.includes('Victoria') ||
            voice.name.includes('Susan') || voice.name.includes('Allison')
        );
        
        const maleVoices = englishVoices.filter(voice => 
            voice.name.includes('Male') || voice.name.includes('male') || 
            voice.name.includes('Alex') || voice.name.includes('Daniel') ||
            voice.name.includes('Thomas') || voice.name.includes('Google UK English Male') ||
            voice.name.includes('Microsoft David') || voice.name.includes('Fred') ||
            voice.name.includes('Oliver') || voice.name.includes('Ralph')
        );
        
        // Add simplified voice options
        if (femaleVoices.length > 0) {
            const option = document.createElement('option');
            option.value = 'female';
            option.textContent = 'Female';
            option.dataset.voice = JSON.stringify(femaleVoices[0]);
            voiceSelect.appendChild(option);
        }
        
        if (maleVoices.length > 0) {
            const option = document.createElement('option');
            option.value = 'male';
            option.textContent = 'Male';
            option.dataset.voice = JSON.stringify(maleVoices[0]);
            voiceSelect.appendChild(option);
        }
        
        // If no categorized voices found, use any English voice
        if (femaleVoices.length === 0 && maleVoices.length === 0 && englishVoices.length > 0) {
            const option = document.createElement('option');
            option.value = '0';
            option.textContent = 'Default Voice';
            option.dataset.voice = JSON.stringify(englishVoices[0]);
            voiceSelect.appendChild(option);
        }
        
        // Ultimate fallback
        if (englishVoices.length === 0) {
            const option = document.createElement('option');
            option.value = '0';
            option.textContent = 'Default Voice';
            voiceSelect.appendChild(option);
        }
    }
    
    function initializeControls() {
        // Speed range control
        const speedRange = document.getElementById('speedRange');
        const speedValue = document.getElementById('speedValue');
        if (speedRange && speedValue) {
            speedRange.addEventListener('input', function() {
                speedValue.textContent = this.value + 'x';
            });
        }
        
        // Volume range control
        const volumeRange = document.getElementById('volumeRange');
        const volumeValue = document.getElementById('volumeValue');
        if (volumeRange && volumeValue) {
            volumeRange.addEventListener('input', function() {
                volumeValue.textContent = Math.round(this.value * 100) + '%';
            });
        }
    }
    
    function playAudio(audioType) {
        let audioText = '';
        
        // Get the text content for the selected audio type
        switch(audioType) {
            case 'countingSong':
                audioText = document.getElementById('countingSongText').textContent;
                break;

            case 'clappingGame':
                audioText = document.getElementById('clappingGameText').textContent;
                break;
            case 'echoPractice':
                audioText = document.getElementById('echoPracticeText').textContent;
                break;
            default:
                audioText = 'Audio content not found.';
        }
        
        if (synthesis.speaking) {
            synthesis.cancel();
        }
        
        currentUtterance = new SpeechSynthesisUtterance(audioText);
        
        // Set voice
        const voiceSelect = document.getElementById('voiceSelect');
        const speedRange = document.getElementById('speedRange');
        const volumeRange = document.getElementById('volumeRange');
        
        if (voiceSelect && voiceSelect.options.length > 0) {
            const selectedOption = voiceSelect.options[voiceSelect.selectedIndex];
            if (selectedOption.dataset.voice) {
                try {
                    const voiceData = JSON.parse(selectedOption.dataset.voice);
                    const matchingVoice = voices.find(voice => voice.name === voiceData.name);
                    if (matchingVoice) {
                        currentUtterance.voice = matchingVoice;
                    }
                } catch (e) {
                    console.warn('Could not parse voice data:', e);
                }
            }
        }
        
        // Set speech properties
        currentUtterance.rate = speedRange ? parseFloat(speedRange.value) : 0.8;
        currentUtterance.pitch = 1.1; // Slightly higher pitch for children
        currentUtterance.volume = volumeRange ? parseFloat(volumeRange.value) : 0.9;
        
        currentUtterance.onstart = function() {
            isPlaying = true;
            isPaused = false;
            updateAudioStatus('🎵 Playing ' + audioType + '...');
        };
        
        currentUtterance.onend = function() {
            isPlaying = false;
            isPaused = false;
            updateAudioStatus('✅ Audio finished! Ready for next lesson.');
        };
        
        currentUtterance.onerror = function(event) {
            isPlaying = false;
            isPaused = false;
            updateAudioStatus('❌ Audio error. Please try again.');
            console.error('Speech synthesis error:', event);
        };
        
        synthesis.speak(currentUtterance);
        updateAudioStatus('🎵 Starting audio lesson...');
    }
    
    function pauseAudio() {
        if (synthesis.speaking && !isPaused) {
            synthesis.pause();
            isPaused = true;
            updateAudioStatus('⏸️ Audio paused');
        } else if (isPaused) {
            synthesis.resume();
            isPaused = false;
            updateAudioStatus('▶️ Audio resumed');
        }
    }
    
    function playLastAudio() {
        if (isPaused) {
            // Resume if paused
            synthesis.resume();
            isPaused = false;
            updateAudioStatus('▶️ Audio resumed');
        } else if (!isPlaying) {
            // Give helpful instructions when play is clicked
            const instructionText = "Hello! Click on the colorful buttons above to start learning. Try the counting song, clapping game, or echo practice!";
            
            if (synthesis.speaking) {
                synthesis.cancel();
            }
            
            currentUtterance = new SpeechSynthesisUtterance(instructionText);
            currentUtterance.rate = 0.8;
            currentUtterance.pitch = 1.1;
            currentUtterance.volume = 0.9;
            
            currentUtterance.onstart = function() {
                isPlaying = true;
                updateAudioStatus('💬 Giving instructions...');
            };
            
            currentUtterance.onend = function() {
                isPlaying = false;
                updateAudioStatus('👆 Click the buttons above to start learning!');
            };
            
            synthesis.speak(currentUtterance);
        }
    }
    
    function playAllNumbers() {
        const numbersText = "Let's count from one to ten together! One! Two! Three! Four! Five! Six! Seven! Eight! Nine! Ten! Great job counting all the way to ten!";
        
        if (synthesis.speaking) {
            synthesis.cancel();
        }
        
        currentUtterance = new SpeechSynthesisUtterance(numbersText);
        
        // Set voice and properties
        const voiceSelect = document.getElementById('voiceSelect');
        const speedRange = document.getElementById('speedRange');
        const volumeRange = document.getElementById('volumeRange');
        
        if (voiceSelect && voiceSelect.options.length > 0) {
            const selectedOption = voiceSelect.options[voiceSelect.selectedIndex];
            if (selectedOption.dataset.voice) {
                try {
                    const voiceData = JSON.parse(selectedOption.dataset.voice);
                    const matchingVoice = voices.find(voice => voice.name === voiceData.name);
                    if (matchingVoice) {
                        currentUtterance.voice = matchingVoice;
                    }
                } catch (e) {
                    console.warn('Could not parse voice data:', e);
                }
            }
        }
        
        currentUtterance.rate = speedRange ? parseFloat(speedRange.value) : 0.8;
        currentUtterance.pitch = 1.1;
        currentUtterance.volume = volumeRange ? parseFloat(volumeRange.value) : 0.9;
        
        currentUtterance.onstart = function() {
            isPlaying = true;
            updateAudioStatus('🔢 Counting from 1 to 10...');
        };
        
        currentUtterance.onend = function() {
            isPlaying = false;
            updateAudioStatus('🎉 Finished counting! Try the other lessons above.');
        };
        
        currentUtterance.onerror = function(event) {
            isPlaying = false;
            updateAudioStatus('❌ Audio error. Please try again.');
            console.error('Speech synthesis error:', event);
        };
        
        synthesis.speak(currentUtterance);
    }
    
    function updateAudioStatus(message) {
        const status = document.getElementById('audioStatus');
        if (status) {
            status.textContent = message;
        }
    }
    
    // Ensure voices are loaded when they become available
    if (speechSynthesis.onvoiceschanged !== undefined) {
        speechSynthesis.onvoiceschanged = loadVoices;
    }
    </script>
    """
    
    # Return appropriate content based on learning style
    if learning_style.lower() == 'visual':
        main_content = visual_content
    elif learning_style.lower() == 'verbal':
        main_content = verbal_content
    elif learning_style.lower() == 'auditory':
        main_content = auditory_content
    else:
        main_content = visual_content  # Default to visual
    
    return {
        'title': f"Numbers 1-10 - {learning_style.title()} Learning",
        'visual': visual_content,
        'verbal': verbal_content,
        'auditory': auditory_content,
        'current_style': learning_style,
        'description': f"Age-appropriate numbers 1-10 lesson for {learning_style} learners",
        'objectives': f"Students will learn to count, recognize, and use numbers 1-10",
        'activities': f"Interactive {learning_style} exercises with numbers 1-10"
    }

def create_primary1_size_content(learning_style, topic):
    """Create Primary 1 math content for Big & Small comparisons"""
    
    # Visual learning content with colorful size comparisons
    visual_content = """
    <h4>🎨 Visual Learning: Big & Small</h4>
    
    <h5>📏 Size Comparison:</h5>
    <div style="background: #f8f9fa; padding: 40px 35px; border-radius: 15px; margin: 20px 0;">
        <div style="display: flex; justify-content: space-between; align-items: center; gap: 40px; flex-wrap: wrap; min-height: 200px;">
            <!-- Big Things Section -->
            <div style="flex: 1; min-width: 250px; text-align: center; height: 180px; display: flex; flex-direction: column; justify-content: space-between;">
                <h6 style="color: #e74c3c; font-size: 26px; margin-bottom: 10px; font-weight: 900;">🔴 BIG Things</h6>
                <div style="flex: 1; display: flex; flex-direction: column; justify-content: center;">
                    <div style="display: flex; justify-content: space-around; align-items: center; margin-bottom: 15px;">
                        <div style="text-align: center;">
                            <div style="font-size: 50px; height: 60px; display: flex; align-items: center; justify-content: center;">🐘</div>
                            <div style="font-size: 12px; color: #2c3e50;">Elephant</div>
                        </div>
                        <div style="text-align: center;">
                            <div style="font-size: 50px; height: 60px; display: flex; align-items: center; justify-content: center;">🦒</div>
                            <div style="font-size: 12px; color: #2c3e50;">Giraffe</div>
                        </div>
                    </div>
                    <div style="display: flex; justify-content: space-around; align-items: center;">
                        <div style="text-align: center;">
                            <div style="font-size: 50px; height: 60px; display: flex; align-items: center; justify-content: center;">🐋</div>
                            <div style="font-size: 12px; color: #2c3e50;">Whale</div>
                        </div>
                        <div style="text-align: center;">
                            <div style="font-size: 50px; height: 60px; display: flex; align-items: center; justify-content: center;">🏠</div>
                            <div style="font-size: 12px; color: #2c3e50;">House</div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- VS Divider -->
            <div style="display: flex; align-items: center; justify-content: center; min-width: 120px;">
                <div style="font-size: 36px; color: #2c3e50; font-weight: bold; padding: 30px; background: #ecf0f1; border-radius: 50%; width: 80px; height: 80px; display: flex; align-items: center; justify-content: center; border: 3px solid #bdc3c7; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">VS</div>
            </div>
            
            <!-- Small Things Section -->
            <div style="flex: 1; min-width: 250px; text-align: center; height: 180px; display: flex; flex-direction: column; justify-content: space-between;">
                <h6 style="color: #3498db; font-size: 26px; margin-bottom: 10px; font-weight: 900;">🔵 SMALL Things</h6>
                <div style="flex: 1; display: flex; flex-direction: column; justify-content: center;">
                    <div style="display: flex; justify-content: space-around; align-items: center; margin-bottom: 15px;">
                        <div style="text-align: center;">
                            <div style="font-size: 24px; height: 60px; display: flex; align-items: center; justify-content: center;">🐭</div>
                            <div style="font-size: 12px; color: #2c3e50;">Mouse</div>
                        </div>
                        <div style="text-align: center;">
                            <div style="font-size: 24px; height: 60px; display: flex; align-items: center; justify-content: center;">🐛</div>
                            <div style="font-size: 12px; color: #2c3e50;">Bug</div>
                        </div>
                    </div>
                    <div style="display: flex; justify-content: space-around; align-items: center;">
                        <div style="text-align: center;">
                            <div style="font-size: 24px; height: 60px; display: flex; align-items: center; justify-content: center;">🐜</div>
                            <div style="font-size: 12px; color: #2c3e50;">Ant</div>
                        </div>
                        <div style="text-align: center;">
                            <div style="font-size: 24px; height: 60px; display: flex; align-items: center; justify-content: center;">🌰</div>
                            <div style="font-size: 12px; color: #2c3e50;">Acorn</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <h5>🔄 Size Comparison Game:</h5>
    <div style="background: #f0f8ff; padding: 20px; border-radius: 10px; margin: 20px 0; border: 2px solid #3498db;">
        <h6>Which is Bigger?</h6>
        <div id="size-game" style="text-align: center;">
            <div id="comparison-display" style="margin: 20px 0;">
                <span style="font-size: 60px;">🐘</span>
                <span style="font-size: 28px; margin: 0 20px; color: #2c3e50;">VS</span>
                <span style="font-size: 24px;">🐭</span>
            </div>
            <p id="size-question" style="font-size: 18px; margin: 15px 0;">Which animal is BIGGER?</p>
            <div id="size-buttons" style="margin: 15px 0;">
                <button onclick="checkSizeAnswer('left')" style="font-size: 18px; margin: 10px; padding: 15px 25px; background: #e74c3c; color: white; border: none; border-radius: 8px; cursor: pointer;">Left One</button>
                <button onclick="checkSizeAnswer('right')" style="font-size: 18px; margin: 10px; padding: 15px 25px; background: #3498db; color: white; border: none; border-radius: 8px; cursor: pointer;">Right One</button>
            </div>
            <div id="size-feedback" style="font-size: 16px; margin: 15px 0; font-weight: bold;"></div>
            <button onclick="nextSizeQuestion()" id="next-size-btn" style="display: none; font-size: 16px; padding: 10px 20px; background: #27ae60; color: white; border: none; border-radius: 5px; cursor: pointer;">Next Question</button>
        </div>
    </div>
    
    <h5>🌈 Size Chart - From Biggest to Smallest:</h5>
    
    <!-- Desktop Horizontal Layout -->
    <div class="desktop-layout" style="background: #ecf0f1; padding: 30px; border-radius: 10px; margin: 20px 0; display: flex; justify-content: space-around; align-items: flex-end; flex-wrap: wrap; gap: 20px;">
        <!-- Dinosaur - BIGGEST -->
        <div style="text-align: center; flex: 1; min-width: 120px;">
            <div style="font-size: 80px; line-height: 1;">🦖</div>
            <div style="color: #e74c3c; font-size: 16px; font-weight: bold; margin-top: 8px;">BIGGEST</div>
            <div style="color: #2c3e50; font-size: 14px; margin-top: 3px;">Dinosaur</div>
        </div>
        
        <!-- Elephant - BIG -->
        <div style="text-align: center; flex: 1; min-width: 120px;">
            <div style="font-size: 64px; line-height: 1;">🐘</div>
            <div style="color: #f39c12; font-size: 16px; font-weight: bold; margin-top: 8px;">BIG</div>
            <div style="color: #2c3e50; font-size: 14px; margin-top: 3px;">Elephant</div>
        </div>
        
        <!-- Dog - MEDIUM -->
        <div style="text-align: center; flex: 1; min-width: 120px;">
            <div style="font-size: 48px; line-height: 1;">🐕</div>
            <div style="color: #2ecc71; font-size: 16px; font-weight: bold; margin-top: 8px;">MEDIUM</div>
            <div style="color: #2c3e50; font-size: 14px; margin-top: 3px;">Dog</div>
        </div>
        
        <!-- Mouse - SMALL -->
        <div style="text-align: center; flex: 1; min-width: 120px;">
            <div style="font-size: 32px; line-height: 1;">🐭</div>
            <div style="color: #3498db; font-size: 16px; font-weight: bold; margin-top: 8px;">SMALL</div>
            <div style="color: #2c3e50; font-size: 14px; margin-top: 3px;">Mouse</div>
        </div>
        
        <!-- Ant - SMALLEST -->
        <div style="text-align: center; flex: 1; min-width: 120px;">
            <div style="font-size: 20px; line-height: 1;">🐜</div>
            <div style="color: #9b59b6; font-size: 16px; font-weight: bold; margin-top: 8px;">SMALLEST</div>
            <div style="color: #2c3e50; font-size: 14px; margin-top: 3px;">Ant</div>
        </div>
    </div>
    
    <!-- Mobile Vertical Layout (hidden on desktop) -->
    <div class="mobile-layout" style="background: #ecf0f1; padding: 40px; border-radius: 10px; margin: 20px 0; max-width: 400px; margin-left: auto; margin-right: auto; display: none;">
        <div style="text-align: center;">
            <!-- Dinosaur - BIGGEST -->
            <div style="margin: 25px 0; padding: 15px; border-bottom: 2px solid #bdc3c7;">
                <div style="font-size: 80px; line-height: 1;">🦖</div>
                <div style="color: #e74c3c; font-size: 24px; font-weight: bold; margin-top: 12px;">BIGGEST</div>
                <div style="color: #2c3e50; font-size: 16px; margin-top: 5px;">Dinosaur</div>
            </div>
            
            <!-- Elephant - BIG -->
            <div style="margin: 25px 0; padding: 15px; border-bottom: 2px solid #bdc3c7;">
                <div style="font-size: 64px; line-height: 1;">🐘</div>
                <div style="color: #f39c12; font-size: 20px; font-weight: bold; margin-top: 12px;">BIG</div>
                <div style="color: #2c3e50; font-size: 16px; margin-top: 5px;">Elephant</div>
            </div>
            
            <!-- Dog - MEDIUM -->
            <div style="margin: 25px 0; padding: 15px; border-bottom: 2px solid #bdc3c7;">
                <div style="font-size: 48px; line-height: 1;">🐕</div>
                <div style="color: #2ecc71; font-size: 18px; font-weight: bold; margin-top: 12px;">MEDIUM</div>
                <div style="color: #2c3e50; font-size: 16px; margin-top: 5px;">Dog</div>
            </div>
            
            <!-- Mouse - SMALL -->
            <div style="margin: 25px 0; padding: 15px; border-bottom: 2px solid #bdc3c7;">
                <div style="font-size: 32px; line-height: 1;">🐭</div>
                <div style="color: #3498db; font-size: 16px; font-weight: bold; margin-top: 12px;">SMALL</div>
                <div style="color: #2c3e50; font-size: 16px; margin-top: 5px;">Mouse</div>
            </div>
            
            <!-- Ant - SMALLEST -->
            <div style="margin: 25px 0; padding: 15px;">
                <div style="font-size: 20px; line-height: 1;">🐜</div>
                <div style="color: #9b59b6; font-size: 14px; font-weight: bold; margin-top: 12px;">SMALLEST</div>
                <div style="color: #2c3e50; font-size: 16px; margin-top: 5px;">Ant</div>
            </div>
        </div>
    </div>
    
    <script>
    // Responsive layout switching
    function adjustSizeChartLayout() {
        const desktopLayout = document.querySelector('.desktop-layout');
        const mobileLayout = document.querySelector('.mobile-layout');
        
        if (window.innerWidth <= 768) {
            if (desktopLayout) desktopLayout.style.display = 'none';
            if (mobileLayout) mobileLayout.style.display = 'block';
        } else {
            if (desktopLayout) desktopLayout.style.display = 'flex';
            if (mobileLayout) mobileLayout.style.display = 'none';
        }
    }
    
    // Run on load and resize
    if (typeof window !== 'undefined') {
        adjustSizeChartLayout();
        window.addEventListener('resize', adjustSizeChartLayout);
    }
    </script>
    
    <h5>🎯 Visual Activities:</h5>
    <ul>
        <li>🔍 Find big and small objects around your home</li>
        <li>📏 Line up toys from biggest to smallest</li>
        <li>🎨 Draw big circles and small circles</li>
        <li>📐 Compare the size of your hands to an adult's hands</li>
    </ul>
    
    <script>
    let sizeQuestions = [
        {left: {emoji: '🐘', size: 60, name: 'elephant'}, right: {emoji: '🐭', size: 24, name: 'mouse'}, answer: 'left'},
        {left: {emoji: '🐜', size: 18, name: 'ant'}, right: {emoji: '🐕', size: 40, name: 'dog'}, answer: 'right'},
        {left: {emoji: '🏠', size: 50, name: 'house'}, right: {emoji: '🌰', size: 20, name: 'acorn'}, answer: 'left'},
        {left: {emoji: '🐛', size: 22, name: 'bug'}, right: {emoji: '🦒', size: 55, name: 'giraffe'}, answer: 'right'},
        {left: {emoji: '🐋', size: 65, name: 'whale'}, right: {emoji: '🐠', size: 25, name: 'fish'}, answer: 'left'}
    ];
    let currentSizeIndex = 0;
    let currentSizeAnswer = 'left';
    
    function checkSizeAnswer(selectedSide) {
        const feedback = document.getElementById('size-feedback');
        const nextBtn = document.getElementById('next-size-btn');
        
        if (selectedSide === currentSizeAnswer) {
            feedback.innerHTML = '🎉 Correct! You found the bigger one!';
            feedback.style.color = '#27ae60';
            nextBtn.style.display = 'inline-block';
        } else {
            feedback.innerHTML = '💭 Try again! Look at the sizes carefully.';
            feedback.style.color = '#e74c3c';
        }
    }
    
    function nextSizeQuestion() {
        currentSizeIndex = (currentSizeIndex + 1) % sizeQuestions.length;
        const question = sizeQuestions[currentSizeIndex];
        
        document.getElementById('comparison-display').innerHTML = 
            `<span style="font-size: ${question.left.size}px;">${question.left.emoji}</span>
             <span style="font-size: 28px; margin: 0 20px; color: #2c3e50;">VS</span>
             <span style="font-size: ${question.right.size}px;">${question.right.emoji}</span>`;
        
        currentSizeAnswer = question.answer;
        
        document.getElementById('size-feedback').innerHTML = '';
        document.getElementById('next-size-btn').style.display = 'none';
    }
    </script>
    """
    
    # Verbal learning content for size concepts
    verbal_content = """
    <h4>📚 Verbal Learning: Big & Small</h4>
    
    <h5>📖 Size Words Dictionary:</h5>
    <div class="size-words" style="background: #f8f9fa; padding: 25px; border-radius: 12px; margin: 20px 0; border: 2px solid #e9ecef;">
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-bottom: 20px;">
            <div style="background: #fff3cd; padding: 15px; border-radius: 8px; border-left: 4px solid #ffc107;">
                <strong style="color: #856404;">BIG Words:</strong><br>
                • Large • Huge • Enormous<br>
                • Giant • Massive • Gigantic
            </div>
            <div style="background: #d1ecf1; padding: 15px; border-radius: 8px; border-left: 4px solid #17a2b8;">
                <strong style="color: #0c5460;">SMALL Words:</strong><br>
                • Little • Tiny • Mini<br>
                • Petite • Miniature • Microscopic
            </div>
        </div>
        <div style="background: #e2e3e5; padding: 15px; border-radius: 8px; text-align: center;">
            <strong>Comparison Words:</strong> BIGGER • SMALLER • BIGGEST • SMALLEST
        </div>
    </div>
    
    <h5>📚 Story Time - The Big and Small Adventure:</h5>
    <div style="background: #e8f5e8; padding: 20px; border-radius: 10px; margin: 20px 0; border: 2px solid #28a745;">
        <p style="font-size: 16px; line-height: 1.6; color: #155724;">
            Once upon a time, there was a <strong>big</strong> friendly giant named George and a <strong>small</strong> clever mouse named Pip. 
            George lived in a <strong>huge</strong> castle with <strong>enormous</strong> doors, while Pip lived in a <strong>tiny</strong> hole in the wall.
        </p>
        <p style="font-size: 16px; line-height: 1.6; color: #155724;">
            One day, George couldn't find his <strong>gigantic</strong> keys! Pip, being <strong>small</strong> enough to fit anywhere, 
            helped search in all the <strong>little</strong> places. Together, they learned that being different sizes can be very helpful!
        </p>
    </div>
    
    <h5>✍️ Reading Practice Sentences:</h5>
    <div style="background: #fff3cd; padding: 20px; border-radius: 10px; margin: 20px 0;">
        <div style="margin-bottom: 15px;">
            <p>"The <strong style="color: #e74c3c;">big</strong> elephant is much larger than the <strong style="color: #3498db;">small</strong> mouse."</p>
            <p>"My dad is <strong style="color: #e74c3c;">bigger</strong> than me, but I am <strong style="color: #e74c3c;">bigger</strong> than my baby sister."</p>
            <p>"The <strong style="color: #3498db;">smallest</strong> ant can carry things much <strong style="color: #e74c3c;">bigger</strong> than itself!"</p>
            <p>"I have a <strong style="color: #e74c3c;">big</strong> teddy bear and a <strong style="color: #3498db;">small</strong> toy car."</p>
        </div>
    </div>
    
    <h5>🎯 Interactive Size Comparisons:</h5>
    <div style="background: #f0f8ff; padding: 20px; border-radius: 10px; margin: 20px 0; border: 2px solid #6f42c1;">
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
            <div style="text-align: center; padding: 15px; background: white; border-radius: 8px;">
                <h6 style="color: #e74c3c; margin-bottom: 10px;">🔴 Things that are BIG:</h6>
                <p>Houses, Cars, Trees, Mountains, Whales, Dinosaurs</p>
            </div>
            <div style="text-align: center; padding: 15px; background: white; border-radius: 8px;">
                <h6 style="color: #3498db; margin-bottom: 10px;">🔵 Things that are SMALL:</h6>
                <p>Buttons, Coins, Ants, Pebbles, Berries, Paperclips</p>
            </div>
        </div>
    </div>
    
    <h5>📝 Creative Writing Activities:</h5>
    <div style="background: #e7f3ff; padding: 20px; border-radius: 10px; margin: 20px 0;">
        <ul style="list-style-type: none; padding: 0;">
            <li style="margin: 10px 0; padding: 10px; background: white; border-radius: 5px; border-left: 4px solid #2196f3;">
                ✏️ <strong>Sentence Building:</strong> Write 5 sentences using "big" and "small"
            </li>
            <li style="margin: 10px 0; padding: 10px; background: white; border-radius: 5px; border-left: 4px solid #4caf50;">
                📋 <strong>My Favorite Things:</strong> Describe your favorite toy - is it big or small?
            </li>
            <li style="margin: 10px 0; padding: 10px; background: white; border-radius: 5px; border-left: 4px solid #ff9800;">
                📖 <strong>Story Creation:</strong> Write a short story about a big animal and a small animal
            </li>
            <li style="margin: 10px 0; padding: 10px; background: white; border-radius: 5px; border-left: 4px solid #9c27b0;">
                💭 <strong>Family Sizes:</strong> Compare the sizes of people in your family
            </li>
        </ul>
    </div>
    
    <h5>🧠 Quick Questions & Answers:</h5>
    <div style="background: #ffe6e6; padding: 20px; border-radius: 10px; margin: 20px 0;">
        <div style="margin-bottom: 15px; padding: 15px; background: white; border-radius: 8px; border-left: 4px solid #e74c3c;">
            <p><strong>Q: Which is bigger - a car or a bicycle?</strong></p>
            <button onclick="toggleAnswer(this)" style="background: #3498db; color: white; border: none; padding: 8px 16px; border-radius: 5px; margin: 10px 0; cursor: pointer; font-weight: bold;">
                🤔 Think & Reveal Answer
            </button>
            <div class="answer" style="display: none; margin-top: 10px; padding: 10px; background: #e8f5e8; border-radius: 5px;">
                <p style="color: #27ae60; font-weight: bold; margin: 0;">A: A car is bigger than a bicycle! 🚗 > 🚲</p>
            </div>
        </div>
        <div style="margin-bottom: 15px; padding: 15px; background: white; border-radius: 8px; border-left: 4px solid #3498db;">
            <p><strong>Q: Which is smaller - a cat or a tiger?</strong></p>
            <button onclick="toggleAnswer(this)" style="background: #e74c3c; color: white; border: none; padding: 8px 16px; border-radius: 5px; margin: 10px 0; cursor: pointer; font-weight: bold;">
                🤔 Think & Reveal Answer
            </button>
            <div class="answer" style="display: none; margin-top: 10px; padding: 10px; background: #e8f5e8; border-radius: 5px;">
                <p style="color: #27ae60; font-weight: bold; margin: 0;">A: A cat is smaller than a tiger! 🐱 < 🐅</p>
            </div>
        </div>
        <div style="margin-bottom: 15px; padding: 15px; background: white; border-radius: 8px; border-left: 4px solid #f39c12;">
            <p><strong>Q: What's the opposite of big?</strong></p>
            <button onclick="toggleAnswer(this)" style="background: #f39c12; color: white; border: none; padding: 8px 16px; border-radius: 5px; margin: 10px 0; cursor: pointer; font-weight: bold;">
                🤔 Think & Reveal Answer
            </button>
            <div class="answer" style="display: none; margin-top: 10px; padding: 10px; background: #e8f5e8; border-radius: 5px;">
                <p style="color: #27ae60; font-weight: bold; margin: 0;">A: Small is the opposite of big! 🔄</p>
            </div>
        </div>
        <div style="padding: 15px; background: white; border-radius: 8px; border-left: 4px solid #9b59b6;">
            <p><strong>Q: Can you name something huge?</strong></p>
            <button onclick="toggleAnswer(this)" style="background: #9b59b6; color: white; border: none; padding: 8px 16px; border-radius: 5px; margin: 10px 0; cursor: pointer; font-weight: bold;">
                🤔 Think & Reveal Answer
            </button>
            <div class="answer" style="display: none; margin-top: 10px; padding: 10px; background: #e8f5e8; border-radius: 5px;">
                <p style="color: #27ae60; font-weight: bold; margin: 0;">A: An elephant, a whale, or a mountain! 🐘🐋🏔️</p>
            </div>
        </div>
    </div>
    
    <script>
    function toggleAnswer(button) {
        const answerDiv = button.nextElementSibling;
        if (answerDiv.style.display === 'none') {
            answerDiv.style.display = 'block';
            button.innerHTML = '✅ Answer Revealed!';
            button.style.background = '#27ae60';
            button.disabled = true;
            button.style.cursor = 'not-allowed';
        }
    }
    </script>
    
    <h5>🎪 Fun Word Games:</h5>
    <div style="background: #f0fff0; padding: 20px; border-radius: 10px; margin: 20px 0; border: 2px solid #90ee90;">
        <div style="margin-bottom: 15px;">
            <h6 style="color: #228b22;">🎯 Size Detective Game:</h6>
            <p>Look around your room and find:</p>
            <ul>
                <li>3 things that are <strong style="color: #e74c3c;">BIG</strong></li>
                <li>3 things that are <strong style="color: #3498db;">SMALL</strong></li>
                <li>1 thing that's the <strong style="color: #f39c12;">BIGGEST</strong> in your room</li>
                <li>1 thing that's the <strong style="color: #9b59b6;">SMALLEST</strong> you can find</li>
            </ul>
        </div>
    </div>
    """
    
    # Auditory learning content for size concepts - simplified layout
    auditory_content = """
    <h4>🎵 Auditory Learning: Big & Small</h4>
    
    <h5>🔢 Interactive Size Lessons</h5>
    
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 20px; margin: 20px 0;">
        <div style="background: white; padding: 20px; border-radius: 10px; border-left: 4px solid #e74c3c; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
            <h6 style="color: #e74c3c; margin-bottom: 15px;">🎵 Size Song</h6>
            <div id="sizeSongText" style="display: none;">
                Big and small, big and small, look around and see them all! Elephants are big and round, ants are small upon the ground. Lions roar with sounds so loud, mice squeak quiet in the crowd. Big things, small things, everywhere, sizes different we can share!
            </div>
            <button onclick="playAudio('sizeSong')" class="audio-btn" style="background: #e74c3c; color: white; border: none; padding: 12px 20px; border-radius: 25px; cursor: pointer; font-weight: 600; margin: 5px;">
                🎵 Play Size Song
            </button>
        </div>
        
        <div style="background: white; padding: 20px; border-radius: 10px; border-left: 4px solid #27ae60; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
            <h6 style="color: #27ae60; margin-bottom: 15px;">🔊 Sound Game</h6>
            <div id="soundGameText" style="display: none;">
                Let's make big and small sounds! Say ROAR like a big lion! ... ... Now say squeak squeak like a small mouse! ... ... Say MOO like a big cow! ... ... Now say chirp chirp like a small bird! ... ... Great job making big and small sounds!
            </div>
            <button onclick="playAudio('soundGame')" class="audio-btn" style="background: #27ae60; color: white; border: none; padding: 12px 20px; border-radius: 25px; cursor: pointer; font-weight: 600; margin: 5px;">
                🔊 Sound Game
            </button>
        </div>
        
        <div style="background: white; padding: 20px; border-radius: 10px; border-left: 4px solid #f39c12; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
            <h6 style="color: #f39c12; margin-bottom: 15px;">🎭 Size Practice</h6>
            <div id="sizePracticeText" style="display: none;">
                Let's practice size words! Say BIG with a loud voice! ... ... Now say small with a tiny voice! ... ... Say HUGE like a giant! ... ... Now say little like a whisper! ... ... Say ENORMOUS very loudly! ... ... Now say tiny very quietly! ... ... Perfect size practice!
            </div>
            <button onclick="playAudio('sizePractice')" class="audio-btn" style="background: #f39c12; color: white; border: none; padding: 12px 20px; border-radius: 25px; cursor: pointer; font-weight: 600; margin: 5px;">
                🎭 Size Practice
            </button>
        </div>
    </div>
    
    <!-- Main Audio Controls -->
    <div style="text-align: center; margin: 25px 0; padding: 20px; background: white; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
        <h6 style="margin-bottom: 15px;">🎮 Audio Controls</h6>
        <div style="display: flex; justify-content: center; gap: 15px; flex-wrap: wrap;">
            <button onclick="pauseAudio()" id="pauseBtn" style="background: #ff6b6b; color: white; border: none; padding: 12px 20px; border-radius: 25px; cursor: pointer; font-weight: 600;">
                ⏸️ Pause
            </button>
            <button onclick="playLastAudio()" id="playBtn" style="background: #28a745; color: white; border: none; padding: 12px 20px; border-radius: 25px; cursor: pointer; font-weight: 600;">
                ▶️ Play
            </button>
            <button onclick="playAllSizes()" style="background: #17a2b8; color: white; border: none; padding: 12px 20px; border-radius: 25px; cursor: pointer; font-weight: 600;">
                📏 Big & Small
            </button>
        </div>
        <div id="audioStatus" style="margin-top: 15px; font-weight: 600; color: #667eea;">Ready to start learning!</div>
    </div>
</div>

<h5>🎯 Additional Size Activities:</h5>
<div style="background: #fff3cd; padding: 20px; border-radius: 10px; margin: 15px 0; border-left: 4px solid #ffc107;">
    <ul style="margin: 0; padding-left: 20px;">
        <li>🎧 Listen to each size lesson above</li>
        <li>🔊 Practice making big and small sounds</li>
        <li>🎤 Use the size practice to learn new words</li>
        <li>🗣️ Try saying size words in different voices</li>
        <li>👂 Listen for size words in stories and songs</li>
    </ul>
</div>

<script>
let synthesis = window.speechSynthesis;
let currentUtterance = null;
let voices = [];
let isPlaying = false;
let isPaused = false;

// Initialize audio system when page loads
document.addEventListener('DOMContentLoaded', function() {
    loadVoices();
    initializeControls();
    
    // Load voices again after a delay (some browsers need this)
    setTimeout(loadVoices, 100);
});

// Load voices
function loadVoices() {
    voices = synthesis.getVoices();
    populateVoiceSelect();
}

function populateVoiceSelect() {
    const voiceSelect = document.getElementById('voiceSelect');
    if (!voiceSelect) return;
    
    voiceSelect.innerHTML = '';
    
    // Filter for English voices and categorize by gender
    const englishVoices = voices.filter(voice => voice.lang.includes('en'));
    
    const femaleVoices = englishVoices.filter(voice => 
        voice.name.includes('Female') || voice.name.includes('female') || 
        voice.name.includes('Samantha') || voice.name.includes('Karen') ||
        voice.name.includes('Moira') || voice.name.includes('Fiona') ||
        voice.name.includes('Google UK English Female') || 
        voice.name.includes('Microsoft Zira') || voice.name.includes('Victoria') ||
        voice.name.includes('Susan') || voice.name.includes('Allison')
    );
    
    const maleVoices = englishVoices.filter(voice => 
        voice.name.includes('Male') || voice.name.includes('male') || 
        voice.name.includes('Alex') || voice.name.includes('Daniel') ||
        voice.name.includes('Thomas') || voice.name.includes('Google UK English Male') ||
        voice.name.includes('Microsoft David') || voice.name.includes('Fred') ||
        voice.name.includes('Oliver') || voice.name.includes('Ralph')
    );
    
    // Add simplified voice options
    if (femaleVoices.length > 0) {
        const option = document.createElement('option');
        option.value = 'female';
        option.textContent = 'Female';
        option.dataset.voice = JSON.stringify(femaleVoices[0]);
        voiceSelect.appendChild(option);
    }
    
    if (maleVoices.length > 0) {
        const option = document.createElement('option');
        option.value = 'male';
        option.textContent = 'Male';
        option.dataset.voice = JSON.stringify(maleVoices[0]);
        voiceSelect.appendChild(option);
    }
    
    // If no categorized voices found, use any English voice
    if (femaleVoices.length === 0 && maleVoices.length === 0 && englishVoices.length > 0) {
        const option = document.createElement('option');
        option.value = '0';
        option.textContent = 'Default Voice';
        option.dataset.voice = JSON.stringify(englishVoices[0]);
        voiceSelect.appendChild(option);
    }
    
    // Ultimate fallback
    if (englishVoices.length === 0) {
        const option = document.createElement('option');
        option.value = '0';
        option.textContent = 'Default Voice';
        voiceSelect.appendChild(option);
    }
}

function initializeControls() {
    // Speed range control
    const speedRange = document.getElementById('speedRange');
    const speedValue = document.getElementById('speedValue');
    if (speedRange && speedValue) {
        speedRange.addEventListener('input', function() {
            speedValue.textContent = this.value + 'x';
        });
    }
    
    // Volume range control
    const volumeRange = document.getElementById('volumeRange');
    const volumeValue = document.getElementById('volumeValue');
    if (volumeRange && volumeValue) {
        volumeRange.addEventListener('input', function() {
            volumeValue.textContent = Math.round(this.value * 100) + '%';
        });
    }
}

function playAudio(audioType) {
    let audioText = '';
    
    // Get the text content for the selected audio type
    switch(audioType) {
        case 'sizeSong':
            audioText = document.getElementById('sizeSongText').textContent;
            break;
        case 'soundGame':
            audioText = document.getElementById('soundGameText').textContent;
            break;
        case 'sizePractice':
            audioText = document.getElementById('sizePracticeText').textContent;
            break;
        default:
            audioText = 'Audio content not found.';
    }
    
    if (synthesis.speaking) {
        synthesis.cancel();
    }
    
    currentUtterance = new SpeechSynthesisUtterance(audioText);
    
    // Set voice
    const voiceSelect = document.getElementById('voiceSelect');
    const speedRange = document.getElementById('speedRange');
    const volumeRange = document.getElementById('volumeRange');
    
    if (voiceSelect && voiceSelect.options.length > 0) {
        const selectedOption = voiceSelect.options[voiceSelect.selectedIndex];
        if (selectedOption.dataset.voice) {
            try {
                const voiceData = JSON.parse(selectedOption.dataset.voice);
                const matchingVoice = voices.find(voice => voice.name === voiceData.name);
                if (matchingVoice) {
                    currentUtterance.voice = matchingVoice;
                }
            } catch (e) {
                console.warn('Could not parse voice data:', e);
            }
        }
    }
    
    // Set speech properties
    currentUtterance.rate = speedRange ? parseFloat(speedRange.value) : 0.8;
    currentUtterance.pitch = 1.1; // Slightly higher pitch for children
    currentUtterance.volume = volumeRange ? parseFloat(volumeRange.value) : 0.9;
    
    currentUtterance.onstart = function() {
        isPlaying = true;
        isPaused = false;
        updateAudioStatus('🎵 Playing ' + audioType + '...');
    };
    
    currentUtterance.onend = function() {
        isPlaying = false;
        isPaused = false;
        updateAudioStatus('✅ Audio finished! Ready for next lesson.');
    };
    
    currentUtterance.onerror = function(event) {
        isPlaying = false;
        isPaused = false;
        updateAudioStatus('❌ Audio error. Please try again.');
        console.error('Speech synthesis error:', event);
    };
    
    synthesis.speak(currentUtterance);
    updateAudioStatus('🎵 Starting audio lesson...');
}

function pauseAudio() {
    if (synthesis.speaking && !isPaused) {
        synthesis.pause();
        isPaused = true;
        updateAudioStatus('⏸️ Audio paused');
    } else if (isPaused) {
        synthesis.resume();
        isPaused = false;
        updateAudioStatus('▶️ Audio resumed');
    }
}

function playLastAudio() {
    if (isPaused) {
        // Resume if paused
        synthesis.resume();
        isPaused = false;
        updateAudioStatus('▶️ Audio resumed');
    } else if (!isPlaying) {
        // Give helpful instructions when play is clicked
        const instructionText = "Hello! Click on the colorful buttons above to start learning about big and small. Try the size song, sound game, or size practice!";
        
        if (synthesis.speaking) {
            synthesis.cancel();
        }
        
        currentUtterance = new SpeechSynthesisUtterance(instructionText);
        currentUtterance.rate = 0.8;
        currentUtterance.pitch = 1.1;
        currentUtterance.volume = 0.9;
        
        currentUtterance.onstart = function() {
            isPlaying = true;
            updateAudioStatus('💬 Giving instructions...');
        };
        
        currentUtterance.onend = function() {
            isPlaying = false;
            updateAudioStatus('👆 Click the buttons above to start learning!');
        };
        
        synthesis.speak(currentUtterance);
    }
}

function playAllSizes() {
    const sizesText = "Let's learn about big and small together! Big things are large like elephants, whales, and houses. Small things are tiny like ants, mice, and buttons. Big and small, they're everywhere!";
    
    if (synthesis.speaking) {
        synthesis.cancel();
    }
    
    currentUtterance = new SpeechSynthesisUtterance(sizesText);
    
    // Set voice and properties
    const voiceSelect = document.getElementById('voiceSelect');
    const speedRange = document.getElementById('speedRange');
    const volumeRange = document.getElementById('volumeRange');
    
    if (voiceSelect && voiceSelect.options.length > 0) {
        const selectedOption = voiceSelect.options[voiceSelect.selectedIndex];
        if (selectedOption.dataset.voice) {
            try {
                const voiceData = JSON.parse(selectedOption.dataset.voice);
                const matchingVoice = voices.find(voice => voice.name === voiceData.name);
                if (matchingVoice) {
                    currentUtterance.voice = matchingVoice;
                }
            } catch (e) {
                console.warn('Could not parse voice data:', e);
            }
        }
    }
    
    currentUtterance.rate = speedRange ? parseFloat(speedRange.value) : 0.8;
    currentUtterance.pitch = 1.1;
    currentUtterance.volume = volumeRange ? parseFloat(volumeRange.value) : 0.9;
    
    currentUtterance.onstart = function() {
        isPlaying = true;
        updateAudioStatus('📏 Learning about big and small...');
    };
    
    currentUtterance.onend = function() {
        isPlaying = false;
        updateAudioStatus('🎉 Finished learning sizes! Try the other lessons above.');
    };
    
    currentUtterance.onerror = function(event) {
        isPlaying = false;
        updateAudioStatus('❌ Audio error. Please try again.');
        console.error('Speech synthesis error:', event);
    };
    
    synthesis.speak(currentUtterance);
}

function updateAudioStatus(message) {
    const status = document.getElementById('audioStatus');
    if (status) {
        status.textContent = message;
    }
}

// Ensure voices are loaded when they become available
if (speechSynthesis.onvoiceschanged !== undefined) {
    speechSynthesis.onvoiceschanged = loadVoices;
}
</script>
    """
    
    return {
        'title': f'Big & Small - {learning_style.title()} Learning',
        'visual': visual_content if learning_style == 'visual' else create_structured_lesson_content('maths', learning_style, topic)['visual'],
        'verbal': verbal_content if learning_style == 'verbal' else create_structured_lesson_content('maths', learning_style, topic)['verbal'],
        'auditory': auditory_content if learning_style == 'auditory' else create_structured_lesson_content('maths', learning_style, topic)['auditory'],
        'physical': '<h3>Physical Learning</h3><p>Hands-on activities for comparing sizes...</p>',
        'logical': '<h3>Logical Learning</h3><p>Step-by-step size ordering and measurement...</p>',
        'social': '<h3>Social Learning</h3><p>Group size comparison games and activities...</p>',
        'solitary': '<h3>Independent Learning</h3><p>Self-paced size recognition and comparison exercises...</p>',
        'current_style': learning_style
    }

def create_structured_lesson_content(subject, learning_style, topic=None):
    """Create structured educational content when AI is not available"""
    
    if not topic:
        topic = f"Introduction to {subject.title()}"
    
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

def generate_study_buddy_response(user_message, context=None):
    """
    Generate Study Buddy AI responses using Claude
    """
    try:
        context_text = ""
        if context:
            context_text = f"\nPrevious conversation context: {context}"

        user_content = f'Student\'s message: "{user_message}"{context_text}\n\nRespond as Study Buddy AI with helpful, engaging advice. Keep responses concise but informative (2-4 sentences max).'

        response = anthropic_client.messages.create(
            model="claude-opus-4-7",
            max_tokens=512,
            system="""You are Study Buddy AI, a friendly educational assistant for children aged 5-11.

Key personality traits:
- Enthusiastic and supportive
- Use age-appropriate language
- Include relevant emojis
- Break down topics into simple steps
- Provide practical examples
- Encourage learning and growth
- Be patient and understanding""",
            messages=[{"role": "user", "content": user_content}]
        )
        return response.content[0].text
    except Exception as e:
        print(f"Claude API error in study buddy: {e}")
        return get_fallback_study_response(user_message)

def get_fallback_study_response(user_message):
    """Fallback responses when AI is unavailable"""
    responses = [
        "That's a great question! I'd love to help you learn more about that topic. Can you tell me which subject you're working on?",
        "Learning is an adventure! What specific area would you like to explore together?",
        "I'm here to help you succeed! What's the most challenging part about this topic for you?",
        "That sounds interesting! Let's break it down into smaller, easier steps. What would you like to start with?"
    ]
    return responses[len(user_message) % len(responses)]