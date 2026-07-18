/**
 * CrowdDashboard — Real-time gate density heatmap with auto-refresh.
 *
 * Features:
 * - Auto-refresh every 30 seconds
 * - useCallback for stable fetch function
 * - Error state display
 * - Progressive color-coded density indicators
 * - Accessible progress bars
 */
import { useState, useEffect, useCallback } from "react";
import { useTranslation } from "react-i18next";
import { RefreshCw } from "lucide-react";
import { getCrowdStatus } from "../services/api";

const AUTO_REFRESH_INTERVAL_MS = 30_000;

const DENSITY_STYLES = {
  low: { bar: "bg-green-500", badge: "bg-green-900 text-green-300", label: "Low" },
  medium: { bar: "bg-yellow-500", badge: "bg-yellow-900 text-yellow-300", label: "Medium" },
  high: { bar: "bg-orange-500", badge: "bg-orange-900 text-orange-300", label: "High" },
  critical: { bar: "bg-red-500", badge: "bg-red-900 text-red-300", label: "Critical" },
};

const DENSITY_WIDTH = { low: "25%", medium: "55%", high: "80%", critical: "100%" };

export default function CrowdDashboard({ highContrast }) {
  const { t } = useTranslation();
  const [gates, setGates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(null);

  const fetchStatus = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getCrowdStatus();
      setGates(data);
      setLastUpdated(new Date().toLocaleTimeString());
    } catch {
      setError(t("error_message"));
    } finally {
      setLoading(false);
    }
  }, [t]);

  useEffect(() => {
    fetchStatus();
    const interval = setInterval(fetchStatus, AUTO_REFRESH_INTERVAL_MS);
    return () => clearInterval(interval);
  }, [fetchStatus]);

  return (
    <section aria-label={t("crowd_dashboard_label")}>
      <div className="flex items-center justify-between mb-4">
        <h2 className="font-semibold text-lg">{t("crowd_dashboard_title")}</h2>
        <div className="flex items-center gap-2">
          {lastUpdated && (
            <span className={`text-xs ${highContrast ? "text-yellow-700" : "text-slate-400"}`} aria-live="polite">
              {t("last_updated")}: {lastUpdated}
            </span>
          )}
          <button
            onClick={fetchStatus}
            disabled={loading}
            aria-label={t("refresh_crowd")}
            className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 transition-colors"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? "animate-spin" : ""}`} aria-hidden="true" />
          </button>
        </div>
      </div>

      {error && (
        <div className="text-red-400 text-sm text-center py-4" role="alert">
          {error}
        </div>
      )}

      {loading && gates.length === 0 && !error ? (
        <div role="status" aria-label={t("loading_label")} className="text-center text-slate-400 py-8">
          {t("loading_crowd")}
        </div>
      ) : (
        <ul className="space-y-3" role="list" aria-label={t("gate_statuses")}>
          {gates.map((gate) => {
            const style = DENSITY_STYLES[gate.density] || DENSITY_STYLES.low;
            return (
              <li key={gate.gate} className={`rounded-xl p-4 ${highContrast ? "bg-yellow-900" : "bg-slate-800"}`}>
                <div className="flex items-center justify-between mb-2">
                  <span className="font-medium text-sm">{gate.gate}</span>
                  <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${style.badge}`}>
                    {t(`density_${gate.density}`)}
                  </span>
                </div>
                {/* Progress bar for density */}
                <div
                  className={`w-full ${highContrast ? "bg-yellow-800" : "bg-slate-700"} rounded-full h-2 mb-2`}
                  role="progressbar"
                  aria-valuenow={gate.wait_minutes}
                  aria-valuemin={0}
                  aria-valuemax={25}
                  aria-label={`${gate.gate} crowd density`}
                >
                  <div
                    className={`${style.bar} h-2 rounded-full transition-all duration-500`}
                    style={{ width: DENSITY_WIDTH[gate.density] }}
                  />
                </div>
                <p className={`text-xs ${highContrast ? "text-yellow-600" : "text-slate-400"}`}>
                  ⏱ {gate.wait_minutes} min wait · {gate.recommendation}
                </p>
              </li>
            );
          })}
        </ul>
      )}
    </section>
  );
}
