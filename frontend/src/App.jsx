
import React, { useState } from 'react';
import SceneUpload from './components/SceneUpload';
import SceneSimulation from './components/SceneSimulation';
import SceneVisualization from './components/SceneVisualization';
import AboutPage from './components/AboutPage';

function App() {
  const [activeScene, setActiveScene] = useState(1);
  const [odkStructure, setOdkStructure] = useState(null);

  const [selectedCountries, setSelectedCountries] = useState([]);
  const [simulationData, setSimulationData] = useState([]);

  // Param state persistence
  const [simParams, setSimParams] = useState({
    startYear: 2020,
    endYear: 2024,
    countPerYear: 10
  });

  return (
    <div className="min-h-screen flex flex-col">
      {/* Header */}
      <header className="bg-white shadow-sm p-4 z-10">
        <div className="max-w-7xl mx-auto flex justify-between items-center">
          <h1 className="text-xl font-bold text-indigo-600 tracking-tight">TULIAN - ODK Simulator</h1>
          <nav className="space-x-2">
            <button
              onClick={() => setActiveScene(1)}
              className={`px-4 py-2 rounded-md transition-colors ${activeScene === 1 ? 'bg-indigo-50 text-indigo-700 font-medium' : 'text-gray-500 hover:text-gray-900'}`}
            >
              1. Cargar ODK
            </button>
            <button
              onClick={() => odkStructure && setActiveScene(2)}
              disabled={!odkStructure}
              className={`px-4 py-2 rounded-md transition-colors ${activeScene === 2 ? 'bg-indigo-50 text-indigo-700 font-medium' : odkStructure ? 'text-gray-500 hover:text-gray-900' : 'text-gray-400 cursor-not-allowed'}`}
            >
              2. Simular
            </button>
            <button
              onClick={() => setActiveScene(3)}
              className={`px-4 py-2 rounded-md transition-colors ${activeScene === 3 ? 'bg-indigo-50 text-indigo-700 font-medium' : 'text-gray-500 hover:text-gray-900'}`}
            >
              3. Analizar
            </button>
            <button
              onClick={() => setActiveScene(4)}
              className={`px-4 py-2 rounded-md transition-colors ${activeScene === 4 ? 'bg-indigo-50 text-indigo-700 font-medium' : 'text-gray-500 hover:text-gray-900'}`}
            >
              ℹ️ Acerca de
            </button>
          </nav>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 bg-gray-50 p-6 overflow-auto">
        <div className="max-w-7xl mx-auto h-full">
          {activeScene === 1 && (
            <SceneUpload
              onUploadComplete={(data) => {
                setOdkStructure(data);
              }}
              onAdvance={() => setActiveScene(2)}
              structure={odkStructure}
            />
          )}

          {activeScene === 2 && odkStructure && (
            <SceneSimulation
              structure={odkStructure}
              selectedCountries={selectedCountries}
              setSelectedCountries={setSelectedCountries}
              simulationData={simulationData}
              setSimulationData={setSimulationData}
              simParams={simParams}
              setSimParams={setSimParams}
            />
          )}

          {activeScene === 3 && (
            <SceneVisualization />
          )}

          {activeScene === 4 && (
            <AboutPage />
          )}
        </div>
      </main>
    </div>
  );
}

export default App;

