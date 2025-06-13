// fe/src/services/appointment.service.js
import axios from 'axios';

// Remove the single API_URL and use specific base URLs
const BASE_URL = 'http://localhost:8000/api/';

axios.defaults.withCredentials = true;

const appointmentService = {
    // Doctor Schedule Management (uses /api/doctor/)
    getDoctorSchedules: async () => {
        try {
            const response = await axios.get(`${BASE_URL}doctor/schedules/`);
            return response.data;
        } catch (error) {
            console.error('Error fetching doctor schedules', error);
            return [];
        }
    },

    createSchedule: async (scheduleData) => {
        try {
            const response = await axios.post(`${BASE_URL}doctor/schedules/`, scheduleData);
            return response.data;
        } catch (error) {
            console.error('Error creating schedule', error);
            throw error;
        }
    },

    updateSchedule: async (scheduleId, scheduleData) => {
        try {
            const response = await axios.put(`${BASE_URL}doctor/schedules/${scheduleId}/`, scheduleData);
            return response.data;
        } catch (error) {
            console.error('Error updating schedule', error);
            throw error;
        }
    },

    deleteSchedule: async (scheduleId) => {
        try {
            await axios.delete(`${BASE_URL}doctor/schedules/${scheduleId}/`);
            return true;
        } catch (error) {
            console.error('Error deleting schedule', error);
            throw error;
        }
    },

    // Patient Booking (uses /api/patient/)
    // In fe/src/services/appointment.service.js
    getDoctors: async (search = '') => {
        try {
            const response = await axios.get(`${BASE_URL}patient/doctors/?search=${search}`);
            return response.data.results; // Return only the results array
        } catch (error) {
            console.error('Error fetching doctors', error);
            return [];
        }
    },

    getDoctorAvailableSchedules: async (doctorId) => {
        try {
            const response = await axios.get(`${BASE_URL}patient/doctors/${doctorId}/schedules/`);
            return response.data;
        } catch (error) {
            console.error('Error fetching doctor schedules', error);
            return [];
        }
    },

    bookAppointment: async (bookingData) => {
        try {
            const response = await axios.post(`${BASE_URL}patient/book/`, bookingData);
            return response.data;
        } catch (error) {
            console.error('Error booking appointment', error);
            throw error;
        }
    },

    // Appointment Management
    getPatientAppointments: async () => {
        try {
            const response = await axios.get(`${BASE_URL}patient/appointments/`);
            return response.data;
        } catch (error) {
            console.error('Error fetching patient appointments', error);
            return [];
        }
    },

    getDoctorAppointments: async () => {
        try {
            const response = await axios.get(`${BASE_URL}doctor/appointments/`);
            return response.data;
        } catch (error) {
            console.error('Error fetching doctor appointments', error);
            return [];
        }
    },

    cancelAppointment: async (appointmentId) => {
        try {
            const response = await axios.patch(`${BASE_URL}patient/appointments/${appointmentId}/cancel/`);
            return response.data;
        } catch (error) {
            console.error('Error canceling appointment', error);
            throw error;
        }
    }
};

export default appointmentService;