// fe/src/components/Doctor/DoctorAppointments.js
import React, { useState, useEffect } from 'react';
import { Card, Table, Badge, Button, Spinner, Alert, Tab, Tabs } from 'react-bootstrap';
import { format } from 'date-fns';
import appointmentService from '../../services/appointment.service';

const DoctorAppointments = () => {
    const [appointments, setAppointments] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    useEffect(() => {
        fetchAppointments();
    }, []);

    const fetchAppointments = async () => {
        setLoading(true);
        try {
            const data = await appointmentService.getDoctorAppointments();
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
    const confirmedAppointments = appointments.filter(app => app.status === 'CONFIRMED');
    const cancelledAppointments = appointments.filter(app => app.status === 'CANCELLED');
    const completedAppointments = appointments.filter(app => app.status === 'COMPLETED');

    if (loading) {
        return <div className="text-center p-5"><Spinner animation="border" /></div>;
    }

    const renderAppointmentsTable = (appointmentList) => (
        appointmentList.length === 0 ? (
            <div className="text-center p-4">
                <p className="mb-0">No appointments found.</p>
            </div>
        ) : (
            <Table responsive hover>
                <thead>
                <tr>
                    <th>Date</th>
                    <th>Time</th>
                    <th>Patient</th>
                    <th>Contact</th>
                    <th>Reason</th>
                    <th>Actions</th>
                </tr>
                </thead>
                <tbody>
                {appointmentList.map((appointment) => (
                    <tr key={appointment.id}>
                        <td>{format(new Date(appointment.date), 'MMMM dd, yyyy')}</td>
                        <td>{appointment.time} - {appointment.end_time}</td>
                        <td>{appointment.patient_details.name}</td>
                        <td>
                            <div>{appointment.patient_details.email}</div>
                            <div>{appointment.patient_details.phone}</div>
                        </td>
                        <td>{appointment.reason}</td>
                        <td>
                            {appointment.status === 'CONFIRMED' && (
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
                    <Tab eventKey="upcoming" title={`Upcoming (${confirmedAppointments.length})`}>
                        {renderAppointmentsTable(confirmedAppointments)}
                    </Tab>
                    <Tab eventKey="cancelled" title={`Cancelled (${cancelledAppointments.length})`}>
                        {renderAppointmentsTable(cancelledAppointments)}
                    </Tab>
                    <Tab eventKey="completed" title={`Completed (${completedAppointments.length})`}>
                        {renderAppointmentsTable(completedAppointments)}
                    </Tab>
                </Tabs>
            </Card.Body>
        </Card>
    );
};

export default DoctorAppointments;