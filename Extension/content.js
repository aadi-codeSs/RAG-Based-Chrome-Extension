// Listens for a request from the popup and returns the readable text
// content of the current page, trimmed to a safe size for the backend.

const MAX_CONTEXT_CHARS = 12000;

function extractPageText() {
  // Prefer the <main> or <article> region if the page has one —
  // it usually contains the real content without nav/footer noise.
  const preferred = document.querySelector("main, article");
  const source = preferred || document.body;

  let text = source ? source.innerText : "";
  text = text.replace(/\s+/g, " ").trim();

  if (text.length > MAX_CONTEXT_CHARS) {
    text = text.slice(0, MAX_CONTEXT_CHARS);
  }

  return {
    title: document.title,
    url: location.href,
    content: text
  };
}

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message?.type === "GET_PAGE_CONTENT") {
    sendResponse(extractPageText());
  }
  return true;
});
