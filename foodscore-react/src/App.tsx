import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Canvas } from '@react-three/fiber';
import { OrbitControls, Sphere, MeshDistortMaterial } from '@react-three/drei';
import { 
  Scan, 
  History, 
  Sun, 
  Moon, 
  User, 
  Heart, 
  Shield, 
  TrendingUp, 
  Users,
  Camera,
  Search,
  Zap,
  Star
} from 'lucide-react';
import EnhancedScanner from './components/EnhancedScanner';
import HistoryModal from './components/HistoryModal';
import { HistoryProvider } from './contexts/HistoryContext';

// 3D Background Component
const FloatingOrbs = () => {
  return (
    <Canvas camera={{ position: [0, 0, 5] }}>
      <ambientLight intensity={0.5} />
      <pointLight position={[10, 10, 10]} />
      {[...Array(6)].map((_, i) => (
        <Sphere key={i} args={[1, 100, 200]} position={[Math.random() * 10 - 5, Math.random() * 10 - 5, Math.random() * 10 - 5]}>
          <MeshDistortMaterial
            color={i % 2 === 0 ? '#22c55e' : '#0ea5e9'}
            attach="material"
            distort={0.3}
            speed={1.5}
            roughness={0.2}
            metalness={0.8}
          />
        </Sphere>
      ))}
      <OrbitControls enableZoom={false} autoRotate autoRotateSpeed={0.5} />
    </Canvas>
  );
};

// Particle System
const ParticleSystem = () => {
  const [particles, setParticles] = useState<Array<{ id: number; x: number; y: number; delay: number }>>([]);

  useEffect(() => {
    const newParticles = Array.from({ length: 50 }, (_, i) => ({
      id: i,
      x: Math.random() * window.innerWidth,
      y: Math.random() * window.innerHeight,
      delay: Math.random() * 5,
    }));
    setParticles(newParticles);
  }, []);

  return (
    <div className="fixed inset-0 pointer-events-none overflow-hidden">
      {particles.map((particle) => (
        <motion.div
          key={particle.id}
          className="particle w-1 h-1 bg-primary-500 rounded-full"
          style={{ left: particle.x, top: particle.y }}
          animate={{
            y: [0, -100, 0],
            opacity: [0, 1, 0],
          }}
          transition={{
            duration: 6,
            delay: particle.delay,
            repeat: Infinity,
            ease: "easeInOut",
          }}
        />
      ))}
    </div>
  );
};

// Theme Context
const ThemeContext = React.createContext<{
  isDark: boolean;
  toggleTheme: () => void;
}>({
  isDark: true,
  toggleTheme: () => {},
});

// Header Component
const Header = () => {
  const [isDark, setIsDark] = useState(() => {
    const saved = localStorage.getItem('theme');
    return saved ? saved === 'dark' : true;
  });
  const [showHistory, setShowHistory] = useState(false);

  const toggleTheme = () => {
    const newTheme = !isDark;
    setIsDark(newTheme);
    localStorage.setItem('theme', newTheme ? 'dark' : 'light');
    document.body.classList.toggle('light', !newTheme);
  };

  useEffect(() => {
    document.body.classList.toggle('light', !isDark);
  }, [isDark]);

  return (
    <ThemeContext.Provider value={{ isDark, toggleTheme }}>
      <motion.header 
        className={`fixed top-0 left-0 right-0 z-50 ${isDark ? 'glass-strong' : 'bg-white/90 backdrop-blur-md border-b border-gray-200'}`}
        initial={{ y: -100 }}
        animate={{ y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <div className="container mx-auto px-4 py-2">
          <div className="flex items-center justify-between">
            {/* Logo */}
            <motion.div 
              className="flex items-center space-x-2"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              <div className="relative">
                <Heart className="w-6 h-6 text-primary-500" />
                <motion.div
                  className="absolute inset-0"
                  animate={{ rotate: 360 }}
                  transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
                >
                  <Heart className="w-6 h-6 text-primary-500 opacity-30" />
                </motion.div>
              </div>
              <div>
                <h1 className={`text-xl font-bold ${isDark ? 'text-white' : 'text-gray-900'}`}>FoodScore</h1>
                <p className={`text-xs ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>Health Platform</p>
              </div>
            </motion.div>

            {/* Navigation */}
            <nav className="hidden md:flex items-center space-x-6">
              <motion.button 
                className={`flex items-center space-x-1 ${isDark ? 'text-white hover:text-primary-500' : 'text-gray-700 hover:text-primary-500'} transition-colors`}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => {
                  const scannerElement = document.getElementById('scanner');
                  scannerElement?.scrollIntoView({ behavior: 'smooth' });
                }}
              >
                <Scan className="w-4 h-4" />
                <span className="text-sm">Scanner</span>
              </motion.button>
              <motion.button 
                className={`flex items-center space-x-1 ${isDark ? 'text-white hover:text-primary-500' : 'text-gray-700 hover:text-primary-500'} transition-colors`}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => setShowHistory(true)}
              >
                <History className="w-4 h-4" />
                <span className="text-sm">History</span>
              </motion.button>
            </nav>

            {/* Theme Toggle & User */}
            <div className="flex items-center space-x-2">
              <motion.button
                className={`p-2 rounded-lg ${isDark ? 'glass hover:bg-primary-500/20' : 'bg-gray-100 hover:bg-gray-200'} transition-colors`}
                onClick={toggleTheme}
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.9 }}
              >
                {isDark ? <Sun className="w-4 h-4 text-white" /> : <Moon className="w-4 h-4 text-blue-600" />}
              </motion.button>
              <motion.button
                className={`p-2 rounded-lg ${isDark ? 'glass hover:bg-primary-500/20' : 'bg-gray-100 hover:bg-gray-200'} transition-colors`}
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.9 }}
              >
                <User className={`w-4 h-4 ${isDark ? 'text-white' : 'text-gray-700'}`} />
              </motion.button>
            </div>
          </div>
        </div>
      </motion.header>
      
      {/* History Modal */}
      <HistoryModal isOpen={showHistory} onClose={() => setShowHistory(false)} />
    </ThemeContext.Provider>
  );
};

// Hero Section
const HeroSection = () => {
  const [currentText, setCurrentText] = useState(0);
  const texts = [
    "Know What You're Really Eating",
    "Scan Any Packaged Food",
    "Get Instant Health Scores",
    "Make Informed Choices"
  ];

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentText((prev) => (prev + 1) % texts.length);
    }, 3000);
    return () => clearInterval(interval);
  }, [texts.length]);

  return (
    <section className="relative min-h-screen flex items-center justify-center overflow-hidden">
      {/* 3D Background */}
      <div className="absolute inset-0 opacity-20">
        <FloatingOrbs />
      </div>

      {/* Particle System */}
      <ParticleSystem />

      {/* Content */}
      <div className="relative z-10 text-center px-6 max-w-6xl mx-auto">
        {/* Badge */}
        <motion.div
          className="inline-flex items-center space-x-2 bg-primary-500/20 backdrop-blur-sm border border-primary-500/30 rounded-full px-4 py-2 mb-8"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
        >
          <Star className="w-4 h-4 text-primary-500" />
          <span className="text-sm font-medium text-primary-500">Evidence-Based Nutrition Analysis</span>
        </motion.div>

        {/* Main Headline */}
        <motion.h1
          className="text-5xl md:text-7xl font-bold mb-6"
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
        >
          <span className="text-white">Know What You're </span>
          <motion.span
            key={currentText}
            className="gradient-text"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.5 }}
          >
            Really Eating
          </motion.span>
        </motion.h1>

        {/* Subtitle */}
        <motion.p
          className="text-xl md:text-2xl text-white mb-12 max-w-3xl mx-auto leading-relaxed"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6 }}
        >
          Scan any packaged food to get an instant health score backed by WHO, FDA, and medical research. 
          Make informed choices with transparency you can trust.
        </motion.p>

        {/* CTA Buttons */}
        <motion.div
          className="flex flex-col sm:flex-row gap-6 justify-center items-center"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.8 }}
        >
          <motion.button
            className="btn-primary text-lg px-8 py-4 flex items-center space-x-3 group"
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            <Camera className="w-6 h-6 group-hover:animate-pulse" />
            <span>Start Scanning</span>
            <Zap className="w-5 h-5 group-hover:animate-bounce" />
          </motion.button>
          
          <motion.button
            className="btn-secondary text-lg px-8 py-4 flex items-center space-x-3 group"
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            <Search className="w-6 h-6" />
            <span>Search Products</span>
          </motion.button>
        </motion.div>

        {/* Stats */}
        <motion.div
          className="grid grid-cols-1 md:grid-cols-3 gap-8 mt-20"
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 1 }}
        >
          <div className="text-center">
            <div className="text-4xl font-bold text-primary-500 mb-2">10K+</div>
            <div className="text-white">Products Analyzed</div>
          </div>
          <div className="text-center">
            <div className="text-4xl font-bold text-accent-500 mb-2">99.9%</div>
            <div className="text-white">Accuracy Rate</div>
          </div>
          <div className="text-center">
            <div className="text-4xl font-bold text-purple-500 mb-2">50K+</div>
            <div className="text-white">Happy Users</div>
          </div>
        </motion.div>
      </div>
    </section>
  );
};

// Feature Cards
const FeatureCards = () => {
  const features = [
    {
      icon: Shield,
      title: "Medical Grade Analysis",
      description: "Scoring based on WHO, FDA guidelines and peer-reviewed research",
      color: "from-green-500 to-emerald-500"
    },
    {
      icon: TrendingUp,
      title: "Instant Insights",
      description: "Get your health score in seconds with clear explanations",
      color: "from-blue-500 to-cyan-500"
    },
    {
      icon: Users,
      title: "Trusted by Thousands",
      description: "Join health-conscious consumers making better choices",
      color: "from-purple-500 to-pink-500"
    }
  ];

  return (
    <section className="py-20 px-6">
      <div className="max-w-6xl mx-auto">
        <motion.div
          className="grid grid-cols-1 md:grid-cols-3 gap-8"
          initial={{ opacity: 0, y: 50 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          viewport={{ once: true }}
        >
          {features.map((feature, index) => (
            <motion.div
              key={index}
              className="feature-card glass rounded-2xl p-8 text-center group"
              initial={{ opacity: 0, y: 50 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.2 }}
              whileHover={{ y: -10, scale: 1.02 }}
            >
              <motion.div
                className={`w-16 h-16 mx-auto mb-6 rounded-2xl bg-gradient-to-r ${feature.color} flex items-center justify-center`}
                whileHover={{ rotate: 360 }}
                transition={{ duration: 0.6 }}
              >
                <feature.icon className="w-8 h-8 text-white" />
              </motion.div>
              <h3 className="text-2xl font-bold text-white mb-4">{feature.title}</h3>
              <p className="text-white leading-relaxed">{feature.description}</p>
            </motion.div>
          ))}
        </motion.div>
      </div>
    </section>
  );
};

// Main App Component
const App = () => {
  const [isDark] = useState(() => {
    const saved = localStorage.getItem('theme');
    return saved ? saved === 'dark' : true;
  });

  useEffect(() => {
    document.body.classList.toggle('light', !isDark);
  }, [isDark]);

  return (
    <HistoryProvider>
      <div className={`min-h-screen transition-colors duration-300 ${isDark ? 'animated-bg' : 'bg-gradient-to-br from-gray-50 to-gray-100'}`}>
        <Header />
        <HeroSection />
        <FeatureCards />
        <section id="scanner" className="py-20">
          <EnhancedScanner />
        </section>
        
        {/* Footer */}
        <footer className={`py-12 px-6 border-t ${isDark ? 'border-gray-800' : 'border-gray-200'}`}>
          <div className="max-w-6xl mx-auto text-center">
            <div className="flex items-center justify-center space-x-3 mb-6">
              <Heart className="w-8 h-8 text-primary-500" />
              <span className={`text-2xl font-bold ${isDark ? 'text-white' : 'text-gray-900'}`}>FoodScore</span>
            </div>
            <p className={`mb-6 ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>
              Empowering healthier choices through transparent nutrition analysis
            </p>
            <div className={`flex justify-center space-x-6 text-sm ${isDark ? 'text-gray-500' : 'text-gray-400'}`}>
              <span>© 2024 FoodScore</span>
              <span>•</span>
              <span>Privacy Policy</span>
              <span>•</span>
              <span>Terms of Service</span>
            </div>
          </div>
        </footer>
      </div>
    </HistoryProvider>
  );
};

export default App;