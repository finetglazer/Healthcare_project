// fe/src/services/appointment.service.js
import axios from 'axios';

const API_URL = 'http://localhost:8000/api/appointments/';

// Maintain consistent configuration with other services
axios.defaults.withCredentials = true;

const appointmentService = {
    // Doctor Schedule Management
    getDoctorSchedules: async () => {
        try {
            const response = await axios.get(API_URL + 'schedules/');
            return response.data;
        } catch (error) {
            console.error('Error fetching doctor schedules', error);
            return [];
        }
    },

    createSchedule: async (scheduleData) => {
        try {
            const response = await axios.post(API_URL + 'schedules/', scheduleData);
            return response.data;
        } catch (error) {
            console.error('Error creating schedule', error);
            throw error;
        }
    },

    updateSchedule: async (scheduleId, scheduleData) => {
        try {
            const response = await axios.put(`${API_URL}schedules/${scheduleId}/`, scheduleData);
            return response.data;
        } catch (error) {
            console.error('Error updating schedule', error);
            throw error;
        }
    },

    deleteSchedule: async (scheduleId) => {
        try {
            await axios.delete(`${API_URL}schedules/${scheduleId}/`);
            return true;
        } catch (error) {
            console.error('Error deleting schedule', error);
            throw error;
        }
    },

    // Patient Booking
    getDoctors: async (search = '') => {
        try {
            const response = await axios.get(`${API_URL}doctors/?search=${search}`);
            return response.data;
        } catch (error) {
            console.error('Error fetching doctors', error);
            return [];
        }
    },

    getDoctorSchedules: async (doctorId) => {
        try {
            const response = await axios.get(`${API_URL}doctors/${doctorId}/schedules/`);
            return response.data;
        } catch (error) {
            console.error('Error fetching doctor schedules', error);
            return [];
        }
    },

    bookAppointment: async (bookingData) => {
        try {
            const response = await axios.post(`${API_URL}book/`, bookingData);
            return response.data;
        } catch (error) {
            console.error('Error booking appointment', error);
            throw error;
        }
    },

    // Appointment Management
    getPatientAppointments: async () => {
        try {
            const response = await axios.get(`${API_URL}patient/appointments/`);
            return response.data;
        } catch (error) {
            console.error('Error fetching patient appointments', error);
            return [];
        }
    },

    getDoctorAppointments: async () => {
        try {
            const response = await axios.get(`${API_URL}doctor/appointments/`);
            return response.data;
        } catch (error) {
            console.error('Error fetching doctor appointments', error);
            return [];
        }
    },

    cancelAppointment: async (appointmentId) => {
        try {
            const response = await axios.patch(`${API_URL}appointments/${appointmentId}/cancel/`);
            return response.data;
        } catch (error) {
            console.error('Error canceling appointment', error);
            throw error;
        }
    }
};

export default appointmentService;