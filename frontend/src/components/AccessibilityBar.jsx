/**
 * AccessibilityBar — High contrast & font size controls with React.memo.
 * Provides WCAG-compliant accessibility toggles.
 */
import { memo, useCallback } from "react";
import { useTranslation } from "react-i18next";
import { Eye, Type } from "lucide-react";

const SIZES = ["small", "base", "large"];

const AccessibilityBar = memo(function AccessibilityBar({
  highContrast,
  setHighContrast,
  fontSize,
  setFontSize,
}) {
  const { t } = useTranslation();

  const cycleFontSize = useCallback(() => {
    const idx = SIZES.indexOf(fontSize);
    setFontSize(SIZES[(idx + 1) % SIZES.length]);
  }, [fontSize, setFontSize]);

  return (
    <div className="flex items-center gap-1" role="toolbar" aria-label={t("accessibility_toolbar")}>
      <button
        onClick={() => setHighContrast((v) => !v)}
        aria-pressed={highContrast}
        aria-label={t("toggle_contrast")}
        title={t("toggle_contrast")}
        className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-colors"
      >
        <Eye className="w-4 h-4" aria-hidden="true" />
      </button>
      <button
        onClick={cycleFontSize}
        aria-label={t("cycle_font_size")}
        title={t("cycle_font_size")}
        className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-colors"
      >
        <Type className="w-4 h-4" aria-hidden="true" />
      </button>
    </div>
  );
});

export default AccessibilityBar;
