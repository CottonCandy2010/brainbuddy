import os
import json
import time
import anthropic
from firebase_config import get_firestore_client
from firebase_admin import firestore

# Initialize Anthropic client (reads ANTHROPIC_API_KEY from environment)
anthropic_client = anthropic.Anthropic()

def generate_and_upload_lessons():
    """
    Generate comprehensive lesson content using OpenAI and upload to Firestore.
    This creates lessons for all subjects and learning styles.
    """
    
    # Get Firestore client
    db = get_firestore_client()
    if not db:
        print("Failed to connect to Firestore. Please check your Firebase configuration.")
        return False
    
    # Define comprehensive curriculum structure
    curriculum = {
        'maths': {
            'beginner': [
                'Understanding Fractions and Basic Operations',
                'Decimals and Place Value',
                'Percentages in Daily Life',
                'Introduction to Basic Algebra',
                'Area and Perimeter of Shapes',
                'Working with Negative Numbers',
                'Simple Ratios and Proportions'
            ],
            'intermediate': [
                'Linear Equations and Graphs',
                'Quadratic Expressions',
                'Probability and Statistics Basics'
            ]
        },
        'science': {
            'beginner': [
                'The Water Cycle and Weather Patterns',
                'Photosynthesis and Plant Life',
                'States of Matter and Particle Theory',
                'Human Body Systems - Digestive System',
                'Basic Electricity and Circuits',
                'The Rock Cycle and Earth\'s Structure',
                'Food Chains and Ecosystems'
            ],
            'intermediate': [
                'Chemical Reactions and Equations',
                'Forces and Motion in Physics',
                'Genetics and Heredity'
            ]
        },
        'english': {
            'beginner': [
                'Creative Writing and Storytelling Techniques',
                'Parts of Speech and Grammar Fundamentals',
                'Reading Comprehension Strategies',
                'Poetry Analysis and Literary Devices',
                'Character Development in Literature',
                'Persuasive Writing and Arguments',
                'Sentence Structure and Paragraph Writing'
            ],
            'intermediate': [
                'Advanced Literary Analysis',
                'Essay Writing and Structure',
                'Creative Fiction Techniques'
            ]
        },
        'computing': {
            'beginner': [
                'Introduction to Programming and Algorithms',
                'Understanding Computer Hardware',
                'Basic Web Design Principles',
                'Digital Citizenship and Online Safety',
                'Introduction to Databases'
            ]
        },
        'history': {
            'beginner': [
                'Ancient Civilizations and Their Impact on Modern Society',
                'Medieval Life and Feudal Systems',
                'The Industrial Revolution',
                'World War History and Its Consequences',
                'Ancient Egypt and the Pyramids'
            ]
        },
        'geography': {
            'beginner': [
                'Climate Change and Global Weather Systems',
                'World Countries and Capitals',
                'Natural Disasters and Their Causes',
                'Rivers, Mountains, and Physical Features',
                'Population and Urbanization'
            ]
        }

    }
    
    total_lessons = sum(len(topics) for subject_data in curriculum.values() 
                       for topics in subject_data.values())
    current_lesson = 0
    
    print(f"Starting generation of {total_lessons} lessons...")
    print("⚠️  WARNING: This will make many Claude API calls. Monitor your usage!")
    print("💡 TIP: You can interrupt this script and resume later if needed.\n")
    
    for subject, levels in curriculum.items():
        print(f"\n📚 Generating lessons for {subject.upper()}...")
        
        for level, topics in levels.items():
            for topic in topics:
                current_lesson += 1
                print(f"  [{current_lesson}/{total_lessons}] Generating: {topic}")
                
                try:
                    # Generate content for all 7 learning styles
                    lesson_content = generate_lesson_content_for_all_styles(subject, topic, level)
                    
                    if lesson_content:
                        # Create lesson document
                        topic_clean = topic.lower().replace(' ', '_').replace("'", '')
                        lesson_doc = {
                            'subject': subject,
                            'topic': topic,
                            'level': level,
                            'lesson_id': f"{subject}_{topic_clean}",
                            'content': lesson_content,
                            'created_at': firestore.SERVER_TIMESTAMP,
                            'keywords': generate_keywords(subject, topic)
                        }
                        
                        # Upload to Firestore
                        doc_ref = db.collection('lessons').add(lesson_doc)
                        print(f"    ✅ Uploaded to Firestore: {doc_ref[1].id}")
                        
                        # Rate limiting - wait between requests
                        time.sleep(2)  # 2 second delay between API calls
                    else:
                        print(f"    ❌ Failed to generate content for: {topic}")
                        
                except Exception as e:
                    print(f"    ❌ Error processing {topic}: {e}")
                    continue
    
    print(f"\n🎉 Lesson generation complete! Generated {current_lesson} lessons.")
    return True

def generate_lesson_content_for_all_styles(subject, topic, level):
    """
    Generate content for all 7 learning styles using Claude
    """
    prompt = f"""You are an expert educational content creator for secondary school students aged 11-16.
Create a comprehensive lesson about "{topic}" for {subject} at {level} level.

Generate content optimized for SEVEN different learning styles:

1. VISUAL learners: Include descriptions of diagrams, charts, visual representations, and step-by-step visual guides
2. VERBAL learners: Provide clear written explanations, definitions, examples, and structured text-based learning
3. AUDITORY learners: Create content that would work well when read aloud, with rhythm, repetition, and conversational tone
4. PHYSICAL learners: Include hands-on activities, experiments, movement-based learning, and tactile experiences
5. LOGICAL learners: Provide step-by-step reasoning, patterns, cause-and-effect relationships, and systematic approaches
6. SOCIAL learners: Include group activities, discussions, collaborative projects, and peer learning opportunities
7. SOLITARY learners: Create self-reflection questions, independent study tasks, personal exploration, and individual challenges

Make the content:
- Age-appropriate for 11-16 year olds
- Engaging and educational
- Clear and easy to understand
- Interactive where possible
- About 150-200 words per learning style
- Appropriate for {level} level understanding

Respond in JSON format with this exact structure:
{{
    "title": "Lesson title",
    "visual": "HTML content for visual learners with descriptions of visual elements",
    "verbal": "HTML content for verbal learners with clear written explanations",
    "auditory": "HTML content for auditory learners with conversational, rhythm-friendly text",
    "physical": "HTML content for physical learners with hands-on activities",
    "logical": "HTML content for logical learners with step-by-step reasoning",
    "social": "HTML content for social learners with group activities",
    "solitary": "HTML content for solitary learners with independent study tasks"
}}

Use HTML tags like <h3>, <p>, <ul>, <li>, <strong>, <em> for formatting. Do not include <div> wrapper tags.
Output only the JSON object, no additional text."""

    try:
        with anthropic_client.messages.stream(
            model="claude-opus-4-7",
            max_tokens=3000,
            messages=[{"role": "user", "content": prompt}]
        ) as stream:
            content_text = stream.get_final_message().content[0].text

        content = json.loads(content_text)

        # Ensure all required keys are present
        required_keys = ['title', 'visual', 'verbal', 'auditory']
        for key in required_keys:
            if key not in content:
                content[key] = f"Content for {key} learning style is being generated..."

        return content

    except Exception as e:
        print(f"    Claude API error: {e}")
        return None

def generate_keywords(subject, topic):
    """
    Generate relevant keywords for search and categorization
    """
    keywords = [subject, topic.lower()]
    
    # Add subject-specific keywords
    subject_keywords = {
        'maths': ['mathematics', 'numbers', 'calculation', 'problem-solving'],
        'science': ['experiment', 'observation', 'hypothesis', 'research'],
        'english': ['language', 'literature', 'writing', 'reading'],
        'computing': ['technology', 'programming', 'digital', 'computer'],
        'history': ['past', 'civilization', 'events', 'culture'],
        'geography': ['world', 'earth', 'environment', 'location']
    }
    
    keywords.extend(subject_keywords.get(subject, []))
    return keywords

def run_lesson_generation():
    """
    Main function to run the lesson generation process
    """
    print("🚀 Starting Brain Buddy Lesson Generation System")
    print("=" * 50)
    
    # Check if required environment variables exist
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("❌ Error: ANTHROPIC_API_KEY not found in environment variables")
        return False
        
    if not os.environ.get("FIREBASE_SERVICE_ACCOUNT_KEY"):
        print("❌ Error: FIREBASE_SERVICE_ACCOUNT_KEY not found in environment variables")
        print("Please add your Firebase service account key to Replit Secrets")
        return False
    
    # Start generation process
    return generate_and_upload_lessons()

if __name__ == "__main__":
    run_lesson_generation()