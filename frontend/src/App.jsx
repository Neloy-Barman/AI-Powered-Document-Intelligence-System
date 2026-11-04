import { useState } from "react"; // useState lets App remember which view is open
import UploadPage from "./pages/UploadPage"; // The upload screen
import ProgressPage from "./pages/ProgressPage"; // The processing progress screen
import SearchPage from "./pages/SearchPage"; // The document search screen
import ProcessingHistoryPage from "./pages/ProcessingHistoryPage"; // Processed document history
import { useProcessingQueue } from "./hooks/useProcessingQueue"; // Shared queue + mock worker

// App is the root component: title, navigation, and the two views
function App() {
  // view decides which screen is visible: "upload" or "progress"
  const [view, setView] = useState("upload");

  // The queue lives here, so processing continues while switching views
  const { items, summary, enqueue, dismissSummary } = useProcessingQueue();
  const isProcessing = items.some((item) => item.status === "processing");

  // startProcessing sends an upload section's files to the queue
  function startProcessing(files, kind) {
    enqueue(files, kind); // add the files to the end of the queue
    setView("progress"); // jump to the progress screen
  }

  return (
    <main className="app">
      {/* Page heading showing the project name */}
      <h1 className="app-title">AI Powered Document Intelligence System</h1>

      {/* Navigation between the two views */}
      <nav className="app-nav">
        <button
          className={`app-nav-button ${view === "upload" ? "app-nav-button-active" : ""}`}
          type="button" // "button" prevents any form submission
          onClick={() => setView("upload")} // show the upload screen
        >
          Upload
        </button>
        <button
          className={`app-nav-button ${view === "progress" ? "app-nav-button-active" : ""}`}
          type="button" // "button" prevents any form submission
          onClick={() => setView("progress")} // show the progress screen
        >
          Progress
        </button>
        <button
          className={`app-nav-button ${view === "search" ? "app-nav-button-active" : ""}`}
          type="button" // "button" prevents any form submission
          onClick={() => setView("search")} // show the search screen
        >
          Search
        </button>
        <button
          className={`app-nav-button ${view === "history" ? "app-nav-button-active" : ""}`}
          type="button"
          onClick={() => setView("history")}
        >
          History
        </button>
      </nav>

      {/* Upload view; kept mounted so an unsubmitted selection survives */}
      <div className={`app-view ${view === "upload" ? "" : "app-view-hidden"}`}>
        <UploadPage onProcess={startProcessing} isProcessing={isProcessing} />
      </div>

      {/* Progress view; kept mounted too, so switching is instant */}
      <div className={`app-view ${view === "progress" ? "" : "app-view-hidden"}`}>
        <ProgressPage items={items} />
      </div>

      {/* Search view */}
      <div className={`app-view ${view === "search" ? "" : "app-view-hidden"}`}>
        <SearchPage />
      </div>

      {/* History view */}
      <div className={`app-view ${view === "history" ? "" : "app-view-hidden"}`}>
        <ProcessingHistoryPage />
      </div>

      {/* Completion popup, shown once the whole queue is done */}
      {summary && (
        <div className="processing-summary">
          {/* Main message */}
          <p className="processing-summary-message">Processing completed.</p>
          {/* Counts for the run that just finished */}
          <p className="processing-summary-counts">
            Successful: {summary.successful}
            <br />
            Failed: {summary.failed}
          </p>
          {/* OK closes the popup */}
          <button
            className="processing-summary-ok"
            type="button" // "button" prevents any form submission
            onClick={dismissSummary} // hide the popup
          >
            OK
          </button>
        </div>
      )}
    </main>
  );
}

export default App; // Export App so main.jsx can render it
