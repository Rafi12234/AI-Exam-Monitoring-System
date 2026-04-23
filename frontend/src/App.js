import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { FlaggedStudentsProvider } from './context/FlaggedStudentsContext';
import Dashboard from './components/Dashboard';
import CameraView from './components/CameraView';
import Navigation from './components/Navigation';
import './App.css';

function App() {
  return (
    <FlaggedStudentsProvider>
      <Router>
        <Navigation />
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/camera" element={<CameraView />} />
        </Routes>
      </Router>
    </FlaggedStudentsProvider>
  );
}

export default App;
