import React, { useState } from 'react';
import {
    LineChart, Line, BarChart, Bar, AreaChart, Area, PieChart, Pie, Cell,
    XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts';

// Indicator Explanations Component
const IndicatorLegend = () => {
    const [isExpanded, setIsExpanded] = useState(false);

    const indicators = [
        {
            code: 'FCS',
            name: 'Food Consumption Score',
            icon: '🍽️',
            color: 'bg-indigo-100 border-indigo-300',
            description: 'Mide la diversidad y frecuencia del consumo de alimentos en los últimos 7 días.',
            interpretation: 'Pobre ≤21 | Límite 21.5-35 | Aceptable >35',
            formula: 'Suma ponderada: Cereales×2 + Legumbres×3 + Lácteos×4 + Proteína×4 + Vegetales×1 + Frutas×1 + Grasas×0.5 + Azúcar×0.5'
        },
        {
            code: 'rCSI',
            name: 'Reduced Coping Strategy Index',
            icon: '📉',
            color: 'bg-pink-100 border-pink-300',
            description: 'Frecuencia de estrategias de supervivencia alimentaria usadas en los últimos 7 días.',
            interpretation: 'Menor = Mejor (0-56). Alto indica mayor vulnerabilidad.',
            formula: 'Alimentos menos preferidos×1 + Prestó alimentos×2 + Redujo porciones×1 + Adultos comen menos×3 + Menos comidas×1'
        },
        {
            code: 'LhCSI',
            name: 'Livelihood Coping Strategies',
            icon: '🏠',
            color: 'bg-orange-100 border-orange-300',
            description: 'Estrategias que afectan los medios de vida y capacidad futura del hogar.',
            interpretation: 'Categorías: Sin estrategias | Estrés | Crisis | Emergencia',
            formula: 'Estrés: vendió ahorros/bienes | Crisis: vendió activos productivos | Emergencia: mendicidad, actos ilegales'
        },
        {
            code: 'HHS',
            name: 'Household Hunger Scale',
            icon: '😔',
            color: 'bg-red-100 border-red-300',
            description: 'Mide la experiencia de hambre severa en el hogar.',
            interpretation: 'No/Raramente/A veces/Frecuente. Afirmativo = inseguridad alimentaria severa.',
            formula: 'Preguntas: ¿Sin comida? ¿Se acostó con hambre? ¿Pasó día sin comer?'
        },
        {
            code: 'FES',
            name: 'Food Expenditure Share',
            icon: '💰',
            color: 'bg-green-100 border-green-300',
            description: 'Porcentaje del gasto total destinado a alimentos.',
            interpretation: '≥75% Pobre | 65-74% Límite | <65% Adecuado',
            formula: '(Gasto en alimentos / Gasto total) × 100'
        },
        {
            code: 'ECMEN',
            name: 'Economic Capacity to Meet Essential Needs',
            icon: '📊',
            color: 'bg-yellow-100 border-yellow-300',
            description: 'Capacidad económica para cubrir necesidades esenciales basada en el gasto.',
            interpretation: 'Adecuado | Límite | Pobre',
            formula: 'Basado en FES y patrones de gasto total'
        },
        {
            code: 'CARI',
            name: 'Consolidated Approach for Reporting Indicators',
            icon: '🎯',
            color: 'bg-purple-100 border-purple-300',
            description: 'Clasificación consolidada que combina todos los indicadores anteriores.',
            interpretation: 'Seguro | Marginalmente Seguro | Moderadamente Inseguro | Severamente Inseguro',
            formula: 'Promedio ponderado de categorías FCS + rCSI + LhCSI + FES'
        }
    ];

    return (
        <div className="bg-slate-800 rounded-xl shadow border border-slate-700 mb-6">
            <button
                onClick={() => setIsExpanded(!isExpanded)}
                className="w-full p-4 flex justify-between items-center text-white hover:bg-slate-700/50 rounded-xl transition-colors"
            >
                <h3 className="text-lg font-semibold flex items-center gap-2">
                    📖 Guía de Indicadores
                    <span className="text-sm font-normal text-slate-400">({indicators.length} indicadores WFP)</span>
                </h3>
                <span className="text-slate-400">{isExpanded ? '▲ Ocultar' : '▼ Mostrar'}</span>
            </button>

            {isExpanded && (
                <div className="p-4 pt-0 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-3">
                    {indicators.map(ind => (
                        <div key={ind.code} className={`p-3 rounded-lg border ${ind.color}`}>
                            <div className="flex items-center gap-2 mb-2">
                                <span className="text-xl">{ind.icon}</span>
                                <div>
                                    <div className="font-bold text-slate-800">{ind.code}</div>
                                    <div className="text-xs text-slate-600">{ind.name}</div>
                                </div>
                            </div>
                            <p className="text-xs text-slate-700 mb-2">{ind.description}</p>
                            <div className="text-xs bg-white/50 p-2 rounded">
                                <strong>Interpretación:</strong> {ind.interpretation}
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};

const DashboardCharts = ({ activeData, selectedCountry }) => {

    const isComparisonMode = selectedCountry === "Comparison" || selectedCountry === "All Countries" || !selectedCountry;

    if (!activeData || activeData.length === 0) {
        return <div className="text-slate-500 p-4">No data available for charts.</div>;
    }

    // ===========================================
    // DATA PROCESSING FUNCTIONS
    // ===========================================

    // FCS Calculation (WFP Formula)
    const calculateFCS = (row) => {
        const weights = {
            FCSStap: 2,    // Staples
            FCSPulse: 3,   // Pulses
            FCSDairy: 4,   // Dairy
            FCSPr: 4,      // Protein
            FCSVeg: 1,     // Vegetables
            FCSFruit: 1,   // Fruits
            FCSFat: 0.5,   // Fats
            FCSSugar: 0.5  // Sugar
        };
        let score = 0;
        Object.entries(weights).forEach(([field, weight]) => {
            score += (parseFloat(row[field]) || 0) * weight;
        });
        return score;
    };

    // rCSI Calculation (WFP Formula)
    const calculateRCSI = (row) => {
        const weights = {
            rCSILessQlty: 1,   // Less preferred food
            rCSIBorrow: 2,     // Borrow food
            rCSIMealSize: 1,   // Reduce meal size
            rCSIMealAdult: 3,  // Adults reduce for children
            rCSIMealNb: 1      // Reduce number of meals
        };
        let score = 0;
        Object.entries(weights).forEach(([field, weight]) => {
            score += (parseFloat(row[field]) || 0) * weight;
        });
        return score;
    };

    // LhCSI Categories
    const getLhCSICategory = (row) => {
        // Check for emergency strategies
        const emergency = ['Lcs_em_ResAsset', 'Lcs_em_Begged', 'Lcs_em_IllegalAct'];
        const crisis = ['Lcs_crisis_ProdAssets', 'Lcs_crisis_Health', 'Lcs_crisis_OutSchool'];
        const stress = ['Lcs_stress_Savings', 'Lcs_stress_BorrowCash', 'Lcs_stress_SoldHHAssets'];

        // Check for any "Yes" (1 or 2) in each category
        const hasEmergency = emergency.some(f => row[f] === '1' || row[f] === '2' || row[f] === 1 || row[f] === 2);
        const hasCrisis = crisis.some(f => row[f] === '1' || row[f] === '2' || row[f] === 1 || row[f] === 2);
        const hasStress = stress.some(f => row[f] === '1' || row[f] === '2' || row[f] === 1 || row[f] === 2);

        if (hasEmergency) return 'Emergency';
        if (hasCrisis) return 'Crisis';
        if (hasStress) return 'Stress';
        return 'None';
    };

    // FES Calculation (Food Expenditure Share)
    const calculateFES = (row) => {
        // Sum food expenditures
        let foodExp = 0;
        let nonFoodExp = 0;

        Object.entries(row).forEach(([key, val]) => {
            const amount = parseFloat(val) || 0;
            if (key.startsWith('HHExpF') && key.includes('_MN_')) {
                foodExp += amount;
            } else if (key.startsWith('HHExpNF') && key.includes('_MN_')) {
                nonFoodExp += amount;
            }
        });

        const total = foodExp + nonFoodExp;
        return total > 0 ? (foodExp / total) * 100 : 0;
    };

    // FCS Category (WFP thresholds)
    const getFCSCategory = (score) => {
        if (score <= 21) return 'Poor';
        if (score <= 35) return 'Borderline';
        return 'Acceptable';
    };

    // CARI Classification (Consolidated Approach)
    const getCARICategory = (row) => {
        const fcs = calculateFCS(row);
        const fcsClass = fcs <= 21 ? 4 : fcs <= 35 ? 3 : fcs <= 42 ? 2 : 1;

        const rcsi = calculateRCSI(row);
        const rcsiClass = rcsi >= 19 ? 4 : rcsi >= 10 ? 3 : rcsi >= 4 ? 2 : 1;

        const lhcsi = getLhCSICategory(row);
        const lhcsiClass = lhcsi === 'Emergency' ? 4 : lhcsi === 'Crisis' ? 3 : lhcsi === 'Stress' ? 2 : 1;

        const fes = calculateFES(row);
        const fesClass = fes >= 75 ? 4 : fes >= 65 ? 3 : fes >= 50 ? 2 : 1;

        // Combined score (average rounded)
        const avg = (fcsClass + rcsiClass + lhcsiClass + fesClass) / 4;
        if (avg >= 3.5) return 'Severely Insecure';
        if (avg >= 2.5) return 'Moderately Insecure';
        if (avg >= 1.5) return 'Marginally Secure';
        return 'Food Secure';
    };

    // ===========================================
    // CHART DATA PROCESSORS
    // ===========================================

    // FCS & rCSI Trend Data
    const processTrendData = () => {
        const years = {};
        activeData.forEach(row => {
            const year = row.SvyDate ? row.SvyDate.substring(0, 4) : 'Unknown';
            if (!years[year]) {
                years[year] = { year, fcs_sum: 0, rcsi_sum: 0, fes_sum: 0, count: 0 };
            }
            years[year].fcs_sum += calculateFCS(row);
            years[year].rcsi_sum += calculateRCSI(row);
            years[year].fes_sum += calculateFES(row);
            years[year].count++;
        });

        return Object.values(years).sort((a, b) => a.year.localeCompare(b.year)).map(y => ({
            year: y.year,
            FCS: (y.fcs_sum / y.count).toFixed(1),
            rCSI: (y.rcsi_sum / y.count).toFixed(1),
            FES: (y.fes_sum / y.count).toFixed(1)
        }));
    };

    // LhCSI Distribution
    const processLhCSIData = () => {
        const years = {};
        activeData.forEach(row => {
            const year = row.SvyDate ? row.SvyDate.substring(0, 4) : 'Unknown';
            const cat = getLhCSICategory(row);
            if (!years[year]) years[year] = { year, None: 0, Stress: 0, Crisis: 0, Emergency: 0 };
            years[year][cat]++;
        });
        return Object.values(years).sort((a, b) => a.year.localeCompare(b.year));
    };

    // HHS Distribution
    const processHHSData = () => {
        const years = {};
        activeData.forEach(row => {
            const year = row.SvyDate ? row.SvyDate.substring(0, 4) : 'Unknown';
            const cat = row.HHSFr || "No";
            if (!years[year]) years[year] = { year, No: 0, Rarely: 0, Sometimes: 0, Often: 0 };
            if (years[year][cat] !== undefined) years[year][cat]++;
        });
        return Object.values(years).sort((a, b) => a.year.localeCompare(b.year));
    };

    // FCS Categories by Year
    const processFCSCategories = () => {
        const years = {};
        activeData.forEach(row => {
            const year = row.SvyDate ? row.SvyDate.substring(0, 4) : 'Unknown';
            const fcs = calculateFCS(row);
            const cat = getFCSCategory(fcs);
            if (!years[year]) years[year] = { year, Poor: 0, Borderline: 0, Acceptable: 0 };
            years[year][cat]++;
        });
        return Object.values(years).sort((a, b) => a.year.localeCompare(b.year));
    };

    // CARI Distribution
    const processCARIData = () => {
        const categories = { 'Food Secure': 0, 'Marginally Secure': 0, 'Moderately Insecure': 0, 'Severely Insecure': 0 };
        activeData.forEach(row => {
            const cat = getCARICategory(row);
            categories[cat]++;
        });
        return Object.entries(categories).map(([name, value]) => ({ name, value }));
    };

    // ECMEN (Economic Capacity) by Year
    const processECMENData = () => {
        const years = {};
        activeData.forEach(row => {
            const year = row.SvyDate ? row.SvyDate.substring(0, 4) : 'Unknown';
            const fes = calculateFES(row);
            // ECMEN categories based on FES
            let cat = 'Adequate';
            if (fes >= 75) cat = 'Poor';
            else if (fes >= 65) cat = 'Borderline';

            if (!years[year]) years[year] = { year, Adequate: 0, Borderline: 0, Poor: 0 };
            years[year][cat]++;
        });
        return Object.values(years).sort((a, b) => a.year.localeCompare(b.year));
    };

    // Process all data
    const trendData = processTrendData();
    const lhcsiData = processLhCSIData();
    const hhsData = processHHSData();
    const fcsCategories = processFCSCategories();
    const cariData = processCARIData();
    const ecmenData = processECMENData();

    // Colors
    const COLORS = {
        fcs: '#818cf8',
        rcsi: '#f472b6',
        fes: '#34d399',
        poor: '#ef4444',
        borderline: '#f97316',
        acceptable: '#22c55e',
        stress: '#eab308',
        crisis: '#f97316',
        emergency: '#ef4444',
        none: '#22c55e',
        cari: ['#22c55e', '#84cc16', '#f97316', '#ef4444']
    };

    const tooltipStyle = { backgroundColor: '#1e293b', border: 'none', color: '#fff' };

    return (
        <div className="space-y-6">
            {/* Indicator Guide - Collapsible */}
            <IndicatorLegend />

            {/* Row 1: FCS Score & rCSI Trends */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* FCS Score Trend */}
                <div className="bg-slate-800 p-6 rounded-xl shadow border border-slate-700">
                    <h3 className="text-lg font-semibold text-white mb-4">📈 FCS - Food Consumption Score</h3>
                    <div className="h-64">
                        <ResponsiveContainer width="100%" height="100%">
                            <LineChart data={trendData}>
                                <CartesianGrid strokeDasharray="3 3" stroke="#444" />
                                <XAxis dataKey="year" stroke="#94a3b8" />
                                <YAxis stroke="#94a3b8" domain={[0, 'auto']} />
                                <Tooltip contentStyle={tooltipStyle} />
                                <Legend />
                                <Line type="monotone" dataKey="FCS" stroke={COLORS.fcs} strokeWidth={3} dot={{ r: 5 }} />
                            </LineChart>
                        </ResponsiveContainer>
                    </div>
                    <p className="text-xs text-slate-400 mt-2">Poor: ≤21 | Borderline: 21.5-35 | Acceptable: &gt;35</p>
                </div>

                {/* rCSI Trend */}
                <div className="bg-slate-800 p-6 rounded-xl shadow border border-slate-700">
                    <h3 className="text-lg font-semibold text-white mb-4">📉 rCSI - Reduced Coping Strategies</h3>
                    <div className="h-64">
                        <ResponsiveContainer width="100%" height="100%">
                            <LineChart data={trendData}>
                                <CartesianGrid strokeDasharray="3 3" stroke="#444" />
                                <XAxis dataKey="year" stroke="#94a3b8" />
                                <YAxis stroke="#94a3b8" domain={[0, 'auto']} />
                                <Tooltip contentStyle={tooltipStyle} />
                                <Legend />
                                <Line type="monotone" dataKey="rCSI" stroke={COLORS.rcsi} strokeWidth={3} dot={{ r: 5 }} />
                            </LineChart>
                        </ResponsiveContainer>
                    </div>
                    <p className="text-xs text-slate-400 mt-2">Menor = Mejor (menos estrategias de afrontamiento)</p>
                </div>
            </div>

            {/* Row 2: LhCSI & HHS/HFA */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* LhCSI Distribution */}
                <div className="bg-slate-800 p-6 rounded-xl shadow border border-slate-700">
                    <h3 className="text-lg font-semibold text-white mb-4">🏠 LhCSI - Livelihood Coping Strategies</h3>
                    <div className="h-64">
                        <ResponsiveContainer width="100%" height="100%">
                            <BarChart data={lhcsiData}>
                                <CartesianGrid strokeDasharray="3 3" stroke="#444" />
                                <XAxis dataKey="year" stroke="#94a3b8" />
                                <YAxis stroke="#94a3b8" />
                                <Tooltip contentStyle={tooltipStyle} />
                                <Legend />
                                <Bar dataKey="None" stackId="a" fill={COLORS.none} name="Sin Estrategias" />
                                <Bar dataKey="Stress" stackId="a" fill={COLORS.stress} name="Estrés" />
                                <Bar dataKey="Crisis" stackId="a" fill={COLORS.crisis} name="Crisis" />
                                <Bar dataKey="Emergency" stackId="a" fill={COLORS.emergency} name="Emergencia" />
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                </div>

                {/* HHS/HFA Distribution */}
                <div className="bg-slate-800 p-6 rounded-xl shadow border border-slate-700">
                    <h3 className="text-lg font-semibold text-white mb-4">🍽️ HHS - Household Hunger Scale (HFA)</h3>
                    <div className="h-64">
                        <ResponsiveContainer width="100%" height="100%">
                            <BarChart data={hhsData}>
                                <CartesianGrid strokeDasharray="3 3" stroke="#444" />
                                <XAxis dataKey="year" stroke="#94a3b8" />
                                <YAxis stroke="#94a3b8" />
                                <Tooltip contentStyle={tooltipStyle} />
                                <Legend />
                                <Bar dataKey="No" stackId="a" fill="#22c55e" name="Sin Hambre" />
                                <Bar dataKey="Rarely" stackId="a" fill="#eab308" name="Raramente" />
                                <Bar dataKey="Sometimes" stackId="a" fill="#f97316" name="A veces" />
                                <Bar dataKey="Often" stackId="a" fill="#ef4444" name="Frecuente" />
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                </div>
            </div>

            {/* Row 3: FES & ECMEN */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* FES Trend */}
                <div className="bg-slate-800 p-6 rounded-xl shadow border border-slate-700">
                    <h3 className="text-lg font-semibold text-white mb-4">💰 FES - Food Expenditure Share</h3>
                    <div className="h-64">
                        <ResponsiveContainer width="100%" height="100%">
                            <AreaChart data={trendData}>
                                <CartesianGrid strokeDasharray="3 3" stroke="#444" />
                                <XAxis dataKey="year" stroke="#94a3b8" />
                                <YAxis stroke="#94a3b8" domain={[0, 100]} tickFormatter={(v) => `${v}%`} />
                                <Tooltip contentStyle={tooltipStyle} formatter={(v) => `${v}%`} />
                                <Legend />
                                <Area type="monotone" dataKey="FES" stroke={COLORS.fes} fill={COLORS.fes} fillOpacity={0.3} name="% Gasto Alimentos" />
                            </AreaChart>
                        </ResponsiveContainer>
                    </div>
                    <p className="text-xs text-slate-400 mt-2">≥75%: Pobre | 65-74%: Límite | &lt;65%: Adecuado</p>
                </div>

                {/* ECMEN Categories */}
                <div className="bg-slate-800 p-6 rounded-xl shadow border border-slate-700">
                    <h3 className="text-lg font-semibold text-white mb-4">📊 ECMEN - Capacidad Económica</h3>
                    <div className="h-64">
                        <ResponsiveContainer width="100%" height="100%">
                            <BarChart data={ecmenData}>
                                <CartesianGrid strokeDasharray="3 3" stroke="#444" />
                                <XAxis dataKey="year" stroke="#94a3b8" />
                                <YAxis stroke="#94a3b8" />
                                <Tooltip contentStyle={tooltipStyle} />
                                <Legend />
                                <Bar dataKey="Adequate" stackId="a" fill="#22c55e" name="Adecuado" />
                                <Bar dataKey="Borderline" stackId="a" fill="#f97316" name="Límite" />
                                <Bar dataKey="Poor" stackId="a" fill="#ef4444" name="Pobre" />
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                </div>
            </div>

            {/* Row 4: CARI (Full Width) */}
            <div className="bg-slate-800 p-6 rounded-xl shadow border border-slate-700">
                <h3 className="text-lg font-semibold text-white mb-4">🎯 CARI - Consolidated Approach for Reporting Indicators</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div className="h-64">
                        <ResponsiveContainer width="100%" height="100%">
                            <PieChart>
                                <Pie
                                    data={cariData}
                                    cx="50%"
                                    cy="50%"
                                    innerRadius={60}
                                    outerRadius={100}
                                    paddingAngle={2}
                                    dataKey="value"
                                    label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                                    labelLine={false}
                                >
                                    {cariData.map((entry, index) => (
                                        <Cell key={`cell-${index}`} fill={COLORS.cari[index % COLORS.cari.length]} />
                                    ))}
                                </Pie>
                                <Tooltip contentStyle={tooltipStyle} />
                            </PieChart>
                        </ResponsiveContainer>
                    </div>
                    <div className="flex flex-col justify-center space-y-3">
                        {cariData.map((item, i) => (
                            <div key={item.name} className="flex items-center gap-3">
                                <div className="w-4 h-4 rounded" style={{ backgroundColor: COLORS.cari[i] }}></div>
                                <span className="text-white font-medium">{item.name}</span>
                                <span className="text-slate-400">({item.value} hogares)</span>
                            </div>
                        ))}
                        <p className="text-xs text-slate-400 mt-4">
                            CARI combina: FCS + rCSI + LhCSI + FES para clasificación de seguridad alimentaria
                        </p>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default DashboardCharts;
