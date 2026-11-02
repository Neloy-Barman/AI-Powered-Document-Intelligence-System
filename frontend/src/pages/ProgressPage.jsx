// STATUS_LABELS maps the stored status to the text shown on screen
const STATUS_LABELS = {
  queued: "Queued", // waiting for its turn
  processing: "Processing…", // currently being worked on
  completed: "Successful", // finished without errors
  failed: "Failed", // finished with an error
};

// ProgressPage shows every file in the shared queue
function ProgressPage({ items }) {
  return (
    <section className="progress-page">
      {/* Screen heading */}
      <h2 className="progress-page-title">Processing Progress</h2>

      {/* Empty state before anything is queued */}
      {items.length === 0 && (
        <p className="progress-empty">No processing in progress.</p>
      )}

      {/* One row per file, in queue order */}
      {items.length > 0 && (
        <ul className="progress-list">
          {items.map((item) => (
            <li className="progress-item" key={item.id}>
              {/* File name */}
              <span className="progress-item-name">{item.file_name}</span>
              {/* Current status; its label comes from STATUS_LABELS */}
              <span
                className={`progress-item-status progress-item-status-${item.status}`}
              >
                {STATUS_LABELS[item.status]}
              </span>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}

export default ProgressPage; // Export so App.jsx can render it
