import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import Dashboard from './components/Dashboard';
import SettingsPage from './components/SettingsPage';
import { LayoutDashboard, Settings } from 'lucide-react';

function App() {
  return (
    <Router>
      <div className="min-h-screen text-slate-100">
        <header className="border-b border-slate-800 bg-slate-900/50 backdrop-blur-lg sticky top-0 z-50">
          <div className="max-w-7xl mx-auto px-4 md:px-8 py-4">
            <div className="flex flex-col md:flex-row items-center justify-between gap-4">
              <Link to="/" className="flex items-center gap-3 hover:opacity-80 transition-opacity">
                <div className="bg-gradient-to-br from-blue-600 to-blue-500 p-3 rounded-xl shadow-lg shadow-blue-900/30">
                  <LayoutDashboard className="text-white w-7 h-7" />
                </div>
                <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-400 via-purple-400 to-pink-400 bg-clip-text text-transparent">
                  Network Monitor
                </h1>
              </Link>
              <Link
                to="/settings"
                className="glass-button px-6 py-2.5 rounded-xl font-medium flex items-center gap-2"
              >
                <Settings className="w-5 h-5" />
                Settings
              </Link>
            </div>
          </div>
        </header>

        <main className="p-4 md:p-8">
          <div className="max-w-7xl mx-auto">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/settings" element={<SettingsPage />} />
            </Routes>
          </div>
        </main>
      </div>
    </Router>
  );
}

export default App;
