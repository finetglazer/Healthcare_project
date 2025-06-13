// fe/src/components/Chatbot/SymptomChecker.js - Fixed Complete Version
import React, { useState, useEffect, useRef } from 'react';
import { Container, Row, Col, Button, Form, Alert, ProgressBar } from 'react-bootstrap';
import { useNavigate } from 'react-router-dom';
import { chatbotQuestions, conversationSteps, analyzeSymptoms } from './ChatbotFlow';

const SymptomChecker = () => {
    const navigate = useNavigate();
    const [currentStep, setCurrentStep] = useState(conversationSteps.GREETING);
    const [conversation, setConversation] = useState([]);
    const [userInputs, setUserInputs] = useState({});
    const [analysis, setAnalysis] = useState(null);
    const [isAnalyzing, setIsAnalyzing] = useState(false);
    const [progress, setProgress] = useState(0);
    const messagesEndRef = useRef(null);

    // Auto scroll to bottom
    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [conversation]);

    // Initialize conversation
    // Initialize conversation
    useEffect(() => {
        if (conversation.length === 0) {
            addBotMessage(chatbotQuestions[conversationSteps.GREETING].message);
        }
    }, []);

    // Update progress based on current step
    const updateProgress = () => {
        const steps = Object.keys(conversationSteps);
        const currentIndex = steps.indexOf(currentStep);
        const progressPercentage = ((currentIndex + 1) / steps.length) * 100;
        setProgress(Math.min(progressPercentage, 85)); // Max 85% until analysis complete
    };

    useEffect(() => {
        updateProgress();
    }, [currentStep]);

    const addBotMessage = (message) => {
        // Ensure message is always a string
        const messageStr = typeof message === 'string' ? message : JSON.stringify(message);
        setConversation(prev => [...prev, {
            type: 'bot',
            message: messageStr,
            timestamp: new Date()
        }]);
    };

    const addUserMessage = (message) => {
        // Handle arrays and objects
        let messageStr;
        if (Array.isArray(message)) {
            messageStr = message.join(', ');
        } else if (typeof message === 'object') {
            messageStr = JSON.stringify(message);
        } else {
            messageStr = String(message);
        }

        setConversation(prev => [...prev, {
            type: 'user',
            message: messageStr,
            timestamp: new Date()
        }]);
    };

    const handleUserInput = async (input) => {
        try {
            addUserMessage(input);

            // Store user input
            const newInputs = { ...userInputs, [currentStep]: input };
            setUserInputs(newInputs);

            // Get current question to determine next step
            const currentQuestion = chatbotQuestions[currentStep];
            if (!currentQuestion) {
                throw new Error('Invalid conversation step');
            }

            const nextStep = currentQuestion.next;

            if (nextStep === conversationSteps.ANALYSIS) {
                // Analyze symptoms
                setIsAnalyzing(true);
                addBotMessage("Let me analyze your symptoms...");

                setTimeout(() => {
                    try {
                        const result = analyzeSymptoms(newInputs);
                        setAnalysis(result);
                        showAnalysisResults(result);
                        setProgress(100);
                        setIsAnalyzing(false);
                    } catch (error) {
                        console.error('Analysis error:', error);
                        addBotMessage("I'm sorry, there was an error analyzing your symptoms. Please try again or consult a healthcare professional.");
                        setIsAnalyzing(false);
                    }
                }, 2000);
            } else {
                // Continue conversation
                setCurrentStep(nextStep);
                setTimeout(() => {
                    const nextMessage = chatbotQuestions[nextStep]?.message || "Please continue...";
                    addBotMessage(nextMessage);
                }, 500);
            }
        } catch (error) {
            console.error('Error handling user input:', error);
            addBotMessage("I'm sorry, something went wrong. Let's try again.");
        }
    };

    const showAnalysisResults = (result) => {
        if (!result || !result.mostLikely) {
            addBotMessage("I couldn't analyze your symptoms properly. Please consult a healthcare professional.");
            return;
        }

        const [condition, confidence] = result.mostLikely;
        const recommendation = result.recommendation || {};
        const { specialist = "healthcare professional", urgency = "routine", note = "Please consult a medical professional" } = recommendation;

        const urgencyLevel = urgency.toLowerCase();
        const urgencyColor = urgencyLevel === 'urgent' ? 'danger' : urgencyLevel === 'moderate' ? 'warning' : 'info';

        const resultMessage = `Based on your symptoms, you might have: **${condition}** 

**Confidence Level:** ${Math.round(confidence * 100)}%

**Recommendation:**
- See a ${specialist}
- Urgency: ${urgency}
- ${note}

**Medical Disclaimer:** This is not a medical diagnosis. Always consult with a qualified healthcare professional for proper medical advice.

Would you like to find ${specialist.toLowerCase()}s in our system?`;

        addBotMessage(resultMessage);

        // Add other possible conditions if available
        if (result.otherConditions && result.otherConditions.length > 0) {
            const otherConditionsMessage = "**Other possible conditions:**\n" +
                result.otherConditions.map(([cond, conf]) =>
                    `- ${cond}: ${Math.round(conf * 100)}%`
                ).join('\n');

            setTimeout(() => addBotMessage(otherConditionsMessage), 1000);
        }
    };

    const getCurrentQuestion = () => {
        return chatbotQuestions[currentStep];
    };

    const renderQuestionInput = () => {
        const question = getCurrentQuestion();
        if (!question || analysis) return null;

        switch (question.type) {
            case 'multiple_choice':
                return (
                    <div>
                        <div className="mb-3">
                            {question.options?.map((option, index) => (
                                <Button
                                    key={index}
                                    variant="outline-primary"
                                    className="me-2 mb-2"
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
                            <label className="form-label">Rate from {question.min || 1} to {question.max || 10}:</label>
                            <div className="d-flex gap-2 flex-wrap">
                                {Array.from({ length: (question.max || 10) - (question.min || 1) + 1 }, (_, i) => (
                                    <Button
                                        key={i}
                                        variant="outline-primary"
                                        size="sm"
                                        onClick={() => handleUserInput((question.min || 1) + i)}
                                        style={{ minWidth: '40px' }}
                                    >
                                        {(question.min || 1) + i}
                                    </Button>
                                ))}
                            </div>
                        </div>
                    </div>
                );

            case 'checkbox':
                return <CheckboxInput options={question.options || []} onSubmit={handleUserInput} />;

            case 'text':
                return <TextInput onSubmit={handleUserInput} placeholder={question.placeholder} />;

            default:
                return (
                    <div>
                        <Button variant="primary" onClick={() => handleUserInput("Continue")}>
                            Continue
                        </Button>
                    </div>
                );
        }
    };

    const renderMessage = (msg) => {
        // Ensure message is a string
        const messageStr = typeof msg.message === 'string' ? msg.message : String(msg.message || '');

        return messageStr.split('\n').map((line, i) => (
            <div key={i}>
                {line.includes('**') ? (
                    <span dangerouslySetInnerHTML={{
                        __html: line.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                    }} />
                ) : line}
            </div>
        ));
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
                                    🏥
                                </div>
                                <div>
                                    <h5 className="mb-0">Medical Assistant</h5>
                                    <small className="text-white-50">Symptom Checker</small>
                                </div>
                            </div>
                        </div>

                        {/* Progress */}
                        <div className="p-4">
                            <div className="mb-2">
                                <small>Progress</small>
                            </div>
                            <ProgressBar now={progress} className="mb-2" />
                            <small className="text-white-50">{Math.round(progress)}% Complete</small>
                        </div>

                        {/* Medical Disclaimer */}
                        <div className="p-4 border-top border-white border-opacity-25 mt-auto">
                            <Alert variant="warning" className="mb-0 small">
                                <strong>⚠️ Medical Disclaimer:</strong> This tool is for informational purposes only and does not replace professional medical advice. Always consult a healthcare professional for medical concerns.
                            </Alert>
                        </div>
                    </div>
                </Col>

                {/* Main Chat Area */}
                <Col md={9} className="p-0 d-flex flex-column">
                    {/* Chat Messages */}
                    <div className="flex-grow-1 p-4" style={{ overflowY: 'auto', maxHeight: 'calc(100vh - 200px)' }}>
                        {conversation.map((msg, index) => (
                            <div
                                key={index}
                                className={`d-flex mb-3 ${msg.type === 'user' ? 'justify-content-end' : 'justify-content-start'}`}
                            >
                                <div
                                    className={`p-3 rounded-3 ${
                                        msg.type === 'user'
                                            ? 'bg-primary text-white'
                                            : 'bg-light text-dark'
                                    }`}
                                    style={{ maxWidth: '75%' }}
                                >
                                    {renderMessage(msg)}
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
                disabled={selected.length === 0}
            >
                Continue
            </Button>
        </div>
    );
};

// Text input component
const TextInput = ({ onSubmit, placeholder = "Type your answer..." }) => {
    const [value, setValue] = useState('');

    const handleSubmit = () => {
        if (value.trim()) {
            onSubmit(value.trim());
            setValue('');
        }
    };

    const handleKeyPress = (e) => {
        if (e.key === 'Enter') {
            handleSubmit();
        }
    };

    return (
        <div className="d-flex gap-2">
            <Form.Control
                type="text"
                value={value}
                onChange={(e) => setValue(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder={placeholder}
            />
            <Button
                variant="primary"
                onClick={handleSubmit}
                disabled={!value.trim()}
            >
                Send
            </Button>
        </div>
    );
};

export default SymptomChecker;