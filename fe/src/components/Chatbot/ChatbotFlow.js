// Enhanced Chatbot Flow with Backend Integration and Smart Logic
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
let symptomsIndex = null;

// Load knowledge base from backend
export const loadKnowledgeBase = async () => {
    try {
        const response = await axios.get(`${API_BASE_URL}/knowledge/`);
        knowledgeBase = response.data;
        symptomsIndex = response.data.symptoms;
        return knowledgeBase;
    } catch (error) {
        console.error('Failed to load knowledge base:', error);
        return null;
    }
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

    return "Please provide more details about your symptoms:";
};

// Generate symptom details options based on primary symptoms
const generateSymptomDetailsOptions = (userInputs) => {
    const primary = userInputs.greeting || [];

    if (primary.includes('Fever and body aches')) {
        return [
            'High fever (over 101°F/38.3°C)',
            'Low-grade fever (99-101°F/37.2-38.3°C)',
            'Chills and sweating',
            'Muscle aches all over',
            'Joint pain',
            'Back pain',
            'Weakness or fatigue'
        ];
    } else if (primary.includes('Runny nose and sneezing')) {
        return [
            'Clear, watery runny nose',
            'Thick, colored nasal discharge',
            'Frequent sneezing',
            'Nasal congestion',
            'Itchy nose',
            'Post-nasal drip',
            'Sinus pressure'
        ];
    } else if (primary.includes('Cough and sore throat')) {
        return [
            'Dry cough',
            'Productive cough with phlegm',
            'Sore throat when swallowing',
            'Scratchy throat',
            'Hoarse voice',
            'Throat irritation',
            'Coughing up blood'
        ];
    } else if (primary.includes('Loss of taste or smell')) {
        return [
            'Complete loss of taste',
            'Partial loss of taste',
            'Complete loss of smell',
            'Partial loss of smell',
            'Altered taste (metallic, strange)',
            'Altered smell',
            'Both taste and smell affected'
        ];
    } else if (primary.includes('Breathing difficulties')) {
        return [
            'Shortness of breath at rest',
            'Shortness of breath with activity',
            'Chest tightness',
            'Wheezing',
            'Rapid breathing',
            'Chest pain with breathing',
            'Feeling like you can\'t get enough air'
        ];
    }

    return [
        'Mild symptoms',
        'Moderate symptoms',
        'Severe symptoms',
        'Symptoms getting worse',
        'Symptoms staying the same',
        'Symptoms improving'
    ];
};

// Generate follow-up questions based on collected symptoms
const generateFollowUpMessage = (userInputs) => {
    const severity = userInputs.severity || 5;
    const duration = userInputs.duration || '';

    if (severity >= 8) {
        return "Since your symptoms are severe, I need to ask about some important signs:";
    } else if (duration.includes('More than a week')) {
        return "Your symptoms have been ongoing. Let me check for some additional signs:";
    }

    return "Based on your symptoms, I'd like to ask about a few more things:";
};

// Generate follow-up options based on symptom patterns
const generateFollowUpOptions = (userInputs) => {
    const primarySymptoms = userInputs.greeting || [];
    const symptomDetails = userInputs.primary_symptoms || [];
    const severity = userInputs.severity || 5;

    let options = [];

    // High fever questions
    if (symptomDetails.includes('High fever (over 101°F/38.3°C)') || severity >= 8) {
        options.push('Difficulty breathing or shortness of breath');
        options.push('Chest pain or pressure');
        options.push('Persistent high fever');
    }

    // Respiratory symptoms
    if (primarySymptoms.includes('Cough and sore throat') || primarySymptoms.includes('Runny nose and sneezing')) {
        options.push('Ear pain or pressure');
        options.push('Facial pain or sinus pressure');
        options.push('Swollen lymph nodes');
    }

    // COVID-specific symptoms
    if (symptomDetails.includes('Complete loss of taste') || symptomDetails.includes('Complete loss of smell')) {
        options.push('Recent exposure to COVID-19');
        options.push('Travel history in past 14 days');
        options.push('Close contact with infected person');
    }

    // General options
    options.push('Recent changes in symptoms');
    options.push('Medications currently taking');
    options.push('Allergies or medical conditions');
    options.push('None of the above');

    return [...new Set(options)]; // Remove duplicates
};

// Generate differential diagnosis questions
const generateDifferentialMessage = (userInputs) => {
    const symptoms = [...(userInputs.greeting || []), ...(userInputs.primary_symptoms || [])];

    // Check for overlapping symptoms that need differentiation
    if (symptoms.some(s => s.includes('fever')) && symptoms.some(s => s.includes('cough'))) {
        return "To help distinguish between different conditions, which best describes your overall experience?";
    } else if (symptoms.some(s => s.includes('runny nose')) && symptoms.some(s => s.includes('sneezing'))) {
        return "These symptoms could be related to different causes. Which scenario sounds most like you?";
    }

    return "To provide the most accurate assessment, please choose the option that best fits your situation:";
};

// Generate differential options to distinguish between conditions
const generateDifferentialOptions = (userInputs) => {
    const symptoms = [...(userInputs.greeting || []), ...(userInputs.primary_symptoms || [])];

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

// Enhanced symptom analysis with backend integration
export const analyzeSymptoms = async (userInputs, sessionId = null) => {
    try {
        // Prepare analysis data
        const analysisData = {
            conversation_step: 'analysis',
            user_inputs: userInputs,
            session_id: sessionId || generateSessionId()
        };

        // Validate symptoms against knowledge base
        const validationResult = await validateSymptoms(userInputs);
        if (!validationResult.valid) {
            throw new Error('Invalid symptoms detected');
        }

        // Call backend analysis endpoint
        const response = await axios.post(`${API_BASE_URL}/analyze/`, analysisData);

        const result = response.data;

        // Enhanced result processing
        return {
            success: true,
            mostLikely: result.analysis?.most_likely || { name: 'Unknown', confidence: 0 },
            allConditions: result.analysis?.ranked_conditions || [],
            recommendations: result.analysis?.recommendations || [],
            urgency: result.analysis?.urgency_level || 'MEDIUM',
            confidence: result.analysis?.confidence || 0,
            disclaimers: result.analysis?.disclaimers || [],
            nextSteps: result.analysis?.next_steps || [],
            sessionId: result.session_id
        };

    } catch (error) {
        console.error('Analysis failed:', error);

        // Fallback to client-side analysis
        return performFallbackAnalysis(userInputs);
    }
};

// Validate symptoms against knowledge base
const validateSymptoms = async (userInputs) => {
    try {
        const response = await axios.post(`${API_BASE_URL}/validate/`, {
            symptoms: extractAllSymptoms(userInputs)
        });

        return response.data;
    } catch (error) {
        console.error('Symptom validation failed:', error);
        return { valid: true, warnings: [] };
    }
};

// Extract all symptoms from user inputs
const extractAllSymptoms = (userInputs) => {
    const allSymptoms = [];

    Object.values(userInputs).forEach(input => {
        if (Array.isArray(input)) {
            allSymptoms.push(...input);
        } else if (typeof input === 'string') {
            allSymptoms.push(input);
        }
    });

    return allSymptoms;
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
        confidence: sortedConditions[0]?.confidence || 0,
        disclaimers: [
            'This is a fallback analysis. Please consult a healthcare provider for proper diagnosis.',
            'If symptoms are severe or persistent, seek immediate medical attention.'
        ],
        nextSteps: [
            'Monitor your symptoms',
            'Rest and stay hydrated',
            'Consult a healthcare provider if symptoms worsen'
        ]
    };
};

// Get fallback recommendations
const getFallbackRecommendations = (topCondition) => {
    if (!topCondition) {
        return [{
            specialist: 'General Practitioner',
            urgency: 'MEDIUM',
            notes: 'Please consult a healthcare provider for proper diagnosis'
        }];
    }

    const recommendations = {
        'COVID-19': [{
            specialist: 'General Practitioner',
            urgency: 'HIGH',
            notes: 'Get tested immediately and isolate until results are available'
        }],
        'Flu': [{
            specialist: 'General Practitioner',
            urgency: 'MEDIUM',
            notes: 'Rest, stay hydrated, and monitor symptoms'
        }],
        'Cold': [{
            specialist: 'General Practitioner',
            urgency: 'LOW',
            notes: 'Rest and use home remedies. See doctor if symptoms worsen'
        }],
        'Allergy': [{
            specialist: 'Allergist',
            urgency: 'LOW',
            notes: 'Consider allergy testing and avoid known triggers'
        }]
    };

    return recommendations[topCondition.name] || [{
        specialist: 'General Practitioner',
        urgency: 'MEDIUM',
        notes: 'Please consult a healthcare provider for proper diagnosis'
    }];
};

// Generate unique session ID
const generateSessionId = () => {
    return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
};

// Export the enhanced chatbot questions
export const chatbotQuestions = generateSmartQuestions;