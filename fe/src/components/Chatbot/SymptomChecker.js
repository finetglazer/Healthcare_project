// fe/src/components/Chatbot/SymptomChecker.js - Minimal Working Fix
import React, { useState, useEffect, useRef } from 'react';
import { Container, Row, Col, Button, Form, Alert, ProgressBar } from 'react-bootstrap';
import { useNavigate } from 'react-router-dom';
import {
    conversationSteps,
    generateSmartQuestions,
    analyzeSymptoms,
    loadKnowledgeBase,
    getNextStep,
    validateInput
} from './ChatbotFlow';

const SymptomChecker = () => {
    const navigate = useNavigate();
    const [currentStep, setCurrentStep] = useState(conversationSteps.GREETING);
    const [conversation, setConversation] = useState([]);
    const [userInputs, setUserInputs] = useState({});
    const [analysis, setAnalysis] = useState(null);
    const [isAnalyzing, setIsAnalyzing] = useState(false);
    const [isInitialized, setIsInitialized] = useState(false);
    const messagesEndRef = useRef(null);

    // Auto scroll to bottom
    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [conversation]);

    // Initialize chatbot
    useEffect(() => {
        const initializeChatbot = async () => {
            try {
                await loadKnowledgeBase();
                const initialQuestion = generateSmartQuestions(conversationSteps.GREETING, {});
                addBotMessage(initialQuestion.message);
                setIsInitialized(true);
            } catch (error) {
                console.error('Failed to initialize chatbot:', error);
                addBotMessage("Hello! I'm your medical assistant. What symptoms are you experiencing?");
                setIsInitialized(true);
            }
        };

        if (!isInitialized) {
            initializeChatbot();
        }
    }, [isInitialized]);

    const addBotMessage = (message) => {
        setConversation(prev => [...prev, {
            type: 'bot',
            message,
            timestamp: new Date()
        }]);
    };

    const addUserMessage = (message) => {
        setConversation(prev => [...prev, {
            type: 'user',
            message: Array.isArray(message) ? message.join(', ') : message,
            timestamp: new Date()
        }]);
    };

    const handleUserInput = async (input) => {
        // Validate input
        const validation = validateInput(currentStep, input);
        if (!validation.isValid) {
            addBotMessage(validation.error);
            return;
        }

        addUserMessage(input);

        // Store user input
        const newInputs = { ...userInputs, [currentStep]: input };
        setUserInputs(newInputs);

        // Get next step
        const nextStep = getNextStep(currentStep, newInputs);

        if (nextStep === conversationSteps.ANALYSIS) {
            // Analyze symptoms
            setIsAnalyzing(true);
            try {
                const result = await analyzeSymptoms(newInputs);
                setAnalysis(result);
                showAnalysisResults(result);
            } catch (error) {
                console.error('Analysis failed:', error);
                addBotMessage("I'm having trouble analyzing your symptoms. Please consult a healthcare provider.");
            } finally {
                setIsAnalyzing(false);
            }
        } else {
            // Continue conversation
            setCurrentStep(nextStep);
            setTimeout(() => {
                const nextQuestion = generateSmartQuestions(nextStep, newInputs);
                addBotMessage(nextQuestion.message);
            }, 500);
        }
    };

    const showAnalysisResults = (result) => {
        if (!result || result.error) {
            addBotMessage("I wasn't able to provide a reliable analysis. Please consult a healthcare provider for proper evaluation.");
            return;
        }

        const [condition, confidence] = result.mostLikely || ['Unknown condition', 0.3];
        const { specialist, urgency, note } = result.recommendation || {};

        const resultMessage = `
Based on your symptoms, you might have: **${condition}** (${Math.round(confidence * 100)}% confidence)

**Recommendation:**
- See a ${specialist || 'General Practitioner'}
- Urgency: ${urgency || 'MODERATE'}
- ${note || 'Please consult a healthcare provider for proper evaluation.'}

**Medical Disclaimer:** This is not a medical diagnosis. Please consult with a qualified healthcare professional for proper medical advice.

Would you like to find ${(specialist || 'doctors').toLowerCase()} in our system?
        `;

        addBotMessage(resultMessage.trim());
    };

    const renderQuestionInput = () => {
        if (isAnalyzing || analysis) return null;

        const question = generateSmartQuestions(currentStep, userInputs);

        if (!question) return null;

        switch (question.type) {
            case 'multiple_choice':
                return (
                    <div>
                        <div className="d-grid gap-2">
                            {question.options?.map((option, index) => (
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
                        <div className="mb-3">
                            <div className="d-flex justify-content-between mb-2">
                                <small>Very Mild</small>
                                <small>Severe</small>
                            </div>
                            <div className="d-flex gap-1">
                                {[...Array(10)].map((_, i) => (
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
                return <CheckboxInput options={question.options || []} onSubmit={handleUserInput} />;

            case 'text':
                return <TextInput onSubmit={handleUserInput} />;

            default:
                return null;
        }
    };

    // Calculate progress
    const steps = Object.keys(conversationSteps).length - 1; // Exclude ANALYSIS
    const currentStepIndex = Object.values(conversationSteps).indexOf(currentStep);
    const progress = Math.min((currentStepIndex / steps) * 100, 100);

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
                                        justifyContent: 'center'
                                    }}
                                >
                                    <span style={{ color: '#0d6efd', fontSize: '24px', fontWeight: 'bold' }}>+</span>
                                </div>
                                <div>
                                    <h5 className="mb-0">MedAssist</h5>
                                    <small className="opacity-75">Symptom Checker</small>
                                </div>
                            </div>
                        </div>

                        {/* Progress */}
                        <div className="p-4 border-bottom border-white border-opacity-25">
                            <div className="mb-2">
                                <small>Progress</small>
                            </div>
                            <ProgressBar
                                now={progress}
                                variant="success"
                                style={{ height: '8px' }}
                            />
                            <small className="opacity-75 mt-1">{Math.round(progress)}% Complete</small>
                        </div>

                        {/* Features */}
                        <div className="p-4 flex-grow-1">
                            <h6 className="mb-3">How it works:</h6>
                            <ul className="list-unstyled">
                                <li className="mb-2">
                                    <small>✓ Answer questions about your symptoms</small>
                                </li>
                                <li className="mb-2">
                                    <small>✓ Get AI-powered condition analysis</small>
                                </li>
                                <li className="mb-2">
                                    <small>✓ Receive specialist recommendations</small>
                                </li>
                                <li className="mb-2">
                                    <small>✓ Find nearby healthcare providers</small>
                                </li>
                            </ul>
                        </div>

                        {/* Disclaimer */}
                        <div className="p-4 border-top border-white border-opacity-25">
                            <Alert variant="warning" className="small mb-0">
                                <strong>Medical Disclaimer:</strong> This tool provides information only and is not a substitute for professional medical advice.
                            </Alert>
                        </div>
                    </div>
                </Col>

                {/* Main Chat Area */}
                <Col md={9} className="d-flex flex-column p-0">
                    {/* Messages */}
                    <div className="flex-grow-1 p-4" style={{ overflowY: 'auto', maxHeight: 'calc(100vh - 200px)' }}>
                        {conversation.map((msg, index) => (
                            <div
                                key={index}
                                className={`d-flex mb-3 ${msg.type === 'user' ? 'justify-content-end' : 'justify-content-start'}`}
                            >
                                <div
                                    className={`rounded-3 p-3 ${
                                        msg.type === 'user'
                                            ? 'bg-primary text-white'
                                            : 'bg-light text-dark'
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
                        ))}

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

// Text input component
const TextInput = ({ onSubmit }) => {
    const [text, setText] = useState('');

    const handleSubmit = (e) => {
        e.preventDefault();
        if (text.trim()) {
            onSubmit(text.trim());
            setText('');
        }
    };

    return (
        <Form onSubmit={handleSubmit}>
            <Form.Group className="mb-3">
                <Form.Control
                    type="text"
                    placeholder="Type your additional symptoms or information..."
                    value={text}
                    onChange={(e) => setText(e.target.value)}
                />
            </Form.Group>
            <Button type="submit" variant="primary" disabled={!text.trim()}>
                Continue
            </Button>
        </Form>
    );
};

export default SymptomChecker;