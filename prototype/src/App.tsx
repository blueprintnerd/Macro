import { useState } from 'react';
import Landing from './components/Landing';
import Auth from './components/Auth';
import Dashboard from './components/Dashboard';
import './styles/index.css';

function App() {
  const [view, setView] = useState<'landing' | 'auth' | 'dashboard'>('landing');
  const [user, setUser] = useState<string | null>(null);

  const handleGetStarted = () => setView('auth');
  
  const handleLogin = (username: string) => {
    setUser(username);
    setView('dashboard');
  };

  const handleLogout = () => {
    setUser(null);
    setView('landing');
  };

  return (
    <div className="App">
      {view === 'landing' && <Landing onGetStarted={handleGetStarted} />}
      {view === 'auth' && <Auth onLogin={handleLogin} />}
      {view === 'dashboard' && user && <Dashboard user={user} onLogout={handleLogout} />}
    </div>
  );
}

export default App;
