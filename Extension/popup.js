const BACKEND_URL = "http://127.0.0.1:8000/ask";

const questionEl = document.getElementById("question");
const askBtn = document.getElementById("askBtn");
const statusEl = document.getElementById("status");
const answerWrap = document.getElementById("answerWrap");
const answerEl = document.getElementById("answer");
const pageTitleEl = document.getElementById("pageTitle");
const sourceUrlEl = document.getElementById("sourceUrl");

let pageContent = "";

function setStatus(text, isError = false) {
  statusEl.textContent = text;
  statusEl.classList.toggle("error", isError);
}

function showAnswer(text) {
  answerEl.textContent = text;
  answerWrap.classList.remove("hidden");
}

async function loadPageContent() {
  try {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    if (!tab?.id) {
      throw new Error("No active tab found.");
    }

    const response = await chrome.tabs.sendMessage(tab.id, { type: "GET_PAGE_CONTENT" });

    if (!response?.content) {
      pageTitleEl.textContent = "Couldn't read this page";
      setStatus("Try reloading the page, then reopen the extension.", true);
      return;
    }

    pageContent = response.content;
    pageTitleEl.textContent = response.title || "Untitled page";
    sourceUrlEl.textContent = response.url || "";
  } catch (err) {
    pageTitleEl.textContent = "Couldn't read this page";
    setStatus("This page can't be read (e.g. chrome:// pages are restricted).", true);
  }
}

async function askQuestion() {
  const question = questionEl.value.trim();

  if (!question) {
    setStatus("Type a question first.", true);
    return;
  }

  if (!pageContent) {
    setStatus("No page content available to search.", true);
    return;
  }

  askBtn.disabled = true;
  answerWrap.classList.add("hidden");
  setStatus("Thinking… this can take up to a minute on first use.");

  try {
    const res = await fetch(BACKEND_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        question,
        context: pageContent
      })
    });

    if (!res.ok) {
      throw new Error(`Server responded with ${res.status}`);
    }

    const data = await res.json();
    showAnswer(data.answer || "No answer returned.");
    setStatus("");
  } catch (err) {
    setStatus(`Couldn't reach the assistant: ${err.message}`, true);
  } finally {
    askBtn.disabled = false;
  }
}

askBtn.addEventListener("click", askQuestion);

questionEl.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) {
    askQuestion();
  }
});

loadPageContent();
