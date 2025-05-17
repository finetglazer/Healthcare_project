// fe/src/App.js
import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import 'bootstrap/dist/css/bootstrap.min.css';
import './App.css';

// Components
import Login from './components/Auth/Login';
import Register from './components/Auth/Register';
import Dashboard from './components/Dashboard/Dashboard';
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

  // Simple auth handler
  const handleLogin = (userData) => {
    setIsLoggedIn(true);
    setCurrentUser(userData);
  };

  if (loading) {
    return <div className="loading-spinner">Loading...</div>;
  }

  return (
      <Router>
        <div className="App">
          <Routes>
            <Route path="/" element={!isLoggedIn ? <Login onLogin={handleLogin} /> : <Navigate to="/dashboard" />} />
            <Route path="/register" element={<Register />} />
            <Route
                path="/dashboard"
                element={isLoggedIn ? <Dashboard user={currentUser} /> : <Navigate to="/" />}
            />
          </Routes>
        </div>
      </Router>
  );
}

export default App;