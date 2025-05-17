// Update fe/src/App.js to include new routes
import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import 'bootstrap/dist/css/bootstrap.min.css';
import './App.css';

// Auth components
import Login from './components/Auth/Login';
import Register from './components/Auth/Register';
import Dashboard from './components/Dashboard/Dashboard';

// Doctor components
import CreateSchedule from './components/Doctor/CreateSchedule';
import DoctorScheduleList from './components/Doctor/DoctorScheduleList';
import DoctorAppointments from './components/Doctor/DoctorAppointments';

// Patient components
import DoctorList from './components/Patient/DoctorList';
import BookAppointment from './components/Patient/BookAppointment';
import PatientAppointments from './components/Patient/PatientAppointments';

import authService from './services/auth.service';

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [currentUser, setCurrentUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // Check if user is already logged in
  useEffect(() => {
    const checkUser = async () => {
      try {
        const user = await authService.getCurrentUser();
        if (user) {
          setIsLoggedIn(true);
          setCurrentUser(user);
        }
      } catch (error) {
        console.error('Error checking user status:', error);
      } finally {
        setLoading(false);
      }
    };

    checkUser();
  }, []);

  // Auth handlers
  const handleLogin = (userData) => {
    setIsLoggedIn(true);
    setCurrentUser(userData);
  };

  const handleLogout = async () => {
    await authService.logout();
    setIsLoggedIn(false);
    setCurrentUser(null);
  };

  if (loading) {
    return <div className="loading-spinner">Loading...</div>;
  }

  return (
      <Router>
        <div className="App">
          <Routes>
            {/* Auth Routes */}
            <Route path="/" element={!isLoggedIn ? <Login onLogin={handleLogin} /> : <Navigate to="/dashboard" />} />
            <Route path="/register" element={<Register />} />

            {/* Dashboard */}
            <Route
                path="/dashboard"
                element={isLoggedIn ? <Dashboard user={currentUser} onLogout={handleLogout} /> : <Navigate to="/" />}
            />

            {/* Doctor Routes */}
            <Route
                path="/doctor/create-schedule"
                element={isLoggedIn && currentUser?.is_doctor ?
                    <Dashboard user={currentUser} onLogout={handleLogout} content={<CreateSchedule />} /> :
                    <Navigate to="/" />}
            />
            <Route
                path="/doctor/schedules"
                element={isLoggedIn && currentUser?.is_doctor ?
                    <Dashboard user={currentUser} onLogout={handleLogout} content={<DoctorScheduleList />} /> :
                    <Navigate to="/" />}
            />
            <Route
                path="/doctor/appointments"
                element={isLoggedIn && currentUser?.is_doctor ?
                    <Dashboard user={currentUser} onLogout={handleLogout} content={<DoctorAppointments />} /> :
                    <Navigate to="/" />}
            />

            {/* Patient Routes */}
            <Route
                path="/find-doctors"
                element={isLoggedIn && currentUser?.is_patient ?
                    <Dashboard user={currentUser} onLogout={handleLogout} content={<DoctorList />} /> :
                    <Navigate to="/" />}
            />
            <Route
                path="/book-appointment/:doctorId"
                element={isLoggedIn && currentUser?.is_patient ?
                    <Dashboard user={currentUser} onLogout={handleLogout} content={<BookAppointment />} /> :
                    <Navigate to="/" />}
            />
            <Route
                path="/my-appointments"
                element={isLoggedIn && currentUser?.is_patient ?
                    <Dashboard user={currentUser} onLogout={handleLogout} content={<PatientAppointments />} /> :
                    <Navigate to="/" />}
            />
          </Routes>
        </div>
      </Router>
  );
}

export default App;