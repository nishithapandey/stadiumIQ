import { useTranslation } from "react-i18next";
import { Eye, Type } from "lucide-react";

export default function AccessibilityBar({ highContrast, setHighContrast, fontSize, setFontSize }) {
  const { t } = useTranslation();
  const sizes = ["small", "base", "large"];
  
  return (
    <div className="flex items-center gap-1" role="toolbar" aria-label={t("accessibility_toolbar")}>
      <button
        onClick={() => setHighContrast((v) => !v)}
        aria-pressed={highContrast}
        aria-label={t("toggle_contrast")}
        title={t("toggle_contrast")}
        className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
      >
        <Eye className="w-4 h-4" aria-hidden="true" />
      </button>
      <button
        onClick={() => {
          const idx = sizes.indexOf(fontSize);
          setFontSize(sizes[(idx + 1) % sizes.length]);
        }}
        aria-label={t("cycle_font_size")}
        title={t("cycle_font_size")}
        className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
      >
        <Type className="w-4 h-4" aria-hidden="true" />
      </button>
    </div>
  );
}
