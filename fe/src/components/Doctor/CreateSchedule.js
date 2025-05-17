// fe/src/components/Doctor/CreateSchedule.js
import React, { useState } from 'react';
import { Form, Button, Card, Row, Col, Alert } from 'react-bootstrap';
import appointmentService from '../../services/appointment.service';

const CreateSchedule = () => {
    const [scheduleData, setScheduleData] = useState({
        date: '',
        start_time: '',
        end_time: '',
        slot_duration: 30,
    });

    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');
    const [loading, setLoading] = useState(false);

    const handleChange = (e) => {
        const { name, value } = e.target;
        setScheduleData({
            ...scheduleData,
            [name]: value
        });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError('');
        setSuccess('');

        try {
            await appointmentService.createSchedule(scheduleData);
            setSuccess('Schedule created successfully');
            setScheduleData({
                date: '',
                start_time: '',
                end_time: '',
                slot_duration: 30,
            });
        } catch (err) {
            setError('Failed to create schedule. Please check your inputs.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <Card className="shadow-sm">
            <Card.Header className="bg-primary text-white">
                <h4 className="mb-0">Create New Schedule</h4>
            </Card.Header>
            <Card.Body>
                {error && <Alert variant="danger">{error}</Alert>}
                {success && <Alert variant="success">{success}</Alert>}

                <Form onSubmit={handleSubmit}>
                    <Form.Group className="mb-3">
                        <Form.Label>Date</Form.Label>
                        <Form.Control
                            type="date"
                            name="date"
                            value={scheduleData.date}
                            onChange={handleChange}
                            required
                            min={new Date().toISOString().split('T')[0]}
                        />
                    </Form.Group>

                    <Row>
                        <Col md={6}>
                            <Form.Group className="mb-3">
                                <Form.Label>Start Time</Form.Label>
                                <Form.Control
                                    type="time"
                                    name="start_time"
                                    value={scheduleData.start_time}
                                    onChange={handleChange}
                                    required
                                />
                            </Form.Group>
                        </Col>
                        <Col md={6}>
                            <Form.Group className="mb-3">
                                <Form.Label>End Time</Form.Label>
                                <Form.Control
                                    type="time"
                                    name="end_time"
                                    value={scheduleData.end_time}
                                    onChange={handleChange}
                                    required
                                />
                            </Form.Group>
                        </Col>
                    </Row>

                    <Form.Group className="mb-4">
                        <Form.Label>Appointment Duration</Form.Label>
                        <Form.Select
                            name="slot_duration"
                            value={scheduleData.slot_duration}
                            onChange={handleChange}
                            required
                        >
                            <option value={30}>30 minutes</option>
                            <option value={60}>1 hour</option>
                            <option value={90}>1 hour 30 minutes</option>
                            <option value={120}>2 hours</option>
                        </Form.Select>
                    </Form.Group>

                    <div className="d-grid">
                        <Button
                            variant="primary"
                            type="submit"
                            className="py-2"
                            disabled={loading}
                        >
                            {loading ? 'Creating...' : 'Create Schedule'}
                        </Button>
                    </div>
                </Form>
            </Card.Body>
        </Card>
    );
};

export default CreateSchedule;