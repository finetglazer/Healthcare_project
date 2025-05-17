// Update fe/src/components/Dashboard/Sidebar.js to link to new routes
import React from 'react';
import { Nav } from 'react-bootstrap';
import { Link } from 'react-router-dom';

const Sidebar = ({ userType }) => {
    return (
        <div className="nav-sidebar">
            <div className="p-3 text-center mb-4">
                <h5>{userType === 'doctor' ? 'Doctor Portal' : 'Patient Portal'}</h5>
            </div>

            <Nav className="flex-column">
                <Nav.Link as={Link} to="/dashboard" className="sidebar-link">
                    Dashboard
                </Nav.Link>

                {userType === 'doctor' ? (
                    // Doctor specific links
                    <>
                        <Nav.Link as={Link} to="/doctor/create-schedule" className="sidebar-link">
                            Create Schedule
                        </Nav.Link>
                        <Nav.Link as={Link} to="/doctor/schedules" className="sidebar-link">
                            My Schedules
                        </Nav.Link>
                        <Nav.Link as={Link} to="/doctor/appointments" className="sidebar-link">
                            Appointments
                        </Nav.Link>
                    </>
                ) : (
                    // Patient specific links
                    <>
                        <Nav.Link as={Link} to="/find-doctors" className="sidebar-link">
                            Find Doctors
                        </Nav.Link>
                        <Nav.Link as={Link} to="/my-appointments" className="sidebar-link">
                            My Appointments
                        </Nav.Link>
                    </>
                )}

                <Nav.Link as={Link} to="/profile" className="sidebar-link">
                    Profile
                </Nav.Link>
            </Nav>
        </div>
    );
};

export default Sidebar;