// fe/src/components/Chatbot/ChatbotFlow.js - Complete Fixed Version
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api/medical/chatbot';

// Enhanced conversation steps with conditional logic
// fe/src/components/Chatbot/ChatbotFlow.js - Complete Enhanced Version

export const conversationSteps = {
    GREETING: 'greeting',
    PRIMARY_SYMPTOMS: 'primary_symptoms',
    SEVERITY: 'severity',
    DURATION: 'duration',
    FEVER_CHECK: 'fever_check',
    RESPIRATORY_SYMPTOMS: 'respiratory_symptoms',
    BODY_SYMPTOMS: 'body_symptoms',
    ADDITIONAL_SYMPTOMS: 'additional_symptoms',
    ANALYSIS: 'analysis'
};

// Knowledge base for the 4 conditions
const conditionsKnowledgeBase = {
    flu: {
        name: 'Influenza (Flu)',
        primarySymptoms: ['fever', 'body_aches', 'fatigue', 'chills', 'headache'],
        secondarySymptoms: ['dry_cough', 'sore_throat', 'nasal_congestion', 'muscle_pain'],
        severity: 'moderate',
        urgency: 'routine',
        specialist: 'General Practitioner',
        note: 'Rest, fluids, and over-the-counter medications can help. Antiviral medications may be prescribed if caught early.'
    },
    cold: {
        name: 'Common Cold',
        primarySymptoms: ['runny_nose', 'sneezing', 'sore_throat', 'nasal_congestion'],
        secondarySymptoms: ['mild_cough', 'low_grade_fever', 'mild_headache', 'fatigue'],
        severity: 'mild',
        urgency: 'routine',
        specialist: 'General Practitioner',
        note: 'Rest, fluids, and symptom management. Usually resolves on its own in 7-10 days.'
    },
    covid: {
        name: 'COVID-19',
        primarySymptoms: ['fever', 'dry_cough', 'loss_of_taste', 'loss_of_smell', 'shortness_of_breath'],
        secondarySymptoms: ['fatigue', 'body_aches', 'sore_throat', 'headache', 'diarrhea'],
        severity: 'moderate',
        urgency: 'moderate',
        specialist: 'General Practitioner or Infectious Disease Specialist',
        note: 'Get tested and isolate. Monitor symptoms closely. Seek immediate care if breathing difficulties occur.'
    },
    allergy: {
        name: 'Allergic Reaction',
        primarySymptoms: ['sneezing', 'itchy_eyes', 'watery_eyes', 'runny_nose', 'itchy_throat'],
        secondarySymptoms: ['nasal_congestion', 'skin_rash', 'hives', 'wheezing'],
        severity: 'mild',
        urgency: 'routine',
        specialist: 'Allergist or General Practitioner',
        note: 'Identify and avoid triggers. Antihistamines and other allergy medications can provide relief.'
    }
};

// Symptom mapping for analysis
const symptomMapping = {
    // Fever related
    'High fever (>101°F/38.3°C)': 'fever',
    'Low-grade fever': 'low_grade_fever',
    'Chills and shivering': 'chills',

    // Respiratory
    'Dry cough': 'dry_cough',
    'Productive cough': 'productive_cough',
    'Sore throat': 'sore_throat',
    'Runny nose': 'runny_nose',
    'Stuffy/blocked nose': 'nasal_congestion',
    'Shortness of breath': 'shortness_of_breath',
    'Wheezing': 'wheezing',

    // Body symptoms
    'Severe body aches': 'body_aches',
    'Muscle pain': 'muscle_pain',
    'Headache': 'headache',
    'Extreme fatigue': 'fatigue',
    'Mild tiredness': 'mild_fatigue',

    // Sensory
    'Loss of taste': 'loss_of_taste',
    'Loss of smell': 'loss_of_smell',

    // Allergic symptoms
    'Itchy, watery eyes': 'itchy_eyes',
    'Frequent sneezing': 'sneezing',
    'Itchy throat': 'itchy_throat',
    'Skin rash or hives': 'skin_rash',

    // Other
    'Nausea or vomiting': 'nausea',
    'Diarrhea': 'diarrhea',
    'None of the above': 'none'
};

export const chatbotQuestions = {
    [conversationSteps.GREETING]: {
        message: "Hello! I'm your medical assistant. I'll help you understand your symptoms for flu, cold, COVID-19, or allergies. \n\n⚠️ **Important:** This is not a medical diagnosis. Always consult a healthcare professional for proper medical advice.\n\nLet's start - what are your main symptoms?",
        type: 'multiple_choice',
        options: [
            'Fever and body aches',
            'Runny nose and sneezing',
            'Cough and breathing issues',
            'Eye/nose itching and allergic symptoms',
            'Multiple different symptoms'
        ],
        next: conversationSteps.PRIMARY_SYMPTOMS
    },

    [conversationSteps.PRIMARY_SYMPTOMS]: {
        message: "Please select all symptoms you're currently experiencing:",
        type: 'checkbox',
        options: [
            'High fever (>101°F/38.3°C)',
            'Low-grade fever',
            'Chills and shivering',
            'Dry cough',
            'Productive cough',
            'Sore throat',
            'Runny nose',
            'Stuffy/blocked nose',
            'Shortness of breath',
            'Severe body aches',
            'Muscle pain',
            'Headache',
            'Extreme fatigue',
            'Loss of taste',
            'Loss of smell',
            'Itchy, watery eyes',
            'Frequent sneezing',
            'Skin rash or hives'
        ],
        next: conversationSteps.SEVERITY
    },

    [conversationSteps.SEVERITY]: {
        message: "On a scale of 1-10, how would you rate the overall severity of your symptoms? \n(1 = very mild, 10 = severe)",
        type: 'scale',
        min: 1,
        max: 10,
        next: conversationSteps.DURATION
    },

    [conversationSteps.DURATION]: {
        message: "How long have you been experiencing these symptoms?",
        type: 'multiple_choice',
        options: [
            'Less than 24 hours',
            '1-2 days',
            '3-5 days',
            '6-7 days',
            'More than a week',
            'More than 2 weeks'
        ],
        next: conversationSteps.FEVER_CHECK
    },

    [conversationSteps.FEVER_CHECK]: {
        message: "If you have fever, what's your temperature range?",
        type: 'multiple_choice',
        options: [
            'No fever',
            '99-100°F (37.2-37.8°C)',
            '100-102°F (37.8-38.9°C)',
            '102-104°F (38.9-40°C)',
            'Above 104°F (40°C)',
            'Haven\'t measured'
        ],
        next: conversationSteps.ADDITIONAL_SYMPTOMS
    },

    [conversationSteps.ADDITIONAL_SYMPTOMS]: {
        message: "Any additional symptoms or concerns you'd like to mention?",
        type: 'checkbox',
        options: [
            'Nausea or vomiting',
            'Diarrhea',
            'Wheezing',
            'Chest pain',
            'Difficulty concentrating',
            'Sleep problems',
            'Appetite loss',
            'Joint pain',
            'Skin irritation',
            'None of the above'
        ],
        next: conversationSteps.ANALYSIS
    }
};

// Enhanced symptom analysis function
export const analyzeSymptoms = (userInputs) => {
    try {
        console.log('Analyzing symptoms with inputs:', userInputs);

        // Extract and normalize symptoms
        const reportedSymptoms = extractSymptoms(userInputs);
        const severity = userInputs[conversationSteps.SEVERITY] || 5;
        const duration = userInputs[conversationSteps.DURATION] || '';
        const feverInfo = userInputs[conversationSteps.FEVER_CHECK] || '';

        console.log('Extracted symptoms:', reportedSymptoms);

        // Calculate probability for each condition
        const probabilities = calculateProbabilities(reportedSymptoms, severity, duration, feverInfo);

        // Sort conditions by probability
        const sortedConditions = Object.entries(probabilities)
            .sort(([,a], [,b]) => b - a)
            .filter(([,prob]) => prob > 0.1); // Only include conditions with >10% probability

        if (sortedConditions.length === 0) {
            return {
                mostLikely: ['Unknown condition', 0.5],
                otherConditions: [],
                recommendation: {
                    specialist: 'healthcare professional',
                    urgency: 'routine',
                    note: 'Your symptoms don\'t clearly match common conditions. Please consult a healthcare professional for proper evaluation.'
                }
            };
        }

        const [topCondition, topProbability] = sortedConditions[0];
        const otherConditions = sortedConditions.slice(1, 3); // Top 2 other conditions

        // Determine urgency based on symptoms and severity
        const urgency = determineUrgency(reportedSymptoms, severity, feverInfo);

        const conditionInfo = conditionsKnowledgeBase[topCondition];

        return {
            mostLikely: [conditionInfo.name, topProbability],
            otherConditions: otherConditions.map(([cond, prob]) => [conditionsKnowledgeBase[cond].name, prob]),
            recommendation: {
                specialist: conditionInfo.specialist,
                urgency: urgency,
                note: conditionInfo.note
            },
            confidence: topProbability,
            severityScore: severity
        };

    } catch (error) {
        console.error('Error in symptom analysis:', error);
        return {
            mostLikely: ['Analysis Error', 0.5],
            otherConditions: [],
            recommendation: {
                specialist: 'healthcare professional',
                urgency: 'routine',
                note: 'There was an error analyzing your symptoms. Please consult a healthcare professional.'
            }
        };
    }
};

// Extract symptoms from user inputs
const extractSymptoms = (userInputs) => {
    const symptoms = new Set();

    // Process primary symptoms
    const primarySymptoms = userInputs[conversationSteps.PRIMARY_SYMPTOMS] || [];
    const additionalSymptoms = userInputs[conversationSteps.ADDITIONAL_SYMPTOMS] || [];

    // Convert symptoms to normalized keys
    [...primarySymptoms, ...additionalSymptoms].forEach(symptom => {
        if (typeof symptom === 'string' && symptomMapping[symptom]) {
            symptoms.add(symptomMapping[symptom]);
        }
    });

    return Array.from(symptoms);
};

// Calculate probabilities for each condition
const calculateProbabilities = (symptoms, severity, duration, feverInfo) => {
    const probabilities = {};

    Object.keys(conditionsKnowledgeBase).forEach(condition => {
        probabilities[condition] = calculateConditionProbability(
            condition,
            symptoms,
            severity,
            duration,
            feverInfo
        );
    });

    return probabilities;
};

// Calculate probability for a specific condition
const calculateConditionProbability = (condition, symptoms, severity, duration, feverInfo) => {
    const conditionData = conditionsKnowledgeBase[condition];
    let probability = 0;
    let totalPossible = 0;

    // Check primary symptoms (higher weight)
    conditionData.primarySymptoms.forEach(symptom => {
        totalPossible += 0.3; // Each primary symptom worth 30%
        if (symptoms.includes(symptom)) {
            probability += 0.3;
        }
    });

    // Check secondary symptoms (lower weight)
    conditionData.secondarySymptoms.forEach(symptom => {
        totalPossible += 0.1; // Each secondary symptom worth 10%
        if (symptoms.includes(symptom)) {
            probability += 0.1;
        }
    });

    // Adjust based on severity
    if (severity >= 7 && conditionData.severity === 'moderate') {
        probability += 0.1;
    } else if (severity <= 4 && conditionData.severity === 'mild') {
        probability += 0.1;
    }

    // Adjust based on duration
    if (duration.includes('Less than 24') && condition === 'flu') {
        probability += 0.05; // Flu can onset rapidly
    } else if (duration.includes('More than a week') && condition === 'cold') {
        probability -= 0.1; // Colds usually resolve faster
    }

    // Fever-specific adjustments
    if (feverInfo.includes('102-104') && (condition === 'flu' || condition === 'covid')) {
        probability += 0.15;
    } else if (feverInfo.includes('No fever') && condition === 'allergy') {
        probability += 0.1;
    }

    // Special symptom combinations
    if (symptoms.includes('loss_of_taste') || symptoms.includes('loss_of_smell')) {
        if (condition === 'covid') {
            probability += 0.3; // Strong indicator for COVID
        } else {
            probability -= 0.1; // Less likely for other conditions
        }
    }

    if (symptoms.includes('itchy_eyes') && symptoms.includes('sneezing')) {
        if (condition === 'allergy') {
            probability += 0.2; // Strong indicator for allergies
        }
    }

    // Normalize probability
    return Math.min(Math.max(probability, 0), 1);
};

// Determine urgency level
const determineUrgency = (symptoms, severity, feverInfo) => {
    // High urgency conditions
    if (symptoms.includes('shortness_of_breath') ||
        feverInfo.includes('Above 104°F') ||
        severity >= 9) {
        return 'urgent';
    }

    // Moderate urgency
    if (severity >= 7 ||
        feverInfo.includes('102-104°F') ||
        (symptoms.includes('loss_of_taste') && symptoms.includes('loss_of_smell'))) {
        return 'moderate';
    }

    // Routine care
    return 'routine';
};

// Validation functions
export const validateUserInput = (step, input) => {
    if (!input || (Array.isArray(input) && input.length === 0)) {
        return { isValid: false, error: 'Please provide an answer to continue.' };
    }

    switch (step) {
        case conversationSteps.SEVERITY:
            const severity = parseInt(input);
            if (isNaN(severity) || severity < 1 || severity > 10) {
                return { isValid: false, error: 'Please select a number between 1 and 10.' };
            }
            break;

        case conversationSteps.PRIMARY_SYMPTOMS:
            if (Array.isArray(input) && input.length === 0) {
                return { isValid: false, error: 'Please select at least one symptom.' };
            }
            break;
    }

    return { isValid: true };
};

export default {
    conversationSteps,
    chatbotQuestions,
    analyzeSymptoms,
    validateUserInput
};