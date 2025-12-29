import React, { useMemo } from 'react';
import { TrendingUp, TrendingDown, AlertTriangle, CheckCircle, MapPin } from 'lucide-react';

const InsightCard = ({ icon: Icon, title, value, type = "neutral", detail }) => {
    const colors = {
        success: "bg-green-500/10 text-green-500 border-green-500/20",
        warning: "bg-yellow-500/10 text-yellow-500 border-yellow-500/20",
        danger: "bg-red-500/10 text-red-500 border-red-500/20",
        neutral: "bg-slate-700/50 text-slate-300 border-slate-600"
    };

    return (
        <div className={`p-4 rounded-xl border ${colors[type]} flex items-start gap-4`}>
            <div className={`p-2 rounded-lg bg-slate-800/50`}>
                <Icon size={24} />
            </div>
            <div>
                <h4 className="text-sm font-semibold opacity-80 uppercase tracking-wider">{title}</h4>
                <div className="text-lg font-bold mt-1">{value}</div>
                {detail && <div className="text-xs mt-2 opacity-70">{detail}</div>}
            </div>
        </div>
    );
};

const DashboardInsights = ({ data, selectedCountries }) => {
    const analysis = useMemo(() => {
        if (!data || data.length === 0) return null;

        // Determine if strictly comparing (2 or more specific countries selected, NO "All Countries")
        const isComparative = selectedCountries && selectedCountries.length > 1 && !selectedCountries.includes("All Countries");
        const isComposite = !selectedCountries || selectedCountries.includes("All Countries") || selectedCountries.length === 0;

        // Group by Year to get global trend
        const years = Array.from(new Set(data.map(r => r.SvyDate ? r.SvyDate.substring(0, 4) : 'N/A'))).sort();
        if (years.length < 2) return { ready: false, text: "Need at least 2 years of data." };

        const firstYear = years[0];
        const lastYear = years[years.length - 1];

        // 1. Global FCS Growth
        const getAvgFCS = (dataset, y) => {
            const recs = dataset.filter(r => r.SvyDate && r.SvyDate.startsWith(y));
            if (!recs.length) return 0;
            return recs.reduce((acc, r) => acc + (parseFloat(r.FCSStap) || 0), 0) / recs.length;
        };

        const fcsStart = getAvgFCS(data, firstYear);
        const fcsEnd = getAvgFCS(data, lastYear);
        const fcsGrowth = fcsStart ? ((fcsEnd - fcsStart) / fcsStart) * 100 : 0;

        // 2. Economic Resilience
        const getAvgFoodShare = (dataset, y) => {
            const recs = dataset.filter(r => r.SvyDate && r.SvyDate.startsWith(y));
            if (!recs.length) return 0;
            let sum = 0, count = 0;
            recs.forEach(r => {
                const f = parseFloat(r.FoodExp) || 0;
                const n = parseFloat(r.NonFoodExp) || 0;
                if (f + n > 0) {
                    sum += (f / (f + n));
                    count++;
                }
            });
            return count ? sum / count : 0;
        };
        const shareStart = getAvgFoodShare(data, firstYear);
        const shareEnd = getAvgFoodShare(data, lastYear);

        // 3. Comparative Analysis (if applicable)
        let comparativeText = "";
        let bestCountry = null;
        let worstCountry = null;

        if (isComparative) {
            // Compare the selected countries
            const countryStats = selectedCountries.map(c => {
                const cData = data.filter(r => r.Country === c);
                const avg = getAvgFCS(cData, lastYear);
                return { country: c, score: avg };
            });

            countryStats.sort((a, b) => b.score - a.score); // Descending
            bestCountry = countryStats[0];
            worstCountry = countryStats[countryStats.length - 1];

            const diff = (bestCountry.score - worstCountry.score).toFixed(1);
            comparativeText = `${bestCountry.country} outperforms ${worstCountry.country} by ${diff} FCS points.`;
        }

        // 4. Regional/Internal Breakdown
        const lastYearData = data.filter(r => r.SvyDate && r.SvyDate.startsWith(lastYear));
        const regions = {};
        const shocks = {};
        lastYearData.forEach(r => {
            const admin = r.ADMIN1 || "Unknown";
            if (!regions[admin]) regions[admin] = { sum: 0, count: 0 };
            regions[admin].sum += (parseFloat(r.FCSStap) || 0);
            regions[admin].count++;

            const ev = r._events_summary;
            if (ev && ev !== "None") {
                const list = ev.split(', ');
                list.forEach(e => shocks[e] = (shocks[e] || 0) + 1);
            }
        });

        let worstRegion = null;
        let minScore = 999;
        Object.entries(regions).forEach(([reg, stats]) => {
            const avg = stats.sum / stats.count;
            if (avg < minScore) {
                minScore = avg;
                worstRegion = reg;
            }
        });

        // Top Shock
        let topShock = "None";
        let maxShockCount = 0;
        Object.entries(shocks).forEach(([s, count]) => {
            if (count > maxShockCount) {
                maxShockCount = count;
                topShock = s;
            }
        });

        return {
            ready: true,
            years,
            fcsGrowth,
            shareStart,
            shareEnd,
            worstRegion,
            worstRegionScore: minScore,
            topShock,
            isComparative,
            comparativeText,
            bestCountry,
            isComposite // True if "All Countries" or empty
        };
    }, [data, selectedCountries]);

    if (!analysis || !analysis.ready) return null;

    return (
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
            <h3 className="text-xl font-bold text-slate-800 mb-6 flex items-center gap-2">
                <div className="w-2 h-6 bg-blue-500 rounded-full"></div>
                {analysis.isComparative ? "Comparative Strategic Insights" : "Automated Strategic Insights"}
            </h3>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* 1. Trend */}
                <InsightCard
                    icon={analysis.fcsGrowth >= 0 ? TrendingUp : TrendingDown}
                    title="Dietary Diversity Trend"
                    value={`${analysis.fcsGrowth > 0 ? '+' : ''}${analysis.fcsGrowth.toFixed(1)}%`}
                    type={analysis.fcsGrowth > 5 ? "success" : "warning"}
                    detail={`Global change ${analysis.years[0]}-${analysis.years[analysis.years.length - 1]}`}
                />

                {/* 2. Resilience */}
                <InsightCard
                    icon={CheckCircle}
                    title="Economic Resilience"
                    value={`${(analysis.shareStart * 100).toFixed(0)}% ➔ ${(analysis.shareEnd * 100).toFixed(0)}%`}
                    type={analysis.shareEnd < 0.6 ? "success" : "warning"}
                    detail="Avg Food Expenditure Share"
                />

                {/* 3. Major Driver */}
                <InsightCard
                    icon={AlertTriangle}
                    title="Major Driver (Last Year)"
                    value={analysis.topShock}
                    type="neutral"
                    detail="Most frequent disaster event"
                />

                {/* 4. Priority / Comparison */}
                {analysis.isComparative ? (
                    <InsightCard
                        icon={MapPin}
                        title="Divergence"
                        value={analysis.bestCountry ? `${analysis.bestCountry.country} ⬆` : "N/A"}
                        type="neutral"
                        detail={`Gap vs Lowest (${analysis.bestCountry.score.toFixed(1)} vs ${analysis.worstRegionScore.toFixed(1)})`}
                    />
                ) : (
                    <InsightCard
                        icon={MapPin}
                        title="Priority Region"
                        value={analysis.worstRegion}
                        type="danger"
                        detail={`Lowest avg FCS (${analysis.worstRegionScore.toFixed(1)})`}
                    />
                )}
            </div>

            <div className="mt-6 p-4 bg-blue-50 rounded-lg text-slate-700 text-sm leading-relaxed border border-blue-100">
                <strong>Executive Summary: </strong>

                {analysis.isComparative ? (
                    <span>
                        Comparing the selected countries reveals a mixed landscape.
                        <strong> {analysis.comparativeText} </strong>
                        The overall trend is {analysis.fcsGrowth > 0 ? "positive" : "negative"} ({analysis.fcsGrowth.toFixed(1)}%).
                        Common vulnerability drivers include "{analysis.topShock}".
                    </span>
                ) : (
                    <span>
                        The simulation indicates a {analysis.fcsGrowth > 0 ? "positive" : "negative"} trajectory in food security.
                        Households have {analysis.shareEnd < analysis.shareStart ? "successfully reduced" : "increased"} their dependency on food expenditure.
                        "{analysis.topShock}" is a significant driver of vulnerability.
                        Geographic targeting should focus on <strong>{analysis.worstRegion}</strong>.
                    </span>
                )}
            </div>
        </div>
    );
};

export default DashboardInsights;
