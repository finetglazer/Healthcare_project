// Simple Chatbot Conversation Flow
// fe/src/components/Chatbot/ChatbotFlow.js

export const conversationSteps = {
    GREETING: 'greeting',
    PRIMARY_SYMPTOMS: 'primary_symptoms',
    SEVERITY: 'severity',
    DURATION: 'duration',
    ADDITIONAL_INFO: 'additional_info',
    ANALYSIS: 'analysis'
};

export const chatbotQuestions = {
    [conversationSteps.GREETING]: {
        message: "Hello! I'm your medical assistant. I'll help you understand your symptoms and find the right doctor. Let's start - what symptoms are you experiencing?",
        type: 'multiple_choice',
        options: [
            'Fever and body aches',
            'Runny nose and sneezing',
            'Cough and sore throat',
            'Skin irritation/rash',
            'Multiple symptoms'
        ],
        next: conversationSteps.PRIMARY_SYMPTOMS
    },

    [conversationSteps.PRIMARY_SYMPTOMS]: {
        message: "How severe are your symptoms on a scale of 1-10?",
        type: 'scale',
        min: 1,
        max: 10,
        next: conversationSteps.SEVERITY
    },

    [conversationSteps.SEVERITY]: {
        message: "How long have you been experiencing these symptoms?",
        type: 'multiple_choice',
        options: [
            'Less than 24 hours',
            '1-3 days',
            '4-7 days',
            'More than a week'
        ],
        next: conversationSteps.DURATION
    },

    [conversationSteps.DURATION]: {
        message: "Any additional symptoms? (Select all that apply)",
        type: 'checkbox',
        options: [
            'Headache',
            'Fatigue',
            'Loss of taste/smell',
            'Difficulty breathing',
            'Nausea',
            'None of the above'
        ],
        next: conversationSteps.ADDITIONAL_INFO
    },

    [conversationSteps.ADDITIONAL_INFO]: {
        message: "Let me analyze your symptoms...",
        type: 'analysis',
        next: conversationSteps.ANALYSIS
    }
};

// Simple symptom matching logic
export const analyzeSymptoms = (userInputs) => {
    const { primarySymptoms, severity, duration, additionalSymptoms } = userInputs;

    // Simple scoring system
    const conditions = {
        'COVID-19': 0,
        'Flu': 0,
        'Cold': 0,
        'Allergy': 0
    };

    // Basic keyword matching (you'll replace with database queries)
    if (primarySymptoms.includes('Fever and body aches')) {
        conditions['Flu'] += 0.6;
        conditions['COVID-19'] += 0.4;
    }

    if (primarySymptoms.includes('Runny nose and sneezing')) {
        conditions['Cold'] += 0.7;
        conditions['Allergy'] += 0.5;
    }

    if (additionalSymptoms.includes('Loss of taste/smell')) {
        conditions['COVID-19'] += 0.8;
    }

    if (additionalSymptoms.includes('Difficulty breathing')) {
        conditions['COVID-19'] += 0.6;
        conditions['Flu'] += 0.3;
    }

    // Severity adjustment
    if (severity >= 7) {
        Object.keys(conditions).forEach(key => {
            if (conditions[key] > 0) conditions[key] += 0.2;
        });
    }

    // Find most likely condition
    const sortedConditions = Object.entries(conditions)
        .sort(([,a], [,b]) => b - a)
        .filter(([,score]) => score > 0);

    return {
        mostLikely: sortedConditions[0] || ['Unknown', 0],
        allScores: sortedConditions,
        recommendation: getRecommendation(sortedConditions[0])
    };
};

const getRecommendation = (topCondition) => {
    if (!topCondition) return { specialist: 'General Practitioner', urgency: 'LOW' };

    const [condition, score] = topCondition;

    const recommendations = {
        'COVID-19': { specialist: 'General Practitioner', urgency: 'HIGH', note: 'Get tested immediately' },
        'Flu': { specialist: 'General Practitioner', urgency: 'MEDIUM', note: 'Rest and monitor symptoms' },
        'Cold': { specialist: 'General Practitioner', urgency: 'LOW', note: 'Rest and home remedies' },
        'Allergy': { specialist: 'Allergist', urgency: 'LOW', note: 'Consider allergy testing' }
    };

    return recommendations[condition] || { specialist: 'General Practitioner', urgency: 'MEDIUM' };
};