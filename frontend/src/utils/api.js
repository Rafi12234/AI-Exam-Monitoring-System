import axios from 'axios';

const API_BASE_URL = 'http://localhost:5000/api';

export const api = {
  getFlaggedStudents: () =>
    axios.get(`${API_BASE_URL}/flagged_students`),

  getStudentOffenses: (studentId) =>
    axios.get(`${API_BASE_URL}/students/${studentId}/offenses`),

  logOffense: (studentId, behaviorType) =>
    axios.post(`${API_BASE_URL}/log_offense`, {
      student_id: studentId,
      behavior_type: behaviorType
    }),

  resetStudent: (studentId) =>
    axios.post(`${API_BASE_URL}/reset_student/${studentId}`),

  clearOffenses: (studentId) =>
    axios.post(`${API_BASE_URL}/clear_offenses/${studentId}`),

  getStats: () =>
    axios.get(`${API_BASE_URL}/stats`)
};

export default api;
