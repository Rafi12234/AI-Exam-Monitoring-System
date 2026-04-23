import React, { useContext } from 'react';
import { FlaggedStudentsContext } from '../context/FlaggedStudentsContext';
import FlaggedStudentCard from './FlaggedStudentCard';
import './Dashboard.css';

const Dashboard = () => {
  const { flaggedStudents, loading, error, stats, resetStudent, clearOffenses } =
    useContext(FlaggedStudentsContext);

  return (
    <div className="dashboard-container">
      <header className="dashboard-header">
        <h1>🎓 Exam Center Monitoring System</h1>
        <p>Real-time Admin Dashboard for Unethical Behavior Detection</p>
      </header>

      <div className="stats-section">
        <div className="stat-card">
          <div className="stat-icon">🚩</div>
          <div className="stat-content">
            <p className="stat-label">Flagged Students</p>
            <h2 className="stat-value">{stats.flagged_students}</h2>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">👥</div>
          <div className="stat-content">
            <p className="stat-label">Students with Offenses</p>
            <h2 className="stat-value">{stats.students_with_offenses}</h2>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">⚠️</div>
          <div className="stat-content">
            <p className="stat-label">Total Offenses</p>
            <h2 className="stat-value">{stats.total_offenses}</h2>
          </div>
        </div>
      </div>

      <div className="students-section">
        <div className="section-header">
          <h2>Flagged Students</h2>
          <span className="count-badge">{flaggedStudents.length}</span>
        </div>

        {error && (
          <div className="error-message">
            <p>Error: {error}</p>
          </div>
        )}

        {loading ? (
          <div className="loading-container">
            <div className="spinner"></div>
            <p>Loading flagged students...</p>
          </div>
        ) : flaggedStudents.length > 0 ? (
          <div className="students-grid">
            {flaggedStudents.map(student => (
              <FlaggedStudentCard
                key={student.student_id}
                student={student}
                onReset={resetStudent}
                onClear={clearOffenses}
              />
            ))}
          </div>
        ) : (
          <div className="empty-state">
            <div className="empty-icon">✨</div>
            <h3>No Flagged Students</h3>
            <p>All students are behaving ethically during the exam.</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default Dashboard;
