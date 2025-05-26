import React, { useState } from 'react';

const HealthcareFooter = () => {
    const [activeKey, setActiveKey] = useState(null);

    const handleToggle = (key) => {
        setActiveKey(activeKey === key ? null : key);
    };

    const FooterSection = ({ title, items, eventKey }) => (
        <div className="footer-section">
            <div className="footer-section-header d-flex justify-content-between align-items-center mb-3">
                <h5 className="text-white mb-0">{title}</h5>
                <button
                    className="btn btn-link text-white p-0 d-md-none"
                    onClick={() => handleToggle(eventKey)}
                    aria-expanded={activeKey === eventKey}
                    style={{ background: 'none', border: 'none', fontSize: '18px' }}
                >
                    {activeKey === eventKey ? '−' : '+'}
                </button>
            </div>
            <ul className={`footer-links list-unstyled ${activeKey === eventKey ? 'd-block' : 'd-none d-md-block'}`}>
                {items.map((item, index) => (
                    <li key={index} className="mb-2">
                        <a href={item.href} className="text-light text-decoration-none footer-link">
                            {item.text}
                        </a>
                    </li>
                ))}
            </ul>
        </div>
    );

    const servicesItems = [
        { text: 'Book Appointment', href: '/find-doctors' },
        { text: 'Find Doctors', href: '/find-doctors' },
        { text: 'Telemedicine', href: '#' },
        { text: 'Emergency Services', href: '#' },
        { text: 'Health Checkups', href: '#' },
        { text: 'Specialist Care', href: '#' }
    ];

    const informationItems = [
        { text: 'Health Topics', href: '#' },
        { text: 'Patient Resources', href: '#' },
        { text: 'Healthcare Tips', href: '#' },
        { text: 'Insurance Information', href: '#' },
        { text: 'Medical Records', href: '#' },
        { text: 'FAQ', href: '#' }
    ];

    const aboutItems = [
        { text: 'About Us', href: '#' },
        { text: 'Our Doctors', href: '#' },
        { text: 'Careers', href: '#' },
        { text: 'News & Updates', href: '#' },
        { text: 'Quality & Safety', href: '#' },
        { text: 'Research', href: '#' }
    ];

    return (
        <footer className="healthcare-footer">
            <div className="footer-main">
                <div className="container">
                    <div className="row">
                        <div className="col-md-8">
                            <div className="row">
                                <div className="col-md-4">
                                    <FooterSection
                                        title="Services"
                                        items={servicesItems}
                                        eventKey="services"
                                    />
                                </div>
                                <div className="col-md-4">
                                    <FooterSection
                                        title="Information"
                                        items={informationItems}
                                        eventKey="information"
                                    />
                                </div>
                                <div className="col-md-4">
                                    <FooterSection
                                        title="About"
                                        items={aboutItems}
                                        eventKey="about"
                                    />
                                </div>
                            </div>
                        </div>

                        <div className="col-md-4">
                            <div className="footer-contact">
                                <h5 className="text-white mb-3">Contact Us</h5>
                                <div className="contact-info mb-4">
                                    <div className="contact-item mb-2">
                                        <span className="contact-icon me-2">📞</span>
                                        <span className="text-light">Emergency: +1-800-HEALTH</span>
                                    </div>
                                    <div className="contact-item mb-2">
                                        <span className="contact-icon me-2">✉️</span>
                                        <span className="text-light">info@healthcare.com</span>
                                    </div>
                                    <div className="contact-item mb-3">
                                        <span className="contact-icon me-2">📍</span>
                                        <span className="text-light">123 Health Street, Medical City</span>
                                    </div>
                                </div>

                                <div className="footer-buttons mb-4">
                                    <a
                                        href="#"
                                        className="btn btn-outline-light mb-2 w-100 footer-btn"
                                    >
                                        <span className="me-2">🔔</span>Subscribe to Newsletter
                                    </a>
                                    <a
                                        href="#"
                                        className="btn btn-outline-light w-100 footer-btn"
                                    >
                                        <span className="me-2">⚠️</span>Report Issue
                                    </a>
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Logo Section */}
                    <div className="row mt-5">
                        <div className="col text-center">
                            <div className="footer-logo mb-4">
                                <div className="d-flex align-items-center justify-content-center">
                                    <div
                                        className="logo-circle me-3"
                                        style={{
                                            width: '60px',
                                            height: '60px',
                                            background: 'linear-gradient(135deg, #ffffff, #f8f9fa)',
                                            borderRadius: '50%',
                                            display: 'flex',
                                            alignItems: 'center',
                                            justifyContent: 'center',
                                            fontSize: '32px'
                                        }}
                                    >
                                        ❤️
                                    </div>
                                    <div className="text-start">
                                        <h3 className="text-white mb-0">HealthCare System</h3>
                                        <p className="text-light mb-0">Your Health, Our Priority</p>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {/* Bottom Section */}
            <div className="footer-bottom">
                <div className="container">
                    <div className="row align-items-center">
                        <div className="col-md-6">
                            <div className="footer-bottom-links">
                                <a href="#" className="text-light text-decoration-none me-4">Privacy Policy</a>
                                <a href="#" className="text-light text-decoration-none me-4">Terms of Service</a>
                                <a href="#" className="text-light text-decoration-none me-4">Cookie Policy</a>
                                <a href="#" className="text-light text-decoration-none">Accessibility</a>
                            </div>
                        </div>
                        <div className="col-md-6">
                            <div className="d-flex justify-content-md-end justify-content-center align-items-center">
                                <div className="social-links me-4">
                                    <a href="#" className="text-light me-3 social-link" aria-label="Facebook">
                                        📘
                                    </a>
                                    <a href="#" className="text-light me-3 social-link" aria-label="Twitter">
                                        🐦
                                    </a>
                                    <a href="#" className="text-light me-3 social-link" aria-label="Instagram">
                                        📷
                                    </a>
                                    <a href="#" className="text-light me-3 social-link" aria-label="LinkedIn">
                                        💼
                                    </a>
                                    <a href="#" className="text-light social-link" aria-label="YouTube">
                                        📺
                                    </a>
                                </div>
                                <div className="copyright text-light">
                                    © 2025 HealthCare System. All rights reserved.
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <style jsx>{`
                .healthcare-footer {
                    background: linear-gradient(135deg, #274375 0%, #1e3557 100%);
                    color: white;
                    margin-top: auto;
                }
                
                .footer-main {
                    padding: 60px 0 40px;
                }
                
                .footer-bottom {
                    background-color: rgba(0, 0, 0, 0.2);
                    padding: 20px 0;
                    border-top: 1px solid rgba(255, 255, 255, 0.1);
                }
                
                .footer-link {
                    transition: all 0.3s ease;
                    position: relative;
                    display: inline-block;
                    padding: 2px 0;
                    color: #e9ecef !important;
                }
                
                .footer-link:hover {
                    color: #87ceeb !important;
                    transform: translateX(5px);
                }
                
                .footer-link::before {
                    content: '';
                    position: absolute;
                    bottom: 0;
                    left: 0;
                    width: 0;
                    height: 1px;
                    background-color: #87ceeb;
                    transition: width 0.3s ease;
                }
                
                .footer-link:hover::before {
                    width: 100%;
                }
                
                .contact-item {
                    transition: all 0.3s ease;
                    display: flex;
                    align-items: center;
                }
                
                .contact-item:hover {
                    transform: translateX(3px);
                }
                
                .contact-icon {
                    font-size: 16px;
                    width: 20px;
                    display: inline-block;
                }
                
                .footer-btn {
                    transition: all 0.3s ease;
                    border: 2px solid rgba(255, 255, 255, 0.3);
                    text-decoration: none;
                    display: inline-block;
                    text-align: center;
                    padding: 8px 16px;
                    border-radius: 4px;
                    color: white;
                }
                
                .footer-btn:hover {
                    border-color: #87ceeb;
                    background-color: rgba(135, 206, 235, 0.1);
                    transform: translateY(-2px);
                    box-shadow: 0 4px 12px rgba(135, 206, 235, 0.2);
                    color: #87ceeb;
                    text-decoration: none;
                }
                
                .social-link {
                    transition: all 0.3s ease;
                    display: inline-block;
                    width: 35px;
                    height: 35px;
                    line-height: 35px;
                    text-align: center;
                    border-radius: 50%;
                    border: 1px solid rgba(255, 255, 255, 0.3);
                    text-decoration: none;
                    font-size: 16px;
                }
                
                .social-link:hover {
                    color: #87ceeb !important;
                    border-color: #87ceeb;
                    transform: translateY(-3px);
                    background-color: rgba(135, 206, 235, 0.1);
                    text-decoration: none;
                }
                
                .footer-logo {
                    transition: all 0.3s ease;
                }
                
                .footer-logo:hover {
                    transform: scale(1.05);
                }
                
                .logo-circle {
                    transition: all 0.3s ease;
                }
                
                .logo-circle:hover {
                    transform: rotate(360deg);
                }
                
                /* Mobile responsiveness */
                @media (max-width: 767px) {
                    .footer-main {
                        padding: 40px 0 30px;
                    }
                    
                    .footer-section {
                        margin-bottom: 30px;
                    }
                    
                    .footer-section-header button {
                        background: none !important;
                        border: none !important;
                        font-size: 18px;
                        color: white;
                    }
                    
                    .footer-bottom {
                        text-align: center;
                    }
                    
                    .footer-bottom-links {
                        margin-bottom: 20px;
                    }
                    
                    .footer-bottom-links a {
                        display: block;
                        margin-bottom: 10px;
                    }
                    
                    .social-links {
                        margin-bottom: 15px !important;
                    }
                    
                    .d-flex.justify-content-md-end.justify-content-center {
                        flex-direction: column;
                        align-items: center;
                    }
                }
                
                /* Hover effects for better UX */
                .footer-section:hover {
                    transform: translateY(-2px);
                    transition: transform 0.3s ease;
                }
                
                .footer-contact:hover {
                    transform: translateY(-2px);
                    transition: transform 0.3s ease;
                }
                
                /* Custom animations */
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
                
                .footer-section,
                .footer-contact {
                    animation: fadeInUp 0.6s ease-out;
                }
                
                .footer-contact {
                    animation-delay: 0.2s;
                }
                
                /* Accessibility improvements */
                .footer-link:focus,
                .footer-btn:focus,
                .social-link:focus {
                    outline: 2px solid #87ceeb;
                    outline-offset: 2px;
                }
                
                /* Print styles */
                @media print {
                    .healthcare-footer {
                        background: #274375 !important;
                        color: black !important;
                    }
                }
            `}</style>
        </footer>
    );
};

export default HealthcareFooter;