// Enhanced Symptom Checker Component - Phase 2
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
    const [disclaimerAccepted, setDisclaimerAccepted] = useState(false);

    // Knowledge base
    const [knowledgeBase, setKnowledgeBase] = useState(null);

    const messagesEndRef = useRef(null);

    // Progress calculation
    const totalSteps = Object.keys(conversationSteps).length - 1; // Exclude ANALYSIS
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
            setError('Failed to load medical assistant. Some features may be limited.');

            // Still show initial message
            const initialQuestion = generateSmartQuestions(conversationSteps.GREETING, {});
            addBotMessage(initialQuestion.message);
        } finally {
            setIsLoading(false);
        }
    };

    const generateSessionId = () => {
        return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    };

    const addBotMessage = (message, type = 'text') => {
        setConversation(prev => [...prev, {
            type: 'bot',
            message,
            timestamp: new Date(),
            messageType: type
        }]);
    };

    const addUserMessage = (message) => {
        const displayMessage = Array.isArray(message) ? message.join(', ') : message;
        setConversation(prev => [...prev, {
            type: 'user',
            message: displayMessage,
            timestamp: new Date()
        }]);
    };

    const handleUserInput = async (input) => {
        try {
            // Add user message to conversation
            addUserMessage(input);

            // Store user input
            const newInputs = { ...userInputs, [currentStep]: input };
            setUserInputs(newInputs);

            // Get next question
            const nextStep = getNextStep(currentStep, input, newInputs);

            if (nextStep === conversationSteps.ANALYSIS) {
                // Start analysis
                await performAnalysis(newInputs);
            } else {
                // Continue conversation
                setCurrentStep(nextStep);

                // Generate next question
                setTimeout(() => {
                    const nextQuestion = generateSmartQuestions(nextStep, newInputs);
                    addBotMessage(nextQuestion.message);
                }, 500);
            }
        } catch (err) {
            console.error('Error processing user input:', err);
            setError('Sorry, there was an error processing your response. Please try again.');
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

        // Skip differential questions if only one clear symptom pattern
        if (current === conversationSteps.FOLLOW_UP_QUESTIONS) {
            const allSymptoms = Object.values(allInputs).flat();
            const uniqueConditionIndicators = new Set();

            if (allSymptoms.some(s => s.includes('loss of taste') || s.includes('loss of smell'))) {
                uniqueConditionIndicators.add('covid');
            }
            if (allSymptoms.some(s => s.includes('itchy') || s.includes('seasonal'))) {
                uniqueConditionIndicators.add('allergy');
            }

            if (uniqueConditionIndicators.size === 1) {
                return conversationSteps.ADDITIONAL_INFO;
            }
        }

        return question.next;
    };

    const performAnalysis = async (inputs) => {
        setIsAnalyzing(true);
        addBotMessage("Analyzing your symptoms...", 'loading');

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
                "I'm sorry, I couldn't complete the analysis. Please consult a healthcare provider for proper diagnosis.",
                'error'
            );
        } finally {
            setIsAnalyzing(false);
        }
    };

    const showAnalysisResults = (result) => {
        const { mostLikely, allConditions, recommendations, urgency, confidence, disclaimers } = result;

        // Build results message
        let resultMessage = `## Analysis Results\n\n`;

        if (mostLikely && mostLikely.confidence > 0.3) {
            resultMessage += `**Most Likely Condition:** ${mostLikely.name}\n`;
            resultMessage += `**Confidence:** ${Math.round(mostLikely.confidence * 100)}%\n\n`;
        }

        if (allConditions && allConditions.length > 1) {
            resultMessage += `**Other Possible Conditions:**\n`;
            allConditions.slice(1, 4).forEach(condition => {
                resultMessage += `• ${condition.name} (${Math.round(condition.confidence * 100)}%)\n`;
            });
            resultMessage += `\n`;
        }

        if (recommendations && recommendations.length > 0) {
            const rec = recommendations[0];
            resultMessage += `**Recommendation:**\n`;
            resultMessage += `• See a ${rec.specialist}\n`;
            resultMessage += `• Urgency: ${rec.urgency}\n`;
            if (rec.notes) {
                resultMessage += `• ${rec.notes}\n`;
            }
        }

        // Add urgency warning
        if (urgency === 'HIGH' || urgency === 'URGENT') {
            addBotMessage(
                "⚠️ **IMPORTANT:** Your symptoms may require immediate medical attention. Please seek care promptly.",
                'warning'
            );
        }

        addBotMessage(resultMessage, 'results');

        // Show disclaimers
        if (disclaimers && disclaimers.length > 0) {
            setTimeout(() => {
                addBotMessage(disclaimers.join('\n\n'), 'disclaimer');
            }, 1000);
        }
    };

    const renderProgressBar = () => (
        <div className="mb-3">
            <div className="d-flex justify-content-between align-items-center mb-2">
                <small className="text-muted">Assessment Progress</small>
                <small className="text-muted">{progress}%</small>
            </div>
            <ProgressBar
                now={progress}
                variant={progress < 50 ? 'info' : progress < 80 ? 'primary' : 'success'}
                style={{ height: '8px' }}
            />
        </div>
    );

    const renderConfidenceMeters = (conditions) => (
        <Card className="mt-3">
            <Card.Body>
                <Card.Title as="h6">Confidence Levels</Card.Title>
                {conditions.slice(0, 3).map((condition, index) => (
                    <div key={index} className="mb-2">
                        <div className="d-flex justify-content-between">
                            <small>{condition.name}</small>
                            <small>{Math.round(condition.confidence * 100)}%</small>
                        </div>
                        <ProgressBar
                            now={condition.confidence * 100}
                            variant={index === 0 ? 'success' : 'info'}
                            size="sm"
                        />
                    </div>
                ))}
            </Card.Body>
        </Card>
    );

    const renderQuestionInput = () => {
        if (isAnalyzing || analysis) return null;

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
                                    className="me-2 mb-2"
                                    onClick={() => handleUserInput(option)}
                                    style={{
                                        display: 'block',
                                        width: '100%',
                                        textAlign: 'left',
                                        whiteSpace: 'normal'
                                    }}
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
                        <Form.Label>Severity Scale (1-10)</Form.Label>
                        <div className="d-flex justify-content-between mb-3">
                            {Array.from({ length: 10 }, (_, i) => (
                                <Button
                                    key={i + 1}
                                    variant={i + 1 <= 3 ? 'success' : i + 1 <= 7 ? 'warning' : 'danger'}
                                    size="sm"
                                    onClick={() => handleUserInput(i + 1)}
                                    style={{ minWidth: '35px' }}
                                >
                                    {i + 1}
                                </Button>
                            ))}
                        </div>
                        <div className="d-flex justify-content-between">
                            <small className="text-muted">Mild</small>
                            <small className="text-muted">Severe</small>
                        </div>
                    </div>
                );

            case 'checkbox':
                return <CheckboxInput options={question.options} onSubmit={handleUserInput} />;

            default:
                return null;
        }
    };

    const renderMessage = (msg, index) => {
        const isBot = msg.type === 'bot';

        return (
            <div key={index} className={`d-flex ${isBot ? 'justify-content-start' : 'justify-content-end'} mb-3`}>
                <div
                    className={`rounded-3 p-3 ${
                        isBot ? 'bg-light text-dark' : 'bg-primary text-white'
                    }`}
                    style={{ maxWidth: '75%' }}
                >
                    {msg.messageType === 'loading' && (
                        <div className="d-flex align-items-center">
                            <div className="spinner-border spinner-border-sm me-2"></div>
                            <span>{msg.message}</span>
                        </div>
                    )}

                    {msg.messageType === 'warning' && (
                        <Alert variant="warning" className="mb-0">
                            {msg.message.split('\n').map((line, i) => (
                                <div key={i} dangerouslySetInnerHTML={{
                                    __html: line.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                                }} />
                            ))}
                        </Alert>
                    )}

                    {msg.messageType === 'results' && (
                        <div>
                            {msg.message.split('\n').map((line, i) => {
                                if (line.startsWith('##')) {
                                    return <h5 key={i} className="mb-2">{line.replace('##', '').trim()}</h5>;
                                } else if (line.startsWith('**')) {
                                    return <div key={i} dangerouslySetInnerHTML={{
                                        __html: line.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                                    }} />;
                                } else {
                                    return <div key={i}>{line}</div>;
                                }
                            })}
                        </div>
                    )}

                    {msg.messageType === 'disclaimer' && (
                        <Alert variant="info" className="mb-0">
                            <small>{msg.message}</small>
                        </Alert>
                    )}

                    {(!msg.messageType || msg.messageType === 'text') && (
                        <div>
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
                    )}
                </div>
            </div>
        );
    };

    if (isLoading) {
        return (
            <Container fluid className="d-flex justify-content-center align-items-center" style={{ height: '100vh' }}>
                <div className="text-center">
                    <div className="spinner-border text-primary mb-3"></div>
                    <p>Loading Medical Assistant...</p>
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
                                        borderRadius: '12px',
                                        display: 'flex',
                                        alignItems: 'center',
                                        justifyContent: 'center',
                                        fontSize: '24px'
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
                            {renderProgressBar()}
                        </div>

                        {/* Features */}
                        <div className="p-4">
                            <h6 className="mb-3">Features</h6>
                            <div className="d-flex flex-column gap-2">
                                <Badge bg="light" text="dark" className="text-start p-2">
                                    ✓ Smart Questioning
                                </Badge>
                                <Badge bg="light" text="dark" className="text-start p-2">
                                    ✓ Symptom Validation
                                </Badge>
                                <Badge bg="light" text="dark" className="text-start p-2">
                                    ✓ Multiple Conditions
                                </Badge>
                                <Badge bg="light" text="dark" className="text-start p-2">
                                    ✓ Urgency Detection
                                </Badge>
                            </div>
                        </div>

                        {/* Disclaimer */}
                        <div className="mt-auto p-4 border-top border-white border-opacity-25">
                            <small className="opacity-75">
                                ⚕️ This tool provides information only.
                                Always consult healthcare professionals for medical advice.
                            </small>
                        </div>
                    </div>
                </Col>

                {/* Main Chat Area */}
                <Col md={9} className="d-flex flex-column p-0">
                    {/* Header */}
                    <div className="bg-white border-bottom p-4">
                        <h4 className="mb-1">Symptom Assessment</h4>
                        <p className="text-muted mb-0">
                            Let's understand your symptoms to provide helpful guidance
                        </p>
                        {error && (
                            <Alert variant="warning" dismissible onClose={() => setError('')} className="mt-2 mb-0">
                                {error}
                            </Alert>
                        )}
                    </div>

                    {/* Messages */}
                    <div className="flex-grow-1 p-4" style={{ overflowY: 'auto' }}>
                        {conversation.map((msg, index) => renderMessage(msg, index))}

                        {/* Analysis results confidence meters */}
                        {analysis && analysis.allConditions && analysis.allConditions.length > 0 && (
                            renderConfidenceMeters(analysis.allConditions)
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
                                    disabled={!analysis.recommendations}
                                >
                                    Find Recommended Doctors
                                </Button>
                                <Button
                                    variant="outline-secondary"
                                    onClick={() => window.location.reload()}
                                >
                                    Start New Assessment
                                </Button>
                                <Button
                                    variant="outline-info"
                                    onClick={() => {
                                        const summary = `Assessment Summary:\n${JSON.stringify(userInputs, null, 2)}\n\nResults:\n${JSON.stringify(analysis, null, 2)}`;
                                        navigator.clipboard.writeText(summary);
                                        alert('Assessment summary copied to clipboard');
                                    }}
                                >
                                    Copy Summary
                                </Button>
                            </div>
                        </div>
                    )}
                </Col>
            </Row>
        </Container>
    );
};

// Enhanced Checkbox Input Component
const CheckboxInput = ({ options, onSubmit }) => {
    const [selected, setSelected] = useState([]);

    const handleToggle = (option) => {
        setSelected(prev => {
            if (option === 'None of the above') {
                return prev.includes(option) ? [] : ['None of the above'];
            }

            const filtered = prev.filter(item => item !== 'None of the above');
            return prev.includes(option)
                ? filtered.filter(item => item !== option)
                : [...filtered, option];
        });
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
                onClick={() => onSubmit(selected.length > 0 ? selected : ['None selected'])}
                className="mt-3"
                disabled={selected.length === 0}
            >
                Continue
            </Button>
        </div>
    );
};

export default SymptomChecker;