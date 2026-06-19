import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Music, Video, HardDrive, Search, Bell, Settings, 
  Play, Pause, SkipBack, SkipForward, Volume2, 
  MoreVertical, Home
} from 'lucide-react';

const Dashboard = ({ user, onLogout }: { user: string; onLogout: () => void }) => {
  const [activeTab, setActiveTab] = useState('Music');
  const [playing, setPlaying] = useState<any>(null);

  const mockData = {
    Music: [
      { id: 1, title: 'Midnight City', artist: 'M83', album: 'Hurry Up, We\'re Dreaming', color: '#ff4b2b' },
      { id: 2, title: 'Starboy', artist: 'The Weeknd', album: 'Starboy', color: '#8e2de2' },
      { id: 3, title: 'Blinding Lights', artist: 'The Weeknd', album: 'After Hours', color: '#f09819' },
      { id: 4, title: "Day 'n' Nite", artist: 'Kid Cudi', album: 'Man on the Moon', color: '#00c6ff' },
      { id: 5, title: 'Levitating', artist: 'Dua Lipa', album: 'Future Nostalgia', color: '#ff0080' },
      { id: 6, title: 'Stay', artist: 'The Kid LAROI', album: 'F*CK LOVE 3', color: '#4facfe' },
    ],
    Video: [
      { id: 7, title: 'Interstellar', year: '2014', duration: '2h 49m', color: '#434343' },
      { id: 8, title: 'The Matrix', year: '1999', duration: '2h 16m', color: '#000000' },
      { id: 9, title: 'Inception', year: '2010', duration: '2h 28m', color: '#30cfd0' },
    ],
    Files: [
      { id: 10, title: 'Resume.pdf', size: '1.2 MB', type: 'PDF' },
      { id: 11, title: 'Project_Final.zip', size: '450 MB', type: 'Archive' },
      { id: 12, title: 'Budget_2026.xlsx', size: '84 KB', type: 'Sheet' },
    ]
  };

  return (
    <div style={{ display: 'flex', height: '100vh', background: '#000' }}>
      {/* Sidebar */}
      <aside style={{ width: '260px', borderRight: '1px solid var(--card-border)', display: 'flex', flexDirection: 'column', padding: '2rem 1.5rem' }}>
        <h1 className="gradient-text" style={{ fontSize: '1.5rem', fontWeight: '800', marginBottom: '3rem' }}>MACRO</h1>
        
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
          {[
            { name: 'Home', icon: <Home size={20} /> },
            { name: 'Music', icon: <Music size={20} /> },
            { name: 'Video', icon: <Video size={20} /> },
            { name: 'Files', icon: <HardDrive size={20} /> },
          ].map((item) => (
            <button
              key={item.name}
              onClick={() => setActiveTab(item.name)}
              style={{
                display: 'flex', alignItems: 'center', gap: '1rem', padding: '12px 16px', borderRadius: '12px',
                background: activeTab === item.name ? 'rgba(255,255,255,0.1)' : 'transparent',
                color: activeTab === item.name ? 'white' : 'var(--text-secondary)',
                fontWeight: activeTab === item.name ? '600' : '400', textAlign: 'left'
              }}
            >
              {item.icon} {item.name}
            </button>
          ))}
        </div>

        <div style={{ marginTop: 'auto', display: 'flex', alignItems: 'center', gap: '1rem', padding: '1rem', borderTop: '1px solid var(--card-border)' }}>
          <div style={{ width: '40px', height: '40px', borderRadius: '50%', background: 'var(--accent-gradient)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 'bold' }}>
            {user[0].toUpperCase()}
          </div>
          <div style={{ flex: 1 }}>
            <p style={{ fontSize: '0.9rem', fontWeight: '600' }}>{user}</p>
            <p style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', cursor: 'pointer' }} onClick={onLogout}>Sign Out</p>
          </div>
          <Settings size={18} style={{ color: 'var(--text-secondary)', cursor: 'pointer' }} />
        </div>
      </aside>

      {/* Main Content */}
      <main style={{ flex: 1, overflowY: 'auto', padding: '2rem 3rem', paddingBottom: '120px' }}>
        <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '3rem' }}>
          <div style={{ position: 'relative', width: '400px' }}>
            <Search size={18} style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-secondary)' }} />
            <input 
              type="text" 
              placeholder={`Search in ${activeTab}...`} 
              style={{ width: '100%', padding: '10px 10px 10px 40px', borderRadius: '10px', background: 'rgba(255,255,255,0.05)', border: '1px solid var(--card-border)', color: 'white' }}
            />
          </div>
          <div style={{ display: 'flex', gap: '1.5rem', alignItems: 'center' }}>
            <Bell size={20} style={{ color: 'var(--text-secondary)', cursor: 'pointer' }} />
            <div style={{ padding: '8px 16px', borderRadius: '8px', background: 'rgba(34, 197, 94, 0.1)', color: '#22c55e', fontSize: '0.8rem', fontWeight: '600' }}>
              ● Server Online
            </div>
          </div>
        </header>

        <h2 style={{ fontSize: '2rem', marginBottom: '2rem' }}>{activeTab === 'Home' ? 'Recently Played' : activeTab}</h2>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))', gap: '2rem' }}>
          {(mockData[activeTab as keyof typeof mockData] || mockData.Music).map((item: any) => (
            <motion.div 
              key={item.id}
              className="glass-card"
              whileHover={{ y: -10 }}
              style={{ overflow: 'hidden', cursor: 'pointer' }}
              onClick={() => setPlaying(item)}
            >
              <div style={{ height: '200px', background: item.color || 'var(--accent-gradient)', display: 'flex', alignItems: 'center', justifyContent: 'center', position: 'relative' }}>
                {activeTab === 'Music' ? <Music size={48} opacity={0.5} /> : <Video size={48} opacity={0.5} />}
                <motion.div 
                  initial={{ opacity: 0 }}
                  whileHover={{ opacity: 1 }}
                  style={{ position: 'absolute', inset: 0, background: 'rgba(0,0,0,0.4)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}
                >
                  <div style={{ width: '50px', height: '50px', borderRadius: '50%', background: 'white', color: 'black', display: 'flex', alignItems: 'center', justifyContent: 'center', paddingLeft: '4px' }}>
                    <Play fill="black" size={24} />
                  </div>
                </motion.div>
              </div>
              <div style={{ padding: '1.25rem' }}>
                <h4 style={{ fontWeight: '600', marginBottom: '0.25rem', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{item.title}</h4>
                <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>{item.artist || item.year || item.size}</p>
              </div>
            </motion.div>
          ))}
        </div>
      </main>

      {/* Player Bar */}
      <AnimatePresence>
        {playing && (
          <motion.div 
            initial={{ y: 100 }}
            animate={{ y: 0 }}
            exit={{ y: 100 }}
            style={{ 
              position: 'fixed', bottom: '24px', left: '284px', right: '24px', height: '90px', 
              background: 'rgba(15, 15, 15, 0.8)', backdropFilter: 'blur(20px)', border: '1px solid var(--card-border)', 
              borderRadius: '20px', display: 'flex', alignItems: 'center', padding: '0 2rem', zIndex: 1000 
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', width: '300px' }}>
              <div style={{ width: '56px', height: '56px', borderRadius: '12px', background: playing.color, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <Music size={24} />
              </div>
              <div>
                <p style={{ fontWeight: '600', fontSize: '0.95rem' }}>{playing.title}</p>
                <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>{playing.artist || 'Macro Stream'}</p>
              </div>
            </div>

            <div style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '0.5rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '2rem' }}>
                <SkipBack size={20} style={{ color: 'var(--text-secondary)', cursor: 'pointer' }} />
                <div style={{ width: '40px', height: '40px', borderRadius: '50%', background: 'white', color: 'black', display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer' }}>
                  <Pause fill="black" size={20} />
                </div>
                <SkipForward size={20} style={{ color: 'var(--text-secondary)', cursor: 'pointer' }} />
              </div>
              <div style={{ width: '100%', maxWidth: '500px', height: '4px', background: 'rgba(255,255,255,0.1)', borderRadius: '2px', position: 'relative' }}>
                <div style={{ width: '35%', height: '100%', background: 'var(--accent-gradient)', borderRadius: '2px' }} />
              </div>
            </div>

            <div style={{ width: '300px', display: 'flex', justifyContent: 'flex-end', alignItems: 'center', gap: '1rem' }}>
              <Volume2 size={20} style={{ color: 'var(--text-secondary)' }} />
              <div style={{ width: '100px', height: '4px', background: 'rgba(255,255,255,0.1)', borderRadius: '2px' }}>
                <div style={{ width: '70%', height: '100%', background: 'white', borderRadius: '2px' }} />
              </div>
              <MoreVertical size={20} style={{ color: 'var(--text-secondary)', marginLeft: '1rem', cursor: 'pointer' }} />
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default Dashboard;
