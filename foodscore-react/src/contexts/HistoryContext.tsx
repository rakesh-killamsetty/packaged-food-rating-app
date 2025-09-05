import React, { createContext, useContext, useState, useEffect } from 'react';
import type { ScanResult } from '../services/api';

interface HistoryContextType {
  history: ScanResult[];
  addToHistory: (result: ScanResult) => void;
  clearHistory: () => void;
  removeFromHistory: (id: string) => void;
}

const HistoryContext = createContext<HistoryContextType | undefined>(undefined);

export const useHistory = () => {
  const context = useContext(HistoryContext);
  if (!context) {
    throw new Error('useHistory must be used within a HistoryProvider');
  }
  return context;
};

export const HistoryProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [history, setHistory] = useState<ScanResult[]>([]);

  // Load history from localStorage on mount
  useEffect(() => {
    const savedHistory = localStorage.getItem('foodscore-history');
    if (savedHistory) {
      try {
        setHistory(JSON.parse(savedHistory));
      } catch (error) {
        console.error('Failed to load history:', error);
      }
    }
  }, []);

  // Save history to localStorage whenever it changes
  useEffect(() => {
    localStorage.setItem('foodscore-history', JSON.stringify(history));
  }, [history]);

  const addToHistory = (result: ScanResult) => {
    const newResult = {
      ...result,
      id: `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      timestamp: new Date().toISOString(),
    };
    
    setHistory(prev => [newResult, ...prev.slice(0, 49)]); // Keep only last 50 items
  };

  const clearHistory = () => {
    setHistory([]);
  };

  const removeFromHistory = (id: string) => {
    setHistory(prev => prev.filter(item => item.id !== id));
  };

  return (
    <HistoryContext.Provider value={{
      history,
      addToHistory,
      clearHistory,
      removeFromHistory,
    }}>
      {children}
    </HistoryContext.Provider>
  );
};
