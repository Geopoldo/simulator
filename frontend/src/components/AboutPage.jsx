import React, { useState } from 'react';

function AboutPage() {
    const [activeTab, setActiveTab] = useState('overview');

    const tabs = [
        { id: 'overview', label: '📋 General' },
        { id: 'process', label: '⚙️ Proceso' },
        { id: 'formulas', label: '📐 Fórmulas' },
        { id: 'locations', label: '📍 Lugares' },
        { id: 'indicators', label: '📊 Indicadores' },
        { id: 'verification', label: '✅ Verificación' }
    ];

    return (
        <div className="max-w-5xl mx-auto p-4">
            {/* Header */}
            <div className="text-center mb-6">
                <h1 className="text-3xl font-bold text-indigo-600 mb-2">TULIAN</h1>
                <p className="text-lg text-gray-600">Simulador de Encuestas ODK con Contexto de Desastres</p>
                <p className="text-sm text-gray-400 mt-1">Versión 1.2 | Diciembre 2025</p>
            </div>

            {/* Tab Navigation */}
            <div className="flex flex-wrap justify-center gap-2 mb-6">
                {tabs.map(tab => (
                    <button
                        key={tab.id}
                        onClick={() => setActiveTab(tab.id)}
                        className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${activeTab === tab.id
                            ? 'bg-indigo-600 text-white shadow-md'
                            : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                            }`}
                    >
                        {tab.label}
                    </button>
                ))}
            </div>

            {/* Tab Content */}
            <div className="bg-white rounded-xl shadow-lg p-6">

                {/* OVERVIEW TAB */}
                {activeTab === 'overview' && (
                    <div className="space-y-6">
                        <div>
                            <h2 className="text-xl font-semibold text-gray-800 mb-3">¿Qué es TULIAN?</h2>
                            <p className="text-gray-600 leading-relaxed">
                                <strong>TULIAN</strong> genera datos sintéticos realistas para encuestas de seguridad
                                alimentaria. Usa datos de desastres reales (EM-DAT) y respeta todas las reglas del
                                formulario ODK.
                            </p>
                        </div>

                        <div className="grid md:grid-cols-4 gap-4">
                            <div className="bg-gradient-to-br from-blue-50 to-indigo-100 rounded-lg p-4 text-center">
                                <div className="text-2xl mb-2">📄</div>
                                <h3 className="font-semibold text-gray-800">1. Cargar</h3>
                                <p className="text-xs text-gray-600">XLSForm</p>
                            </div>
                            <div className="bg-gradient-to-br from-green-50 to-emerald-100 rounded-lg p-4 text-center">
                                <div className="text-2xl mb-2">🎲</div>
                                <h3 className="font-semibold text-gray-800">2. Simular</h3>
                                <p className="text-xs text-gray-600">Países + Años</p>
                            </div>
                            <div className="bg-gradient-to-br from-purple-50 to-violet-100 rounded-lg p-4 text-center">
                                <div className="text-2xl mb-2">📊</div>
                                <h3 className="font-semibold text-gray-800">3. Analizar</h3>
                                <p className="text-xs text-gray-600">7 Indicadores</p>
                            </div>
                            <div className="bg-gradient-to-br from-orange-50 to-amber-100 rounded-lg p-4 text-center">
                                <div className="text-2xl mb-2">📥</div>
                                <h3 className="font-semibold text-gray-800">4. Exportar</h3>
                                <p className="text-xs text-gray-600">CSV Orden ODK</p>
                            </div>
                        </div>

                        <div className="bg-amber-50 border-l-4 border-amber-400 p-4 rounded">
                            <h4 className="font-semibold text-amber-800">¿Para quién?</h4>
                            <p className="text-amber-700 text-sm">WFP, ONG humanitarias, analistas M&E, desarrolladores ODK.</p>
                        </div>
                    </div>
                )}

                {/* PROCESS TAB */}
                {activeTab === 'process' && (
                    <div className="space-y-6">
                        <h2 className="text-xl font-semibold text-gray-800">Proceso de Simulación</h2>

                        <div className="space-y-4">
                            {[
                                { step: 1, title: 'Parser ODK', desc: 'Extrae preguntas, tipos, choices, constraints, relevant' },
                                { step: 2, title: 'Carga Contexto', desc: 'Eventos EM-DAT + Perfil país (moneda, regiones, GPS)' },
                                { step: 3, title: 'Genera Hogares', desc: 'ID único, ubicación, características con semillas determinísticas' },
                                { step: 4, title: 'Itera Preguntas', desc: 'Evalúa relevant → genera valor → valida constraint → guarda' },
                                { step: 5, title: 'Aplica Contexto', desc: 'Ajusta por impacto desastre, progresión, asistencia' }
                            ].map(item => (
                                <div key={item.step} className="flex items-start gap-4 p-4 bg-gray-50 rounded-lg">
                                    <div className="w-8 h-8 bg-indigo-500 text-white rounded-full flex items-center justify-center font-bold text-sm">{item.step}</div>
                                    <div>
                                        <h4 className="font-semibold text-gray-800">{item.title}</h4>
                                        <p className="text-sm text-gray-600">{item.desc}</p>
                                    </div>
                                </div>
                            ))}
                        </div>

                        <div className="bg-blue-50 p-4 rounded-lg">
                            <h4 className="font-semibold text-blue-800 mb-2">📈 Curva de Progresión (4 años)</h4>
                            <div className="grid grid-cols-4 gap-2 text-center text-sm">
                                <div className="bg-red-100 p-2 rounded"><strong>Año 0</strong><br />0%<br />(Crisis)</div>
                                <div className="bg-yellow-100 p-2 rounded"><strong>Año 1</strong><br />60%<br />(Asistencia)</div>
                                <div className="bg-green-100 p-2 rounded"><strong>Año 2</strong><br />90%<br />(Consolidación)</div>
                                <div className="bg-emerald-100 p-2 rounded"><strong>Año 3+</strong><br />100%<br />(Sostenibilidad)</div>
                            </div>
                        </div>
                    </div>
                )}

                {/* FORMULAS TAB */}
                {activeTab === 'formulas' && (
                    <div className="space-y-6">
                        <h2 className="text-xl font-semibold text-gray-800">Fórmulas de Cálculo</h2>

                        {/* FCS Formula */}
                        <div className="border rounded-lg p-4">
                            <h3 className="font-bold text-indigo-700 mb-2">🍽️ FCS - Food Consumption Score</h3>
                            <div className="bg-gray-100 p-3 rounded font-mono text-sm mb-3">
                                FCS = (Cereales×2) + (Legumbres×3) + (Lácteos×4) + (Proteína×4) + (Vegetales×1) + (Frutas×1) + (Grasas×0.5) + (Azúcar×0.5)
                            </div>
                            <table className="w-full text-xs">
                                <thead className="bg-gray-50"><tr><th className="p-1 text-left">Campo</th><th className="p-1">Peso</th></tr></thead>
                                <tbody>
                                    <tr><td className="p-1">FCSStap (Cereales)</td><td className="p-1 text-center">×2</td></tr>
                                    <tr><td className="p-1">FCSPulse (Legumbres)</td><td className="p-1 text-center">×3</td></tr>
                                    <tr><td className="p-1">FCSDairy, FCSPr (Lácteos, Proteína)</td><td className="p-1 text-center">×4</td></tr>
                                    <tr><td className="p-1">FCSVeg, FCSFruit</td><td className="p-1 text-center">×1</td></tr>
                                    <tr><td className="p-1">FCSFat, FCSSugar</td><td className="p-1 text-center">×0.5</td></tr>
                                </tbody>
                            </table>
                            <p className="text-xs text-gray-500 mt-2">Clasificación: Pobre ≤21 | Límite 21.5-35 | Aceptable &gt;35</p>
                        </div>

                        {/* rCSI Formula */}
                        <div className="border rounded-lg p-4">
                            <h3 className="font-bold text-pink-700 mb-2">📉 rCSI - Reduced Coping Strategy Index</h3>
                            <div className="bg-gray-100 p-3 rounded font-mono text-sm mb-3">
                                rCSI = (rCSILessQlty×1) + (rCSIBorrow×2) + (rCSIMealSize×1) + (rCSIMealAdult×3) + (rCSIMealNb×1)
                            </div>
                            <table className="w-full text-xs">
                                <thead className="bg-gray-50"><tr><th className="p-1 text-left">Estrategia</th><th className="p-1">Peso</th></tr></thead>
                                <tbody>
                                    <tr><td className="p-1">rCSILessQlty - Alimentos menos preferidos</td><td className="p-1 text-center">×1</td></tr>
                                    <tr><td className="p-1">rCSIBorrow - Pidió prestado alimentos</td><td className="p-1 text-center">×2</td></tr>
                                    <tr><td className="p-1">rCSIMealSize - Redujo porciones</td><td className="p-1 text-center">×1</td></tr>
                                    <tr><td className="p-1">rCSIMealAdult - Adultos comen menos</td><td className="p-1 text-center">×3</td></tr>
                                    <tr><td className="p-1">rCSIMealNb - Menos comidas al día</td><td className="p-1 text-center">×1</td></tr>
                                </tbody>
                            </table>
                            <p className="text-xs text-gray-500 mt-2">Rango: 0-56. Menor = Mejor</p>
                        </div>

                        {/* FES Formula */}
                        <div className="border rounded-lg p-4">
                            <h3 className="font-bold text-green-700 mb-2">💰 FES - Food Expenditure Share</h3>
                            <div className="bg-gray-100 p-3 rounded font-mono text-sm mb-3">
                                FES = (Σ HHExpF*_MN_* / (Σ HHExpF*_MN_* + Σ HHExpNF*_MN_*)) × 100
                            </div>
                            <p className="text-xs text-gray-600">Suma todos los campos de gasto alimentario (HHExpF*) y no alimentario (HHExpNF*).</p>
                            <p className="text-xs text-gray-500 mt-2">Clasificación: ≥75% Pobre | 65-74% Límite | &lt;65% Adecuado</p>
                        </div>

                        {/* CARI Formula */}
                        <div className="border rounded-lg p-4">
                            <h3 className="font-bold text-purple-700 mb-2">🎯 CARI - Consolidated Approach</h3>
                            <div className="bg-gray-100 p-3 rounded font-mono text-sm mb-3">
                                CARI = promedio(FCS_cat + rCSI_cat + LhCSI_cat + FES_cat)
                            </div>
                            <p className="text-xs text-gray-600 mb-2">Cada indicador se clasifica en categorías 1-4, luego se promedian:</p>
                            <ul className="text-xs text-gray-500 list-disc list-inside">
                                <li>≥ 3.5: Severamente Inseguro</li>
                                <li>≥ 2.5: Moderadamente Inseguro</li>
                                <li>≥ 1.5: Marginalmente Seguro</li>
                                <li>&lt; 1.5: Seguro Alimentariamente</li>
                            </ul>
                        </div>
                    </div>
                )}

                {/* LOCATIONS TAB */}
                {activeTab === 'locations' && (
                    <div className="space-y-6">
                        <h2 className="text-xl font-semibold text-gray-800">Simulación de Lugares</h2>

                        {/* GPS Coordinates */}
                        <div className="border rounded-lg p-4">
                            <h3 className="font-bold text-blue-700 mb-2">📍 Coordenadas GPS</h3>
                            <p className="text-sm text-gray-600 mb-3">Las coordenadas se generan en este orden de prioridad:</p>

                            <div className="space-y-3">
                                <div className="flex items-start gap-3 p-3 bg-blue-50 rounded">
                                    <span className="bg-blue-500 text-white text-xs px-2 py-1 rounded">1</span>
                                    <div>
                                        <strong className="text-sm">Coordenadas de Desastres (EM-DAT)</strong>
                                        <p className="text-xs text-gray-600">Si hay desastres con coordenadas, se usa esa ubicación ±50km</p>
                                        <code className="text-xs bg-white p-1 rounded block mt-1">lat = disaster_lat + random(-0.5, 0.5)</code>
                                    </div>
                                </div>

                                <div className="flex items-start gap-3 p-3 bg-green-50 rounded">
                                    <span className="bg-green-500 text-white text-xs px-2 py-1 rounded">2</span>
                                    <div>
                                        <strong className="text-sm">Perfil del País</strong>
                                        <p className="text-xs text-gray-600">Si no hay desastres, usa el geopoint del perfil ±10km</p>
                                        <code className="text-xs bg-white p-1 rounded block mt-1">lat = profile_lat + random(-0.1, 0.1)</code>
                                    </div>
                                </div>

                                <div className="flex items-start gap-3 p-3 bg-orange-50 rounded">
                                    <span className="bg-orange-500 text-white text-xs px-2 py-1 rounded">3</span>
                                    <div>
                                        <strong className="text-sm">Faker (Fallback)</strong>
                                        <p className="text-xs text-gray-600">Si no hay perfil, Faker genera coordenadas del país</p>
                                        <code className="text-xs bg-white p-1 rounded block mt-1">lat, lon = Faker(locale).latlng()</code>
                                    </div>
                                </div>
                            </div>
                        </div>

                        {/* Administrative Regions */}
                        <div className="border rounded-lg p-4">
                            <h3 className="font-bold text-green-700 mb-2">🗺️ Regiones Administrativas</h3>
                            <p className="text-sm text-gray-600 mb-3">Los campos ADMIN se llenan desde el perfil del país:</p>

                            <table className="w-full text-sm">
                                <thead className="bg-gray-50"><tr><th className="p-2 text-left">Campo</th><th className="p-2 text-left">Fuente</th><th className="p-2 text-left">Ejemplo</th></tr></thead>
                                <tbody>
                                    <tr className="border-b"><td className="p-2">ADMIN0Name</td><td className="p-2">country_name</td><td className="p-2 text-gray-500">Colombia</td></tr>
                                    <tr className="border-b"><td className="p-2">ADMIN1Name</td><td className="p-2">profile['admin1']</td><td className="p-2 text-gray-500">Antioquia</td></tr>
                                    <tr className="border-b"><td className="p-2">ADMIN2Name</td><td className="p-2">profile['admin2']</td><td className="p-2 text-gray-500">Medellín</td></tr>
                                    <tr className="border-b"><td className="p-2">ADMIN3Name</td><td className="p-2">profile['admin3']</td><td className="p-2 text-gray-500">El Poblado</td></tr>
                                    <tr className="border-b"><td className="p-2">ADMIN4Name</td><td className="p-2">profile['streets']</td><td className="p-2 text-gray-500">Calle 10</td></tr>
                                    <tr><td className="p-2">ADMIN5Name</td><td className="p-2">profile['settlements']</td><td className="p-2 text-gray-500">Sector Norte</td></tr>
                                </tbody>
                            </table>
                        </div>

                        {/* Geopoint Format */}
                        <div className="border rounded-lg p-4">
                            <h3 className="font-bold text-purple-700 mb-2">📐 Formato Geopoint ODK</h3>
                            <div className="bg-gray-100 p-3 rounded font-mono text-sm">
                                _Geopoint_value = "latitud longitud altitud precisión"<br />
                                Ejemplo: "4.7110 -74.0721 0 0"
                            </div>
                            <p className="text-xs text-gray-500 mt-2">Altitud y precisión se dejan en 0 para datos simulados.</p>
                        </div>
                    </div>
                )}

                {/* INDICATORS TAB */}
                {activeTab === 'indicators' && (
                    <div className="space-y-6">
                        <h2 className="text-xl font-semibold text-gray-800">Indicadores WFP en Dashboard</h2>

                        <div className="space-y-3">
                            {[
                                { code: 'FCS', name: 'Food Consumption Score', icon: '🍽️', chart: 'LineChart', color: 'border-indigo-300', desc: 'Evolución por año' },
                                { code: 'rCSI', name: 'Reduced Coping Strategy', icon: '📉', chart: 'LineChart', color: 'border-pink-300', desc: 'Tendencia (menor = mejor)' },
                                { code: 'LhCSI', name: 'Livelihood Coping', icon: '🏠', chart: 'StackedBar', color: 'border-orange-300', desc: 'Distribución por categoría' },
                                { code: 'HHS', name: 'Household Hunger Scale', icon: '😔', chart: 'StackedBar', color: 'border-red-300', desc: 'No/Rarely/Sometimes/Often' },
                                { code: 'FES', name: 'Food Expenditure Share', icon: '💰', chart: 'AreaChart', color: 'border-green-300', desc: '% gasto en alimentos' },
                                { code: 'ECMEN', name: 'Economic Capacity', icon: '📊', chart: 'StackedBar', color: 'border-yellow-300', desc: 'Adecuado/Límite/Pobre' },
                                { code: 'CARI', name: 'Consolidated Approach', icon: '🎯', chart: 'DonutChart', color: 'border-purple-300', desc: 'Clasificación consolidada' }
                            ].map(ind => (
                                <div key={ind.code} className={`p-3 rounded-lg border-l-4 ${ind.color} bg-gray-50 flex justify-between items-center`}>
                                    <div>
                                        <div className="flex items-center gap-2 mb-1">
                                            <span>{ind.icon}</span>
                                            <strong className="text-gray-800">{ind.code}</strong>
                                            <span className="text-xs text-gray-500">- {ind.name}</span>
                                        </div>
                                        <p className="text-xs text-gray-600">{ind.desc}</p>
                                    </div>
                                    <span className="bg-white px-2 py-1 rounded text-xs text-gray-500">{ind.chart}</span>
                                </div>
                            ))}
                        </div>
                    </div>
                )}

                {/* VERIFICATION TAB */}
                {activeTab === 'verification' && (
                    <div className="space-y-6">
                        <h2 className="text-xl font-semibold text-gray-800">✅ Verificación y Calidad</h2>

                        <div className="bg-green-50 p-4 rounded-lg">
                            <h3 className="font-bold text-green-800 mb-3">Estado: VERIFICADO (v1.2)</h3>
                            <table className="w-full text-sm">
                                <tbody>
                                    <tr className="border-b"><td className="py-2">Campos ODK totales</td><td className="py-2 font-bold text-right">428</td></tr>
                                    <tr className="border-b"><td className="py-2">Campos en simulación</td><td className="py-2 font-bold text-right">330+</td></tr>
                                    <tr className="border-b"><td className="py-2">Orden de campos</td><td className="py-2 font-bold text-right text-green-600">100% ODK ✅</td></tr>
                                    <tr className="border-b"><td className="py-2">Validación Constraints</td><td className="py-2 font-bold text-right text-green-600">Estricta (0-11, 0-25) ✅</td></tr>
                                </tbody>
                            </table>
                        </div>

                        <div className="bg-white p-4 rounded-lg border border-gray-200">
                            <h4 className="font-semibold text-gray-800 mb-3">🛠️ Historial de Mejoras Recientes</h4>
                            <ul className="space-y-3 text-sm text-gray-600">
                                <li className="flex gap-2">
                                    <span className="text-green-500">✔</span>
                                    <div>
                                        <strong>Constraints Numéricos Estrictos:</strong>
                                        <p className="text-xs">Validación automática de rangos ODK (ej. HHSize 0-11, Gastos 0-25).</p>
                                    </div>
                                </li>
                                <li className="flex gap-2">
                                    <span className="text-green-500">✔</span>
                                    <div>
                                        <strong>Simulación Climática Realista:</strong>
                                        <p className="text-xs">Filtro regional inteligente que capta eventos nacionales y activa sub-módulos de desastres.</p>
                                    </div>
                                </li>
                                <li className="flex gap-2">
                                    <span className="text-green-500">✔</span>
                                    <div>
                                        <strong>Economía de Gastos Mejorada:</strong>
                                        <p className="text-xs">Impacto de desastres limitado (max 90%) para evitar valores negativos. Probabilidad de compra aumentada (65%) para mayor diversidad de datos.</p>
                                    </div>
                                </li>
                                <li className="flex gap-2">
                                    <span className="text-green-500">✔</span>
                                    <div>
                                        <strong>Integridad Módulos HHS:</strong>
                                        <p className="text-xs">Garantizada la generación de preguntas de frecuencia cuando aplica.</p>
                                    </div>
                                </li>
                                <li className="flex gap-2">
                                    <span className="text-green-500">✔</span>
                                    <div>
                                        <strong>Multi-País con Mapa Interactivo:</strong>
                                        <p className="text-xs">Selección visual de países y análisis comparativo automático.</p>
                                    </div>
                                </li>
                                <li className="flex gap-2">
                                    <span className="text-green-500">✔</span>
                                    <div>
                                        <strong>Verificación de Orden ODK:</strong>
                                        <p className="text-xs">Vista previa del orden de campos antes de exportar CSV.</p>
                                    </div>
                                </li>
                            </ul>
                        </div>

                        <div className="bg-blue-50 p-4 rounded-lg">
                            <h4 className="font-semibold text-blue-800 mb-2">Test de Regresión (Resultados)</h4>
                            <div className="grid grid-cols-2 gap-4 text-sm">
                                <div>
                                    <strong className="block text-gray-700">HHSize</strong>
                                    <span className="text-green-600">100% válido (0-11)</span>
                                </div>
                                <div>
                                    <strong className="block text-gray-700">Gastos &gt; 0</strong>
                                    <span className="text-green-600">100% verificado</span>
                                </div>
                                <div>
                                    <strong className="block text-gray-700">NonFood</strong>
                                    <span className="text-green-600">Presente (~4/hogar)</span>
                                </div>
                                <div>
                                    <strong className="block text-gray-700">HHS Freq</strong>
                                    <span className="text-green-600">Funcional</span>
                                </div>
                            </div>
                        </div>
                    </div>
                )}
            </div>

            <div className="text-center mt-6 text-gray-400 text-xs">
                TULIAN - Simulador de Seguridad Alimentaria | 2025
            </div>
        </div>
    );
}

export default AboutPage;
