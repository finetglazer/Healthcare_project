// Medical Chatbot UI Component
// fe/src/components/Chatbot/SymptomChecker.js (Fixed)

import React, { useState, useEffect, useRef } from 'react';
import { Container, Row, Col, Button, Form, Alert, ProgressBar } from 'react-bootstrap';
import { useNavigate } from 'react-router-dom';
import { chatbotQuestions, conversationSteps, analyzeSymptoms } from './ChatbotFlow';
import medicalImage from '../../assets/images/medical-image.jpg'; // Placeholder for medical image


const SymptomChecker = () => {
    const navigate = useNavigate();
    const [currentStep, setCurrentStep] = useState(conversationSteps.GREETING);
    const [conversation, setConversation] = useState([]);
    const [userInputs, setUserInputs] = useState({});
    const [analysis, setAnalysis] = useState(null);
    const [isAnalyzing, setIsAnalyzing] = useState(false);
    const messagesEndRef = useRef(null);

    // Auto scroll to bottom
    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [conversation]);

    // Initialize conversation
    useEffect(() => {
        addBotMessage(chatbotQuestions[conversationSteps.GREETING].message);
    }, []);

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
            message,
            timestamp: new Date()
        }]);
    };

    const handleUserInput = async (input) => {
        addUserMessage(Array.isArray(input) ? input.join(', ') : input);

        // Store user input
        const newInputs = { ...userInputs, [currentStep]: input };
        setUserInputs(newInputs);

        // Get next step
        const nextStep = chatbotQuestions[currentStep].next;

        if (nextStep === conversationSteps.ANALYSIS) {
            // Analyze symptoms
            setIsAnalyzing(true);
            setTimeout(() => {
                const result = analyzeSymptoms(newInputs);
                setAnalysis(result);
                showAnalysisResults(result);
                setIsAnalyzing(false);
            }, 2000);
        } else {
            // Continue conversation
            setCurrentStep(nextStep);
            setTimeout(() => {
                addBotMessage(chatbotQuestions[nextStep].message);
            }, 500);
        }
    };

    const showAnalysisResults = (result) => {
        const [condition, confidence] = result.mostLikely;
        const { specialist, urgency, note } = result.recommendation;

        const resultMessage = `
Based on your symptoms, you might have: **${condition}** (${Math.round(confidence * 100)}% confidence)

**Recommendation:**
- See a ${specialist}
- Urgency: ${urgency}
- ${note}

Would you like to find ${specialist.toLowerCase()}s in our system?
`;

        addBotMessage(resultMessage);
    };

    const getProgressPercentage = () => {
        const steps = Object.values(conversationSteps);
        const currentIndex = steps.indexOf(currentStep);
        return ((currentIndex + 1) / steps.length) * 100;
    };

    const renderQuestionInput = () => {
        const question = chatbotQuestions[currentStep];
        if (!question || currentStep === conversationSteps.ANALYSIS) return null;

        switch (question.type) {
            case 'multiple_choice':
                return (
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
                );

            case 'scale':
                return (
                    <div>
                        <div className="d-flex justify-content-between mb-2">
                            <span>Mild (1)</span>
                            <span>Severe (10)</span>
                        </div>
                        <div className="d-flex gap-1 justify-content-center">
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
                );

            case 'checkbox':
                return <CheckboxInput options={question.options} onSubmit={handleUserInput} />;

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
                                        fontSize: '24px'
                                    }}
                                >
                                    🤖
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
                            <ProgressBar
                                now={getProgressPercentage()}
                                variant="light"
                                style={{ height: '8px' }}
                            />
                        </div>

                        {/* Info */}
                        <div className="p-4 mt-auto">
                            <Alert variant="light" className="mb-0">
                                <small>
                                    <strong>Note:</strong> This is for guidance only.
                                    Always consult a healthcare professional for accurate diagnosis.
                                </small>
                            </Alert>
                        </div>
                    </div>
                </Col>

                {/* Chat Area */}
                <Col md={9} className="d-flex flex-column p-0">
                    {/* Header */}
                    <div className="bg-white border-bottom p-3">
                        <div className="d-flex justify-content-between align-items-center">
                            <h4 className="mb-0">Symptom Assessment</h4>
                            <Button
                                variant="outline-secondary"
                                size="sm"
                                onClick={() => navigate('/find-doctors')}
                            >
                                Skip to Doctor List
                            </Button>
                        </div>
                    </div>

                    {/* Messages */}
                    <div className="flex-grow-1 p-4" style={{ overflowY: 'auto' }}>
                        {conversation.map((msg, index) => (
                            <div
                                key={index}
                                className={`d-flex mb-3 ${msg.type === 'user' ? 'justify-content-end' : ''}`}
                            >
                                <div
                                    className={`rounded-3 p-3 max-width-75 ${
                                        msg.type === 'bot'
                                            ? 'bg-light text-dark'
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
                onClick={() => onSubmit(selected.length > 0 ? selected : ['None'])}
                className="mt-3"
                disabled={selected.length === 0 && !selected.includes('None of the above')}
            >
                Continue
            </Button>
        </div>
    );
};

export default SymptomChecker;