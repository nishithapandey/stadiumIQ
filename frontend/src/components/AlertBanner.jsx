/**
 * AlertBanner — Dismissible alert notification with React.memo.
 * Pure component for crowd density alerts and system notifications.
 */
import { memo } from "react";
import { X } from "lucide-react";

const AlertBanner = memo(function AlertBanner({ message, onClose }) {
  return (
    <div
      role="alert"
      aria-live="assertive"
      className="bg-amber-900 border-l-4 border-amber-400 text-amber-100 px-4 py-2.5 flex items-center justify-between text-sm animate-slide-down"
    >
      <span>{message}</span>
      <button
        onClick={onClose}
        aria-label="Dismiss alert"
        className="ml-4 hover:text-white focus:outline-none focus:ring-2 focus:ring-amber-400 rounded p-0.5 transition-colors"
      >
        <X className="w-4 h-4" aria-hidden="true" />
      </button>
    </div>
  );
});

export default AlertBanner;
