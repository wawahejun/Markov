import React, { useState } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { ChevronDown } from 'lucide-react';
import { FloatingNav } from './components/walrus/FloatingNav';
import { HomePage } from './components/walrus/HomePage';
import { SovereigntyCenter } from './components/walrus/SovereigntyCenter';
import { PrivacyDiscovery } from './components/walrus/PrivacyDiscovery';
import { EventForge } from './components/walrus/EventForge';
import { ZKEntry } from './components/walrus/ZKEntry';
import { ReputationSystem } from './components/walrus/ReputationSystem';
import { GovernanceHall } from './components/walrus/GovernanceHall';
import { cn } from './components/ui/utils';

// Background Particles Component
const StarField = () => {
  const [dimensions, setDimensions] = useState({ width: 0, height: 0 });

  React.useEffect(() => {
    const handleResize = () => {
      setDimensions({ width: window.innerWidth, height: window.innerHeight });
    };
    handleResize();
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  return (
    <div className="absolute inset-0 overflow-hidden pointer-events-none">
      {dimensions.width > 0 && [...Array(20)].map((_, i) => (
        <motion.div
          key={i}
          className="absolute rounded-full"
          initial={{
            x: Math.random() * dimensions.width,
            y: Math.random() * dimensions.height,
            opacity: Math.random() * 0.3 + 0.1,
            scale: Math.random() * 0.5 + 0.5
          }}
          animate={{
            y: [null, Math.random() * dimensions.height],
            opacity: [null, Math.random() * 0.3 + 0.1]
          }}
          transition={{
            duration: Math.random() * 10 + 10,
            repeat: Infinity,
            ease: "linear"
          }}
          style={{
            width: Math.random() * 3 + 1 + 'px',
            height: Math.random() * 3 + 1 + 'px',
            background: i % 2 === 0 ? '#F59E0B' : '#FBBF24',
          }}
        />
      ))}
    </div>
  );
};

export default function App() {
  const [activePage, setActivePage] = useState('discovery');
  const [calendarOpen, setCalendarOpen] = useState(false);

  const renderPage = () => {
    switch (activePage) {
      case 'landing': return <HomePage onNavigate={setActivePage} />;
      case 'home': return <SovereigntyCenter />;
      case 'discovery': return <PrivacyDiscovery />;
      case 'forge': return <EventForge />;
      case 'zkentry': return <ZKEntry />;
      case 'reputation': return <ReputationSystem />;
      case 'governance': return <GovernanceHall />;
      default: return <HomePage onNavigate={setActivePage} />;
    }
  };

  return (
    <div className="relative w-full h-screen bg-gradient-to-br from-amber-50 via-orange-50/60 to-rose-50/40 text-gray-800 overflow-hidden font-sans selection:bg-amber-200/40">
      {/* Global Background */}
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top_right,_var(--tw-gradient-stops))] from-amber-100/40 via-orange-50/30 to-yellow-50/30" />
      <StarField />

      {/* Global Calendar Drawer */}
      <motion.div
        initial={{ y: '-100%' }}
        animate={{ y: calendarOpen ? 0 : '-95%' }}
        transition={{ type: "spring", stiffness: 100, damping: 20 }}
        className="absolute top-0 left-0 right-0 h-2/3 bg-white/95 backdrop-blur-xl z-40 border-b-2 border-amber-200 flex flex-col shadow-2xl"
      >
        <div className="flex-1 p-8">
          <h2 className="text-2xl font-bold text-gray-800 mb-6">Global Timeline</h2>
          <div className="grid grid-cols-7 gap-4 h-full pb-12">
            {['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'].map(d => (
              <div key={d} className="text-center text-gray-500 uppercase tracking-widest text-xs font-medium">{d}</div>
            ))}
            {Array.from({ length: 35 }).map((_, i) => (
              <div key={i} className="border-2 border-amber-100 rounded-lg p-2 hover:bg-amber-50 transition-colors relative bg-white">
                <span className="text-xs text-gray-600">{i + 1}</span>
                {[5, 12, 18, 24].includes(i + 1) && (
                  <div className="absolute bottom-2 right-2 w-2 h-2 rounded-full bg-amber-500 shadow-[0_0_5px_rgba(245,158,11,0.6)]" />
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Pull Tab */}
        <div
          className="h-12 w-full flex items-center justify-center cursor-pointer hover:bg-amber-50 transition-colors border-t-2 border-amber-200"
          onClick={() => setCalendarOpen(!calendarOpen)}
        >
          <ChevronDown
            className={cn("text-amber-600 transition-transform", calendarOpen ? "rotate-180" : "")}
          />
        </div>
      </motion.div>

      {/* Main Content Area */}
      <div className="relative z-10 w-full h-full pt-16">
        <AnimatePresence mode="wait">
          <motion.div
            key={activePage}
            initial={{ opacity: 0, y: 20, filter: 'blur(10px)' }}
            animate={{ opacity: 1, y: 0, filter: 'blur(0px)' }}
            exit={{ opacity: 0, y: -20, filter: 'blur(10px)' }}
            transition={{ duration: 0.3 }}
            className="w-full h-full"
          >
            {renderPage()}
          </motion.div>
        </AnimatePresence>
      </div>

      {/* Navigation */}
      <FloatingNav activePage={activePage} setActivePage={setActivePage} />
    </div>
  );
}
