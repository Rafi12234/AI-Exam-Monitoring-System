import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './FlaggedStudentCard.css';

const FlaggedStudentCard = ({ student, onReset, onClear }) => {
  const [offenses, setOffenses] = useState([]);
  const [showDetails, setShowDetails] = useState(false);
  const [loading, setLoading] = useState(false);

  const fetchOffenses = async () => {
    try {
      setLoading(true);
      const response = await axios.get(
        `http://localhost:5000/api/students/${student.student_id}/offenses`
      );
      if (response.data.status === 'success') {
        setOffenses(response.data.data);
      }
    } catch (err) {
      console.error('Error fetching offenses:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (showDetails) {
      fetchOffenses();
    }
  }, [showDetails]);

  const getBehaviorColor = (behaviorType) => {
    const colors = {
      'back': '#FF6B6B',
      'left': '#FFA500',
      'right': '#FFA500',
      'talking': '#FF4500',
      'unethical': '#DC143C'
    };
    return colors[behaviorType] || '#808080';
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleString();
  };

  return (
    <div className="student-card">
      <div className="card-header">
        <div className="student-info">
          <h3>{student.student_id}</h3>
          <span className={`offense-badge ${student.offenses_count >= 3 ? 'critical' : 'warning'}`}>
            {student.offenses_count} Offense{student.offenses_count !== 1 ? 's' : ''}
          </span>
        </div>
        <div className="card-actions">
          <button
            className="btn btn-details"
            onClick={() => setShowDetails(!showDetails)}
          >
            {showDetails ? 'Hide' : 'Show'} Details
          </button>
          <button
            className="btn btn-reset"
            onClick={() => onReset(student.student_id)}
          >
            Reset
          </button>
          <button
            className="btn btn-clear"
            onClick={() => onClear(student.student_id)}
          >
            Clear
          </button>
        </div>
      </div>

      {showDetails && (
        <div className="card-details">
          {loading ? (
            <p className="loading">Loading offenses...</p>
          ) : offenses.length > 0 ? (
            <div className="offenses-list">
              <h4>Recent Offenses:</h4>
              {offenses.slice(0, 5).map((offense, idx) => (
                <div key={idx} className="offense-item">
                  <span
                    className="behavior-type"
                    style={{ backgroundColor: getBehaviorColor(offense.behavior_type) }}
                  >
                    {offense.behavior_type}
                  </span>
                  <span className="offense-time">
                    {formatDate(offense.timestamp)}
                  </span>
                </div>
              ))}
              {offenses.length > 5 && (
                <p className="more-offenses">
                  +{offenses.length - 5} more offense{offenses.length - 5 !== 1 ? 's' : ''}
                </p>
              )}
            </div>
          ) : (
            <p className="no-offenses">No offense details available</p>
          )}
        </div>
      )}

      <div className="card-footer">
        <small>Status: {student.status}</small>
        <small>Flagged at: {new Date(student.flagged_at).toLocaleString()}</small>
      </div>
    </div>
  );
};

export default FlaggedStudentCard;
