// fe/src/components/Dashboard/Navbar.js
import React from 'react';
import { Navbar, Container, Nav, NavDropdown, Button } from 'react-bootstrap';
import { List } from 'react-bootstrap-icons';

const TopNavbar = ({ user, onLogout, onToggleSidebar, isMobile }) => {
    return (
        <Navbar expand="lg" className="top-navbar py-2 fixed-top">
            <Container fluid>
                {/* Mobile menu toggle */}
                {isMobile && (
                    <Button
                        variant="link"
                        className="p-0 me-3 text-primary"
                        onClick={onToggleSidebar}
                        title="Toggle Menu"
                    >
                        <List size={24} />
                    </Button>
                )}

                <Navbar.Brand href="#dashboard" className="d-flex align-items-center">
                    <span className="ms-2 fw-bold">HealthCare System</span>
                </Navbar.Brand>

                <Navbar.Toggle aria-controls="basic-navbar-nav" />
                <Navbar.Collapse id="basic-navbar-nav" className="justify-content-end">
                    <Nav>
                        <NavDropdown
                            title={`${user?.first_name || 'User'} ${user?.last_name || ''}`}
                            id="basic-nav-dropdown"
                            align="end"
                        >
                            <NavDropdown.Item href="#profile">Profile</NavDropdown.Item>
                            <NavDropdown.Item href="#settings">Settings</NavDropdown.Item>
                            <NavDropdown.Divider />
                            <NavDropdown.Item onClick={onLogout}>Logout</NavDropdown.Item>
                        </NavDropdown>
                    </Nav>
                </Navbar.Collapse>
            </Container>
        </Navbar>
    );
};

export default TopNavbar;