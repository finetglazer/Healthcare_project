import React, { useState } from 'react';
import { Menu, X, Calendar, User, Heart, Phone, Globe, ChevronDown } from 'lucide-react';

const HealthcareHeader = () => {
    const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
    const [isLanguageOpen, setIsLanguageOpen] = useState(false);

    const toggleMobileMenu = () => {
        setIsMobileMenuOpen(!isMobileMenuOpen);
    };

    const toggleLanguageMenu = () => {
        setIsLanguageOpen(!isLanguageOpen);
    };

    return (
        <header className="bg-white shadow-lg border-b-4 border-blue-600">
            {/* Top Bar */}
            <div className="bg-blue-50 border-b border-blue-100">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="flex justify-between items-center py-2 text-sm">
                        <div className="flex items-center space-x-6">
                            <span className="text-blue-800 font-medium">Healthcare Appointment System</span>
                            <div className="hidden md:flex items-center space-x-4">
                <span className="flex items-center text-blue-700">
                  <Phone className="w-4 h-4 mr-1" />
                  Emergency: +1-800-HEALTH
                </span>
                            </div>
                        </div>
                        <div className="flex items-center space-x-4">
                            {/* Language Selector */}
                            <div className="relative">
                                <button
                                    onClick={toggleLanguageMenu}
                                    className="flex items-center text-blue-700 hover:text-blue-900 transition-colors"
                                >
                                    <Globe className="w-4 h-4 mr-1" />
                                    <span className="hidden sm:inline">EN</span>
                                    <ChevronDown className="w-3 h-3 ml-1" />
                                </button>
                                {isLanguageOpen && (
                                    <div className="absolute right-0 mt-2 w-32 bg-white rounded-md shadow-lg border border-gray-200 z-50">
                                        <div className="py-1">
                                            <a href="#" className="block px-4 py-2 text-sm text-gray-700 hover:bg-blue-50">English</a>
                                            <a href="#" className="block px-4 py-2 text-sm text-gray-700 hover:bg-blue-50">Español</a>
                                            <a href="#" className="block px-4 py-2 text-sm text-gray-700 hover:bg-blue-50">Français</a>
                                            <a href="#" className="block px-4 py-2 text-sm text-gray-700 hover:bg-blue-50">中文</a>
                                        </div>
                                    </div>
                                )}
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {/* Main Header */}
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="flex justify-between items-center py-4">
                    {/* Logo */}
                    <div className="flex items-center">
                        <div className="flex-shrink-0 flex items-center">
                            <div className="w-12 h-12 bg-gradient-to-br from-blue-600 to-blue-700 rounded-full flex items-center justify-center mr-3">
                                <Heart className="w-7 h-7 text-white" />
                            </div>
                            <div className="hidden sm:block">
                                <h1 className="text-2xl font-bold text-blue-900">HealthCare</h1>
                                <p className="text-sm text-blue-600 -mt-1">Appointment System</p>
                            </div>
                        </div>
                    </div>

                    {/* Desktop Navigation */}
                    <nav className="hidden lg:flex items-center space-x-8">
                        <a href="#" className="text-gray-700 hover:text-blue-600 font-medium transition-colors px-3 py-2 rounded-md hover:bg-blue-50">
                            Home
                        </a>
                        <a href="#" className="text-gray-700 hover:text-blue-600 font-medium transition-colors px-3 py-2 rounded-md hover:bg-blue-50">
                            Book Appointment
                        </a>
                        <a href="#" className="text-gray-700 hover:text-blue-600 font-medium transition-colors px-3 py-2 rounded-md hover:bg-blue-50">
                            Find Doctor
                        </a>
                        <a href="#" className="text-gray-700 hover:text-blue-600 font-medium transition-colors px-3 py-2 rounded-md hover:bg-blue-50">
                            Health Topics
                        </a>
                        <a href="#" className="text-gray-700 hover:text-blue-600 font-medium transition-colors px-3 py-2 rounded-md hover:bg-blue-50">
                            About Us
                        </a>
                    </nav>

                    {/* Action Buttons */}
                    <div className="hidden lg:flex items-center space-x-4">
                        <button className="flex items-center text-blue-600 hover:text-blue-700 font-medium transition-colors">
                            <User className="w-5 h-5 mr-2" />
                            Sign In
                        </button>
                        <button className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-full font-medium transition-colors flex items-center">
                            <Calendar className="w-5 h-5 mr-2" />
                            Book Now
                        </button>
                    </div>

                    {/* Mobile menu button */}
                    <div className="lg:hidden">
                        <button
                            onClick={toggleMobileMenu}
                            className="text-gray-700 hover:text-blue-600 transition-colors p-2"
                        >
                            {isMobileMenuOpen ? (
                                <X className="w-6 h-6" />
                            ) : (
                                <Menu className="w-6 h-6" />
                            )}
                        </button>
                    </div>
                </div>
            </div>

            {/* Mobile Navigation */}
            {isMobileMenuOpen && (
                <div className="lg:hidden bg-white border-t border-gray-200">
                    <div className="px-4 py-6 space-y-4">
                        <a href="#" className="block text-gray-700 hover:text-blue-600 font-medium py-2 border-b border-gray-100">
                            Home
                        </a>
                        <a href="#" className="block text-gray-700 hover:text-blue-600 font-medium py-2 border-b border-gray-100">
                            Book Appointment
                        </a>
                        <a href="#" className="block text-gray-700 hover:text-blue-600 font-medium py-2 border-b border-gray-100">
                            Find Doctor
                        </a>
                        <a href="#" className="block text-gray-700 hover:text-blue-600 font-medium py-2 border-b border-gray-100">
                            Health Topics
                        </a>
                        <a href="#" className="block text-gray-700 hover:text-blue-600 font-medium py-2 border-b border-gray-100">
                            About Us
                        </a>

                        <div className="pt-4 space-y-3">
                            <button className="w-full flex items-center justify-center text-blue-600 hover:text-blue-700 font-medium py-2">
                                <User className="w-5 h-5 mr-2" />
                                Sign In
                            </button>
                            <button className="w-full bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-full font-medium transition-colors flex items-center justify-center">
                                <Calendar className="w-5 h-5 mr-2" />
                                Book Appointment Now
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </header>
    );
};

export default HealthcareHeader;