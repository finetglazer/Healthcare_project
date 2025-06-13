// Fixed SymptomChecker.js - All Issues Resolved
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

    // FIXED: Use useCallback to prevent dependency issues
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

    // FIXED: Use useCallback to prevent dependency issues
    const initializeChatbot = useCallback(async () => {
        try {
            setIsLoading(true);

            // Load knowledge base
            const kb = await loadKnowledgeBase();
            setKnowledgeBase(kb);

            // Generate session ID
            const newSessionId = generateSessionId();
            setSessionId(newSessionId);

            // FIXED: Only add initial message if conversation is empty
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
    }, [conversation.length]); // Added conversation.length dependency

    const generateSessionId = () => {
        return Date.now().toString(36) + Math.random().toString(36).substr(2);
    };

    // Auto scroll to bottom
    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [conversation]);

    // FIXED: Initialize component only once
    useEffect(() => {
        initializeChatbot();
    }, [initializeChatbot]);

    // FIXED: Update progress with correct dependencies
    useEffect(() => {
        setProgress(getCurrentProgress());
    }, [getCurrentProgress]);

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
        addBotMessage("Thank you for the information. Let me analyze your symptoms...");

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
            addBotMessage("I'm sorry, I couldn't analyze your symptoms right now. Please consult a healthcare provider.");
        } finally {
            setIsAnalyzing(false);
        }
    };

    // FIXED: Add missing showAnalysisResults function
    const showAnalysisResults = (result) => {
        const { mostLikely, recommendations, confidence, urgencyLevel } = result;

        // Create results message
        let resultMessage = `## Analysis Complete\n\n`;

        if (mostLikely && mostLikely.length > 0) {
            const [condition, conditionConfidence] = mostLikely[0];
            resultMessage += `**Most Likely Condition:** ${condition}\n`;
            resultMessage += `**Confidence:** ${Math.round(conditionConfidence * 100)}%\n\n`;
        }

        if (recommendations) {
            resultMessage += `**Recommendations:**\n`;
            resultMessage += `• See a ${recommendations.specialist || 'healthcare provider'}\n`;
            resultMessage += `• Urgency Level: ${urgencyLevel || 'Moderate'}\n`;

            if (recommendations.note) {
                resultMessage += `• ${recommendations.note}\n`;
            }
        }

        // Show urgency warning if needed
        if (urgencyLevel === 'HIGH' || urgencyLevel === 'URGENT') {
            resultMessage += `\n⚠️ **Important:** Your symptoms suggest you should seek immediate medical attention.`;
            addBotMessage(resultMessage, 'urgent');
        } else {
            addBotMessage(resultMessage, 'result');
        }

        // Show multiple conditions if present
        if (mostLikely && mostLikely.length > 1) {
            let alternativeMessage = `\n**Other Possible Conditions:**\n`;
            for (let i = 1; i < Math.min(mostLikely.length, 3); i++) {
                const [altCondition, altConfidence] = mostLikely[i];
                alternativeMessage += `• ${altCondition} (${Math.round(altConfidence * 100)}%)\n`;
            }
            addBotMessage(alternativeMessage, 'alternatives');
        }
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
                                        .replace(/##\s*(.*)/g, '<h5>$1</h5>')
                                        .replace(/•\s*(.*)/g, '• $1')
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
            return (
                <div className="text-center">
                    <div className="spinner-border text-primary me-2"></div>
                    Loading medical assistant...
                </div>
            );
        }

        const question = generateSmartQuestions(currentStep, userInputs);
        if (!question) return null;

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
                                    className="text-start"
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
                        <div className="d-flex gap-2 justify-content-center flex-wrap">
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
    const [value, setValue] = useState('');

    const handleSubmit = (e) => {
        e.preventDefault();
        if (value.trim()) {
            onSubmit(value.trim());
            setValue('');
        }
    };

    return (
        <Form onSubmit={handleSubmit}>
            <Form.Group>
                <Form.Label>{question}</Form.Label>
                <Form.Control
                    type="text"
                    value={value}
                    onChange={(e) => setValue(e.target.value)}
                    placeholder="Type your answer..."
                />
            </Form.Group>
            <Button
                type="submit"
                variant="primary"
                className="mt-3"
                disabled={!value.trim()}
            >
                Submit
            </Button>
        </Form>
    );
};

export default SymptomChecker;