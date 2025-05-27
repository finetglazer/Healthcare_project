// fe/src/components/Dashboard/Dashboard.js
import React, { useEffect } from 'react';
import { Container, Row, Col, Card } from 'react-bootstrap';
import { useNavigate } from 'react-router-dom';
import Navbar from './Navbar';
import Sidebar from './Sidebar';
import { useSidebar } from '../../hooks/useSidebar';

// Enhanced Hero Section Component
const HealthcareHeroSection = ({
                                   title = "Your Health, Our Priority",
                                    str = "Good health is the first step of living well",
                                   backgroundImage = "https://cdn.who.int/media/images/default-source/who_homepage/world-health-assembly-committee-a.tmb-1920v.jpg?sfvrsn=d8f2a319_6"
                               }) => {
    return (
        <div className="healthcare-hero-wrapper mb-4">
            <div
                className="healthcare-hero-inner"
                style={{
                    // 1. ENHANCED TRANSPARENCY - Reduced opacity from 0.7/0.8 to 0.2/0.3
                    backgroundImage: `linear-gradient(rgba(39, 67, 117, 0.2), rgba(30, 53, 87, 0.3)), url(${backgroundImage})`
                }}
            >
                <div className="container hero-container">
                    <div className="hero-content">
                        {/* 2. ONLY THE TITLE - Removed subtitle and button */}
                        <h1 className="hero-title">
                            {title}
                        </h1>
                        <h5 className="text-white">
                            {str}
                        </h5>
                    </div>
                </div>
            </div>
        </div>
    );
};

const Dashboard = ({ user, onLogout, content }) => {
    const navigate = useNavigate();

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
            {/* Hero Section - Simplified */}
            <HealthcareHeroSection
                title="Your Health, Our Priority"
                backgroundImage="https://cdn.who.int/media/images/default-source/who_homepage/world-health-assembly-committee-a.tmb-1920v.jpg?sfvrsn=d8f2a319_6"
            />

            {/* Welcome Section */}
            <Row className="mb-4">
                <Col>
                    <Card className="shadow-sm">
                        <Card.Body>
                            <h2>Welcome to Healthcare System</h2>
                            <p className="lead">Hello, {user?.first_name} {user?.last_name}!</p>

                            <div className="user-info mt-4">
                                <h5>Your Information</h5>
                                <Row>
                                    <Col md={6}>
                                        <p><strong>Username:</strong> {user?.username}</p>
                                        <p><strong>Email:</strong> {user?.email}</p>
                                    </Col>
                                    <Col md={6}>
                                        <p><strong>Phone:</strong> {user?.phone_number}</p>
                                        <p><strong>Role:</strong> {user?.is_doctor ? 'Doctor' : 'Patient'}</p>
                                    </Col>
                                </Row>

                                {user?.is_doctor && (
                                    <p><strong>Specialization:</strong> {user?.doctor_profile?.specialization}</p>
                                )}
                            </div>
                        </Card.Body>
                    </Card>
                </Col>
            </Row>

            {/* Quick Actions */}
            <Row>
                <Col>
                    <Card className="shadow-sm">
                        <Card.Body>
                            <h5>Quick Actions</h5>
                            {user?.is_doctor ? (
                                <div>
                                    <p>Manage your schedule and appointments from the sidebar menu.</p>
                                    <div className="d-flex gap-2 flex-wrap">
                                        <button
                                            className="btn btn-outline-primary"
                                            onClick={() => navigate('/doctor/create-schedule')}
                                        >
                                            Create Schedule
                                        </button>
                                        <button
                                            className="btn btn-outline-secondary"
                                            onClick={() => navigate('/doctor/appointments')}
                                        >
                                            View Appointments
                                        </button>
                                    </div>
                                </div>
                            ) : (
                                <div>
                                    <p>Book appointments and view your medical history from the sidebar menu.</p>
                                    <div className="d-flex gap-2 flex-wrap">
                                        <button
                                            className="btn btn-outline-primary"
                                            onClick={() => navigate('/find-doctors')}
                                        >
                                            Find Doctors
                                        </button>
                                        <button
                                            className="btn btn-outline-secondary"
                                            onClick={() => navigate('/my-appointments')}
                                        >
                                            My Appointments
                                        </button>
                                    </div>
                                </div>
                            )}
                        </Card.Body>
                    </Card>
                </Col>
            </Row>
        </div>
    );

    return (
        <>
            <style jsx>{`
                .healthcare-hero-wrapper {
                    width: 100%;
                    position: relative;
                }

                .healthcare-hero-inner {
                    position: relative;
                    width: 100%;
                    min-height: 400px;
                    background-repeat: no-repeat;
                    background-size: cover;
                    background-position: center center;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    border-radius: 12px;
                    overflow: hidden;
                    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
                }

                .hero-container {
                    position: relative;
                    z-index: 2;
                    height: 100%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                }

                /* 3. REMOVED BACKGROUND - No more glass-morphism effect */
                .hero-content {
                    text-align: center;
                    color: white;
                    max-width: 600px;
                    padding: 2.5rem;
                    /* Removed background, backdrop-filter, border, and box-shadow */
                }

                .hero-title {
                    font-size: 2.5rem;
                    font-weight: 700;
                    margin-bottom: 1rem;
                    color: white;
                    text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.8);
                    line-height: 1.2;
                }

                /* Responsive Design */
                @media (max-width: 768px) {
                    .healthcare-hero-inner {
                        min-height: 300px;
                    }

                    .hero-title {
                        font-size: 2rem;
                    }

                    .hero-content {
                        padding: 2rem;
                        margin: 0 1rem;
                    }
                }

                /* Animation Effects */
                @keyframes fadeInUp {
                    from {
                        opacity: 0;
                        transform: translateY(30px);
                    }
                    to {
                        opacity: 1;
                        transform: translateY(0);
                    }
                }

                .hero-content {
                    animation: fadeInUp 0.8s ease-out;
                }

                .hero-title {
                    animation: fadeInUp 0.8s ease-out 0.2s both;
                }

                /* Enhanced transparency effect */
                .healthcare-hero-inner::before {
                    content: '';
                    position: absolute;
                    top: 0;
                    left: 0;
                    right: 0;
                    bottom: 0;
                    /* Reduced overlay opacity for better image visibility */
                    background: linear-gradient(
                            135deg,
                            rgba(39, 67, 117, 0.1) 0%,
                            rgba(30, 53, 87, 0.2) 100%
                    );
                    z-index: 1;
                    transition: all 0.3s ease;
                }

                .healthcare-hero-inner:hover::before {
                    background: linear-gradient(
                            135deg,
                            rgba(39, 67, 117, 0.05) 0%,
                            rgba(30, 53, 87, 0.15) 100%
                    );
                }
            `}</style>

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
        </>
    );
};

export default Dashboard;