import { useState, useEffect } from "react";
import { useTranslation } from "react-i18next";
import { getTransport } from "../services/api";

export default function TransportPanel({ highContrast }) {
  const { t } = useTranslation();
  const [options, setOptions] = useState([]);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    getTransport().then((d) => { setOptions(d.options); setLoading(false); });
  }, []);
  
  if (loading) return <p className="text-slate-400 text-sm">{t("loading_label")}</p>;
  
  return (
    <section aria-label={t("transport_section_label")}>
      <h2 className="font-semibold text-lg mb-4">{t("transport_title")}</h2>
      <ul className="space-y-3" role="list">
        {options.map((opt, i) => (
          <li key={i} className={`rounded-xl p-4 ${highContrast ? "bg-yellow-900 text-yellow-100" : "bg-slate-800"}`}>
            <div className="flex items-center justify-between mb-1">
              <span className="font-medium text-sm">{opt.type}</span>
              {opt.accessibility && (
                <span className="text-xs bg-blue-900 text-blue-300 px-2 py-0.5 rounded-full" aria-label="Accessible">♿ Accessible</span>
              )}
            </div>
            <ul className="text-xs text-slate-400 space-y-0.5 mb-2" aria-label={`${opt.type} routes`}>
              {opt.routes.map((r, j) => <li key={j}>• {r}</li>)}
            </ul>
            <p className="text-xs text-slate-400">🕐 {opt.frequency}</p>
            {opt.eco_note && <p className="text-xs text-green-400 mt-1">{opt.eco_note}</p>}
          </li>
        ))}
      </ul>
    </section>
  );
}
