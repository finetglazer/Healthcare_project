// Chatbot Service - API Integration
// fe/src/services/chatbot.service.js

import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api/medical';
const CHATBOT_API_URL = `${API_BASE_URL}/chatbot`;

// Configure axios defaults
axios.defaults.withCredentials = true;

// Get CSRF token from cookies
function getCSRFToken() {
    const cookieValue = document.cookie
        .split('; ')
        .find(row => row.startsWith('csrftoken='))
        ?.split('=')[1];
    return cookieValue;
}

// Add CSRF token to requests
axios.interceptors.request.use(config => {
    const csrfToken = getCSRFToken();
    if (csrfToken) {
        config.headers['X-CSRFToken'] = csrfToken;
    }
    return config;
});

// Response interceptor for error handling
axios.interceptors.response.use(
    response => response,
    error => {
        console.error('API Error:', error);

        // Handle specific error cases
        if (error.response?.status === 503) {
            console.warn('Service temporarily unavailable, using fallback');
        } else if (error.response?.status === 429) {
            console.warn('Rate limit exceeded');
        }

        return Promise.reject(error);
    }
);

const chatbotService = {
    // Load knowledge base data
    loadKnowledgeBase: async () => {
        try {
            const response = await axios.get(`${CHATBOT_API_URL}/knowledge/`, {
                timeout: 10000 // 10 second timeout
            });

            return {
                success: true,
                data: response.data,
                cached: response.headers['x-cache-status'] === 'HIT'
            };
        } catch (error) {
            console.error('Failed to load knowledge base:', error);

            return {
                success: false,
                error: error.message,
                fallback: true,
                data: getFallbackKnowledgeBase()
            };
        }
    },

    // Validate symptoms
    validateSymptoms: async (symptoms) => {
        try {
            const response = await axios.post(`${CHATBOT_API_URL}/validate/`, {
                symptoms: symptoms
            });

            return {
                success: true,
                valid: response.data.valid,
                warnings: response.data.warnings || [],
                suggestions: response.data.suggestions || []
            };
        } catch (error) {
            console.error('Symptom validation failed:', error);

            // Fallback validation
            return {
                success: false,
                valid: true, // Allow to continue
                warnings: ['Unable to validate symptoms - proceeding with analysis'],
                fallback: true
            };
        }
    },

    // Analyze symptoms
    analyzeSymptoms: async (userInputs, sessionId = null) => {
        try {
            const analysisData = {
                conversation_step: 'analysis',
                user_inputs: userInputs,
                session_id: sessionId || generateSessionId(),
                timestamp: new Date().toISOString()
            };

            const response = await axios.post(`${CHATBOT_API_URL}/analyze/`, analysisData, {
                timeout: 30000 // 30 second timeout for analysis
            });

            return {
                success: true,
                data: response.data,
                sessionId: response.data.session_id,
                cached: response.headers['x-cache-status'] === 'HIT'
            };
        } catch (error) {
            console.error('Analysis failed:', error);

            // Return structured error for fallback handling
            return {
                success: false,
                error: error.message,
                fallback: true,
                userInputs: userInputs
            };
        }
    },

    // Submit feedback
    submitFeedback: async (sessionId, feedback) => {
        try {
            const response = await axios.post(`${CHATBOT_API_URL}/feedback/`, {
                session_id: sessionId,
                feedback: feedback,
                timestamp: new Date().toISOString()
            });

            return {
                success: true,
                data: response.data
            };
        } catch (error) {
            console.error('Failed to submit feedback:', error);
            return {
                success: false,
                error: error.message
            };
        }
    },

    // Get conversation session
    getConversationSession: async (sessionId) => {
        try {
            const response = await axios.get(`${CHATBOT_API_URL}/session/${sessionId}/`);

            return {
                success: true,
                data: response.data
            };
        } catch (error) {
            console.error('Failed to get conversation session:', error);
            return {
                success: false,
                error: error.message
            };
        }
    },

    // Get specific condition details
    getConditionDetails: async (conditionKey) => {
        try {
            const response = await axios.get(`${API_BASE_URL}/conditions/${conditionKey}/`);

            return {
                success: true,
                data: response.data
            };
        } catch (error) {
            console.error('Failed to get condition details:', error);
            return {
                success: false,
                error: error.message
            };
        }
    },

    // Search symptoms
    searchSymptoms: async (query) => {
        try {
            const response = await axios.get(`${API_BASE_URL}/symptoms/search/`, {
                params: { q: query }
            });

            return {
                success: true,
                data: response.data
            };
        } catch (error) {
            console.error('Failed to search symptoms:', error);
            return {
                success: false,
                error: error.message
            };
        }
    },

    // Health check
    healthCheck: async () => {
        try {
            const response = await axios.get(`${API_BASE_URL}/health/`, {
                timeout: 5000
            });

            return {
                success: true,
                status: response.data.status,
                services: response.data.services
            };
        } catch (error) {
            return {
                success: false,
                error: error.message
            };
        }
    }
};

// Helper Functions

function generateSessionId() {
    return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
}

function getFallbackKnowledgeBase() {
    return {
        conditions: {
            'flu': {
                name: 'Influenza (Flu)',
                description: 'Viral respiratory illness',
                severity_level: 'MODERATE',
                primary_symptoms: [
                    'High fever',
                    'Body aches',
                    'Fatigue',
                    'Chills',
                    'Headache'
                ]
            },
            'cold': {
                name: 'Common Cold',
                description: 'Viral upper respiratory infection',
                severity_level: 'MILD',
                primary_symptoms: [
                    'Runny nose',
                    'Sneezing',
                    'Sore throat',
                    'Mild cough',
                    'Congestion'
                ]
            },
            'covid-19': {
                name: 'COVID-19',
                description: 'Coronavirus disease',
                severity_level: 'MODERATE',
                primary_symptoms: [
                    'Fever',
                    'Cough',
                    'Loss of taste/smell',
                    'Shortness of breath',
                    'Fatigue'
                ]
            },
            'allergy': {
                name: 'Allergic Reaction',
                description: 'Immune system response to allergens',
                severity_level: 'MILD',
                primary_symptoms: [
                    'Sneezing',
                    'Itchy eyes',
                    'Runny nose',
                    'Nasal congestion',
                    'Itchy throat'
                ]
            }
        },
        symptoms: [
            { name: 'fever', frequency: 0.8, conditions: ['flu', 'covid-19'] },
            { name: 'cough', frequency: 0.7, conditions: ['flu', 'covid-19', 'cold'] },
            { name: 'runny nose', frequency: 0.9, conditions: ['cold', 'allergy'] },
            { name: 'sneezing', frequency: 0.8, conditions: ['cold', 'allergy'] },
            { name: 'body aches', frequency: 0.6, conditions: ['flu'] },
            { name: 'loss of taste', frequency: 0.7, conditions: ['covid-19'] },
            { name: 'shortness of breath', frequency: 0.5, conditions: ['covid-19'] },
            { name: 'itchy eyes', frequency: 0.6, conditions: ['allergy'] }
        ],
        metadata: {
            version: 'fallback-1.0',
            source: 'client-fallback',
            last_updated: new Date().toISOString()
        }
    };
}

// Fallback Analysis Function
export const performFallbackAnalysis = (userInputs) => {
    const conditions = {
        'COVID-19': { score: 0, indicators: [] },
        'Flu': { score: 0, indicators: [] },
        'Cold': { score: 0, indicators: [] },
        'Allergy': { score: 0, indicators: [] }
    };

    const allSymptoms = extractAllSymptoms(userInputs).join(' ').toLowerCase();

    // COVID-19 scoring
    if (allSymptoms.includes('loss of taste') || allSymptoms.includes('loss of smell')) {
        conditions['COVID-19'].score += 0.8;
        conditions['COVID-19'].indicators.push('Loss of taste/smell');
    }
    if (allSymptoms.includes('shortness of breath') || allSymptoms.includes('difficulty breathing')) {
        conditions['COVID-19'].score += 0.6;
        conditions['COVID-19'].indicators.push('Breathing difficulties');
    }
    if (allSymptoms.includes('fever')) {
        conditions['COVID-19'].score += 0.4;
        conditions['COVID-19'].indicators.push('Fever');
    }

    // Flu scoring
    if (allSymptoms.includes('high fever') && allSymptoms.includes('body aches')) {
        conditions['Flu'].score += 0.7;
        conditions['Flu'].indicators.push('High fever with body aches');
    }
    if (allSymptoms.includes('sudden onset') || allSymptoms.includes('severe')) {
        conditions['Flu'].score += 0.5;
        conditions['Flu'].indicators.push('Sudden onset');
    }
    if (allSymptoms.includes('fatigue') || allSymptoms.includes('weakness')) {
        conditions['Flu'].score += 0.3;
        conditions['Flu'].indicators.push('Fatigue');
    }

    // Cold scoring
    if (allSymptoms.includes('runny nose') && allSymptoms.includes('sneezing')) {
        conditions['Cold'].score += 0.6;
        conditions['Cold'].indicators.push('Runny nose and sneezing');
    }
    if (allSymptoms.includes('sore throat')) {
        conditions['Cold'].score += 0.4;
        conditions['Cold'].indicators.push('Sore throat');
    }
    if (allSymptoms.includes('gradual') || allSymptoms.includes('mild')) {
        conditions['Cold'].score += 0.3;
        conditions['Cold'].indicators.push('Gradual onset');
    }

    // Allergy scoring
    if (allSymptoms.includes('itchy') || allSymptoms.includes('watery eyes')) {
        conditions['Allergy'].score += 0.7;
        conditions['Allergy'].indicators.push('Itchy/watery symptoms');
    }
    if (allSymptoms.includes('seasonal') || allSymptoms.includes('environmental')) {
        conditions['Allergy'].score += 0.6;
        conditions['Allergy'].indicators.push('Environmental triggers');
    }
    if (allSymptoms.includes('sneezing') && !allSymptoms.includes('fever')) {
        conditions['Allergy'].score += 0.4;
        conditions['Allergy'].indicators.push('Sneezing without fever');
    }

    // Severity adjustment
    const severity = userInputs.severity || 5;
    if (severity >= 8) {
        ['COVID-19', 'Flu'].forEach(condition => {
            if (conditions[condition].score > 0) {
                conditions[condition].score += 0.2;
            }
        });
    }

    // Convert to ranked results
    const rankedConditions = Object.entries(conditions)
        .map(([name, data]) => ({
            name,
            confidence: Math.min(data.score, 1.0),
            indicators: data.indicators
        }))
        .filter(condition => condition.confidence > 0.1)
        .sort((a, b) => b.confidence - a.confidence);

    const mostLikely = rankedConditions[0] || { name: 'Unknown', confidence: 0, indicators: [] };

    return {
        success: true,
        mostLikely,
        allConditions: rankedConditions,
        recommendations: getFallbackRecommendations(mostLikely),
        urgency: getUrgencyLevel(userInputs, mostLikely),
        confidence: mostLikely.confidence,
        disclaimers: [
            '⚕️ This is a preliminary assessment based on limited data.',
            '🔒 Always consult a healthcare provider for proper medical diagnosis.',
            '🚨 If symptoms are severe or worsening, seek immediate medical care.'
        ],
        nextSteps: [
            'Monitor your symptoms closely',
            'Rest and stay hydrated',
            'Avoid contact with others if infectious disease is suspected',
            'Consult a healthcare provider for proper diagnosis'
        ],
        fallback: true
    };
};

function extractAllSymptoms(userInputs) {
    const allSymptoms = [];

    Object.values(userInputs).forEach(input => {
        if (Array.isArray(input)) {
            allSymptoms.push(...input);
        } else if (typeof input === 'string') {
            allSymptoms.push(input);
        }
    });

    return allSymptoms;
}

function getFallbackRecommendations(topCondition) {
    if (!topCondition || topCondition.confidence < 0.3) {
        return [{
            specialist: 'General Practitioner',
            urgency: 'MEDIUM',
            notes: 'Please consult a healthcare provider for proper evaluation',
            next_steps: ['Schedule an appointment', 'Monitor symptoms', 'Rest and stay hydrated']
        }];
    }

    const recommendations = {
        'COVID-19': [{
            specialist: 'General Practitioner or Urgent Care',
            urgency: 'HIGH',
            notes: 'Get tested for COVID-19 immediately and isolate until results are available',
            next_steps: ['Get COVID-19 test', 'Isolate from others', 'Monitor symptoms closely', 'Seek immediate care if breathing becomes difficult']
        }],
        'Flu': [{
            specialist: 'General Practitioner',
            urgency: 'MEDIUM',
            notes: 'Rest, stay hydrated, and consider antiviral medication if seen within 48 hours',
            next_steps: ['Rest and hydrate', 'Monitor fever', 'Avoid contact with others', 'See doctor if symptoms worsen']
        }],
        'Cold': [{
            specialist: 'General Practitioner (if needed)',
            urgency: 'LOW',
            notes: 'Home remedies and rest should help. See doctor if symptoms persist beyond 10 days',
            next_steps: ['Rest and hydrate', 'Use home remedies', 'Monitor symptoms', 'See doctor if no improvement in 7-10 days']
        }],
        'Allergy': [{
            specialist: 'Allergist or General Practitioner',
            urgency: 'LOW',
            notes: 'Consider allergy testing and avoid known triggers',
            next_steps: ['Identify and avoid triggers', 'Consider antihistamines', 'See allergist for testing', 'Keep symptom diary']
        }]
    };

    return recommendations[topCondition.name] || [{
        specialist: 'General Practitioner',
        urgency: 'MEDIUM',
        notes: 'Please consult a healthcare provider for proper diagnosis',
        next_steps: ['Schedule appointment', 'Monitor symptoms', 'Rest and care for yourself']
    }];
}

function getUrgencyLevel(userInputs, topCondition) {
    const severity = userInputs.severity || 5;
    const symptoms = extractAllSymptoms(userInputs).join(' ').toLowerCase();

    // High urgency indicators
    if (severity >= 9 ||
        symptoms.includes('difficulty breathing') ||
        symptoms.includes('chest pain') ||
        symptoms.includes('persistent high fever')) {
        return 'URGENT';
    }

    // High urgency for COVID with breathing issues
    if (topCondition.name === 'COVID-19' && severity >= 7) {
        return 'HIGH';
    }

    // Medium urgency for moderate symptoms
    if (severity >= 6) {
        return 'MEDIUM';
    }

    return 'LOW';
}

export default chatbotService;