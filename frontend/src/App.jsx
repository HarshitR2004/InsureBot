import React from "react";
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import AudioPipeline from "./services/AudioPipeline";

const App = () => {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Navigate to="/chat" />} />
        <Route path="/chat" element={<AudioPipeline />} />
      </Routes>
    </Router>
  );
};

export default App;

