import "./LoadingSpinner.css";


export default function LoadingSpinner({ label, size = "medium" }) {
  return (
    <div className={`loading-spinner-wrap loading-spinner-${size}`} role="status" aria-live="polite">
      <span className="loading-spinner" aria-hidden="true" />
      {label && <span className="loading-spinner-label">{label}</span>}
    </div>
  );
}
