const API_URL = "http://127.0.0.1:8000";

// ==========================================
// ASK HR POLICY QUESTION
// ==========================================

async function askQuestion() {
  const questionInput = document.getElementById("question");

  const answerSection = document.getElementById("answerSection");

  const answerElement = document.getElementById("answer");

  const citationsElement = document.getElementById("citations");

  // Get question
  const question = questionInput.value.trim();

  // Validate question
  if (!question) {
    alert("Please enter a question.");

    questionInput.focus();

    return;
  }

  // Show answer section
  answerSection.style.display = "block";

  // Loading state
  answerElement.textContent = "Searching the HR policies...";

  citationsElement.innerHTML = "";

  try {
    const response = await fetch(`${API_URL}/ask`, {
      method: "POST",

      headers: {
        "Content-Type": "application/json",
      },

      body: JSON.stringify({
        question: question,
      }),
    });

    const data = await response.json();

    // Handle backend error
    if (!response.ok) {
      throw new Error(data.detail || "Request failed.");
    }

    // ==========================================
    // DISPLAY ANSWER
    // ==========================================

    answerElement.textContent = data.answer
        .replace(/\*\*/g, "")
        .replace(/\*/g, "");
    // ==========================================
    // DISPLAY CITATIONS
    // ==========================================

    citationsElement.innerHTML = "";

    if (!data.citations || data.citations.length === 0) {
      const noSource = document.createElement("p");

      noSource.textContent = "No policy source available.";

      noSource.className = "no-citation";

      citationsElement.appendChild(noSource);

      return;
    }

    data.citations.forEach((citation) => {
      const citationDiv = document.createElement("div");

      citationDiv.className = "citation";

      // Document name
      const documentLabel = document.createElement("strong");

      documentLabel.textContent = "Document: ";

      const documentName = document.createTextNode(citation.document);

      // Section
      const sectionLabel = document.createElement("strong");

      sectionLabel.textContent = "Section: ";

      const sectionName = document.createTextNode(citation.section);

      const lineBreak = document.createElement("br");

      citationDiv.appendChild(documentLabel);

      citationDiv.appendChild(documentName);

      citationDiv.appendChild(lineBreak);

      citationDiv.appendChild(sectionLabel);

      citationDiv.appendChild(sectionName);

      citationsElement.appendChild(citationDiv);
    });
  } catch (error) {
    console.error("HR Assistant error:", error);

    answerElement.textContent = `Error: ${error.message}`;

    citationsElement.innerHTML = "";
  }
}
