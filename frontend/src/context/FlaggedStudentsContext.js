import React, { createContext, useState, useEffect, useCallback } from 'react';
import { socket } from '../utils/socket';
import axios from 'axios';

export const FlaggedStudentsContext = createContext();

export const FlaggedStudentsProvider = ({ children }) => {
  const [flaggedStudents, setFlaggedStudents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [stats, setStats] = useState({
    flagged_students: 0,
    students_with_offenses: 0,
    total_offenses: 0
  });

  // Fetch flagged students from backend
  const fetchFlaggedStudents = useCallback(async () => {
    try {
      setLoading(true);
      const response = await axios.get('http://localhost:5000/api/flagged_students');
      if (response.data.status === 'success') {
        setFlaggedStudents(response.data.data);
        setError(null);
      }
    } catch (err) {
      setError(err.message);
      console.error('Error fetching flagged students:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  // Fetch statistics
  const fetchStats = useCallback(async () => {
    try {
      const response = await axios.get('http://localhost:5000/api/stats');
      if (response.data.status === 'success') {
        setStats(response.data.data);
      }
    } catch (err) {
      console.error('Error fetching stats:', err);
    }
  }, []);

  // Reset student function
  const resetStudent = useCallback(async (studentId) => {
    try {
      const response = await axios.post(
        `http://localhost:5000/api/reset_student/${studentId}`
      );
      if (response.data.status === 'success') {
        fetchFlaggedStudents();
        fetchStats();
      }
    } catch (err) {
      console.error('Error resetting student:', err);
    }
  }, [fetchFlaggedStudents, fetchStats]);

  // Clear offenses function
  const clearOffenses = useCallback(async (studentId) => {
    try {
      const response = await axios.post(
        `http://localhost:5000/api/clear_offenses/${studentId}`
      );
      if (response.data.status === 'success') {
        fetchFlaggedStudents();
        fetchStats();
      }
    } catch (err) {
      console.error('Error clearing offenses:', err);
    }
  }, [fetchFlaggedStudents, fetchStats]);

  // Initial data fetch
  useEffect(() => {
    fetchFlaggedStudents();
    fetchStats();

    // Set up polling to refresh stats every 5 seconds
    const interval = setInterval(fetchStats, 5000);

    return () => clearInterval(interval);
  }, [fetchFlaggedStudents, fetchStats]);

  // Set up Socket.IO listeners
  useEffect(() => {
    socket.on('student_flagged', (data) => {
      setFlaggedStudents(prev => {
        const exists = prev.find(s => s.student_id === data.student_id);
        if (exists) {
          return prev.map(s =>
            s.student_id === data.student_id
              ? { ...s, offenses_count: data.offenses_count }
              : s
          );
        }
        return [...prev, data];
      });
      fetchStats();
    });

    socket.on('student_reset', (data) => {
      setFlaggedStudents(prev =>
        prev.filter(s => s.student_id !== data.student_id)
      );
      fetchStats();
    });

    socket.on('student_cleared', (data) => {
      setFlaggedStudents(prev =>
        prev.filter(s => s.student_id !== data.student_id)
      );
      fetchStats();
    });

    return () => {
      socket.off('student_flagged');
      socket.off('student_reset');
      socket.off('student_cleared');
    };
  }, [fetchStats]);

  const value = {
    flaggedStudents,
    loading,
    error,
    stats,
    fetchFlaggedStudents,
    fetchStats,
    resetStudent,
    clearOffenses
  };

  return (
    <FlaggedStudentsContext.Provider value={value}>
      {children}
    </FlaggedStudentsContext.Provider>
  );
};
