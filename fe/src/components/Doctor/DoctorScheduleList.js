// fe/src/components/Doctor/DoctorScheduleList.js
import React, { useState, useEffect } from 'react';
import { Card, Table, Badge, Button, Spinner, Alert } from 'react-bootstrap';
import { format } from 'date-fns';
import appointmentService from '../../services/appointment.service';

const DoctorScheduleList = () => {
    const [schedules, setSchedules] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    useEffect(() => {
        fetchSchedules();
    }, []);

    const fetchSchedules = async () => {
        setLoading(true);
        try {
            const data = await appointmentService.getDoctorSchedules();
            setSchedules(data);
        } catch (err) {
            setError('Failed to load schedules');
        } finally {
            setLoading(false);
        }
    };

    const handleDelete = async (id) => {
        if (window.confirm('Are you sure you want to delete this schedule?')) {
            try {
                await appointmentService.deleteSchedule(id);
                setSchedules(schedules.filter(schedule => schedule.id !== id));
            } catch (err) {
                setError('Failed to delete schedule');
            }
        }
    };

    if (loading) {
        return <div className="text-center p-5"><Spinner animation="border" /></div>;
    }

    return (
        <Card className="shadow-sm">
            <Card.Header className="bg-white">
                <h4 className="mb-0">My Schedules</h4>
            </Card.Header>
            <Card.Body>
                {error && <Alert variant="danger">{error}</Alert>}

                {schedules.length === 0 ? (
                    <div className="text-center p-4">
                        <p className="mb-0">You haven't created any schedules yet.</p>
                    </div>
                ) : (
                    <Table responsive hover>
                        <thead>
                        <tr>
                            <th>Date</th>
                            <th>Time</th>
                            <th>Duration</th>
                            <th>Status</th>
                            <th>Actions</th>
                        </tr>
                        </thead>
                        <tbody>
                        {schedules.map((schedule) => (
                            <tr key={schedule.id}>
                                <td>{format(new Date(schedule.date), 'MMMM dd, yyyy')}</td>
                                <td>{schedule.start_time} - {schedule.end_time}</td>
                                <td>{schedule.slot_duration} minutes</td>
                                <td>
                                    <Badge bg={schedule.is_available ? 'success' : 'secondary'}>
                                        {schedule.is_available ? 'Available' : 'Fully Booked'}
                                    </Badge>
                                </td>
                                <td>
                                    <Button
                                        variant="outline-danger"
                                        size="sm"
                                        onClick={() => handleDelete(schedule.id)}
                                    >
                                        Delete
                                    </Button>
                                </td>
                            </tr>
                        ))}
                        </tbody>
                    </Table>
                )}
            </Card.Body>
        </Card>
    );
};

export default DoctorScheduleList;