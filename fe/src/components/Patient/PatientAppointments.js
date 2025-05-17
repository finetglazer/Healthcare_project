// fe/src/components/Patient/PatientAppointments.js
import React, { useState, useEffect } from 'react';
import { Card, Table, Badge, Button, Spinner, Alert, Tab, Tabs } from 'react-bootstrap';
import { format } from 'date-fns';
import appointmentService from '../../services/appointment.service';

const PatientAppointments = () => {
    const [appointments, setAppointments] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    useEffect(() => {
        fetchAppointments();
    }, []);

    const fetchAppointments = async () => {
        setLoading(true);
        try {
            const data = await appointmentService.getPatientAppointments();
            setAppointments(data);
        } catch (err) {
            setError('Failed to load appointments');
        } finally {
            setLoading(false);
        }
    };

    const handleCancel = async (id) => {
        if (window.confirm('Are you sure you want to cancel this appointment?')) {
            try {
                const updated = await appointmentService.cancelAppointment(id);
                setAppointments(appointments.map(app =>
                    app.id === id ? updated : app
                ));
            } catch (err) {
                setError('Failed to cancel appointment');
            }
        }
    };

    // Filter appointments by status
    const upcomingAppointments = appointments.filter(app =>
        app.status === 'CONFIRMED' && new Date(app.date) >= new Date()
    );
    const pastAppointments = appointments.filter(app =>
        app.status === 'CONFIRMED' && new Date(app.date) < new Date()
    );
    const cancelledAppointments = appointments.filter(app => app.status === 'CANCELLED');

    if (loading) {
        return <div className="text-center p-5"><Spinner animation="border" /></div>;
    }

    const getStatusBadge = (status, date) => {
        if (status === 'CANCELLED') {
            return <Badge bg="danger">Cancelled</Badge>;
        } else if (new Date(date) < new Date()) {
            return <Badge bg="secondary">Completed</Badge>;
        } else {
            return <Badge bg="success">Upcoming</Badge>;
        }
    };

    const renderAppointmentsTable = (appointmentList) => (
        appointmentList.length === 0 ? (
            <div className="text-center p-4">
                <p className="mb-0">No appointments found.</p>
            </div>
        ) : (
            <Table responsive hover>
                <thead>
                <tr>
                    <th>Doctor</th>
                    <th>Specialization</th>
                    <th>Date</th>
                    <th>Time</th>
                    <th>Status</th>
                    <th>Reason</th>
                    <th>Actions</th>
                </tr>
                </thead>
                <tbody>
                {appointmentList.map((appointment) => (
                    <tr key={appointment.id}>
                        <td>Dr. {appointment.doctor_details.name}</td>
                        <td>{appointment.doctor_details.specialization}</td>
                        <td>{format(new Date(appointment.date), 'MMMM dd, yyyy')}</td>
                        <td>{appointment.time.substring(0, 5)} - {appointment.end_time.substring(0, 5)}</td>
                        <td>{getStatusBadge(appointment.status, appointment.date)}</td>
                        <td>{appointment.reason}</td>
                        <td>
                            {appointment.status === 'CONFIRMED' && new Date(appointment.date) >= new Date() && (
                                <Button
                                    variant="outline-danger"
                                    size="sm"
                                    onClick={() => handleCancel(appointment.id)}
                                >
                                    Cancel
                                </Button>
                            )}
                        </td>
                    </tr>
                ))}
                </tbody>
            </Table>
        )
    );

    return (
        <Card className="shadow-sm">
            <Card.Header className="bg-white">
                <h4 className="mb-0">My Appointments</h4>
            </Card.Header>
            <Card.Body>
                {error && <Alert variant="danger">{error}</Alert>}

                <Tabs defaultActiveKey="upcoming" className="mb-4">
                    <Tab eventKey="upcoming" title={`Upcoming (${upcomingAppointments.length})`}>
                        {renderAppointmentsTable(upcomingAppointments)}
                    </Tab>
                    <Tab eventKey="past" title={`Past (${pastAppointments.length})`}>
                        {renderAppointmentsTable(pastAppointments)}
                    </Tab>
                    <Tab eventKey="cancelled" title={`Cancelled (${cancelledAppointments.length})`}>
                        {renderAppointmentsTable(cancelledAppointments)}
                    </Tab>
                </Tabs>
            </Card.Body>
        </Card>
    );
};

export default PatientAppointments;