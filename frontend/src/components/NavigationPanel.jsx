import { useState } from "react";
import { useTranslation } from "react-i18next";
import { MapPin, Loader2 } from "lucide-react";
import { getNavigation } from "../services/api";

const LOCATIONS = [
  "Main Entrance (Gate A)", "My Seat (Section 212)", "Nearest Restroom",
  "Food Court (Concourse B)", "Medical Station", "Exit (Gate C)",
  "Accessibility Elevator", "Information Desk", "Souvenir Shop",
];

export default function NavigationPanel({ language, highContrast }) {
  const { t } = useTranslation();
  const [from, setFrom] = useState("");
  const [to, setTo] = useState("");
  const [wheelchair, setWheelchair] = useState(false);
  const [steps, setSteps] = useState([]);
  const [eta, setEta] = useState(null);
  const [accNote, setAccNote] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  
  const handleNavigate = async () => {
    if (!from || !to) return;
    setLoading(true);
    setError(null);
    try {
      const data = await getNavigation({ from_location: from, to_location: to, accessibility_needed: wheelchair, language });
      setSteps(data.steps);
      setEta(data.estimated_minutes);
      setAccNote(data.accessibility_note);
    } catch {
      setError(t("error_message"));
    } finally {
      setLoading(false);
    }
  };
  
  const selectClass = `w-full rounded-lg border px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500
    ${highContrast ? "bg-black border-yellow-300 text-yellow-300" : "bg-slate-800 border-slate-600 text-white"}`;
  
  return (
    <section aria-label={t("navigation_section_label")}>
      <h2 className="font-semibold text-lg mb-4">{t("navigation_title")}</h2>
      <div className="space-y-3 mb-4">
        <div>
          <label htmlFor="from-select" className="text-xs text-slate-400 block mb-1">{t("from_label")}</label>
          <select id="from-select" value={from} onChange={(e) => setFrom(e.target.value)} className={selectClass}>
            <option value="">{t("select_location")}</option>
            {LOCATIONS.map((l) => <option key={l} value={l}>{l}</option>)}
          </select>
        </div>
        <div>
          <label htmlFor="to-select" className="text-xs text-slate-400 block mb-1">{t("to_label")}</label>
          <select id="to-select" value={to} onChange={(e) => setTo(e.target.value)} className={selectClass}>
            <option value="">{t("select_location")}</option>
            {LOCATIONS.filter((l) => l !== from).map((l) => <option key={l} value={l}>{l}</option>)}
          </select>
        </div>
        <label className="flex items-center gap-2 text-sm cursor-pointer">
          <input
            type="checkbox"
            checked={wheelchair}
            onChange={(e) => setWheelchair(e.target.checked)}
            className="w-4 h-4 accent-blue-500"
          />
          ♿ {t("wheelchair_accessible_route")}
        </label>
      </div>
      
      <button
        onClick={handleNavigate}
        disabled={!from || !to || loading}
        className="w-full bg-blue-600 hover:bg-blue-500 disabled:opacity-40 disabled:cursor-not-allowed text-white font-medium py-2.5 rounded-xl transition-colors flex items-center justify-center gap-2 focus:outline-none focus:ring-2 focus:ring-blue-400"
      >
        {loading ? <Loader2 className="w-4 h-4 animate-spin" aria-hidden="true" /> : <MapPin className="w-4 h-4" aria-hidden="true" />}
        {t("get_directions")}
      </button>
      
      {error && <p className="text-red-400 text-sm mt-3" role="alert">{error}</p>}
      
      {steps.length > 0 && (
        <div className="mt-4" aria-live="polite">
          {accNote && (
            <div className="bg-blue-900 text-blue-200 text-sm px-3 py-2 rounded-lg mb-3" role="status">
              {accNote}
            </div>
          )}
          <p className="text-xs text-slate-400 mb-2">🕐 ~{eta} min walk</p>
          <ol className="space-y-2" aria-label={t("navigation_steps")}>
            {steps.map((step, i) => (
              <li key={i} className="flex gap-3 text-sm">
                <span className="bg-blue-600 text-white rounded-full w-5 h-5 flex items-center justify-center text-xs flex-shrink-0 mt-0.5" aria-hidden="true">
                  {i + 1}
                </span>
                <span>{step}</span>
              </li>
            ))}
          </ol>
        </div>
      )}
    </section>
  );
}
