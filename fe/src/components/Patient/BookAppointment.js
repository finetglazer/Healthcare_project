// fe/src/components/Patient/BookAppointment.js
import React, { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Card, Form, Button, Row, Col, Alert, Spinner, ListGroup } from 'react-bootstrap';
import { format, parse, isAfter } from 'date-fns';
import appointmentService from '../../services/appointment.service';

const BookAppointment = () => {
    const { doctorId } = useParams();
    const navigate = useNavigate();

    const [doctor, setDoctor] = useState(null);
    const [schedules, setSchedules] = useState([]);
    const [selectedSchedule, setSelectedSchedule] = useState(null);
    const [selectedTime, setSelectedTime] = useState('');
    const [reason, setReason] = useState('');
    const [availableSlots, setAvailableSlots] = useState([]);

    const [loading, setLoading] = useState(true);
    const [bookingLoading, setBookingLoading] = useState(false);
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');

    const fetchDoctorAndSchedules = useCallback(async () => {
        setLoading(true);
        try {
            // In a real implementation, you'd fetch the doctor details
            const doctorsData = await appointmentService.getDoctors();
            const doctorData = doctorsData.find(d => d.id === parseInt(doctorId));

            if (doctorData) {
                setDoctor(doctorData);
            }

            const schedulesData = await appointmentService.getDoctorAvailableSchedules(doctorId);
            setSchedules(schedulesData);
        } catch (err) {
            setError('Failed to load doctor information');
        } finally {
            setLoading(false);
        }
    }, [doctorId]);

    useEffect(() => {
        fetchDoctorAndSchedules();
    }, [fetchDoctorAndSchedules]);

    useEffect(() => {
        if (selectedSchedule) {
            generateTimeSlots(selectedSchedule);
        }
    }, [selectedSchedule]);

    const generateTimeSlots = (schedule) => {
        const { start_time, end_time, slot_duration } = schedule;
        const slots = [];

        let currentTime = parse(start_time, 'HH:mm:ss', new Date());
        const endTimeObj = parse(end_time, 'HH:mm:ss', new Date());

        while (isAfter(endTimeObj, currentTime)) {
            slots.push(format(currentTime, 'HH:mm'));
            currentTime = new Date(currentTime.getTime() + slot_duration * 60000);
        }

        setAvailableSlots(slots);
    };

    const handleScheduleSelect = (schedule) => {
        setSelectedSchedule(schedule);
        setSelectedTime('');
    };

    const handleSubmit = async (e) => {
        e.preventDefault();

        if (!selectedSchedule || !selectedTime || !reason) {
            setError('Please fill out all required fields');
            return;
        }

        setBookingLoading(true);
        setError('');

        try {
            await appointmentService.bookAppointment({
                schedule_id: selectedSchedule.id,
                time: selectedTime,
                reason: reason
            });

            setSuccess('Appointment booked successfully!');

            // Reset form
            setSelectedSchedule(null);
            setSelectedTime('');
            setReason('');

            // Redirect after short delay
            setTimeout(() => {
                navigate('/my-appointments');
            }, 2000);
        } catch (err) {
            setError('Failed to book appointment. Please try again.');
        } finally {
            setBookingLoading(false);
        }
    };

    if (loading) {
        return <div className="text-center p-5"><Spinner animation="border" /></div>;
    }

    return (
        <div>
            <h4 className="mb-4">Book an Appointment</h4>

            {doctor && (
                <Card className="mb-4 shadow-sm">
                    <Card.Body>
                        <Card.Title>Dr. {doctor.user.first_name} {doctor.user.last_name}</Card.Title>
                        <Card.Subtitle className="mb-3 text-muted">
                            {doctor.specialization}
                        </Card.Subtitle>
                    </Card.Body>
                </Card>
            )}

            {error && <Alert variant="danger">{error}</Alert>}
            {success && <Alert variant="success">{success}</Alert>}

            <Form onSubmit={handleSubmit}>
                <Row>
                    <Col md={6}>
                        <Card className="mb-4 shadow-sm">
                            <Card.Header className="bg-light">
                                <h5 className="mb-0">Available Dates</h5>
                            </Card.Header>
                            <Card.Body style={{ maxHeight: '300px', overflowY: 'auto' }}>
                                {schedules.length === 0 ? (
                                    <div className="text-center p-3">
                                        <p className="mb-0">No available schedules found for this doctor.</p>
                                    </div>
                                ) : (
                                    <ListGroup>
                                        {schedules.map((schedule) => (
                                            <ListGroup.Item
                                                key={schedule.id}
                                                action
                                                active={selectedSchedule?.id === schedule.id}
                                                onClick={() => handleScheduleSelect(schedule)}
                                                className="d-flex justify-content-between align-items-center"
                                            >
                                                <div>
                                                    <div className="fw-bold">
                                                        {format(new Date(schedule.date), 'EEEE, MMMM d, yyyy')}
                                                    </div>
                                                    <div className="text-muted">
                                                        {schedule.start_time.substring(0, 5)} - {schedule.end_time.substring(0, 5)}
                                                    </div>
                                                </div>
                                                <div>
                                                    <span className="badge bg-info rounded-pill">
                                                        {schedule.slot_duration} min slots
                                                    </span>
                                                </div>
                                            </ListGroup.Item>
                                        ))}
                                    </ListGroup>
                                )}
                            </Card.Body>
                        </Card>
                    </Col>

                    <Col md={6}>
                        <Card className="mb-4 shadow-sm">
                            <Card.Header className="bg-light">
                                <h5 className="mb-0">Select Time Slot</h5>
                            </Card.Header>
                            <Card.Body style={{ height: '300px', overflowY: 'auto' }}>
                                {!selectedSchedule ? (
                                    <div className="text-center p-3">
                                        <p className="mb-0">Please select a date first</p>
                                    </div>
                                ) : availableSlots.length === 0 ? (
                                    <div className="text-center p-3">
                                        <p className="mb-0">No available time slots for this date</p>
                                    </div>
                                ) : (
                                    <div className="d-flex flex-wrap gap-2">
                                        {availableSlots.map((slot) => (
                                            <Button
                                                key={slot}
                                                variant={selectedTime === slot ? "primary" : "outline-primary"}
                                                size="sm"
                                                onClick={() => setSelectedTime(slot)}
                                                className="mb-2"
                                            >
                                                {slot}
                                            </Button>
                                        ))}
                                    </div>
                                )}
                            </Card.Body>
                        </Card>
                    </Col>
                </Row>

                <Card className="shadow-sm mb-4">
                    <Card.Header className="bg-light">
                        <h5 className="mb-0">Appointment Details</h5>
                    </Card.Header>
                    <Card.Body>
                        <Form.Group className="mb-3">
                            <Form.Label>Reason for Visit*</Form.Label>
                            <Form.Control
                                as="textarea"
                                rows={3}
                                placeholder="Please describe your symptoms or reason for the appointment"
                                value={reason}
                                onChange={(e) => setReason(e.target.value)}
                                required
                            />
                        </Form.Group>

                        <div className="d-grid mt-4">
                            <Button
                                variant="primary"
                                type="submit"
                                className="py-2"
                                disabled={!selectedSchedule || !selectedTime || !reason || bookingLoading}
                            >
                                {bookingLoading ? 'Booking...' : 'Book Appointment'}
                            </Button>
                        </div>
                    </Card.Body>
                </Card>
            </Form>
        </div>
    );
};

export default BookAppointment;