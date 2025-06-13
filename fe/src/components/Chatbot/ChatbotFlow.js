// Fixed ChatbotFlow.js - ESLint Warnings Fix
// fe/src/components/Chatbot/ChatbotFlow.js - Phase 2

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
// REMOVED: let symptomsIndex = null; (unused variable)

// Load knowledge base from backend
export const loadKnowledgeBase = async () => {
    try {
        const response = await axios.get(`${API_BASE_URL}/knowledge/`);
        knowledgeBase = response.data;
        // REMOVED: symptomsIndex = response.data.symptoms; (unused variable)
        return knowledgeBase;
    } catch (error) {
        console.error('Failed to load knowledge base:', error);
        // Fallback to mock data for development
        return getFallbackKnowledgeBase();
    }
};

// Fallback knowledge base for development
const getFallbackKnowledgeBase = () => {
    return {
        conditions: {
            flu: { name: 'Flu', symptoms: ['fever', 'body aches', 'fatigue'] },
            cold: { name: 'Cold', symptoms: ['runny nose', 'sneezing', 'sore throat'] },
            covid: { name: 'COVID-19', symptoms: ['loss of taste', 'loss of smell', 'cough'] },
            allergy: { name: 'Allergy', symptoms: ['sneezing', 'itchy eyes', 'runny nose'] }
        },
        symptoms: ['fever', 'cough', 'runny nose', 'sneezing', 'body aches']
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
                '1-2 days',
                '3-5 days',
                '6-7 days',
                'More than a week',
                'More than 2 weeks'
            ],
            next: conversationSteps.DURATION
        },

        [conversationSteps.DURATION]: {
            message: generateFollowUpMessage(userInputs),
            type: 'checkbox',
            options: generateFollowUpOptions(userInputs),
            next: conversationSteps.FOLLOW_UP_QUESTIONS
        },

        [conversationSteps.FOLLOW_UP_QUESTIONS]: {
            message: generateDifferentialMessage(userInputs),
            type: 'multiple_choice',
            options: generateDifferentialOptions(userInputs),
            next: conversationSteps.DIFFERENTIAL_QUESTIONS
        },

        [conversationSteps.DIFFERENTIAL_QUESTIONS]: {
            message: "Any other symptoms or concerns you'd like to mention?",
            type: 'checkbox',
            options: [
                'Fatigue or weakness',
                'Headache',
                'Nausea or vomiting',
                'Difficulty sleeping',
                'Changes in appetite',
                'Joint or muscle pain',
                'None of the above'
            ],
            next: conversationSteps.ADDITIONAL_INFO
        },

        [conversationSteps.ADDITIONAL_INFO]: {
            message: "Thank you for the information. Let me analyze your symptoms...",
            type: 'analysis',
            next: conversationSteps.ANALYSIS
        }
    };

    return questions[currentStep];
};

// Generate symptom details message based on primary symptoms
const generateSymptomDetailsMessage = (userInputs) => {
    const primary = userInputs.greeting || [];

    if (primary.includes('Fever and body aches')) {
        return "Let me ask more about your fever and body aches. Which of these apply to you?";
    } else if (primary.includes('Runny nose and sneezing')) {
        return "Tell me more about your nasal symptoms. Which of these are you experiencing?";
    } else if (primary.includes('Cough and sore throat')) {
        return "Let's get details about your cough and throat symptoms:";
    } else if (primary.includes('Loss of taste or smell')) {
        return "This is an important symptom. Please tell me more:";
    } else if (primary.includes('Breathing difficulties')) {
        return "Breathing issues are serious. Please describe what you're experiencing:";
    }

    return "Please select all symptoms that apply to you:";
};

// Generate symptom details options based on primary symptoms
const generateSymptomDetailsOptions = (userInputs) => {
    const primary = userInputs.greeting || [];

    if (primary.includes('Fever and body aches')) {
        return [
            'High fever (over 101°F/38.3°C)',
            'Low-grade fever',
            'Severe body aches',
            'Mild body aches',
            'Chills',
            'Sweating',
            'Headache'
        ];
    } else if (primary.includes('Runny nose and sneezing')) {
        return [
            'Clear nasal discharge',
            'Thick nasal discharge',
            'Frequent sneezing',
            'Nasal congestion',
            'Postnasal drip',
            'Itchy nose',
            'Loss of smell'
        ];
    } else if (primary.includes('Cough and sore throat')) {
        return [
            'Dry cough',
            'Productive cough with phlegm',
            'Severe sore throat',
            'Mild throat irritation',
            'Difficulty swallowing',
            'Hoarse voice',
            'Swollen glands'
        ];
    } else if (primary.includes('Loss of taste or smell')) {
        return [
            'Complete loss of taste',
            'Partial loss of taste',
            'Complete loss of smell',
            'Partial loss of smell',
            'Metallic taste',
            'Food tastes different',
            'Both taste and smell affected'
        ];
    }

    // Default options
    return [
        'Fever',
        'Cough',
        'Runny nose',
        'Sore throat',
        'Body aches',
        'Fatigue',
        'Headache'
    ];
};

// Generate follow-up message based on symptoms
const generateFollowUpMessage = (userInputs) => {
    const allSymptoms = extractAllSymptoms(userInputs);

    if (allSymptoms.some(s => s.includes('fever'))) {
        return "Since you have fever, let me ask about related symptoms:";
    } else if (allSymptoms.some(s => s.includes('cough'))) {
        return "About your cough, which of these also apply?";
    } else if (allSymptoms.some(s => s.includes('runny nose'))) {
        return "For nasal symptoms, please check any additional symptoms:";
    }

    return "Please select any additional symptoms you're experiencing:";
};

// Generate follow-up options based on symptoms
const generateFollowUpOptions = (userInputs) => {
    const allSymptoms = extractAllSymptoms(userInputs);

    if (allSymptoms.some(s => s.includes('fever'))) {
        return [
            'Night sweats',
            'Shivering',
            'Dehydration',
            'Dizziness',
            'Rapid heartbeat',
            'None of these'
        ];
    } else if (allSymptoms.some(s => s.includes('cough'))) {
        return [
            'Coughing up blood',
            'Chest pain when coughing',
            'Shortness of breath',
            'Wheezing',
            'Cough worse at night',
            'None of these'
        ];
    }

    return [
        'Fatigue or weakness',
        'Muscle aches',
        'Joint pain',
        'Skin rash',
        'Nausea',
        'None of these'
    ];
};

// Generate differential message
const generateDifferentialMessage = (userInputs) => {
    const symptoms = extractAllSymptoms(userInputs);

    if (symptoms.some(s => s.includes('fever')) && symptoms.some(s => s.includes('body aches'))) {
        return "These symptoms could indicate different conditions. Which describes your situation best?";
    } else if (symptoms.some(s => s.includes('runny nose')) && symptoms.some(s => s.includes('sneezing'))) {
        return "These symptoms could be related to different causes. Which scenario sounds most like you?";
    }

    return "To provide the most accurate assessment, please choose the option that best fits your situation:";
};

// Generate differential options to distinguish between conditions
const generateDifferentialOptions = (userInputs) => {
    const symptoms = extractAllSymptoms(userInputs);

    // Flu vs COVID vs Cold differentiation
    if (symptoms.some(s => s.includes('fever'))) {
        return [
            'Sudden onset of severe symptoms',
            'Gradual onset of symptoms',
            'Symptoms mainly affecting nose/throat',
            'Whole body feels affected',
            'Mainly respiratory symptoms',
            'Gastrointestinal symptoms too'
        ];
    }

    // Allergy vs Cold differentiation
    if (symptoms.some(s => s.includes('sneezing'))) {
        return [
            'Symptoms worse in certain environments',
            'Symptoms consistent throughout day',
            'Seasonal pattern to symptoms',
            'Recent cold exposure',
            'Itchy eyes or throat',
            'Symptoms started after being around others who were sick'
        ];
    }

    return [
        'Symptoms getting progressively worse',
        'Symptoms staying about the same',
        'Symptoms come and go',
        'Symptoms worse at certain times',
        'Symptoms affect daily activities',
        'Symptoms are manageable'
    ];
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

// Enhanced symptom analysis with backend integration
export const analyzeSymptoms = async (userInputs, sessionId = null) => {
    try {
        // Prepare analysis data
        const analysisData = {
            conversation_step: 'analysis',
            user_inputs: userInputs,
            session_id: sessionId || generateSessionId()
        };

        // Try backend analysis first
        try {
            const response = await axios.post(`${API_BASE_URL}/analyze/`, analysisData);
            return response.data;
        } catch (apiError) {
            console.warn('Backend analysis failed, using fallback:', apiError);
            return performFallbackAnalysis(userInputs);
        }

    } catch (error) {
        console.error('Analysis failed:', error);
        return performFallbackAnalysis(userInputs);
    }
};

// Fallback analysis when backend is unavailable
const performFallbackAnalysis = (userInputs) => {
    // Simple client-side analysis
    const conditions = {
        'COVID-19': 0,
        'Flu': 0,
        'Cold': 0,
        'Allergy': 0
    };

    const allSymptoms = extractAllSymptoms(userInputs).join(' ').toLowerCase();

    // COVID-19 indicators
    if (allSymptoms.includes('loss of taste') || allSymptoms.includes('loss of smell')) {
        conditions['COVID-19'] += 0.8;
    }
    if (allSymptoms.includes('shortness of breath') || allSymptoms.includes('difficulty breathing')) {
        conditions['COVID-19'] += 0.6;
    }

    // Flu indicators
    if (allSymptoms.includes('high fever') && allSymptoms.includes('body aches')) {
        conditions['Flu'] += 0.7;
    }
    if (allSymptoms.includes('sudden onset')) {
        conditions['Flu'] += 0.5;
    }

    // Cold indicators
    if (allSymptoms.includes('runny nose') && allSymptoms.includes('sneezing')) {
        conditions['Cold'] += 0.6;
    }
    if (allSymptoms.includes('gradual onset')) {
        conditions['Cold'] += 0.4;
    }

    // Allergy indicators
    if (allSymptoms.includes('itchy') || allSymptoms.includes('seasonal')) {
        conditions['Allergy'] += 0.7;
    }

    // Severity adjustment
    const severity = userInputs.severity || 5;
    if (severity >= 8) {
        Object.keys(conditions).forEach(key => {
            if (conditions[key] > 0 && key !== 'Allergy') {
                conditions[key] += 0.2;
            }
        });
    }

    const sortedConditions = Object.entries(conditions)
        .sort(([,a], [,b]) => b - a)
        .filter(([,score]) => score > 0)
        .map(([name, confidence]) => ({ name, confidence }));

    return {
        success: true,
        mostLikely: sortedConditions[0] || { name: 'Unknown', confidence: 0 },
        allConditions: sortedConditions,
        recommendations: getFallbackRecommendations(sortedConditions[0]),
        urgency: severity >= 8 ? 'HIGH' : 'MEDIUM',
        disclaimers: [
            'This is a fallback analysis. Please consult a healthcare provider for proper diagnosis.',
            'If symptoms are severe or persistent, seek immediate medical attention.'
        ]
    };
};

// Get fallback recommendations
const getFallbackRecommendations = (condition) => {
    if (!condition) {
        return {
            action: 'Consult a healthcare provider',
            note: 'Unable to determine condition from symptoms'
        };
    }

    const recommendations = {
        'COVID-19': {
            action: 'Isolate and contact healthcare provider',
            note: 'Consider COVID-19 testing. Monitor symptoms closely.'
        },
        'Flu': {
            action: 'Rest, fluids, and monitor symptoms',
            note: 'Consider antiviral medication if caught early. Seek care if symptoms worsen.'
        },
        'Cold': {
            action: 'Rest and supportive care',
            note: 'Stay hydrated, use throat lozenges, get plenty of rest.'
        },
        'Allergy': {
            action: 'Avoid triggers and consider antihistamines',
            note: 'Identify and avoid allergens. Consider over-the-counter allergy medication.'
        }
    };

    return recommendations[condition.name] || {
        action: 'Consult a healthcare provider',
        note: 'Please seek professional medical advice for proper diagnosis.'
    };
};

// Validate symptoms against knowledge base
export const validateSymptoms = async (userInputs) => {
    try {
        if (!knowledgeBase) {
            await loadKnowledgeBase();
        }

        // Simple validation - check if symptoms exist in knowledge base
        const allSymptoms = extractAllSymptoms(userInputs);
        const validSymptoms = allSymptoms.filter(symptom => {
            return knowledgeBase.symptoms && knowledgeBase.symptoms.includes(symptom.toLowerCase());
        });

        return {
            valid: validSymptoms.length > 0,
            validSymptoms,
            invalidSymptoms: allSymptoms.filter(s => !validSymptoms.includes(s))
        };
    } catch (error) {
        console.error('Validation error:', error);
        return { valid: true, validSymptoms: [], invalidSymptoms: [] }; // Allow all in case of error
    }
};

// Generate session ID
export const generateSessionId = () => {
    return Date.now().toString(36) + Math.random().toString(36).substr(2);
};