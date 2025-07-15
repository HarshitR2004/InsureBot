import { useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, useNavigate, Navigate } from 'react-router-dom'
import { LoadingScreen } from '../pages/LoadingScreen'
import SystemReady from '../pages/SystemReady'
import './App.css'

// Loading Page Component that handles navigation
const LoadingPage = () => {
  const navigate = useNavigate()

  const handleSystemReady = () => {
    navigate('/system-ready')
  }

  return <LoadingScreen onSystemReady={handleSystemReady} />
}

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<LoadingPage />} />
        <Route path="/system-ready" element={<SystemReady />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Router>
  )
}

export default App
