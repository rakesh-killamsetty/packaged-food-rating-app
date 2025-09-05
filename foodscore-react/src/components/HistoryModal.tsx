import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Clock, Trash2, Eye, Calendar } from 'lucide-react';
import { useHistory } from '../contexts/HistoryContext';
import HealthScoreRing from './HealthScoreRing';

interface HistoryModalProps {
  isOpen: boolean;
  onClose: () => void;
}

const HistoryModal: React.FC<HistoryModalProps> = ({ isOpen, onClose }) => {
  const { history, clearHistory, removeFromHistory } = useHistory();

  const formatDate = (timestamp: string) => {
    return new Date(timestamp).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-500';
    if (score >= 60) return 'text-white';
    if (score >= 40) return 'text-orange-500';
    return 'text-red-500';
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          className="fixed inset-0 z-50 flex items-center justify-center p-4"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
        >
          {/* Backdrop */}
          <motion.div
            className="absolute inset-0 bg-black/50 backdrop-blur-sm"
            onClick={onClose}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
          />
          
          {/* Modal */}
          <motion.div
            className="relative w-full max-w-4xl max-h-[90vh] glass rounded-3xl overflow-hidden"
            initial={{ scale: 0.9, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0.9, opacity: 0 }}
            transition={{ type: "spring", damping: 25, stiffness: 300 }}
          >
            {/* Header */}
            <div className="flex items-center justify-between p-6 border-b border-gray-700">
              <div className="flex items-center space-x-3">
                <Clock className="w-6 h-6 text-primary-500" />
                <h2 className="text-2xl font-bold text-white">Scan History</h2>
                <span className="px-3 py-1 bg-primary-500/20 text-primary-500 rounded-full text-sm">
                  {history.length} items
                </span>
              </div>
              <div className="flex items-center space-x-2">
                {history.length > 0 && (
                  <motion.button
                    className="px-4 py-2 text-red-400 hover:text-red-300 hover:bg-red-500/10 rounded-lg transition-colors"
                    onClick={clearHistory}
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                  >
                    <Trash2 className="w-4 h-4" />
                  </motion.button>
                )}
                <motion.button
                  className="p-2 hover:bg-gray-700 rounded-lg transition-colors"
                  onClick={onClose}
                  whileHover={{ scale: 1.1 }}
                  whileTap={{ scale: 0.9 }}
                >
                  <X className="w-5 h-5 text-gray-400" />
                </motion.button>
              </div>
            </div>

            {/* Content */}
            <div className="p-6 max-h-[60vh] overflow-y-auto">
              {history.length === 0 ? (
                <div className="text-center py-12">
                  <Clock className="w-16 h-16 text-gray-600 mx-auto mb-4" />
                  <h3 className="text-xl font-semibold text-gray-400 mb-2">No History Yet</h3>
                  <p className="text-gray-500">Start scanning products to see your history here</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {history.map((item, index) => (
                    <motion.div
                      key={item.id || index}
                      className="glass rounded-2xl p-6 hover:bg-gray-700/50 transition-colors"
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: index * 0.1 }}
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-start space-x-4">
                            {/* Health Score */}
                            <div className="flex-shrink-0">
                              <HealthScoreRing score={item.score} size={60} />
                            </div>
                            
                            {/* Product Info */}
                            <div className="flex-1 min-w-0">
                              <h3 className="text-lg font-semibold text-white truncate">
                                {item.product_name}
                              </h3>
                              <p className="text-gray-400 text-sm">{item.brand}</p>
                              {item.barcode && (
                                <p className="text-gray-500 text-xs">Barcode: {item.barcode}</p>
                              )}
                              
                              {/* Quick Stats */}
                              <div className="flex items-center space-x-4 mt-2">
                                <div className="flex items-center space-x-1">
                                  <Calendar className="w-3 h-3 text-gray-500" />
                                  <span className="text-xs text-gray-500">
                                    {formatDate(item.timestamp || new Date().toISOString())}
                                  </span>
                                </div>
                                <div className={`text-sm font-medium ${getScoreColor(item.score)}`}>
                                  {item.score}/100 ({item.band})
                                </div>
                              </div>
                              
                              {/* Nutrition Summary */}
                              <div className="flex items-center space-x-4 mt-2 text-xs text-gray-500">
                                <span>{item.nutrition.calories} cal</span>
                                <span>{item.nutrition.total_sugars}g sugar</span>
                                <span>{item.nutrition.sodium}mg sodium</span>
                              </div>
                            </div>
                          </div>
                        </div>
                        
                        {/* Actions */}
                        <div className="flex items-center space-x-2 ml-4">
                          <motion.button
                            className="p-2 hover:bg-gray-600 rounded-lg transition-colors"
                            onClick={() => {
                              // TODO: Implement view details
                              console.log('View details for:', item.product_name);
                            }}
                            whileHover={{ scale: 1.1 }}
                            whileTap={{ scale: 0.9 }}
                          >
                            <Eye className="w-4 h-4 text-gray-400" />
                          </motion.button>
                          <motion.button
                            className="p-2 hover:bg-red-500/20 text-red-400 hover:text-red-300 rounded-lg transition-colors"
                            onClick={() => removeFromHistory(item.id || index.toString())}
                            whileHover={{ scale: 1.1 }}
                            whileTap={{ scale: 0.9 }}
                          >
                            <Trash2 className="w-4 h-4" />
                          </motion.button>
                        </div>
                      </div>
                    </motion.div>
                  ))}
                </div>
              )}
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
};

export default HistoryModal;
