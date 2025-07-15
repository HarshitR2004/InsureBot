import React, { useState, useEffect } from 'react'
import { ScaleLoader } from 'react-spinners'


export const LoadingScreen = ({ onSystemReady }) => {
  const [initStatus, setInitStatus] = useState({
    overall_ready: false,
    total_progress: 0,
    current_step: "Initializing..."
  });

  useEffect(() => {
    const checkSystemStatus = async () => {
      try {
        const response = await fetch('http://localhost:8000/status');
        const data = await response.json();
        
        setInitStatus({
          overall_ready: data.initialization_status.overall_ready,
          total_progress: data.initialization_status.total_progress,
          current_step: data.initialization_status.current_step
        });

        // If system is ready and callback exists, notify parent
        if (data.initialization_status.overall_ready && onSystemReady) {
          setTimeout(() => {
            onSystemReady();
          }, 1000); // Small delay to show completion
        }
      } catch (error) {
        console.error('Failed to fetch system status:', error);
      }
    };

    // Check status immediately
    checkSystemStatus();

    // Poll for status updates every 500ms
    const interval = setInterval(checkSystemStatus, 500);

    // Cleanup interval on component unmount
    return () => clearInterval(interval);
  }, [onSystemReady]);

  // Don't render if system is ready
  if (initStatus.overall_ready) {
    return null;
  }

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      width: '100vw',
      height: '100vh',
      backgroundColor: 'black',
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      zIndex: 9999
    }}>
      <ScaleLoader
        color="#90EE90"
        loading={true}
        size={150}
      />
    </div>
  )
}
