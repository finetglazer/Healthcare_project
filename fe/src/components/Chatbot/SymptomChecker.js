// Fixed SymptomChecker.js - Analysis Results Display
// fe/src/components/Chatbot/SymptomChecker.js

import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Container, Row, Col, Button, Form, Alert, ProgressBar } from 'react-bootstrap';
import { useNavigate } from 'react-router-dom';
import {
    conversationSteps,
    generateSmartQuestions,
    analyzeSymptoms,
    loadKnowledgeBase
} from './ChatbotFlow';

const SymptomChecker = () => {
    const navigate = useNavigate();

    // Core state
    const [currentStep, setCurrentStep] = useState(conversationSteps.GREETING);
    const [conversation, setConversation] = useState([]);
    const [userInputs, setUserInputs] = useState({});
    const [analysis, setAnalysis] = useState(null);
    const [sessionId, setSessionId] = useState(null);

    // UI state
    const [isAnalyzing, setIsAnalyzing] = useState(false);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState('');
    const [progress, setProgress] = useState(0);

    // Knowledge base
    const [knowledgeBase, setKnowledgeBase] = useState(null);

    const messagesEndRef = useRef(null);

    const getCurrentProgress = useCallback(() => {
        const stepOrder = [
            conversationSteps.GREETING,
            conversationSteps.PRIMARY_SYMPTOMS,
            conversationSteps.SYMPTOM_DETAILS,
            conversationSteps.SEVERITY,
            conversationSteps.DURATION,
            conversationSteps.FOLLOW_UP_QUESTIONS,
            conversationSteps.DIFFERENTIAL_QUESTIONS,
            conversationSteps.ADDITIONAL_INFO
        ];

        const currentIndex = stepOrder.indexOf(currentStep);
        return Math.round((currentIndex / (stepOrder.length - 1)) * 100);
    }, [currentStep]);

    const generateSessionId = () => {
        return Date.now().toString(36) + Math.random().toString(36).substr(2);
    };

    const initializeChatbot = useCallback(async () => {
        try {
            setIsLoading(true);

            // Load knowledge base
            const kb = await loadKnowledgeBase();
            setKnowledgeBase(kb);

            // Generate session ID
            const newSessionId = generateSessionId();
            setSessionId(newSessionId);

            // Only add initial message if conversation is empty
            if (conversation.length === 0) {
                const initialQuestion = generateSmartQuestions(conversationSteps.GREETING, {});
                addBotMessage(initialQuestion.message);
            }

            setError('');
        } catch (err) {
            console.error('Failed to initialize chatbot:', err);
            setError('Failed to load medical assistant. Please try again.');
        } finally {
            setIsLoading(false);
        }
    }, [conversation.length]);

    // Auto scroll to bottom
    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [conversation]);

    // Initialize component only once
    useEffect(() => {
        initializeChatbot();
    }, []);

    // Update progress
    useEffect(() => {
        setProgress(getCurrentProgress());
    }, [getCurrentProgress]);

    const addBotMessage = (message, type = 'text') => {
        const messageText = typeof message === 'string' ? message :
            typeof message === 'object' ? JSON.stringify(message) :
                String(message);

        setConversation(prev => [...prev, {
            type: 'bot',
            message: messageText,
            messageType: type,
            timestamp: new Date()
        }]);
    };

    const addUserMessage = (message) => {
        const messageText = Array.isArray(message) ? message.join(', ') :
            typeof message === 'string' ? message :
                String(message);

        setConversation(prev => [...prev, {
            type: 'user',
            message: messageText,
            timestamp: new Date()
        }]);
    };

    const handleUserInput = async (input) => {
        addUserMessage(input);

        // Store user input
        const newInputs = { ...userInputs, [currentStep]: input };
        setUserInputs(newInputs);

        // Get next step
        const nextStep = getNextStep(currentStep, input, newInputs);

        if (nextStep === conversationSteps.ANALYSIS) {
            // Perform analysis
            await performAnalysis(newInputs);
        } else {
            // Continue conversation
            setCurrentStep(nextStep);
            setTimeout(() => {
                const nextQuestion = generateSmartQuestions(nextStep, newInputs);
                addBotMessage(nextQuestion.message);
            }, 500);
        }
    };

    const getNextStep = (current, input, allInputs) => {
        const question = generateSmartQuestions(current, allInputs);

        // Smart step logic - skip irrelevant questions
        if (current === conversationSteps.SEVERITY && allInputs.primary_symptoms) {
            const symptoms = allInputs.primary_symptoms || [];

            // Skip follow-up questions for mild symptoms
            if (input <= 3 && !symptoms.some(s => s.includes('breathing') || s.includes('chest'))) {
                return conversationSteps.DURATION;
            }
        }

        return question.next;
    };

    // FIXED: Improved analysis handling
    const performAnalysis = async (inputs) => {
        setIsAnalyzing(true);
        addBotMessage("Thank you for the information. Let me analyze your symptoms...");

        try {
            console.log('Starting analysis with inputs:', inputs);

            const result = await analyzeSymptoms(inputs, sessionId);
            console.log('Analysis result:', result);

            // FIXED: Handle different response structures
            let analysisData;
            if (result.success && result.data) {
                // If response has success wrapper
                analysisData = result.data;
            } else if (result.analysis) {
                // If response has analysis directly
                analysisData = result.analysis;
            } else if (result.mostLikely || result.conditions) {
                // If response is analysis data directly
                analysisData = result;
            } else {
                throw new Error('Invalid analysis response structure');
            }

            console.log('Processed analysis data:', analysisData);

            setAnalysis(analysisData);
            showAnalysisResults(analysisData);

        } catch (err) {
            console.error('Analysis error:', err);
            setError('Analysis failed. Please consult a healthcare provider.');
            addBotMessage("I'm sorry, I couldn't analyze your symptoms right now. Please consult a healthcare provider.");

            // Try fallback analysis
            try {
                const fallbackResult = await performFallbackAnalysis(inputs);
                if (fallbackResult) {
                    setAnalysis(fallbackResult);
                    showAnalysisResults(fallbackResult);
                }
            } catch (fallbackErr) {
                console.error('Fallback analysis also failed:', fallbackErr);
            }
        } finally {
            setIsAnalyzing(false);
        }
    };

    // FIXED: Comprehensive result display function
    const showAnalysisResults = (analysisData) => {
        console.log('Showing analysis results:', analysisData);

        try {
            let resultMessage = `## 🏥 Analysis Complete\n\n`;

            // Handle different response structures
            const conditions = analysisData.conditions || analysisData.mostLikely || analysisData.results || [];
            const urgency = analysisData.urgency || analysisData.urgencyLevel || 'MEDIUM';
            const recommendations = analysisData.recommendations || analysisData.recommendation || {};
            const confidence = analysisData.confidence || 0;

            // Display primary condition
            if (conditions && conditions.length > 0) {
                let primaryCondition;
                let primaryConfidence;

                if (Array.isArray(conditions[0])) {
                    // Format: [["condition", confidence], ...]
                    [primaryCondition, primaryConfidence] = conditions[0];
                } else if (conditions[0].condition || conditions[0].name) {
                    // Format: [{condition: "", confidence: 0.8}, ...]
                    primaryCondition = conditions[0].condition || conditions[0].name;
                    primaryConfidence = conditions[0].confidence || conditions[0].probability;
                } else {
                    // Fallback
                    primaryCondition = String(conditions[0]);
                    primaryConfidence = confidence;
                }

                resultMessage += `**Most Likely Condition:** ${primaryCondition}\n`;
                resultMessage += `**Confidence:** ${Math.round((primaryConfidence || 0) * 100)}%\n\n`;

                // Show confidence meter
                const confidencePercentage = Math.round((primaryConfidence || 0) * 100);
                const confidenceColor = confidencePercentage >= 70 ? 'success' :
                    confidencePercentage >= 50 ? 'warning' : 'danger';

                addBotMessage(`📊 **Confidence Level:** ${confidencePercentage}%`, 'confidence');
            }

            // Display recommendations
            if (recommendations.specialist || recommendations.action) {
                resultMessage += `**🩺 Recommendations:**\n`;
                resultMessage += `• See a ${recommendations.specialist || 'healthcare provider'}\n`;
                resultMessage += `• Urgency Level: ${urgency}\n`;

                if (recommendations.note || recommendations.message) {
                    resultMessage += `• ${recommendations.note || recommendations.message}\n`;
                }
            }

            // Urgency warnings
            if (urgency === 'HIGH' || urgency === 'URGENT') {
                resultMessage += `\n⚠️ **IMPORTANT:** Your symptoms suggest you should seek immediate medical attention.\n`;
                addBotMessage(resultMessage, 'urgent');
            } else if (urgency === 'MEDIUM') {
                resultMessage += `\n⚡ **Note:** Please consider consulting a healthcare provider soon.\n`;
                addBotMessage(resultMessage, 'result');
            } else {
                addBotMessage(resultMessage, 'result');
            }

            // Show alternative conditions
            if (conditions && conditions.length > 1) {
                let alternativeMessage = `\n**🔍 Other Possible Conditions:**\n`;
                for (let i = 1; i < Math.min(conditions.length, 3); i++) {
                    let altCondition, altConfidence;

                    if (Array.isArray(conditions[i])) {
                        [altCondition, altConfidence] = conditions[i];
                    } else {
                        altCondition = conditions[i].condition || conditions[i].name;
                        altConfidence = conditions[i].confidence || conditions[i].probability;
                    }

                    alternativeMessage += `• ${altCondition} (${Math.round((altConfidence || 0) * 100)}%)\n`;
                }
                addBotMessage(alternativeMessage, 'alternatives');
            }

            // Medical disclaimer
            const disclaimerMessage = `\n⚖️ **Medical Disclaimer:** This analysis is for informational purposes only and should not replace professional medical advice. Always consult with a qualified healthcare provider for proper diagnosis and treatment.`;
            addBotMessage(disclaimerMessage, 'disclaimer');

        } catch (err) {
            console.error('Error displaying results:', err);
            addBotMessage("Analysis completed, but there was an issue displaying the results. Please consult a healthcare provider.", 'error');
        }
    };

    // Fallback analysis for when backend fails
    const performFallbackAnalysis = async (inputs) => {
        console.log('Performing fallback analysis...');

        // Simple client-side analysis
        const conditions = {
            'COVID-19': 0,
            'Flu': 0,
            'Cold': 0,
            'Allergy': 0
        };

        const allSymptoms = Object.values(inputs).flat().join(' ').toLowerCase();

        // COVID-19 indicators
        if (allSymptoms.includes('loss of taste') || allSymptoms.includes('loss of smell')) {
            conditions['COVID-19'] += 0.8;
        }
        if (allSymptoms.includes('cough') || allSymptoms.includes('fever')) {
            conditions['COVID-19'] += 0.4;
        }

        // Flu indicators
        if (allSymptoms.includes('fever') || allSymptoms.includes('body aches')) {
            conditions['Flu'] += 0.7;
        }
        if (allSymptoms.includes('fatigue') || allSymptoms.includes('chills')) {
            conditions['Flu'] += 0.5;
        }

        // Cold indicators
        if (allSymptoms.includes('runny nose') || allSymptoms.includes('sneezing')) {
            conditions['Cold'] += 0.8;
        }
        if (allSymptoms.includes('sore throat')) {
            conditions['Cold'] += 0.6;
        }

        // Allergy indicators
        if (allSymptoms.includes('sneezing') || allSymptoms.includes('itchy')) {
            conditions['Allergy'] += 0.9;
        }

        // Find most likely condition
        const mostLikely = Object.entries(conditions)
            .sort(([,a], [,b]) => b - a)
            .filter(([,score]) => score > 0);

        if (mostLikely.length === 0) {
            return null;
        }

        return {
            conditions: mostLikely,
            urgency: 'MEDIUM',
            recommendations: {
                specialist: 'General Practitioner',
                message: 'Based on limited analysis, please consult a healthcare provider.'
            },
            fallback: true
        };
    };

    const renderMessage = (msg, index) => {
        const isBot = msg.type === 'bot';
        const isUrgent = msg.messageType === 'urgent';
        const isResult = msg.messageType === 'result';

        return (
            <div
                key={index}
                className={`d-flex mb-3 ${isBot ? 'justify-content-start' : 'justify-content-end'}`}
            >
                <div
                    className={`p-3 rounded-3 ${
                        isBot
                            ? isUrgent
                                ? 'bg-danger text-white'
                                : isResult
                                    ? 'bg-success text-white'
                                    : 'bg-light text-dark'
                            : 'bg-primary text-white'
                    }`}
                    style={{ maxWidth: '75%' }}
                >
                    {msg.message.split('\n').map((line, i) => (
                        <div key={i}>
                            {line.includes('**') ? (
                                <span dangerouslySetInnerHTML={{
                                    __html: line.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                                }} />
                            ) : line}
                        </div>
                    ))}
                </div>
            </div>
        );
    };

    const renderQuestionInput = () => {
        if (isLoading) {
            return <div>Loading...</div>;
        }

        const question = generateSmartQuestions(currentStep, userInputs);

        switch (question.type) {
            case 'multiple_choice':
                return (
                    <div>
                        <p className="mb-3">{question.message}</p>
                        <div className="d-grid gap-2">
                            {question.options.map((option, index) => (
                                <Button
                                    key={index}
                                    variant="outline-primary"
                                    onClick={() => handleUserInput(option)}
                                >
                                    {option}
                                </Button>
                            ))}
                        </div>
                    </div>
                );

            case 'scale':
                return (
                    <div>
                        <p className="mb-3">{question.message}</p>
                        <div className="d-flex flex-wrap gap-2">
                            {Array.from({ length: question.max - question.min + 1 }, (_, i) => (
                                <Button
                                    key={i + question.min}
                                    variant="outline-primary"
                                    size="sm"
                                    onClick={() => handleUserInput(i + question.min)}
                                    style={{ minWidth: '40px' }}
                                >
                                    {i + question.min}
                                </Button>
                            ))}
                        </div>
                    </div>
                );

            case 'checkbox':
                return <CheckboxInput options={question.options} onSubmit={handleUserInput} />;

            case 'text':
                return <TextInput question={question.message} onSubmit={handleUserInput} />;

            default:
                return null;
        }
    };

    return (
        <Container fluid style={{ height: '100vh', background: '#f8f9fa' }}>
            <Row style={{ height: '100%' }}>
                {/* Sidebar */}
                <Col md={3} className="bg-primary text-white p-0">
                    <div className="d-flex flex-column h-100">
                        {/* Logo */}
                        <div className="p-4 border-bottom border-white border-opacity-25">
                            <div className="d-flex align-items-center">
                                <div
                                    className="me-3"
                                    style={{
                                        width: '48px',
                                        height: '48px',
                                        background: 'white',
                                        borderRadius: '12px',
                                        display: 'flex',
                                        alignItems: 'center',
                                        justifyContent: 'center'
                                    }}
                                >
                                    🏥
                                </div>
                                <div>
                                    <h5 className="mb-0">Medical Assistant</h5>
                                    <small className="opacity-75">Symptom Checker</small>
                                </div>
                            </div>
                        </div>

                        {/* Progress */}
                        <div className="p-4">
                            <div className="mb-2">
                                <small>Progress</small>
                            </div>
                            <ProgressBar now={progress} variant="light" />
                            <small className="opacity-75">{progress}% Complete</small>
                        </div>

                        {/* Disclaimer */}
                        <div className="mt-auto p-4">
                            <Alert variant="warning" className="mb-0 small">
                                ⚠️ This is a preliminary assessment tool.
                                Always consult healthcare professionals for medical advice.
                            </Alert>
                        </div>
                    </div>
                </Col>

                {/* Main Chat Area */}
                <Col md={9} className="d-flex flex-column p-0">
                    {/* Chat Messages */}
                    <div className="flex-grow-1 p-4" style={{ overflowY: 'auto', maxHeight: 'calc(100vh - 100px)' }}>
                        {error && (
                            <Alert variant="danger" className="mb-3">
                                {error}
                            </Alert>
                        )}

                        {conversation.map((msg, index) => renderMessage(msg, index))}

                        {isAnalyzing && (
                            <div className="d-flex justify-content-center">
                                <div className="bg-light rounded-3 p-3">
                                    <div className="d-flex align-items-center">
                                        <div className="spinner-border spinner-border-sm me-2"></div>
                                        Analyzing your symptoms...
                                    </div>
                                </div>
                            </div>
                        )}

                        <div ref={messagesEndRef} />
                    </div>

                    {/* Input Area */}
                    {!analysis && (
                        <div className="bg-white border-top p-4">
                            {renderQuestionInput()}
                        </div>
                    )}

                    {/* Results Actions */}
                    {analysis && (
                        <div className="bg-white border-top p-4">
                            <div className="d-flex gap-2 justify-content-center">
                                <Button
                                    variant="primary"
                                    onClick={() => navigate('/find-doctors')}
                                >
                                    Find Recommended Doctors
                                </Button>
                                <Button
                                    variant="outline-secondary"
                                    onClick={() => window.location.reload()}
                                >
                                    Start Over
                                </Button>
                            </div>
                        </div>
                    )}
                </Col>
            </Row>
        </Container>
    );
};

// Checkbox input component
const CheckboxInput = ({ options, onSubmit }) => {
    const [selected, setSelected] = useState([]);

    const handleToggle = (option) => {
        setSelected(prev =>
            prev.includes(option)
                ? prev.filter(item => item !== option)
                : [...prev, option]
        );
    };

    return (
        <div>
            <Form>
                {options.map((option, index) => (
                    <Form.Check
                        key={index}
                        type="checkbox"
                        id={`symptom-${index}`}
                        label={option}
                        checked={selected.includes(option)}
                        onChange={() => handleToggle(option)}
                        className="mb-2"
                    />
                ))}
            </Form>
            <Button
                variant="primary"
                onClick={() => onSubmit(selected.length > 0 ? selected : ['None'])}
                className="mt-3"
                disabled={selected.length === 0}
            >
                Continue
            </Button>
        </div>
    );
};

// Text input component
const TextInput = ({ question, onSubmit }) => {
    const [input, setInput] = useState('');

    const handleSubmit = (e) => {
        e.preventDefault();
        if (input.trim()) {
            onSubmit(input.trim());
            setInput('');
        }
    };

    return (
        <Form onSubmit={handleSubmit}>
            <Form.Group>
                <Form.Label>{question}</Form.Label>
                <Form.Control
                    type="text"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    placeholder="Type your answer..."
                />
            </Form.Group>
            <Button
                type="submit"
                variant="primary"
                className="mt-2"
                disabled={!input.trim()}
            >
                Continue
            </Button>
        </Form>
    );
};

export default SymptomChecker;