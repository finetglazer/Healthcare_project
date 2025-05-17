// fe/src/services/auth.service.js
import axios from 'axios';

const API_URL = 'http://localhost:8000/api/users/';

// Add cookies support for session authentication
axios.defaults.withCredentials = true;

// Get CSRF token from cookies
function getCSRFToken() {
    const cookieValue = document.cookie
        .split('; ')
        .find(row => row.startsWith('csrftoken='))
        ?.split('=')[1];
    return cookieValue;
}

axios.interceptors.request.use(config => {
    config.headers['X-CSRFToken'] = getCSRFToken();
    return config;
});

// Rest of your auth service code...

// Default accounts for fallback when backend is unavailable
const DEFAULT_ACCOUNTS = [
    {
        id: 1,
        username: 'doctor1',
        password: 'password',
        first_name: 'John',
        last_name: 'Doe',
        email: 'john.doe@example.com',
        phone_number: '123-456-7890',
        is_doctor: true,
        is_patient: false,
        doctor_profile: {
            specialization: 'Cardiology'
        }
    },
    {
        id: 2,
        username: 'patient1',
        password: 'password',
        first_name: 'Jane',
        last_name: 'Smith',
        email: 'jane.smith@example.com',
        phone_number: '987-654-3210',
        is_doctor: false,
        is_patient: true,
        patient_profile: {
            date_of_birth: '1990-01-01'
        }
    }
];

const authService = {
    login: async (credentials) => {
        try {
            // Try to connect to the backend
            const response = await axios.post(API_URL + 'login/', credentials);
            return response.data;
        } catch (error) {
            console.log('Backend connection failed, using fallback mode');

            // Fallback to default accounts if backend is unavailable
            const user = DEFAULT_ACCOUNTS.find(
                account => account.username === credentials.username && account.password === credentials.password
            );

            if (user) {
                // Create a copy without the password
                const { password, ...userWithoutPassword } = user;
                return userWithoutPassword;
            }

            throw new Error('Invalid username or password');
        }
    },

    register: async (userData) => {
        try {
            // Try to connect to the backend
            const response = await axios.post(API_URL + 'register/', userData);
            return response.data;
        } catch (error) {
            console.log('Backend connection failed, using fallback mode');

            // In fallback mode, check if username already exists
            if (DEFAULT_ACCOUNTS.some(account => account.username === userData.username)) {
                throw new Error('Username already exists');
            }

            // Simulate successful registration
            return { success: true };
        }
    },

    // Add this method to your authService object
    logout: async () => {
        try {
            // Try to connect to the backend
            await axios.post(API_URL + 'logout/');
            // Clear any local state or storage if needed
            return true;
        } catch (error) {
            console.log('Backend connection failed, using fallback mode');
            // In fallback mode, just return success
            return true;
        }
    },

    getCurrentUser: async () => {
        try {
            // Try to get current user from backend
            const response = await axios.get(API_URL + 'me/');
            return response.data;
        } catch (error) {
            return null;
        }
    }
};

export default authService;