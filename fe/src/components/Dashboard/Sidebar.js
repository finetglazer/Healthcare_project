// fe/src/components/Dashboard/Sidebar.js
import React from 'react';
import { Nav, Button, OverlayTrigger, Tooltip } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import {
    House,
    Calendar,
    CalendarPlus,
    CalendarCheck,
    Search,
    PersonCircle,
    List,
    ChevronLeft,
    ChevronRight
} from 'react-bootstrap-icons';

const Sidebar = ({ userType, collapsed, onToggle, isMobile, mobileMenuOpen, onCloseMobile }) => {
    // Navigation items configuration
    const doctorNavItems = [
        { path: '/dashboard', icon: House, label: 'Dashboard' },
        { path: '/doctor/create-schedule', icon: CalendarPlus, label: 'Create Schedule' },
        { path: '/doctor/schedules', icon: List, label: 'My Schedules' },
        { path: '/doctor/appointments', icon: CalendarCheck, label: 'Appointments' },
        { path: '/profile', icon: PersonCircle, label: 'Profile' }
    ];

    const patientNavItems = [
        { path: '/dashboard', icon: House, label: 'Dashboard' },
        { path: '/find-doctors', icon: Search, label: 'Find Doctors' },
        { path: '/my-appointments', icon: Calendar, label: 'My Appointments' },
        { path: '/profile', icon: PersonCircle, label: 'Profile' }
    ];

    const navItems = userType === 'doctor' ? doctorNavItems : patientNavItems;

    // Render navigation item with tooltip when collapsed
    const renderNavItem = (item) => {
        const navLink = (
            <Nav.Link
                as={Link}
                to={item.path}
                className={`sidebar-link ${collapsed ? 'collapsed' : ''}`}
                onClick={isMobile ? onCloseMobile : undefined}
            >
                <item.icon size={20} className="nav-icon" />
                {!collapsed && <span className="nav-text">{item.label}</span>}
            </Nav.Link>
        );

        // Wrap with tooltip when collapsed (only on desktop)
        if (collapsed && !isMobile) {
            return (
                <OverlayTrigger
                    key={item.path}
                    placement="right"
                    overlay={<Tooltip>{item.label}</Tooltip>}
                >
                    <div>{navLink}</div>
                </OverlayTrigger>
            );
        }

        return <div key={item.path}>{navLink}</div>;
    };

    return (
        <div className={`nav-sidebar ${collapsed ? 'collapsed' : ''} ${isMobile ? (mobileMenuOpen ? 'show' : '') : ''}`}>
            {/* Header with toggle button */}
            <div className="sidebar-header">
                {!collapsed && (
                    <div className="p-3 text-center mb-2">
                        <h6 className="sidebar-title">
                            {userType === 'doctor' ? 'Doctor Portal' : 'Patient Portal'}
                        </h6>
                    </div>
                )}

                {!isMobile && (
                    <Button
                        variant="link"
                        className="toggle-btn"
                        onClick={onToggle}
                        title={collapsed ? 'Expand Sidebar' : 'Collapse Sidebar'}
                    >
                        {collapsed ? <ChevronRight size={20} /> : <ChevronLeft size={20} />}
                    </Button>
                )}

                {isMobile && (
                    <Button
                        variant="link"
                        className="toggle-btn mobile-close"
                        onClick={onCloseMobile}
                        title="Close Menu"
                    >
                        <ChevronLeft size={20} />
                    </Button>
                )}
            </div>

            {/* Navigation */}
            <Nav className="flex-column sidebar-nav">
                {navItems.map(renderNavItem)}
            </Nav>

            {/* Footer info when expanded */}
            {!collapsed && (
                <div className="sidebar-footer">
                    <div className="p-3 text-center">
                        <small className="text-light opacity-75">
                            Healthcare System v1.0
                        </small>
                    </div>
                </div>
            )}
        </div>
    );
};

export default Sidebar;