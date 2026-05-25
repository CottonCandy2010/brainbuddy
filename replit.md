# Brain Buddy - Educational Platform

## Overview

Brain Buddy is an AI-powered educational platform designed for children aged 5-16, focusing on personalized learning through adaptive content delivery. The platform utilizes Flask as the backend framework, Firebase for data storage, and integrates with Google Gemini AI and OpenAI APIs for content generation. The system provides an interactive learning experience with avatar customization, progress tracking, and multi-modal content delivery.

## User Preferences

Preferred communication style: Simple, everyday language.
Animation preferences: No celebration animations or complex visual effects - focus on core learning features.

## System Architecture

### Backend Architecture
- **Framework**: Flask (Python)
- **Database**: Firebase Firestore for document storage
- **Authentication**: Flask-Login with parent/child account system
- **API Integration**: Google Gemini AI and OpenAI for content generation
- **Text-to-Speech**: pyttsx3 for audio content generation
- **CORS**: Enabled for cross-origin requests

### Frontend Architecture
- **Templates**: Jinja2 templating engine
- **Styling**: Bootstrap 5 with custom CSS
- **JavaScript**: Vanilla JavaScript for interactivity
- **Responsive Design**: Mobile-first approach
- **Accessibility**: ARIA labels and semantic HTML

### Data Storage Solutions
- **Primary Database**: Firebase Firestore
  - Collections: lessons, students, progress, avatars
  - Real-time synchronization capabilities
  - Offline support for mobile devices
- **Session Management**: Flask sessions for user state
- **Local Storage**: Browser storage for temporary data

## Key Components

### 1. Content Generation System
- **AI Content Generator** (`ai_content_generator.py`): Uses Gemini AI to create personalized lesson content
- **Lesson Generator** (`lesson_generator.py`): Batch generates comprehensive curriculum content
- **Learning Styles**: Visual, auditory, verbal, physical, logical, social, solitary
- **Age-Appropriate Content**: Tailored for different educational levels (P1-P7, Secondary)

### 2. Adaptive Learning Engine
- **Adaptive Difficulty** (`adaptive_difficulty.py`): Dynamically adjusts lesson complexity based on performance
- **Performance Tracking**: Monitors student progress and learning patterns
- **Difficulty Levels**: Beginner, easy, medium, hard, expert
- **Animation System** (`adaptive_difficulty_animations.py`): Visual feedback for level changes

### 3. Avatar System
- **Avatar Customization** (`avatar_service.py`): Comprehensive avatar creation and management
- **Emotion System** (`emotion_avatar_system.py`): Dynamic expressions based on learning states
- **Mood Expressions** (`mood_expressions.py`): Contextual avatar reactions
- **Achievement Unlocks** (`achievement_system.py`): Reward system for learning milestones

### 4. Progress & Gamification
- **Progress Service** (`progress_service.py`): Comprehensive learning analytics
- **Quest System** (`quest_system.py`): Daily, weekly, and special challenges
- **Achievement System**: Badge and reward mechanisms
- **Learning Analytics**: Performance metrics and insights

### 5. User Management
- **Parent-Child Model**: Hierarchical account structure
- **Student Progress Tracking**: Individual learning paths
- **Authentication**: Secure login system with role-based access

## Data Flow

1. **User Authentication**: Parent logs in → selects child profile
2. **Content Selection**: Child chooses subject and learning style
3. **AI Content Generation**: System generates personalized lesson content
4. **Adaptive Delivery**: Content difficulty adjusts based on performance
5. **Progress Tracking**: Learning data stored in Firebase
6. **Gamification**: Achievements and rewards unlock based on progress

## External Dependencies

### AI Services
- **Google Gemini AI**: Primary content generation
- **OpenAI API**: Fallback content generation
- **Text-to-Speech**: pyttsx3 for audio content

### Database & Storage
- **Firebase Firestore**: Document database for lessons and progress
- **Firebase Authentication**: User management (optional)

### Frontend Libraries
- **Bootstrap 5**: UI framework
- **Font Awesome**: Icons
- **Chart.js**: Progress visualization (planned)

### Python Packages
- **Flask**: Web framework
- **Flask-SQLAlchemy**: Database ORM
- **Flask-Login**: Authentication
- **Flask-CORS**: Cross-origin requests
- **google-generativeai**: Gemini AI integration
- **firebase-admin**: Firebase integration
- **pyttsx3**: Text-to-speech

## Deployment Strategy

### Development Environment
- **Platform**: Replit for development and testing
- **Database**: Firebase Firestore (cloud-hosted)
- **Environment Variables**: Stored in Replit Secrets
- **Hot Reload**: Flask debug mode enabled

### Production Considerations
- **Environment Variables**: API keys and service account credentials
- **Security**: Firebase security rules for data access
- **Performance**: Content caching and optimization
- **Scalability**: Firebase auto-scaling capabilities

### Key Configuration
- **Firebase Service Account**: JSON credentials for backend access
- **API Keys**: Gemini AI and OpenAI tokens
- **Database URL**: Firebase project configuration
- **Session Secret**: Flask session encryption key

The application follows a modular architecture with clear separation of concerns, making it maintainable and extensible for future educational features and content types.