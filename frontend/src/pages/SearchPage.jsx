import { useState } from "react";
import { searchDocuments, getDownloadUrl } from "../lib/apiClient";

function SearchPage() {
  const [query, setQuery] = useState("");
  const [status, setStatus] = useState("idle"); // idle | processing | completed
  const [results, setResults] = useState([]);
  const [error, setError] = useState("");

  async function handleSearch(event) {
    event.preventDefault();

    const trimmedQuery = query.trim();
    if (!trimmedQuery) {
      setError("Please enter a search query.");
      return;
    }

    setError("");
    setResults([]);
    setStatus("processing");

    try {
      const data = await searchDocuments(trimmedQuery);
      const uniqueResults = [];
      const seenFiles = new Set();

      for (const result of data.results || []) {
        if (seenFiles.has(result.file_name)) {
          continue;
        }
        seenFiles.add(result.file_name);
        uniqueResults.push(result);
      }

      setResults(uniqueResults);
      setStatus("completed");
    } catch (err) {
      setError(err.message || "Search failed. Please try again.");
      setStatus("idle");
    }
  }

  function handleDownload(fileName) {
    window.location.href = getDownloadUrl(fileName);
  }

  const isSearching = status === "processing";

  return (
    <section className="search-page">
      <h2 className="search-page-title">Search Documents</h2>

      <form className="search-form" onSubmit={handleSearch}>
        <input
          className="search-input"
          type="text"
          value={query}
          onChange={(event) => setQuery(event.target.value)}
          placeholder="Search previously processed documents..."
          disabled={isSearching}
        />
        <button
          className="search-button"
          type="submit"
          disabled={isSearching}
        >
          {isSearching ? "Searching..." : "Search"}
        </button>
      </form>

      {error && <p className="search-error">{error}</p>}

      {isSearching && (
        <div className="search-loading">
          <span className="search-spinner" aria-hidden="true" />
          <span>Searching documents...</span>
        </div>
      )}

      {status === "completed" && results.length === 0 && (
        <p className="search-empty">No matching documents found.</p>
      )}

      {results.length > 0 && (
        <div className="search-results">
          {results.map((result, index) => (
            <article
              className="search-result-card"
              key={`${result.file_name}-${index}`}
            >
              <div className="search-result-main">
                <h3 className="search-result-title">{result.file_name}</h3>
                {/* <p className="search-result-meta">
                  Match score: {Math.round((result.score || 0) * 100)}%
                </p> */}
                {result.text_content && (
                  <p className="search-result-preview">{result.text_content}</p>
                )}
              </div>

              <button
                className="search-download-button"
                type="button"
                onClick={() => handleDownload(result.file_name)}
              >
                Download
              </button>
            </article>
          ))}
        </div>
      )}
    </section>
  );
}

export default SearchPage;
