// Fixed ChatbotFlow.js - Backend Integration
// fe/src/components/Chatbot/ChatbotFlow.js

import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api/medical/chatbot';

// Enhanced conversation steps with conditional logic
export const conversationSteps = {
    GREETING: 'greeting',
    PRIMARY_SYMPTOMS: 'primary_symptoms',
    SYMPTOM_DETAILS: 'symptom_details',
    SEVERITY: 'severity',
    DURATION: 'duration',
    FOLLOW_UP_QUESTIONS: 'follow_up_questions',
    DIFFERENTIAL_QUESTIONS: 'differential_questions',
    ADDITIONAL_INFO: 'additional_info',
    ANALYSIS: 'analysis'
};

// Knowledge base cache
let knowledgeBase = null;

// Load knowledge base from backend
export const loadKnowledgeBase = async () => {
    try {
        console.log('Loading knowledge base from:', `${API_BASE_URL}/knowledge/`);
        const response = await axios.get(`${API_BASE_URL}/knowledge/`, {
            timeout: 10000 // 10 second timeout
        });

        console.log('Knowledge base loaded:', response.data);
        knowledgeBase = response.data;
        return knowledgeBase;
    } catch (error) {
        console.error('Failed to load knowledge base:', error);
        // Fallback to mock data for development
        const fallbackKB = getFallbackKnowledgeBase();
        knowledgeBase = fallbackKB;
        return fallbackKB;
    }
};

// Fallback knowledge base for development
const getFallbackKnowledgeBase = () => {
    return {
        conditions: {
            flu: {
                name: 'Influenza (Flu)',
                symptoms: ['fever', 'body aches', 'fatigue', 'chills', 'headache']
            },
            cold: {
                name: 'Common Cold',
                symptoms: ['runny nose', 'sneezing', 'sore throat', 'congestion']
            },
            covid: {
                name: 'COVID-19',
                symptoms: ['loss of taste', 'loss of smell', 'cough', 'fever', 'shortness of breath']
            },
            allergy: {
                name: 'Allergic Reaction',
                symptoms: ['sneezing', 'itchy eyes', 'runny nose', 'watery eyes']
            }
        },
        symptoms: ['fever', 'cough', 'runny nose', 'sneezing', 'body aches', 'fatigue', 'sore throat']
    };
};

// Smart question generation based on previous answers
export const generateSmartQuestions = (currentStep, userInputs) => {
    const questions = {
        [conversationSteps.GREETING]: {
            message: "Hello! I'm your medical assistant. I'll help you understand your symptoms. Let's start with your main concern - what symptoms are you experiencing?",
            type: 'multiple_choice',
            options: [
                'Fever and body aches',
                'Runny nose and sneezing',
                'Cough and sore throat',
                'Loss of taste or smell',
                'Breathing difficulties',
                'Skin irritation or rash',
                'Multiple symptoms'
            ],
            next: conversationSteps.PRIMARY_SYMPTOMS
        },

        [conversationSteps.PRIMARY_SYMPTOMS]: {
            message: generateSymptomDetailsMessage(userInputs),
            type: 'checkbox',
            options: generateSymptomDetailsOptions(userInputs),
            next: conversationSteps.SYMPTOM_DETAILS
        },

        [conversationSteps.SYMPTOM_DETAILS]: {
            message: "How severe are your symptoms on a scale of 1-10? (1 = very mild, 10 = severe)",
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
                'More than a week',
                'On and off for weeks/months'
            ],
            next: conversationSteps.DURATION
        },

        [conversationSteps.DURATION]: {
            message: generateFollowUpMessage(userInputs),
            type: 'multiple_choice',
            options: generateFollowUpOptions(userInputs),
            next: conversationSteps.FOLLOW_UP_QUESTIONS
        },

        [conversationSteps.FOLLOW_UP_QUESTIONS]: {
            message: generateDifferentialMessage(userInputs),
            type: 'checkbox',
            options: generateDifferentialOptions(userInputs),
            next: conversationSteps.DIFFERENTIAL_QUESTIONS
        },

        [conversationSteps.DIFFERENTIAL_QUESTIONS]: {
            message: "Any other symptoms or information you'd like to mention?",
            type: 'text',
            next: conversationSteps.ANALYSIS
        },

        [conversationSteps.ADDITIONAL_INFO]: {
            message: "Thank you for the detailed information. Let me analyze your symptoms now.",
            type: 'none',
            next: conversationSteps.ANALYSIS
        }
    };

    return questions[currentStep] || questions[conversationSteps.GREETING];
};

// Generate symptom details message based on primary symptoms
const generateSymptomDetailsMessage = (inputs) => {
    const primarySymptoms = inputs[conversationSteps.PRIMARY_SYMPTOMS] || inputs.primary_symptoms;

    if (!primarySymptoms) {
        return "Let's get more specific about your symptoms. Which of these are you experiencing?";
    }

    if (Array.isArray(primarySymptoms) && primarySymptoms.length > 0) {
        const symptomText = primarySymptoms[0];

        if (symptomText.includes('Fever')) {
            return "You mentioned fever and body aches. Please select all specific symptoms you're experiencing:";
        } else if (symptomText.includes('Runny nose')) {
            return "You mentioned runny nose and sneezing. Please select all specific symptoms you're experiencing:";
        } else if (symptomText.includes('Cough')) {
            return "You mentioned cough and sore throat. Please select all specific symptoms you're experiencing:";
        } else if (symptomText.includes('Loss of taste')) {
            return "You mentioned loss of taste or smell. Please select all specific symptoms you're experiencing:";
        }
    }

    return "Please select all the specific symptoms you're currently experiencing:";
};

// Generate symptom details options based on primary symptoms
const generateSymptomDetailsOptions = (inputs) => {
    const primarySymptoms = inputs[conversationSteps.PRIMARY_SYMPTOMS] || inputs.primary_symptoms;

    const allSymptoms = [
        'High fever (over 101°F/38.3°C)',
        'Low-grade fever',
        'Severe body aches',
        'Mild body aches',
        'Extreme fatigue',
        'Mild tiredness',
        'Dry cough',
        'Wet cough with phlegm',
        'Severe sore throat',
        'Mild throat irritation',
        'Runny nose (clear)',
        'Runny nose (colored)',
        'Frequent sneezing',
        'Occasional sneezing',
        'Complete loss of taste',
        'Reduced taste',
        'Complete loss of smell',
        'Reduced smell',
        'Shortness of breath',
        'Chest tightness',
        'Headache',
        'Chills or sweats',
        'Nausea or vomiting',
        'Itchy, watery eyes',
        'Skin rash or hives'
    ];

    // Filter based on primary symptoms if available
    if (primarySymptoms && Array.isArray(primarySymptoms) && primarySymptoms.length > 0) {
        const symptomText = primarySymptoms[0].toLowerCase();

        if (symptomText.includes('fever')) {
            return [
                'High fever (over 101°F/38.3°C)',
                'Low-grade fever',
                'Severe body aches',
                'Mild body aches',
                'Extreme fatigue',
                'Chills or sweats',
                'Headache',
                'Dry cough',
                'Sore throat'
            ];
        } else if (symptomText.includes('runny')) {
            return [
                'Runny nose (clear)',
                'Runny nose (colored)',
                'Frequent sneezing',
                'Itchy, watery eyes',
                'Mild throat irritation',
                'Post-nasal drip',
                'Facial pressure',
                'Low-grade fever'
            ];
        } else if (symptomText.includes('cough')) {
            return [
                'Dry cough',
                'Wet cough with phlegm',
                'Severe sore throat',
                'Mild throat irritation',
                'Hoarse voice',
                'Chest tightness',
                'Low-grade fever',
                'Runny nose'
            ];
        } else if (symptomText.includes('loss')) {
            return [
                'Complete loss of taste',
                'Reduced taste',
                'Complete loss of smell',
                'Reduced smell',
                'Dry cough',
                'Shortness of breath',
                'Fever',
                'Fatigue',
                'Sore throat'
            ];
        }
    }

    return allSymptoms.slice(0, 12); // Return first 12 as default
};

// Generate follow-up message based on inputs
const generateFollowUpMessage = (inputs) => {
    const severity = inputs[conversationSteps.SEVERITY] || inputs.severity || 5;

    if (severity >= 8) {
        return "Your symptoms seem quite severe. Have you experienced any of these concerning symptoms?";
    } else if (severity >= 6) {
        return "Your symptoms are moderate. Let me ask about some additional concerns:";
    } else {
        return "Your symptoms seem mild. Let me ask about a few more things:";
    }
};

// Generate follow-up options based on severity and symptoms
const generateFollowUpOptions = (inputs) => {
    const severity = inputs[conversationSteps.SEVERITY] || inputs.severity || 5;
    const symptoms = inputs[conversationSteps.SYMPTOM_DETAILS] || inputs.symptom_details || [];

    const baseOptions = [
        'No other concerns',
        'Recent travel',
        'Contact with sick people',
        'Taking any medications',
        'Chronic health conditions'
    ];

    if (severity >= 8) {
        return [
            'Difficulty breathing',
            'Chest pain',
            'Persistent high fever',
            'Severe dehydration',
            'Confusion or dizziness',
            ...baseOptions
        ];
    } else if (severity >= 6) {
        return [
            'Worsening symptoms',
            'Difficulty sleeping',
            'Decreased appetite',
            'Mild breathing issues',
            ...baseOptions
        ];
    }

    return baseOptions;
};

// Generate differential diagnosis questions
const generateDifferentialMessage = (inputs) => {
    const symptoms = inputs[conversationSteps.SYMPTOM_DETAILS] || inputs.symptom_details || [];
    const symptomText = symptoms.join(' ').toLowerCase();

    if (symptomText.includes('fever') && symptomText.includes('cough')) {
        return "To help distinguish between similar conditions, which of these apply to you?";
    } else if (symptomText.includes('runny') && symptomText.includes('sneezing')) {
        return "To better understand if this might be allergies or a cold:";
    } else {
        return "A few final questions to help with the analysis:";
    }
};

// Generate differential diagnosis options
const generateDifferentialOptions = (inputs) => {
    const symptoms = inputs[conversationSteps.SYMPTOM_DETAILS] || inputs.symptom_details || [];
    const symptomText = symptoms.join(' ').toLowerCase();

    if (symptomText.includes('fever') && symptomText.includes('cough')) {
        return [
            'Symptoms came on suddenly',
            'Symptoms came on gradually',
            'Had close contact with COVID-19 case',
            'Seasonal pattern to symptoms',
            'Symptoms worse at certain times of day'
        ];
    } else if (symptomText.includes('runny') && symptomText.includes('sneezing')) {
        return [
            'Symptoms worse outdoors',
            'Symptoms worse indoors',
            'Symptoms year-round',
            'Symptoms only certain seasons',
            'Eyes are very itchy',
            'Symptoms improved with antihistamines'
        ];
    }

    return [
        'Symptoms getting worse',
        'Symptoms staying the same',
        'Symptoms improving',
        'Had similar symptoms before',
        'Family members also sick'
    ];
};

// Enhanced symptom analysis with backend integration
export const analyzeSymptoms = async (userInputs, sessionId = null) => {
    try {
        console.log('Starting symptom analysis:', userInputs);

        // Prepare analysis data
        const analysisData = {
            conversation_step: 'analysis',
            user_inputs: userInputs,
            session_id: sessionId || generateSessionId(),
            timestamp: new Date().toISOString()
        };

        console.log('Sending analysis request:', analysisData);

        // Try backend analysis first
        try {
            const response = await axios.post(`${API_BASE_URL}/analyze/`, analysisData, {
                timeout: 30000, // 30 second timeout
                headers: {
                    'Content-Type': 'application/json',
                }
            });

            console.log('Backend analysis response:', response.data);

            // Handle different response formats
            if (response.data.analysis) {
                return {
                    success: true,
                    data: response.data.analysis,
                    sessionId: response.data.session_id,
                    backend: true
                };
            } else {
                return {
                    success: true,
                    data: response.data,
                    sessionId: response.data.session_id || sessionId,
                    backend: true
                };
            }

        } catch (apiError) {
            console.warn('Backend analysis failed, using fallback:', apiError);

            // Check if it's a network error or server error
            if (apiError.response && apiError.response.status >= 500) {
                console.log('Server error, trying fallback analysis');
            } else if (apiError.code === 'ECONNREFUSED') {
                console.log('Connection refused, backend may be down');
            }

            return await performFallbackAnalysis(userInputs);
        }

    } catch (error) {
        console.error('Analysis failed completely:', error);
        return await performFallbackAnalysis(userInputs);
    }
};

// Fallback analysis when backend is unavailable
const performFallbackAnalysis = async (userInputs) => {
    console.log('Performing client-side fallback analysis');

    // Simple client-side analysis
    const conditions = {
        'COVID-19': 0,
        'Influenza (Flu)': 0,
        'Common Cold': 0,
        'Allergic Reaction': 0
    };

    // Extract all symptoms from user inputs
    const allSymptoms = extractAllSymptoms(userInputs).join(' ').toLowerCase();
    console.log('All symptoms for analysis:', allSymptoms);

    // COVID-19 indicators
    if (allSymptoms.includes('loss of taste') || allSymptoms.includes('loss of smell')) {
        conditions['COVID-19'] += 0.8;
    }
    if (allSymptoms.includes('shortness of breath') || allSymptoms.includes('breathing')) {
        conditions['COVID-19'] += 0.7;
    }
    if (allSymptoms.includes('dry cough')) {
        conditions['COVID-19'] += 0.6;
    }
    if (allSymptoms.includes('fever')) {
        conditions['COVID-19'] += 0.4;
    }

    // Flu indicators
    if (allSymptoms.includes('high fever') || allSymptoms.includes('severe body aches')) {
        conditions['Influenza (Flu)'] += 0.8;
    }
    if (allSymptoms.includes('extreme fatigue')) {
        conditions['Influenza (Flu)'] += 0.7;
    }
    if (allSymptoms.includes('chills') || allSymptoms.includes('sweats')) {
        conditions['Influenza (Flu)'] += 0.6;
    }
    if (allSymptoms.includes('body aches') || allSymptoms.includes('headache')) {
        conditions['Influenza (Flu)'] += 0.5;
    }

    // Cold indicators
    if (allSymptoms.includes('runny nose') || allSymptoms.includes('nasal')) {
        conditions['Common Cold'] += 0.8;
    }
    if (allSymptoms.includes('sneezing')) {
        conditions['Common Cold'] += 0.7;
    }
    if (allSymptoms.includes('sore throat') || allSymptoms.includes('throat')) {
        conditions['Common Cold'] += 0.6;
    }
    if (allSymptoms.includes('mild') || allSymptoms.includes('low-grade fever')) {
        conditions['Common Cold'] += 0.4;
    }

    // Allergy indicators
    if (allSymptoms.includes('itchy') || allSymptoms.includes('watery eyes')) {
        conditions['Allergic Reaction'] += 0.9;
    }
    if (allSymptoms.includes('frequent sneezing')) {
        conditions['Allergic Reaction'] += 0.8;
    }
    if (allSymptoms.includes('clear') && allSymptoms.includes('runny nose')) {
        conditions['Allergic Reaction'] += 0.7;
    }
    if (allSymptoms.includes('seasonal') || allSymptoms.includes('outdoors')) {
        conditions['Allergic Reaction'] += 0.6;
    }

    // Severity adjustments
    const severity = userInputs.severity || 5;
    if (severity <= 3) {
        conditions['Allergic Reaction'] *= 1.2;
        conditions['Common Cold'] *= 1.1;
    } else if (severity >= 8) {
        conditions['COVID-19'] *= 1.2;
        conditions['Influenza (Flu)'] *= 1.1;
    }

    // Find most likely conditions
    const sortedConditions = Object.entries(conditions)
        .sort(([,a], [,b]) => b - a)
        .filter(([,score]) => score > 0)
        .map(([condition, score]) => [condition, Math.min(score, 1.0)]); // Cap at 100%

    console.log('Fallback analysis results:', sortedConditions);

    if (sortedConditions.length === 0) {
        return {
            success: false,
            error: 'Unable to analyze symptoms',
            fallback: true
        };
    }

    // Determine urgency
    let urgency = 'LOW';
    if (severity >= 8 || allSymptoms.includes('breathing') || allSymptoms.includes('chest')) {
        urgency = 'HIGH';
    } else if (severity >= 6 || allSymptoms.includes('high fever')) {
        urgency = 'MEDIUM';
    }

    return {
        success: true,
        data: {
            conditions: sortedConditions,
            mostLikely: sortedConditions,
            urgency: urgency,
            urgencyLevel: urgency,
            recommendations: {
                specialist: urgency === 'HIGH' ? 'Emergency Room' :
                    urgency === 'MEDIUM' ? 'Primary Care Physician' :
                        'Healthcare Provider',
                message: urgency === 'HIGH' ?
                    'Your symptoms suggest you should seek immediate medical attention.' :
                    'Please consider consulting a healthcare provider for proper evaluation.',
                action: urgency === 'HIGH' ? 'Seek immediate care' : 'Schedule appointment'
            },
            confidence: sortedConditions.length > 0 ? sortedConditions[0][1] : 0,
            fallback: true
        },
        sessionId: generateSessionId(),
        backend: false
    };
};

// Extract all symptoms from user inputs
const extractAllSymptoms = (userInputs) => {
    const allSymptoms = [];

    Object.values(userInputs).forEach(value => {
        if (Array.isArray(value)) {
            allSymptoms.push(...value);
        } else if (typeof value === 'string') {
            allSymptoms.push(value);
        }
    });

    return allSymptoms;
};

// Generate session ID
const generateSessionId = () => {
    return Date.now().toString(36) + Math.random().toString(36).substr(2);
};

export default {
    conversationSteps,
    generateSmartQuestions,
    analyzeSymptoms,
    loadKnowledgeBase
};