import React, { useState } from 'react';
import { Navbar, Nav, Container, Dropdown, Button } from 'react-bootstrap';
// Import the medical image
import medicalImage from '../../assets/images/medical-image.jpg';

const HealthcareHeader = () => {
    const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

    const toggleMobileMenu = () => {
        setIsMobileMenuOpen(!isMobileMenuOpen);
    };

    return (
        <header>
            {/* Top Bar */}
            <div style={{ backgroundColor: '#eff6ff', borderBottom: '1px solid #dbeafe' }}>
                <Container>
                    <div className="d-flex justify-content-between align-items-center py-2">
                        <div className="d-flex align-items-center">
                            <span className="text-primary fw-medium">Healthcare Appointment System</span>
                            <div className="d-none d-md-flex align-items-center ms-4">
                                <span className="text-primary">
                                    📞 Emergency: +1-800-HEALTH
                                </span>
                            </div>
                        </div>
                        <div className="d-flex align-items-center">
                            {/* Language Selector */}
                            <Dropdown>
                                <Dropdown.Toggle
                                    variant="link"
                                    className="text-primary text-decoration-none p-0"
                                    id="language-dropdown"
                                >
                                    🌐 EN
                                </Dropdown.Toggle>
                                <Dropdown.Menu>
                                    <Dropdown.Item href="#">English</Dropdown.Item>
                                    <Dropdown.Item href="#">Español</Dropdown.Item>
                                    <Dropdown.Item href="#">Français</Dropdown.Item>
                                    <Dropdown.Item href="#">中文</Dropdown.Item>
                                </Dropdown.Menu>
                            </Dropdown>
                        </div>
                    </div>
                </Container>
            </div>

            {/* Main Header */}
            <Navbar
                expand="lg"
                className="py-3 shadow-lg"
                style={{ borderBottom: '4px solid #274375' }}
                bg="white"
            >
                <Container>
                    {/* Logo - Updated with medical image */}
                    <Navbar.Brand href="#" className="d-flex align-items-center">
                        <div
                            className="d-flex align-items-center justify-content-center me-3"
                            style={{
                                width: '48px',
                                height: '48px',
                                background: 'linear-gradient(135deg, #274375, #1e3557)',
                                borderRadius: '50%',
                                overflow: 'hidden',
                                border: '2px solid #ffffff',
                                boxShadow: '0 2px 8px rgba(0, 0, 0, 0.1)'
                            }}
                        >
                            <img
                                src={medicalImage}
                                alt="Medical Logo"
                                style={{
                                    width: '100%',
                                    height: '100%',
                                    objectFit: 'cover',
                                    objectPosition: 'center'
                                }}
                                onError={(e) => {
                                    // Fallback to heart emoji if image fails to load
                                    e.target.style.display = 'none';
                                    e.target.parentNode.innerHTML = '❤️';
                                    e.target.parentNode.style.fontSize = '24px';
                                    e.target.parentNode.style.color = 'white';
                                }}
                            />
                        </div>
                        <div className="d-none d-sm-block">
                            <h4 className="mb-0 text-primary fw-bold">HealthCare</h4>
                            <small className="text-muted">Appointment System</small>
                        </div>
                    </Navbar.Brand>

                    {/* Mobile Toggle */}
                    <Navbar.Toggle
                        aria-controls="basic-navbar-nav"
                        onClick={toggleMobileMenu}
                    />

                    {/* Navigation */}
                    <Navbar.Collapse id="basic-navbar-nav">
                        <Nav className="me-auto d-none d-lg-flex">
                            <Nav.Link
                                href="#"
                                className="text-dark fw-medium mx-2 px-3 py-2 rounded hover-bg-light"
                            >
                                Home
                            </Nav.Link>
                            <Nav.Link
                                href="#"
                                className="text-dark fw-medium mx-2 px-3 py-2 rounded hover-bg-light"
                            >
                                Book Appointment
                            </Nav.Link>
                            <Nav.Link
                                href="#"
                                className="text-dark fw-medium mx-2 px-3 py-2 rounded hover-bg-light"
                            >
                                Find Doctor
                            </Nav.Link>
                            <Nav.Link
                                href="#"
                                className="text-dark fw-medium mx-2 px-3 py-2 rounded hover-bg-light"
                            >
                                Health Topics
                            </Nav.Link>
                            <Nav.Link
                                href="#"
                                className="text-dark fw-medium mx-2 px-3 py-2 rounded hover-bg-light"
                            >
                                About Us
                            </Nav.Link>
                        </Nav>

                        {/* Action Buttons - Desktop */}
                        <div className="d-none d-lg-flex align-items-center">
                            <Button
                                variant="link"
                                className="text-primary fw-medium me-3 text-decoration-none"
                            >
                                👤 Sign In
                            </Button>
                            <Button
                                variant="primary"
                                className="rounded-pill px-4"
                            >
                                📅 Book Now
                            </Button>
                        </div>

                        {/* Mobile Menu */}
                        <div className="d-lg-none mt-3">
                            <Nav className="flex-column">
                                <Nav.Link href="#" className="text-dark fw-medium py-2 border-bottom">
                                    Home
                                </Nav.Link>
                                <Nav.Link href="#" className="text-dark fw-medium py-2 border-bottom">
                                    Book Appointment
                                </Nav.Link>
                                <Nav.Link href="#" className="text-dark fw-medium py-2 border-bottom">
                                    Find Doctor
                                </Nav.Link>
                                <Nav.Link href="#" className="text-dark fw-medium py-2 border-bottom">
                                    Health Topics
                                </Nav.Link>
                                <Nav.Link href="#" className="text-dark fw-medium py-2 border-bottom">
                                    About Us
                                </Nav.Link>
                            </Nav>

                            <div className="mt-3 d-flex flex-column gap-2">
                                <Button
                                    variant="outline-primary"
                                    className="w-100"
                                >
                                    👤 Sign In
                                </Button>
                                <Button
                                    variant="primary"
                                    className="w-100 rounded-pill"
                                >
                                    📅 Book Appointment Now
                                </Button>
                            </div>
                        </div>
                    </Navbar.Collapse>
                </Container>
            </Navbar>

            {/* Add custom CSS for hover effects */}
            <style jsx>{`
                .hover-bg-light:hover {
                    background-color: #f8f9fa !important;
                    color: #274375 !important;
                }
            `}</style>
        </header>
    );
};

export default HealthcareHeader;