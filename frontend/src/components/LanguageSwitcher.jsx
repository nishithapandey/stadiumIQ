/**
 * LanguageSwitcher — Language selector with RTL support and React.memo.
 * Updates i18n, document lang, and direction attributes.
 */
import { memo, useCallback } from "react";
import { useTranslation } from "react-i18next";

const LANGUAGES = [
  { code: "en", label: "EN", name: "English" },
  { code: "es", label: "ES", name: "Español" },
  { code: "fr", label: "FR", name: "Français" },
  { code: "ar", label: "عر", name: "العربية" },
];

const LanguageSwitcher = memo(function LanguageSwitcher({ language, setLanguage }) {
  const { i18n } = useTranslation();

  const handleChange = useCallback(
    (code) => {
      setLanguage(code);
      i18n.changeLanguage(code);
      document.documentElement.lang = code;
      document.documentElement.dir = code === "ar" ? "rtl" : "ltr";
    },
    [setLanguage, i18n]
  );

  return (
    <select
      value={language}
      onChange={(e) => handleChange(e.target.value)}
      aria-label="Select language"
      className="bg-slate-800 border border-slate-700 text-white text-xs rounded-lg px-2 py-1.5 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-colors"
    >
      {LANGUAGES.map((l) => (
        <option key={l.code} value={l.code} lang={l.code}>
          {l.label} – {l.name}
        </option>
      ))}
    </select>
  );
});

export default LanguageSwitcher;
