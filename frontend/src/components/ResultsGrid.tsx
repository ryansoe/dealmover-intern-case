import { useState } from "react";

function ResultsGrid() {
  const [file, setFile] = useState<File | null>(null);
  const [periodEndDate, setPeriodEndDate] = useState<string>("");

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = event.target.files?.[0];
    if (selectedFile) {
      setFile(selectedFile);
    }
  };

  const handleSubmit = (event: React.FormEvent) => {
    event.preventDefault();

    // For now, just log the data to console
    console.log("Selected file:", file?.name);
    console.log("Period end date:", periodEndDate);

    if (!file) {
      alert("Please select a PDF file");
      return;
    }

    alert(
      `File selected: ${file.name}${
        periodEndDate ? `, Date: ${periodEndDate}` : ""
      }`
    );
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
          disabled={!file}
          style={{
            padding: "10px 20px",
            backgroundColor: !file ? "#ccc" : "#007bff",
            color: "white",
            border: "none",
            borderRadius: "4px",
            cursor: !file ? "not-allowed" : "pointer",
            fontSize: "16px",
          }}
        >
          Process File
        </button>
      </form>
    </div>
  );
}

export default ResultsGrid;
