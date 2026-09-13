const API_URL = "https://hr-policy-assistant-ji8i.onrender.com";
const suggestedQuestions = {
  password: [
    "Can I reuse my personal account password?",
    "Can I share my password with colleagues?",
    "What should I do if my device is lost?",
  ],

  leave: [
    "How many casual leave days can I carry forward?",
    "How many sick leave days are available?",
    "Can unused sick leave be carried forward?",
  ],

  lta: [
    "What is the annual LTA limit for Band C?",
    "Who is eligible for LTA?",
    "What expenses are covered under LTA?",
  ],

  security: [
    "What should I do if I receive a phishing email?",
    "What are the company device requirements?",
    "Which browser extensions require approval?",
  ],
};

function getQuestionTopic(question) {
  const q = question.toLowerCase();

  if (q.includes("password") || q.includes("otp") || q.includes("session")) {
    return "password";
  }

  if (
    q.includes("leave") ||
    q.includes("casual") ||
    q.includes("sick") ||
    q.includes("privilege")
  ) {
    return "leave";
  }

  if (q.includes("lta") || q.includes("travel allowance")) {
    return "lta";
  }

  if (
    q.includes("phishing") ||
    q.includes("device") ||
    q.includes("laptop") ||
    q.includes("browser")
  ) {
    return "security";
  }

  return null;
}

function showSuggestedQuestions(question) {
  const topic = getQuestionTopic(question);

  const suggestedSection = document.getElementById("suggestedQuestions");
  const suggestedList = document.getElementById("suggestedList");

  if (!topic || !suggestedQuestions[topic]) {
    suggestedSection.style.display = "none";
    suggestedList.innerHTML = "";
    return;
  }

  suggestedList.innerHTML = "";

  suggestedQuestions[topic]
    .filter(function (suggestedQuestion) {
      return suggestedQuestion.toLowerCase() !== question.toLowerCase();
    })
    .forEach(function (suggestedQuestion) {
      const button = document.createElement("button");

      button.className = "suggested-question";
      button.textContent = suggestedQuestion;

      button.onclick = function () {
        askSuggestedQuestion(suggestedQuestion);
      };

      suggestedList.appendChild(button);
    });

  suggestedSection.style.display = "block";
}

function askSuggestedQuestion(question) {
  const questionInput = document.getElementById("question");

  questionInput.value = question;

  askQuestion();
}

// ==========================================
// ASK HR POLICY QUESTION
// ==========================================

async function askQuestion() {
  const askButton = document.getElementById("askButton");
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
  askButton.disabled = true;
  askButton.innerHTML = `
    <span class="loading-spinner"></span>
    Searching...
`;

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

    if (data.citations && data.citations.length > 0) {
      showSuggestedQuestions(question);
    } else {
      document.getElementById("suggestedQuestions").style.display = "none";
    }
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
  } finally {
    askButton.disabled = false;
    askButton.innerHTML = `
        Ask Assistant
        <span class="arrow">→</span>
    `;
  }
}

function askDemoQuestion(question) {
  const questionInput = document.getElementById("question");

  questionInput.value = question;

  askQuestion();
}
