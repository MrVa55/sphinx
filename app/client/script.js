// Conversation script for The Turning Point experience
const experienceScript = {
    // Main conversation flow
    mainFlow: [
        { type: 'script', text: "Welcome to The Turning Point experience." },
        { type: 'script', text: "I'd like to explore with you the thoughts that might be holding you back." },
        { type: 'script', text: "Take a moment to reflect as we begin this journey together." },
        { type: 'script', text: "When you see the blinking red dot, please speak into the microphone." },
        { type: 'user', prompt: "What is the thought that most inhibits you from achieving what you want in your life?" },
        { type: 'script', text: "Thank you for sharing that." },
        { type: 'script', text: "Another question to consider..." },
        { type: 'user', prompt: "If this limiting thought were suddenly removed, what would you do differently?" },
        { type: 'script', text: "Thank you for participating in The Turning Point experience." },
        { type: 'script', text: "The images you've seen were generated based on your emotional responses, creating a unique visual journey for you." },
        { type: 'script', text: "This experience is now complete. Take what you've discovered with you." }
    ],
    
    // Alternative paths or follow-up questions (for future expansion)
    followUps: {
        confidence: [
            { type: 'script', text: "Many people struggle with confidence. What helps you feel most confident?" },
            { type: 'user', prompt: "When do you feel most confident and capable?" }
        ],
        fear: [
            { type: 'script', text: "Fear often has important messages for us, even when it holds us back." },
            { type: 'user', prompt: "What do you think this fear is trying to protect you from?" }
        ],
        perfectionism: [
            { type: 'script', text: "Perfectionism can be a heavy burden to carry." },
            { type: 'user', prompt: "How would your life be different if you allowed yourself to be imperfect?" }
        ]
    },
    
    // Opening and closing statements
    opening: "This experience invites you to reflect on the thoughts that shape your reality. The visuals you see will evolve based on the emotions in your responses.",
    closing: "Thank you for participating in The Turning Point. May you carry these insights forward."
}; 