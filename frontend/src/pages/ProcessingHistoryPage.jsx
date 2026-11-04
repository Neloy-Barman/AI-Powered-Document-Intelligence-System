import { useEffect, useState } from "react";
import { getProcessingHistory } from "../lib/apiClient";

function ProcessingHistoryPage() {
  const [documents, setDocuments] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let isMounted = true;

    async function loadHistory() {
      try {
        const data = await getProcessingHistory();
        if (isMounted) {
          setDocuments(data.documents || []);
        }
      } catch (err) {
        if (isMounted) {
          setError(err.message || "Failed to load processing history.");
        }
      } finally {
        if (isMounted) {
          setIsLoading(false);
        }
      }
    }

    loadHistory();

    return () => {
      isMounted = false;
    };
  }, []);

  if (isLoading) {
    return <p>Loading processing history...</p>;
  }

  if (error) {
    return <p className="search-error">{error}</p>;
  }

  return (
    <section className="processing-history-page">
      <h2>Processing History</h2>

      {documents.length === 0 && (
        <p>No processed documents found.</p>
      )}

      {documents.length > 0 && (
        <table className="processing-history-table">
          <thead>
            <tr>
              <th>File Name</th>
              <th>Type</th>
              <th>Status</th>
              <th>Size (bytes)</th>
              <th>Processed At</th>
            </tr>
          </thead>
          <tbody>
            {documents.map((document) => (
              <tr key={document.id}>
                <td>{document.file_name}</td>
                <td>{document.file_type}</td>
                <td>{document.status}</td>
                <td>{document.file_size_bytes}</td>
                <td>{document.created_at}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </section>
  );
}

export default ProcessingHistoryPage;
