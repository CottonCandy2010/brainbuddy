// Brain Buddy - Main JavaScript File

document.addEventListener('DOMContentLoaded', function() {
    // Initialize the application
    initApp();
});

function initApp() {
    // Set up event listeners for the selection cards
    setupSelectionCards();
    
    // Set up event listeners for the style tabs in the lesson page
    setupStyleTabs();
    
    // Set up navigation buttons
    setupNavigationButtons();
    
    // Add animations to page elements
    addAnimations();
    
    // Initialize audio controller if we're on a lesson page
    if (document.getElementById('audioText')) {
        initializeAudioControls();
    }
}

// Audio Learning Controller
function initializeAudioControls() {
    let synthesis = window.speechSynthesis;
    let currentUtterance = null;
    let voices = [];
    let selectedVoice = null;
    let volume = 0.8;
    let isPlaying = false;
    let isPaused = false;
    
    // Wait for voices to load
    function loadVoices() {
        voices = synthesis.getVoices();
        populateVoiceSelector();
    }
    
    function populateVoiceSelector() {
        const voiceSelect = document.getElementById('voiceSelect');
        if (!voiceSelect) return;
        
        // Clear existing options
        voiceSelect.innerHTML = '';
        
        // Filter for English voices
        const englishVoices = voices.filter(voice => voice.lang.startsWith('en'));
        
        const femaleVoices = englishVoices.filter(voice => 
            voice.name.toLowerCase().includes('female') || 
            voice.name.toLowerCase().includes('woman') ||
            voice.name.toLowerCase().includes('zira') ||
            voice.name.toLowerCase().includes('helena')
        );
        
        const maleVoices = englishVoices.filter(voice => 
            voice.name.toLowerCase().includes('male') || 
            voice.name.toLowerCase().includes('man') ||
            voice.name.toLowerCase().includes('david') ||
            voice.name.toLowerCase().includes('mark')
        );
        
        // Add female voices
        femaleVoices.slice(0, 2).forEach((voice, index) => {
            const option = document.createElement('option');
            option.value = voice.name;
            option.textContent = `Female Voice ${index + 1}`;
            voiceSelect.appendChild(option);
        });
        
        // Add male voices
        maleVoices.slice(0, 2).forEach((voice, index) => {
            const option = document.createElement('option');
            option.value = voice.name;
            option.textContent = `Male Voice ${index + 1}`;
            voiceSelect.appendChild(option);
        });
        
        // If no gendered voices found, add best available
        if (voiceSelect.children.length === 0) {
            englishVoices.slice(0, 4).forEach((voice, index) => {
                const option = document.createElement('option');
                option.value = voice.name;
                option.textContent = voice.name || `Voice ${index + 1}`;
                voiceSelect.appendChild(option);
            });
        }
        
        // Set default voice
        if (voiceSelect.children.length > 0) {
            selectedVoice = voices.find(voice => voice.name === voiceSelect.value);
        }
    }
    
    function playAudio() {
        const audioText = document.getElementById('audioText');
        if (!audioText) return;
        
        const text = cleanTextForSpeech(audioText.textContent);
        
        if (isPaused && currentUtterance) {
            synthesis.resume();
            isPaused = false;
        } else {
            currentUtterance = new SpeechSynthesisUtterance(text);
            
            if (selectedVoice) {
                currentUtterance.voice = selectedVoice;
            }
            currentUtterance.volume = volume;
            currentUtterance.rate = 0.9;
            currentUtterance.pitch = 1.0;
            
            currentUtterance.onstart = () => {
                isPlaying = true;
                updateAudioStatus('🎵 Playing audio lesson...');
                toggleButtons(true);
            };
            
            currentUtterance.onend = () => {
                isPlaying = false;
                isPaused = false;
                updateAudioStatus('✅ Audio lesson completed!');
                toggleButtons(false);
            };
            
            currentUtterance.onerror = () => {
                updateAudioStatus('❌ Error playing audio. Please try again.');
                toggleButtons(false);
            };
            
            synthesis.speak(currentUtterance);
        }
        
        updateAudioStatus('🎵 Playing audio lesson...');
        toggleButtons(true);
    }
    
    function pauseAudio() {
        if (synthesis.speaking && !synthesis.paused) {
            synthesis.pause();
            isPaused = true;
            updateAudioStatus('⏸️ Audio paused');
            toggleButtons(false);
        }
    }
    
    function stopAudio() {
        synthesis.cancel();
        isPlaying = false;
        isPaused = false;
        currentUtterance = null;
        updateAudioStatus('⏹️ Audio stopped');
        toggleButtons(false);
    }
    
    function toggleButtons(playing) {
        const playBtn = document.getElementById('playAudioBtn');
        const pauseBtn = document.getElementById('pauseAudioBtn');
        const stopBtn = document.getElementById('stopAudioBtn');
        
        if (playBtn && pauseBtn && stopBtn) {
            if (playing) {
                playBtn.style.display = 'none';
                pauseBtn.style.display = 'flex';
                stopBtn.style.display = 'flex';
            } else {
                playBtn.style.display = 'flex';
                pauseBtn.style.display = 'none';
                stopBtn.style.display = 'none';
            }
        }
    }
    
    function updateAudioStatus(message) {
        const status = document.getElementById('audioStatus');
        if (status) {
            status.textContent = message;
        }
    }
    
    function cleanTextForSpeech(text) {
        // Remove HTML tags
        text = text.replace(/<[^>]*>/g, '');
        
        // Replace common symbols
        text = text.replace(/&/g, 'and');
        text = text.replace(/%/g, 'percent');
        text = text.replace(/\$/g, 'dollars');
        
        // Add natural pauses
        text = text.replace(/\./g, '. ');
        text = text.replace(/,/g, ', ');
        text = text.replace(/:/g, ': ');
        text = text.replace(/;/g, '; ');
        
        // Clean up whitespace
        text = text.replace(/\s+/g, ' ').trim();
        
        return text;
    }
    
    // Initialize voices
    if (synthesis.getVoices().length !== 0) {
        loadVoices();
    } else {
        synthesis.addEventListener('voiceschanged', loadVoices);
    }
    
    // Setup event listeners
    const playBtn = document.getElementById('playAudioBtn');
    if (playBtn) {
        playBtn.addEventListener('click', playAudio);
    }
    
    const pauseBtn = document.getElementById('pauseAudioBtn');
    if (pauseBtn) {
        pauseBtn.addEventListener('click', pauseAudio);
    }
    
    const stopBtn = document.getElementById('stopAudioBtn');
    if (stopBtn) {
        stopBtn.addEventListener('click', stopAudio);
    }
    
    const voiceSelect = document.getElementById('voiceSelect');
    if (voiceSelect) {
        voiceSelect.addEventListener('change', (e) => {
            selectedVoice = voices.find(voice => voice.name === e.target.value);
        });
    }
    
    const volumeSlider = document.getElementById('volumeSlider');
    const volumeValue = document.getElementById('volumeValue');
    if (volumeSlider && volumeValue) {
        volumeSlider.addEventListener('input', (e) => {
            volume = e.target.value / 100;
            volumeValue.textContent = e.target.value + '%';
            
            if (currentUtterance) {
                currentUtterance.volume = volume;
            }
        });
    }
}

function setupSelectionCards() {
    // Get all selection cards
    const selectionCards = document.querySelectorAll('.selection-card');
    
    // Add click event listener to each card
    selectionCards.forEach(card => {
        card.addEventListener('click', function() {
            // Remove active class from all cards in the same category
            const categoryCards = document.querySelectorAll(`.${this.dataset.category}-card`);
            categoryCards.forEach(c => c.classList.remove('active'));
            
            // Add active class to the clicked card
            this.classList.add('active');
            
            // If it's a subject card, navigate directly to curriculum topics
            if (this.dataset.category === 'subject') {
                const selectedSubject = this.dataset.value;
                const selectedAge = localStorage.getItem('studentAge') || '10';
                const selectedLevel = localStorage.getItem('ageGroup') || 'p5';
                
                // Store the selected subject
                localStorage.setItem('selectedSubject', selectedSubject);
                
                // Navigate directly to curriculum topics for the subject
                window.location.href = `/curriculum-topics?level=${selectedLevel}&age=${selectedAge}&subject=${selectedSubject}`;
            }
            
            // If it's a style card, navigate directly to lesson content
            if (this.dataset.category === 'style') {
                const selectedStyle = this.dataset.value;
                const selectedSubject = localStorage.getItem('selectedSubject') || new URLSearchParams(window.location.search).get('subject') || 'maths';
                const selectedTopic = localStorage.getItem('selectedTopic') || new URLSearchParams(window.location.search).get('topic') || 'Numbers 1-10';
                
                // Navigate directly to lesson page
                window.location.href = `/lesson?subject=${selectedSubject}&style=${selectedStyle}&topic=${encodeURIComponent(selectedTopic)}`;
            }
        });
    });
}

function enableContinueButtonIfReady() {
    // Get the continue button
    const continueBtn = document.getElementById('continue-btn');
    if (!continueBtn) return;
    
    // For subject selection page
    if (document.querySelector('.subject-selection')) {
        const selectedSubject = document.querySelector('.subject-card.active');
        continueBtn.disabled = !selectedSubject;
    }
    
    // For style selection page
    if (document.querySelector('.style-selection')) {
        const selectedStyle = document.querySelector('.style-card.active');
        continueBtn.disabled = !selectedStyle;
    }
}

function setupStyleTabs() {
    // Get all style tabs on the lesson page
    const styleTabs = document.querySelectorAll('.style-tab');
    
    // Add click event listener to each tab
    styleTabs.forEach(tab => {
        tab.addEventListener('click', function() {
            // Remove active class from all tabs
            styleTabs.forEach(t => t.classList.remove('active'));
            
            // Add active class to the clicked tab
            this.classList.add('active');
            
            // Hide all content sections
            const contentSections = document.querySelectorAll('.style-content');
            contentSections.forEach(section => {
                section.style.display = 'none';
            });
            
            // Show the selected content section
            const selectedStyle = this.dataset.style;
            const selectedContent = document.getElementById(`${selectedStyle}-content`);
            if (selectedContent) {
                selectedContent.style.display = 'block';
            }
        });
    });
}

function setupNavigationButtons() {
    // Get all continue buttons
    const continueButtons = document.querySelectorAll('.continue-btn');
    
    // Add click event listener to each button
    continueButtons.forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            
            // If it's the subject selection page, proceed to subject explorer
            if (this.dataset.step === 'subject') {
                const selectedSubject = document.querySelector('.subject-card.active');
                if (selectedSubject) {
                    const educationLevel = localStorage.getItem('ageGroup') || 'highschool';
                    window.location.href = `/subject-explorer?level=${educationLevel}&subject=${selectedSubject.dataset.value}`;
                }
            }
            
            // If it's the style selection page, proceed to lesson page
            if (this.dataset.step === 'style') {
                const selectedStyle = document.querySelector('.style-card.active');
                const subjectValue = document.getElementById('subject-value').value;
                
                if (selectedStyle && subjectValue) {
                    window.location.href = `/lesson?subject=${subjectValue}&style=${selectedStyle.dataset.value}`;
                }
            }
        });
    });
    
    // Get all back buttons
    const backButtons = document.querySelectorAll('.back-btn');
    
    // Add click event listener to each button
    backButtons.forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            
            // If it's the style selection page, go back to subject selection
            if (this.dataset.step === 'style') {
                window.location.href = '/select_subject';
            }
            
            // If it's the lesson page, go back to style selection
            if (this.dataset.step === 'lesson') {
                const subjectValue = document.getElementById('subject-value').value;
                window.location.href = `/select_style?subject=${subjectValue}`;
            }
        });
    });
}

function addAnimations() {
    // Add fade-in animation to main content elements
    const animatedElements = document.querySelectorAll('.animate-fade-in');
    
    // Add animation with staggered delay
    animatedElements.forEach((element, index) => {
        element.style.opacity = '0';
        element.style.animation = `fadeIn 0.5s ease forwards ${index * 0.1}s`;
    });
}

// Function to play audio in the auditory learning style section
function playAudio(audioType) {
    // Get the text content for the specific audio type
    let textToSpeak = '';
    
    switch(audioType) {
        case 'countingSong':
            textToSpeak = `Let's count together from one to ten! One, two, buckle my shoe. Three, four, knock at the door. Five, six, pick up sticks. Seven, eight, lay them straight. Nine, ten, a big fat hen! Now you know how to count to ten!`;
            break;

        case 'clappingGame':
            textToSpeak = `Let's play the clapping game! Clap your hands once for number one! ... ... Now clap your hands twice for number two! ... ... Now clap your hands three times for number three! ... ... Now clap your hands four times for number four! ... ... Now clap your hands five times for number five! ... ... Great job clapping and counting!`;
            break;
        case 'echoPractice':
            textToSpeak = `Let's practice saying numbers! I'll say a number and you repeat it back! One! Two! Three! Four! Five! Six! Seven! Eight! Nine! Ten! Great job repeating the numbers!`;
            break;
        default:
            const audioText = document.getElementById('audioText');
            if (audioText) {
                textToSpeak = audioText.textContent;
            }
    }
    
    if (textToSpeak) {
        // Use the Web Speech API to speak the text
        if ('speechSynthesis' in window) {
            const utterance = new SpeechSynthesisUtterance(textToSpeak);
            utterance.volume = 0.8;
            utterance.rate = 0.9;
            utterance.pitch = 1.0;
            
            // Get selected voice
            const voiceSelect = document.getElementById('voiceSelect');
            if (voiceSelect) {
                const voices = speechSynthesis.getVoices();
                const selectedVoiceName = voiceSelect.value;
                const selectedVoice = voices.find(voice => voice.name === selectedVoiceName);
                if (selectedVoice) {
                    utterance.voice = selectedVoice;
                }
            }
            
            speechSynthesis.speak(utterance);
        } else {
            alert('Sorry, your browser does not support text-to-speech!');
        }
    }
}

// Additional helper functions for the lesson buttons

function startClappingGame() {
    playAudio('clappingGame');
}

function startEchoPractice() {
    playAudio('echoPractice');
}

// Update volume control for the new audio system
function updateVolume() {
    const volumeSlider = document.getElementById('volumeSlider');
    const volumeDisplay = document.getElementById('volumeDisplay');
    
    if (volumeSlider && volumeDisplay) {
        const volume = volumeSlider.value;
        volumeDisplay.textContent = volume + '%';
        
        // Update the visual track
        volumeSlider.style.setProperty('--volume-percent', volume + '%');
    }
}

// Update voice selection for the new audio system
function updateVoice() {
    // Voice selection is now handled within the playAudio function
    console.log('Voice updated');
}
