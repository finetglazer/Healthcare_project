// Update fe/src/components/Dashboard/Dashboard.js
import React from 'react';
import { Container, Row, Col } from 'react-bootstrap';
import Navbar from './Navbar';
import Sidebar from './Sidebar';

const Dashboard = ({ user, onLogout, content }) => {
    const WelcomeDashboard = () => (
        <div className="dashboard-content">
            <h2>Welcome to Healthcare System</h2>
            <div className="card mt-4 p-4">
                <h4>{user?.is_doctor ? "Doctor Dashboard" : "Patient Dashboard"}</h4>
                <p>Welcome, {user?.first_name} {user?.last_name}</p>

                <div className="user-info mt-4">
                    <h5>Your Information</h5>
                    <p><strong>Username:</strong> {user?.username}</p>
                    <p><strong>Email:</strong> {user?.email}</p>
                    <p><strong>Phone:</strong> {user?.phone_number}</p>

                    {user?.is_doctor && (
                        <p><strong>Specialization:</strong> {user?.doctor_profile?.specialization}</p>
                    )}
                </div>

                <div className="dashboard-actions mt-4">
                    {user?.is_doctor ? (
                        <div>
                            <h5>Quick Actions</h5>
                            <p>Manage your schedule and appointments from the sidebar menu.</p>
                        </div>
                    ) : (
                        <div>
                            <h5>Quick Actions</h5>
                            <p>Book appointments and view your medical history from the sidebar menu.</p>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );

    return (
        <div className="dashboard-container">
            <Navbar user={user} onLogout={onLogout} />
            <Container fluid>
                <Row>
                    <Col md={2} className="px-0">
                        <Sidebar userType={user?.is_doctor ? 'doctor' : 'patient'} />
                    </Col>
                    <Col md={10} className="p-4">
                        {content || <WelcomeDashboard />}
                    </Col>
                </Row>
            </Container>
        </div>
    );
};

export default Dashboard;