import React from 'react';
import { Navbar, Container, Nav, NavDropdown } from 'react-bootstrap';

const TopNavbar = ({ user }) => {
    return (
        <Navbar expand="lg" className="top-navbar py-2">
            <Container fluid>
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
                            <NavDropdown.Item href="#logout">Logout</NavDropdown.Item>
                        </NavDropdown>
                    </Nav>
                </Navbar.Collapse>
            </Container>
        </Navbar>
    );
};

export default TopNavbar;
