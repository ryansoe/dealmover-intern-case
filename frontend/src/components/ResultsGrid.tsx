import { useState } from "react";

interface ApiResponse {
  period_end_date: string;
  results: {
    revenue: string;
    cos: string;
  };
}

function ResultsGrid() {
  const [file, setFile] = useState<File | null>(null);
  const [periodEndDate, setPeriodEndDate] = useState<string>("");
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string>("");
  const [results, setResults] = useState<ApiResponse | null>(null);

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = event.target.files?.[0];
    if (selectedFile) {
      setFile(selectedFile);
      setError(""); // Clear any previous errors
    }
  };

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();

    if (!file) {
      setError("Please select a PDF file");
      return;
    }

    setLoading(true);
    setError("");
    setResults(null);

    try {
      const formData = new FormData();
      formData.append("file", file);

      if (periodEndDate) {
        formData.append("period_end_date", periodEndDate);
      }

      const apiBaseUrl =
        import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";
      const response = await fetch(`${apiBaseUrl}/api/extract/`, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || "Failed to extract data");
      }

      const data: ApiResponse = await response.json();
      setResults(data);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "An error occurred while processing the file"
      );
      setResults(null);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: "20px", maxWidth: "600px", margin: "0 auto" }}>
      <h2>Financial Data Extractor</h2>

      <form onSubmit={handleSubmit} style={{ marginBottom: "30px" }}>
        <div style={{ marginBottom: "15px" }}>
          <label
            htmlFor="file-input"
            style={{ display: "block", marginBottom: "5px" }}
          >
            Upload PDF File:
          </label>
          <input
            id="file-input"
            type="file"
            accept=".pdf"
            onChange={handleFileChange}
            style={{
              padding: "8px",
              border: "1px solid #ccc",
              borderRadius: "4px",
              width: "100%",
            }}
          />
          {file && (
            <p style={{ marginTop: "5px", color: "#666", fontSize: "14px" }}>
              Selected: {file.name}
            </p>
          )}
        </div>

        <div style={{ marginBottom: "15px" }}>
          <label
            htmlFor="date-input"
            style={{ display: "block", marginBottom: "5px" }}
          >
            Period End Date (optional):
          </label>
          <input
            id="date-input"
            type="date"
            value={periodEndDate}
            onChange={(e) => setPeriodEndDate(e.target.value)}
            style={{
              padding: "8px",
              border: "1px solid #ccc",
              borderRadius: "4px",
              width: "200px",
            }}
          />
        </div>

        <button
          type="submit"
          disabled={loading || !file}
          style={{
            padding: "10px 20px",
            backgroundColor: loading || !file ? "#ccc" : "#007bff",
            color: "white",
            border: "none",
            borderRadius: "4px",
            cursor: loading || !file ? "not-allowed" : "pointer",
            fontSize: "16px",
          }}
        >
          {loading ? "Processing..." : "Extract Data"}
        </button>
      </form>

      {error && (
        <div
          style={{
            color: "red",
            backgroundColor: "#ffebee",
            padding: "15px",
            borderRadius: "4px",
            marginBottom: "20px",
            border: "1px solid #ffcdd2",
          }}
        >
          <strong>Error:</strong> {error}
        </div>
      )}

      {results && (
        <div
          style={{
            backgroundColor: "#e8f5e8",
            padding: "15px",
            borderRadius: "4px",
            border: "1px solid #c8e6c9",
          }}
        >
          <h3>Success!</h3>
          <p>
            <strong>Period End Date:</strong> {results.period_end_date}
          </p>
          <p>
            <strong>Revenue:</strong> $
            {parseInt(results.results.revenue).toLocaleString()}
          </p>
          <p>
            <strong>Cost of Sales:</strong> $
            {parseInt(results.results.cos).toLocaleString()}
          </p>
        </div>
      )}
    </div>
  );
}

export default ResultsGrid;
