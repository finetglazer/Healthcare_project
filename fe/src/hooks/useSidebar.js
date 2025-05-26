// fe/src/hooks/useSidebar.js
import { useState, useEffect } from 'react';

export const useSidebar = () => {
    const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
    const [isMobile, setIsMobile] = useState(false);
    const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

    // Check if screen is mobile size
    useEffect(() => {
        const checkScreenSize = () => {
            setIsMobile(window.innerWidth <= 768);
            // Auto-collapse sidebar on mobile
            if (window.innerWidth <= 768) {
                setSidebarCollapsed(true);
            }
        };

        checkScreenSize();
        window.addEventListener('resize', checkScreenSize);

        return () => window.removeEventListener('resize', checkScreenSize);
    }, []);

    const toggleSidebar = () => {
        if (isMobile) {
            setMobileMenuOpen(!mobileMenuOpen);
        } else {
            setSidebarCollapsed(!sidebarCollapsed);
        }
    };

    const closeMobileMenu = () => {
        if (isMobile) {
            setMobileMenuOpen(false);
        }
    };

    return {
        sidebarCollapsed,
        isMobile,
        mobileMenuOpen,
        toggleSidebar,
        closeMobileMenu,
        setSidebarCollapsed
    };
};