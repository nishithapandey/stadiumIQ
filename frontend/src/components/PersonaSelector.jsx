/**
 * PersonaSelector — Role selection with React.memo for performance.
 * Pure component that only re-renders when props change.
 */
import { memo } from "react";
import { useTranslation } from "react-i18next";

const PERSONAS = [
  { id: "fan", emoji: "⚽", labelKey: "persona_fan" },
  { id: "staff", emoji: "👷", labelKey: "persona_staff" },
  { id: "volunteer", emoji: "🙋", labelKey: "persona_volunteer" },
  { id: "organizer", emoji: "📋", labelKey: "persona_organizer" },
];

const PersonaSelector = memo(function PersonaSelector({ persona, setPersona, highContrast }) {
  const { t } = useTranslation();

  return (
    <fieldset>
      <legend className="sr-only">{t("select_persona")}</legend>
      <div className="flex gap-2 flex-wrap" role="group">
        {PERSONAS.map((p) => {
          const selected = persona === p.id;
          return (
            <button
              key={p.id}
              onClick={() => setPersona(p.id)}
              aria-pressed={selected}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full text-sm font-medium border transition-all
                focus:outline-none focus:ring-2 focus:ring-blue-500
                ${selected
                  ? highContrast
                    ? "bg-yellow-300 text-black border-yellow-300"
                    : "bg-blue-600 text-white border-blue-600"
                  : highContrast
                    ? "bg-black text-yellow-300 border-yellow-300 hover:bg-yellow-900"
                    : "bg-slate-800 text-slate-300 border-slate-700 hover:border-blue-500"
                }`}
            >
              <span aria-hidden="true">{p.emoji}</span>
              {t(p.labelKey)}
            </button>
          );
        })}
      </div>
    </fieldset>
  );
});

export default PersonaSelector;
