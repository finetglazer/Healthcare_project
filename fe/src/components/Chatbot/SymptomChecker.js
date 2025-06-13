// Fixed SymptomChecker.js - Runtime Error Fix
// fe/src/components/Chatbot/SymptomChecker.js

import React, { useState, useEffect, useRef } from 'react';
import { Container, Row, Col, Button, Form, Alert, ProgressBar, Card, Badge } from 'react-bootstrap';
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

    // Progress calculation
    const getCurrentProgress = () => {
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
    };

    // Auto scroll to bottom
    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [conversation]);

    // Initialize component
    useEffect(() => {
        initializeChatbot();
    }, []);

    // Update progress
    useEffect(() => {
        setProgress(getCurrentProgress());
    }, [currentStep]);

    const initializeChatbot = async () => {
        try {
            setIsLoading(true);

            // Load knowledge base
            const kb = await loadKnowledgeBase();
            setKnowledgeBase(kb);

            // Generate session ID
            const newSessionId = generateSessionId();
            setSessionId(newSessionId);

            // Show initial message
            const initialQuestion = generateSmartQuestions(conversationSteps.GREETING, {});
            addBotMessage(initialQuestion.message);

            setError('');
        } catch (err) {
            console.error('Failed to initialize chatbot:', err);
            setError('Failed to load medical assistant. Please try again.');
        } finally {
            setIsLoading(false);
        }
    };

    const generateSessionId = () => {
        return Date.now().toString(36) + Math.random().toString(36).substr(2);
    };

    // FIXED: Ensure message is always a string
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

    const performAnalysis = async (inputs) => {
        setIsAnalyzing(true);
        addBotMessage("Analyzing your symptoms...");

        try {
            const result = await analyzeSymptoms(inputs, sessionId);

            if (result.success) {
                setAnalysis(result);
                showAnalysisResults(result);
            } else {
                throw new Error('Analysis failed');
            }
        } catch (err) {
            console.error('Analysis error:', err);
            setError('Analysis failed. Please consult a healthcare provider.');

            // Show fallback message
            addBotMessage(
                "I'm sorry, I couldn't complete the analysis. Please consult a healthcare provider for proper diagnosis."
            );
        } finally {
            setIsAnalyzing(false);
        }
    };

    const showAnalysisResults = (result) => {
        const mostLikely = result.mostLikely || { name: 'Unknown', confidence: 0 };
        const recommendations = result.recommendations || {};

        const resultMessage = `
Based on your symptoms, you might have: **${mostLikely.name}** (${Math.round(mostLikely.confidence * 100)}% confidence)

**Recommendation:**
- ${recommendations.action || 'Consult a healthcare provider'}
- Urgency: ${result.urgency || 'MEDIUM'}
- ${recommendations.note || 'Please seek professional medical advice'}

**Medical Disclaimer:**
This analysis is for informational purposes only and should not replace professional medical advice. Please consult with a healthcare provider for proper diagnosis and treatment.

Would you like to find recommended doctors in our system?`;

        addBotMessage(resultMessage);
    };

    // FIXED: Safe message rendering
    const renderMessage = (msg, index) => {
        // Ensure message is always a string
        const messageText = typeof msg.message === 'string' ? msg.message : String(msg.message);

        return (
            <div key={index} className={`d-flex mb-3 ${msg.type === 'user' ? 'justify-content-end' : 'justify-content-start'}`}>
                <div
                    className={`p-3 rounded-3 ${
                        msg.type === 'user'
                            ? 'bg-primary text-white'
                            : 'bg-light text-dark'
                    }`}
                    style={{ maxWidth: '75%' }}
                >
                    {messageText.split('\n').map((line, i) => (
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
        if (!knowledgeBase || isLoading) {
            return <div className="text-center">Loading...</div>;
        }

        const question = generateSmartQuestions(currentStep, userInputs);
        if (!question) return null;

        switch (question.type) {
            case 'multiple_choice':
                return (
                    <div>
                        <div className="mb-3">
                            {question.options.map((option, index) => (
                                <Button
                                    key={index}
                                    variant="outline-primary"
                                    className="d-block w-100 mb-2 text-start"
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
                        <div className="mb-3">
                            <div className="d-flex justify-content-between mb-2">
                                <small>Very Mild</small>
                                <small>Severe</small>
                            </div>
                            <div className="d-flex gap-2 flex-wrap justify-content-center">
                                {Array.from({ length: question.max - question.min + 1 }, (_, i) => (
                                    <Button
                                        key={i + 1}
                                        variant="outline-primary"
                                        size="sm"
                                        onClick={() => handleUserInput(i + 1)}
                                        style={{ minWidth: '40px' }}
                                    >
                                        {i + 1}
                                    </Button>
                                ))}
                            </div>
                        </div>
                    </div>
                );

            case 'checkbox':
                return <CheckboxInput options={question.options} onSubmit={handleUserInput} />;

            default:
                return null;
        }
    };

    if (isLoading) {
        return (
            <Container className="d-flex justify-content-center align-items-center" style={{ height: '100vh' }}>
                <div className="text-center">
                    <div className="spinner-border text-primary mb-3"></div>
                    <div>Loading Medical Assistant...</div>
                </div>
            </Container>
        );
    }

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
                                        borderRadius: '50%',
                                        display: 'flex',
                                        alignItems: 'center',
                                        justifyContent: 'center',
                                        fontSize: '20px',
                                        color: '#0d6efd'
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
                            <ProgressBar now={progress} className="mb-2" />
                            <small className="opacity-75">{progress}% Complete</small>
                        </div>

                        {/* Disclaimer */}
                        <div className="p-4 mt-auto">
                            <Alert variant="warning" className="mb-0 small">
                                <strong>Medical Disclaimer:</strong> This tool is for informational purposes only. Always consult healthcare professionals for medical advice.
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
                onClick={() => onSubmit(selected.length > 0 ? selected : ['None of the above'])}
                className="mt-3"
                disabled={selected.length === 0}
            >
                Continue
            </Button>
        </div>
    );
};

export default SymptomChecker;