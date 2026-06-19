import { useState, useEffect } from 'react';
import { Music, Video, Image, HardDrive } from 'lucide-react';
import { motion } from 'framer-motion';

const Landing = ({ onGetStarted }: { onGetStarted: () => void }) => {
  const [priceIndex, setPriceIndex] = useState(0);
  const prices = ["$0", "Free", "0 BTC", "There is no price"];

  useEffect(() => {
    const interval = setInterval(() => {
      setPriceIndex((prev) => (prev + 1) % prices.length);
    }, 2000);
    return () => clearInterval(interval);
  }, []);

  const features = [
    { icon: <Music size={24} />, title: 'Music', desc: 'Stream your entire library in high fidelity.' },
    { icon: <Video size={24} />, title: 'Video', desc: '4K playback for all your movies and shows.' },
    { icon: <Image size={24} />, title: 'Photos', desc: 'Securely store and browse your memories.' },
    { icon: <HardDrive size={24} />, title: 'Storage', desc: 'Your private cloud, accessible anywhere.' },
  ];

  return (
    <div className="landing-container">
      <nav style={{ padding: '2rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h1 className="gradient-text" style={{ fontSize: '2rem', fontWeight: '800' }}>MACRO</h1>
        <button className="secondary-btn" onClick={onGetStarted}>Sign In</button>
      </nav>

      <main style={{ maxWidth: '1200px', margin: '0 auto', padding: '4rem 2rem', textAlign: 'center' }}>
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
        >
          <h2 style={{ fontSize: '4.5rem', fontWeight: '900', marginBottom: '1.5rem', lineHeight: '1.1' }}>
            Your Media. <br />
            <span className="gradient-text">No Strings Attached.</span>
          </h2>
          <p style={{ fontSize: '1.25rem', color: 'var(--text-secondary)', marginBottom: '2.5rem', maxWidth: '600px', marginInline: 'auto' }}>
            The ultimate self-hosted alternative to Plex and Spotify. 
            Free, open-source, and entirely yours.
          </p>
          <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center', marginBottom: '5rem' }}>
            <button className="primary-btn" onClick={onGetStarted}>Get Started Now</button>
            <button className="secondary-btn">Github</button>
          </div>
        </motion.div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '2rem', marginBottom: '6rem' }}>
          {features.map((f, i) => (
            <motion.div 
              key={i}
              className="glass-card" 
              style={{ padding: '2rem', textAlign: 'left' }}
              whileHover={{ scale: 1.05 }}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.1 }}
            >
              <div style={{ background: 'var(--accent-gradient)', width: '48px', height: '48px', borderRadius: '12px', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: '1.5rem' }}>
                {f.icon}
              </div>
              <h3 style={{ fontSize: '1.5rem', marginBottom: '0.5rem' }}>{f.title}</h3>
              <p style={{ color: 'var(--text-secondary)' }}>{f.desc}</p>
            </motion.div>
          ))}
        </div>

        <motion.div 
          className="glass-card" 
          style={{ padding: '4rem 2rem', background: 'linear-gradient(rgba(255,255,255,0.03), rgba(255,255,255,0.01))' }}
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
        >
          <h3 style={{ fontSize: '2rem', marginBottom: '1rem' }}>Get it for the price of</h3>
          <h1 className="gradient-text" style={{ fontSize: '5rem', fontWeight: '900' }}>{prices[priceIndex]}</h1>
          <p style={{ marginTop: '1.5rem', color: 'var(--text-secondary)' }}>Set and forget. Complete the setup once and own your data forever.</p>
        </motion.div>
      </main>

      <footer style={{ padding: '4rem 2rem', textAlign: 'center', color: 'var(--text-secondary)', borderTop: '1px solid var(--card-border)' }}>
        <p>© 2026 Macro Media. Built with Scutoid Design.</p>
      </footer>
    </div>
  );
};

export default Landing;
