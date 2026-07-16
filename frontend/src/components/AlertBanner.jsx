import { X } from "lucide-react";

export default function AlertBanner({ message, onClose }) {
  return (
    <div
      role="alert"
      aria-live="assertive"
      className="bg-amber-900 border-l-4 border-amber-400 text-amber-100 px-4 py-2.5 flex items-center justify-between text-sm"
    >
      <span>{message}</span>
      <button onClick={onClose} aria-label="Dismiss alert" className="ml-4 hover:text-white focus:outline-none focus:ring-2 focus:ring-amber-400 rounded">
        <X className="w-4 h-4" aria-hidden="true" />
      </button>
    </div>
  );
}
