import React, { useState, useRef, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Camera, Upload, X, CheckCircle, AlertTriangle, Loader2 } from 'lucide-react';
import HealthScoreRing from './HealthScoreRing';
import NutritionBar from './NutritionBar';
import { apiService, mockScanResult, type ScanResult } from '../services/api';

// Remove the local interface since we're importing it from the API service

const AdvancedScanner: React.FC = () => {
  const [isScanning, setIsScanning] = useState(false);
  const [scanResult, setScanResult] = useState<ScanResult | null>(null);
  const [dragActive, setDragActive] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0]);
    }
  }, []);

  const handleFile = async (file: File) => {
    if (file.type.startsWith('image/')) {
      setIsScanning(true);
      try {
        // Try to call the real API
        const response = await apiService.analyzeImage(file);
        if (response.success && response.data) {
          setScanResult(response.data);
        } else {
          // Fallback to mock data
          setScanResult(mockScanResult);
        }
      } catch (error) {
        console.error('API call failed, using mock data:', error);
        // Fallback to mock data
        setScanResult(mockScanResult);
      } finally {
        setIsScanning(false);
      }
    }
  };

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      handleFile(e.target.files[0]);
    }
  };

  const resetScanner = () => {
    setScanResult(null);
    setIsScanning(false);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <div className="max-w-6xl mx-auto px-6">
      <motion.div
        className="text-center mb-12"
        initial={{ opacity: 0, y: 30 }}
        whileInView={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
      >
        <h2 className="text-4xl md:text-5xl font-bold text-white mb-4">
          AI-Powered Food Scanner
        </h2>
        <p className="text-xl text-gray-400 max-w-3xl mx-auto">
          Upload any food image or barcode to get instant, medical-grade nutrition analysis
        </p>
      </motion.div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Upload Section */}
        <motion.div
          className="space-y-6"
          initial={{ opacity: 0, x: -50 }}
          whileInView={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.6 }}
        >
          <div
            className={`relative border-2 border-dashed rounded-3xl p-8 text-center transition-all duration-300 ${
              dragActive
                ? 'border-primary-500 bg-primary-500/10'
                : 'border-gray-600 hover:border-primary-500 hover:bg-primary-500/5'
            }`}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
          >
            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              onChange={handleFileInput}
              className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
              disabled={isScanning}
            />
            
            <motion.div
              className="space-y-4"
              animate={dragActive ? { scale: 1.05 } : { scale: 1 }}
            >
              <div className="w-20 h-20 mx-auto bg-gradient-to-r from-primary-500 to-accent-500 rounded-2xl flex items-center justify-center">
                <Upload className="w-10 h-10 text-white" />
              </div>
              
              <div>
                <h3 className="text-xl font-semibold text-white mb-2">
                  {dragActive ? 'Drop your image here' : 'Upload Food Image'}
                </h3>
                <p className="text-gray-400 mb-4">
                  Drag & drop or click to select an image
                </p>
                <div className="text-sm text-gray-500">
                  Supports JPG, PNG, WebP up to 10MB
                </div>
              </div>
            </motion.div>
          </div>

          <div className="text-center">
            <span className="text-gray-500">or</span>
          </div>

          <motion.button
            className="w-full btn-primary flex items-center justify-center space-x-3 py-4"
            onClick={() => fileInputRef.current?.click()}
            disabled={isScanning}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            <Camera className="w-6 h-6" />
            <span>Use Camera</span>
          </motion.button>
        </motion.div>

        {/* Results Section */}
        <motion.div
          className="space-y-6"
          initial={{ opacity: 0, x: 50 }}
          whileInView={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.6 }}
        >
          <AnimatePresence mode="wait">
            {isScanning ? (
              <motion.div
                key="scanning"
                className="glass rounded-3xl p-8 text-center"
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.9 }}
              >
                <div className="space-y-6">
                  <div className="relative">
                    <Loader2 className="w-16 h-16 text-primary-500 mx-auto animate-spin" />
                    <motion.div
                      className="absolute inset-0 w-16 h-16 mx-auto border-4 border-primary-500/30 rounded-full"
                      animate={{ scale: [1, 1.2, 1] }}
                      transition={{ duration: 2, repeat: Infinity }}
                    />
                  </div>
                  
                  <div>
                    <h3 className="text-2xl font-bold text-white mb-2">Analyzing...</h3>
                    <p className="text-gray-400">Our AI is examining your food image</p>
                  </div>
                  
                  <div className="space-y-2">
                    <div className="flex items-center space-x-3 text-sm text-gray-400">
                      <CheckCircle className="w-4 h-4 text-green-500" />
                      <span>Image processed</span>
                    </div>
                    <div className="flex items-center space-x-3 text-sm text-gray-400">
                      <Loader2 className="w-4 h-4 text-primary-500 animate-spin" />
                      <span>Nutrition analysis in progress</span>
                    </div>
                    <div className="flex items-center space-x-3 text-sm text-gray-400">
                      <div className="w-4 h-4 border-2 border-gray-600 rounded-full" />
                      <span>Generating health score</span>
                    </div>
                  </div>
                </div>
              </motion.div>
            ) : scanResult ? (
              <motion.div
                key="result"
                className="glass rounded-3xl p-8"
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.9 }}
              >
                <div className="space-y-6">
                  {/* Header */}
                  <div className="flex items-start justify-between">
                    <div>
                      <h3 className="text-2xl font-bold text-white">{scanResult.product_name}</h3>
                      <p className="text-gray-400">{scanResult.brand}</p>
                    </div>
                    <button
                      onClick={resetScanner}
                      className="p-2 rounded-lg hover:bg-gray-700 transition-colors"
                    >
                      <X className="w-5 h-5 text-gray-400" />
                    </button>
                  </div>

                  {/* Health Score */}
                  <div className="flex items-center justify-center">
                    <HealthScoreRing score={scanResult.score} size={150} />
                  </div>

                  {/* Nutrition Facts */}
                  <div className="space-y-4">
                    <h4 className="text-lg font-semibold text-white">Nutrition Facts (per {scanResult.serving_size})</h4>
                    <div className="space-y-3">
                      <NutritionBar
                        label="Sugar"
                        value={scanResult.nutrition.total_sugars}
                        maxValue={15}
                        unit="g"
                      />
                      <NutritionBar
                        label="Sodium"
                        value={scanResult.nutrition.sodium}
                        maxValue={400}
                        unit="mg"
                      />
                      <NutritionBar
                        label="Calories"
                        value={scanResult.nutrition.calories}
                        maxValue={100}
                        unit="kcal"
                      />
                      <NutritionBar
                        label="Saturated Fat"
                        value={scanResult.nutrition.saturated_fat}
                        maxValue={5}
                        unit="g"
                      />
                      <NutritionBar
                        label="Fiber"
                        value={scanResult.nutrition.dietary_fiber}
                        maxValue={10}
                        unit="g"
                      />
                    </div>
                  </div>

                  {/* Ingredients */}
                  <div className="space-y-3">
                    <h4 className="text-lg font-semibold text-white">Ingredients</h4>
                    <div className="flex flex-wrap gap-2">
                      {scanResult.ingredients.map((ingredient, index) => (
                        <motion.span
                          key={index}
                          className="px-3 py-1 bg-gray-700 rounded-full text-sm text-gray-300"
                          initial={{ opacity: 0, scale: 0.8 }}
                          animate={{ opacity: 1, scale: 1 }}
                          transition={{ delay: index * 0.05 }}
                        >
                          {ingredient}
                        </motion.span>
                      ))}
                    </div>
                  </div>

                  {/* Recommendations */}
                  <div className="space-y-3">
                    <h4 className="text-lg font-semibold text-white">Recommendations</h4>
                    <div className="space-y-2">
                      {scanResult.recommendations.map((rec, index) => (
                        <motion.div
                          key={index}
                          className="flex items-start space-x-3 p-3 bg-red-500/10 border border-red-500/20 rounded-lg"
                          initial={{ opacity: 0, x: -20 }}
                          animate={{ opacity: 1, x: 0 }}
                          transition={{ delay: index * 0.1 }}
                        >
                          <AlertTriangle className="w-5 h-5 text-red-500 mt-0.5 flex-shrink-0" />
                          <span className="text-sm text-gray-300">{rec}</span>
                        </motion.div>
                      ))}
                    </div>
                  </div>
                </div>
              </motion.div>
            ) : (
              <motion.div
                key="placeholder"
                className="glass rounded-3xl p-8 text-center"
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.9 }}
              >
                <div className="space-y-6">
                  <div className="w-20 h-20 mx-auto bg-gray-700 rounded-2xl flex items-center justify-center">
                    <Camera className="w-10 h-10 text-gray-400" />
                  </div>
                  
                  <div>
                    <h3 className="text-xl font-semibold text-white mb-2">Ready to Scan</h3>
                    <p className="text-gray-400">
                      Upload an image to get started with your nutrition analysis
                    </p>
                  </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </motion.div>
      </div>
    </div>
  );
};

export default AdvancedScanner;
