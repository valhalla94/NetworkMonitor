import React, { useState, useEffect, createContext, useContext } from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import Dashboard from './components/Dashboard';
import SettingsPage from './components/SettingsPage';
import StatusPage from './components/StatusPage';
import { LayoutDashboard, Settings, Sun, Moon, Activity } from 'lucide-react';

export const ThemeContext = createContext({ dark: true, toggle: () => {} });

function App() {
  const [dark, setDark] = useState(() => {
    const stored = localStorage.getItem('theme');
    return stored ? stored === 'dark' : true;
  });

  useEffect(() => {
    document.documentElement.classList.toggle('dark', dark);
    localStorage.setItem('theme', dark ? 'dark' : 'light');
  }, [dark]);

  return (
    <ThemeContext.Provider value={{ dark, toggle: () => setDark(d => !d) }}>
      <Router>
        <div className="min-h-screen text-slate-100 dark:text-slate-100">
          <header className="border-b border-slate-800 bg-slate-900/50 backdrop-blur-lg sticky top-0 z-50">
            <div className="max-w-7xl mx-auto px-4 md:px-8 py-4">
              <div className="flex items-center justify-between gap-4">
                <Link to="/" className="flex items-center gap-3 hover:opacity-80 transition-opacity min-w-0">
                  <div className="bg-gradient-to-br from-blue-600 to-blue-500 p-2.5 md:p-3 rounded-xl shadow-lg shadow-blue-900/30 flex-shrink-0">
                    <LayoutDashboard className="text-white w-5 h-5 md:w-7 md:h-7" />
                  </div>
                  <h1 className="text-2xl md:text-4xl font-bold bg-gradient-to-r from-blue-400 via-purple-400 to-pink-400 bg-clip-text text-transparent truncate">
                    Network Monitor
                  </h1>
                </Link>
                <div className="flex items-center gap-2 flex-shrink-0">
                  <Link to="/status"
                    className="px-3 md:px-4 py-2 rounded-xl font-medium text-slate-400 hover:text-white hover:bg-slate-800/50 transition-all flex items-center gap-1.5 text-sm">
                    <Activity className="w-4 h-4" />
                    <span className="hidden sm:inline">Status</span>
                  </Link>
                  <button
                    onClick={() => setDark(d => !d)}
                    className="p-2 rounded-xl text-slate-400 hover:text-white hover:bg-slate-800/50 transition-all"
                    title={dark ? 'Switch to light mode' : 'Switch to dark mode'}
                  >
                    {dark ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
                  </button>
                  <Link to="/settings"
                    className="glass-button px-4 md:px-6 py-2 md:py-2.5 rounded-xl font-medium flex items-center gap-2 text-sm">
                    <Settings className="w-4 h-4 md:w-5 md:h-5" />
                    <span className="hidden sm:inline">Settings</span>
                  </Link>
                </div>
              </div>
            </div>
          </header>

          <main className="p-4 md:p-8">
            <div className="max-w-7xl mx-auto">
              <Routes>
                <Route path="/" element={<Dashboard />} />
                <Route path="/settings" element={<SettingsPage />} />
                <Route path="/status" element={<StatusPage />} />
              </Routes>
            </div>
          </main>
        </div>
      </Router>
    </ThemeContext.Provider>
  );
}

export default App;
