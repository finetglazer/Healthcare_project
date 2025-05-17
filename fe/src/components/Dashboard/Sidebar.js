import React from 'react';
import { Nav } from 'react-bootstrap';

const Sidebar = ({ userType }) => {
    return (
        <div className="nav-sidebar">
            <div className="p-3 text-center mb-4">
                <h5>{userType === 'doctor' ? 'Doctor Portal' : 'Patient Portal'}</h5>
            </div>

            <Nav className="flex-column">
                <Nav.Link href="#dashboard" className="sidebar-link">
                    Dashboard
                </Nav.Link>

                {userType === 'doctor' ? (
                    // Doctor specific links
                    <>
                        <Nav.Link href="#schedule" className="sidebar-link">
                            My Schedule
                        </Nav.Link>
                        <Nav.Link href="#appointments" className="sidebar-link">
                            Appointments
                        </Nav.Link>
                        <Nav.Link href="#patients" className="sidebar-link">
                            My Patients
                        </Nav.Link>
                    </>
                ) : (
                    // Patient specific links
                    <>
                        <Nav.Link href="#book" className="sidebar-link">
                            Book Appointment
                        </Nav.Link>
                        <Nav.Link href="#appointments" className="sidebar-link">
                            My Appointments
                        </Nav.Link>
                        <Nav.Link href="#doctors" className="sidebar-link">
                            Find Doctors
                        </Nav.Link>
                        <Nav.Link href="#records" className="sidebar-link">
                            Medical Records
                        </Nav.Link>
                    </>
                )}

                <Nav.Link href="#profile" className="sidebar-link">
                    Profile
                </Nav.Link>
            </Nav>
        </div>
    );
};

export default Sidebar;