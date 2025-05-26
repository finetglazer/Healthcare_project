// fe/src/components/Dashboard/Dashboard.js
import React, { useEffect } from 'react';
import { Container, Row, Col } from 'react-bootstrap';
import Navbar from './Navbar';
import Sidebar from './Sidebar';
import { useSidebar } from '../../hooks/useSidebar';

const Dashboard = ({ user, onLogout, content }) => {
    // Use custom hook for sidebar management
    const {
        sidebarCollapsed,
        isMobile,
        mobileMenuOpen,
        toggleSidebar,
        closeMobileMenu
    } = useSidebar();

    // Add keyboard shortcut for toggling sidebar (Ctrl+B)
    useEffect(() => {
        const handleKeyPress = (e) => {
            if (e.ctrlKey && e.key === 'b') {
                e.preventDefault();
                toggleSidebar();
            }
        };

        window.addEventListener('keydown', handleKeyPress);
        return () => window.removeEventListener('keydown', handleKeyPress);
    }, [toggleSidebar]);

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
            <Navbar
                user={user}
                onLogout={onLogout}
                onToggleSidebar={toggleSidebar}
                isMobile={isMobile}
            />

            {/* Mobile overlay */}
            {isMobile && mobileMenuOpen && (
                <div
                    className="sidebar-overlay show"
                    onClick={closeMobileMenu}
                />
            )}

            <Container fluid className="p-0">
                <Row className="g-0">
                    {!isMobile && (
                        <Col
                            md={sidebarCollapsed ? 1 : 2}
                            className="sidebar-column"
                            style={{ transition: 'all 0.3s ease' }}
                        >
                            <Sidebar
                                userType={user?.is_doctor ? 'doctor' : 'patient'}
                                collapsed={sidebarCollapsed}
                                onToggle={toggleSidebar}
                                isMobile={isMobile}
                                mobileMenuOpen={mobileMenuOpen}
                                onCloseMobile={closeMobileMenu}
                            />
                        </Col>
                    )}

                    <Col
                        md={isMobile ? 12 : (sidebarCollapsed ? 11 : 10)}
                        className={`main-content-column p-4 ${sidebarCollapsed && !isMobile ? 'collapsed' : ''}`}
                        style={{ transition: 'all 0.3s ease' }}
                    >
                        {content || <WelcomeDashboard />}
                    </Col>
                </Row>
            </Container>

            {/* Mobile sidebar */}
            {isMobile && (
                <Sidebar
                    userType={user?.is_doctor ? 'doctor' : 'patient'}
                    collapsed={sidebarCollapsed}
                    onToggle={toggleSidebar}
                    isMobile={isMobile}
                    mobileMenuOpen={mobileMenuOpen}
                    onCloseMobile={closeMobileMenu}
                />
            )}
        </div>
    );
};

export default Dashboard;