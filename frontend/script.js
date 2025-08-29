const API_BASE = "http://127.0.0.1:8000";  // Backend URL

// Handle resume upload
document.getElementById("uploadForm").addEventListener("submit", async (e) => {
  e.preventDefault();

  const fileInput = document.getElementById("resumeFile");
  const resultDiv = document.getElementById("result");

  if (!fileInput.files.length) {
    alert("Please select a PDF file");
    return;
  }

  const formData = new FormData();
  formData.append("file", fileInput.files[0]);

  resultDiv.innerHTML = "<p>⏳ Uploading and analyzing...</p>";

  try {
    const response = await fetch(`${API_BASE}/upload-resume`, {
      method: "POST",
      body: formData,
    });

    if (!response.ok) throw new Error("Upload failed");

    const data = await response.json();
    resultDiv.innerHTML = `
      <div class="card">
        <h3>📄 ${data.filename}</h3>
        <p>${data.summary}</p>
      </div>
    `;
  } catch (error) {
    console.error(error);
    resultDiv.innerHTML = "<p style='color:red;'>❌ Error uploading file</p>";
  }
});

// Fetch insights history
async function fetchHistory() {
  const historyList = document.getElementById("historyList");
  historyList.innerHTML = "<p>⏳ Loading history...</p>";

  try {
    const response = await fetch(`${API_BASE}/insights`);
    if (!response.ok) throw new Error("Failed to fetch history");

    const data = await response.json();
    historyList.innerHTML = "";

    if (data.length === 0) {
      historyList.innerHTML = "<p>No history found</p>";
      return;
    }

    data.forEach((item) => {
      const div = document.createElement("div");
      div.className = "card";
      div.innerHTML = `
        <h4>📄 ${item.filename}</h4>
        <small>${new Date(item.timestamp).toLocaleString()}</small>
        <p>${item.summary}</p>
      `;
      historyList.appendChild(div);
    });
  } catch (error) {
    console.error(error);
    historyList.innerHTML = "<p style='color:red;'>❌ Error loading history</p>";
  }
}
