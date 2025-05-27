// Updated Find Doctors Page with Chatbot Integration
// fe/src/components/Patient/DoctorList.js (Updated)

import React, { useState, useEffect } from 'react';
import { Card, Row, Col, Form, InputGroup, Button, Spinner, Alert } from 'react-bootstrap';
import { Search, Robot, PersonFill } from 'react-bootstrap-icons';
import { useNavigate } from 'react-router-dom';
import appointmentService from '../../services/appointment.service';

const DoctorList = () => {
    const [doctors, setDoctors] = useState([]);
    const [loading, setLoading] = useState(true);
    const [searchTerm, setSearchTerm] = useState('');
    const [showChatbotPrompt, setShowChatbotPrompt] = useState(true);
    const navigate = useNavigate();

    useEffect(() => {
        fetchDoctors();
    }, []);

    const fetchDoctors = async (search = '') => {
        setLoading(true);
        try {
            const data = await appointmentService.getDoctors(search);
            setDoctors(data);
        } catch (err) {
            console.error('Error fetching doctors', err);
        } finally {
            setLoading(false);
        }
    };

    const handleSearch = (e) => {
        e.preventDefault();
        fetchDoctors(searchTerm);
    };

    const handleViewSchedule = (doctorId) => {
        navigate(`/book-appointment/${doctorId}`);
    };

    // Chatbot Prompt Component
    const ChatbotPrompt = () => (
        <Card className="mb-4 border-primary shadow-sm">
            <Card.Body className="bg-gradient" style={{
                background: 'linear-gradient(135deg, #e3f2fd 0%, #f3e5f5 100%)'
            }}>
                <Row className="align-items-center">
                    <Col md={2} className="text-center">
                        <div
                            className="d-inline-flex align-items-center justify-content-center"
                            style={{
                                width: '80px',
                                height: '80px',
                                background: 'linear-gradient(135deg, #274375, #1e3557)',
                                borderRadius: '50%',
                                color: 'white',
                                fontSize: '32px'
                            }}
                        >
                            🤖
                        </div>
                    </Col>
                    <Col md={7}>
                        <div>
                            <h5 className="text-primary mb-2">
                                <Robot className="me-2" />
                                Need Help Choosing the Right Doctor?
                            </h5>
                            <p className="mb-2 text-muted">
                                Before browsing doctors, let our medical assistant help you identify your
                                symptoms and recommend the most suitable specialists for your condition.
                            </p>
                            <div className="d-flex align-items-center text-success">
                                <span className="me-2">✓</span>
                                <small>Quick symptom assessment (2-3 minutes)</small>
                            </div>
                            <div className="d-flex align-items-center text-success">
                                <span className="me-2">✓</span>
                                <small>Personalized doctor recommendations</small>
                            </div>
                        </div>
                    </Col>
                    <Col md={3} className="text-center">
                        <div className="d-grid gap-2">
                            <Button
                                variant="primary"
                                size="lg"
                                onClick={() => navigate('/symptom-checker')}
                                className="mb-2"
                            >
                                <Robot className="me-2" />
                                Start Assessment
                            </Button>
                            <Button
                                variant="outline-secondary"
                                size="sm"
                                onClick={() => setShowChatbotPrompt(false)}
                            >
                                Skip - Browse All Doctors
                            </Button>
                        </div>
                    </Col>
                </Row>
            </Card.Body>
        </Card>
    );

    return (
        <div>
            {/* Chatbot Integration Prompt */}
            {showChatbotPrompt && <ChatbotPrompt />}

            {/* Search Section */}
            <Card className="shadow-sm mb-4">
                <Card.Body>
                    <Form onSubmit={handleSearch}>
                        <InputGroup>
                            <Form.Control
                                placeholder="Search by name or specialization..."
                                value={searchTerm}
                                onChange={(e) => setSearchTerm(e.target.value)}
                            />
                            <Button variant="primary" type="submit">
                                <Search /> Search
                            </Button>
                        </InputGroup>
                    </Form>
                </Card.Body>
            </Card>

            {/* Header with count */}
            <div className="d-flex justify-content-between align-items-center mb-3">
                <h4 className="mb-0">
                    <PersonFill className="me-2 text-primary" />
                    Available Doctors
                </h4>
                {!loading && (
                    <Badge bg="primary" className="fs-6">
                        {doctors.length} doctor{doctors.length !== 1 ? 's' : ''} found
                    </Badge>
                )}
            </div>

            {/* Loading State */}
            {loading ? (
                <div className="text-center p-5">
                    <Spinner animation="border" variant="primary" />
                    <div className="mt-2">Loading doctors...</div>
                </div>
            ) : (
                <Row>
                    {doctors.length === 0 ? (
                        <Col>
                            <Card className="text-center p-4">
                                <Card.Body>
                                    <div className="mb-3" style={{ fontSize: '48px' }}>🔍</div>
                                    <h5>No doctors found</h5>
                                    <p className="text-muted">
                                        Try adjusting your search criteria or
                                        <Button
                                            variant="link"
                                            className="p-0 ms-1"
                                            onClick={() => navigate('/symptom-checker')}
                                        >
                                            use our symptom checker
                                        </Button>
                                        for personalized recommendations.
                                    </p>
                                </Card.Body>
                            </Card>
                        </Col>
                    ) : (
                        doctors.map((doctor) => (
                            <Col key={doctor.id} md={6} lg={4} className="mb-4">
                                <Card className="h-100 shadow-sm hover-card">
                                    <Card.Body>
                                        <div className="d-flex align-items-start mb-3">
                                            <div
                                                className="me-3 d-flex align-items-center justify-content-center"
                                                style={{
                                                    width: '50px',
                                                    height: '50px',
                                                    background: '#f8f9fa',
                                                    borderRadius: '50%',
                                                    fontSize: '20px'
                                                }}
                                            >
                                                👨‍⚕️
                                            </div>
                                            <div className="flex-grow-1">
                                                <Card.Title className="mb-1">
                                                    Dr. {doctor.user.first_name} {doctor.user.last_name}
                                                </Card.Title>
                                                <Card.Subtitle className="mb-2 text-muted">
                                                    {doctor.specialization}
                                                </Card.Subtitle>
                                            </div>
                                        </div>

                                        <div className="mt-auto">
                                            <div className="d-grid">
                                                <Button
                                                    variant="outline-primary"
                                                    onClick={() => handleViewSchedule(doctor.id)}
                                                >
                                                    View Schedule & Book
                                                </Button>
                                            </div>
                                        </div>
                                    </Card.Body>
                                </Card>
                            </Col>
                        ))
                    )}
                </Row>
            )}

            {/* Bottom CTA for Chatbot */}
            {!showChatbotPrompt && doctors.length > 0 && (
                <Card className="mt-4 bg-light border-primary">
                    <Card.Body className="text-center">
                        <p className="mb-2">
                            Still not sure which doctor to choose?
                        </p>
                        <Button
                            variant="primary"
                            size="sm"
                            onClick={() => navigate('/symptom-checker')}
                        >
                            <Robot className="me-2" />
                            Get Personalized Recommendations
                        </Button>
                    </Card.Body>
                </Card>
            )}
        </div>
    );
};

export default DoctorList;