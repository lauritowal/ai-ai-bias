import React, { useEffect } from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import Setup from './pages/Setup';
import Comparisons from './pages/Comparisons';
import Results from './pages/Results';
import Admin from './pages/Admin';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/admin" element={<Admin />} />
        <Route path="/" element={<Setup />} />
        <Route path="/comparisons" element={<Comparisons />} />
        <Route path="/results" element={<Results />} />
      </Routes>
    </Router>
  );
}

export default App;