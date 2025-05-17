// fe/src/components/Patient/DoctorList.js
import React, { useState, useEffect } from 'react';
import { Card, Row, Col, Form, InputGroup, Button, Spinner } from 'react-bootstrap';
import { Search } from 'react-bootstrap-icons';
import { useNavigate } from 'react-router-dom';
import appointmentService from '../../services/appointment.service';

const DoctorList = () => {
    const [doctors, setDoctors] = useState([]);
    const [loading, setLoading] = useState(true);
    const [searchTerm, setSearchTerm] = useState('');
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

    return (
        <div>
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

            <h4 className="mb-3">Available Doctors</h4>

            {loading ? (
                <div className="text-center p-5">
                    <Spinner animation="border" />
                </div>
            ) : (
                <Row>
                    {doctors.length === 0 ? (
                        <Col>
                            <Card className="text-center p-4">
                                <p>No doctors found matching your search criteria.</p>
                            </Card>
                        </Col>
                    ) : (
                        doctors.map((doctor) => (
                            <Col key={doctor.id} md={6} lg={4} className="mb-4">
                                <Card className="h-100 shadow-sm hover-card">
                                    <Card.Body>
                                        <Card.Title>Dr. {doctor.user.first_name} {doctor.user.last_name}</Card.Title>
                                        <Card.Subtitle className="mb-3 text-muted">
                                            {doctor.specialization}
                                        </Card.Subtitle>
                                        <div className="d-grid mt-4">
                                            <Button
                                                variant="outline-primary"
                                                onClick={() => handleViewSchedule(doctor.id)}
                                            >
                                                View Schedule & Book
                                            </Button>
                                        </div>
                                    </Card.Body>
                                </Card>
                            </Col>
                        ))
                    )}
                </Row>
            )}
        </div>
    );
};

export default DoctorList;