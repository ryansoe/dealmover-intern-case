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

  const calculateGrossProfit = () => {
    if (!results) return 0;
    const revenue = parseInt(results.results.revenue);
    const cos = parseInt(results.results.cos);
    return revenue - cos;
  };

  return (
    <div style={{ padding: "20px", maxWidth: "800px", margin: "0 auto" }}>
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
        <div>
          <h3>
            Financial Results for Period Ending: {results.period_end_date}
          </h3>
          <div
            style={{
              border: "1px solid #ddd",
              borderRadius: "4px",
              overflow: "hidden",
              backgroundColor: "#f9f9f9",
              boxShadow: "0 2px 4px rgba(0,0,0,0.1)",
            }}
          >
            <table
              style={{
                width: "100%",
                borderCollapse: "collapse",
                backgroundColor: "white",
              }}
            >
              <thead>
                <tr style={{ backgroundColor: "#e3f2fd" }}>
                  <th
                    style={{
                      padding: "15px 20px",
                      textAlign: "left",
                      borderBottom: "2px solid #ddd",
                      fontWeight: "bold",
                      fontSize: "16px",
                      color: "#1565c0",
                    }}
                  >
                    Metric
                  </th>
                  <th
                    style={{
                      padding: "15px 20px",
                      textAlign: "right",
                      borderBottom: "2px solid #ddd",
                      fontWeight: "bold",
                      fontSize: "16px",
                      color: "#1565c0",
                    }}
                  >
                    Amount (in millions)
                  </th>
                </tr>
              </thead>
              <tbody>
                <tr style={{ backgroundColor: "white" }}>
                  <td
                    style={{
                      padding: "15px 20px",
                      borderBottom: "1px solid #eee",
                      fontSize: "15px",
                      fontWeight: "500",
                      color: "#333",
                    }}
                  >
                    Revenue
                  </td>
                  <td
                    style={{
                      padding: "15px 20px",
                      textAlign: "right",
                      borderBottom: "1px solid #eee",
                      fontFamily: "monospace",
                      fontSize: "16px",
                      fontWeight: "bold",
                      color: "#333",
                    }}
                  >
                    ${parseInt(results.results.revenue).toLocaleString()}
                  </td>
                </tr>
                <tr style={{ backgroundColor: "#f8f9fa" }}>
                  <td
                    style={{
                      padding: "15px 20px",
                      borderBottom: "1px solid #eee",
                      fontSize: "15px",
                      fontWeight: "500",
                      color: "#333",
                    }}
                  >
                    Gross Profit
                  </td>
                  <td
                    style={{
                      padding: "15px 20px",
                      textAlign: "right",
                      borderBottom: "1px solid #eee",
                      fontFamily: "monospace",
                      fontSize: "16px",
                      fontWeight: "bold",
                      color:
                        calculateGrossProfit() >= 0 ? "#2e7d32" : "#d32f2f",
                    }}
                  >
                    ${calculateGrossProfit().toLocaleString()}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          {/* Additional info */}
          <div
            style={{
              marginTop: "15px",
              padding: "15px",
              backgroundColor: "#e8f5e8",
              borderRadius: "4px",
              fontSize: "14px",
              color: "#2e7d32",
              border: "1px solid #c8e6c9",
            }}
          >
            <strong>Note:</strong> Gross Profit = Revenue - Cost of Sales ($
            {parseInt(results.results.cos).toLocaleString()})
          </div>
        </div>
      )}
    </div>
  );
}

export default ResultsGrid;
