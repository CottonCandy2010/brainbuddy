import os
import anthropic

class ClaudeAPI:
    def __init__(self):
        self.client = anthropic.Anthropic()

    def generate_educational_content(self, subject, learning_style, topic, age_group="5-7"):
        """
        Generate educational content using Claude AI
        """
        prompt = f"""Create an engaging educational lesson for children aged {age_group} on the topic: "{topic}" in {subject}.

Learning Style: {learning_style}

Requirements:
- Age-appropriate content for {age_group} year olds
- Use simple, clear language
- Include interactive elements and activities
- Make it fun and engaging
- Focus on {learning_style} learning approaches

Format as:
LESSON TITLE: [Creative title]

LEARNING OBJECTIVES:
- [3-4 clear objectives]

MAIN CONTENT:
[Engaging lesson content with examples]

ACTIVITIES:
[3-4 hands-on activities]

PRACTICE QUESTIONS:
[2-3 simple questions to check understanding]
"""

        try:
            response = self.client.messages.create(
                model="claude-opus-4-7",
                max_tokens=1500,
                system="You are an expert primary school educator specializing in creating engaging, age-appropriate educational content for young children.",
                messages=[{"role": "user", "content": prompt}]
            )
            content = response.content[0].text

            return {
                'title': f"{topic} - {learning_style.title()} Learning",
                'content': content,
                'source': 'claude',
                'success': True
            }
        except Exception as e:
            print(f"Claude API request failed: {e}")
            return None

    def generate_study_buddy_response(self, user_message, context=None):
        """
        Generate Study Buddy AI responses using Claude
        """
        system_prompt = """You are Brain Buddy, a friendly AI tutor for primary school children (ages 5-7).
You help with learning mathematics, science, and English in a fun, encouraging way.

Guidelines:
- Use simple, child-friendly language
- Be encouraging and positive
- Make learning fun with examples from daily life
- Ask engaging questions to help children think
- Give clear, step-by-step explanations
- Use emojis sparingly and appropriately
"""

        try:
            response = self.client.messages.create(
                model="claude-opus-4-7",
                max_tokens=800,
                system=system_prompt,
                messages=[{"role": "user", "content": user_message}]
            )
            return response.content[0].text
        except Exception as e:
            print(f"Claude API request failed: {e}")
            return None


# Initialize Claude API instance (backward-compatible name)
deepseek_api = ClaudeAPI()
