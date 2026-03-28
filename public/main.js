const API_URL = "https://ask-ai-fldu3cj6vq-uc.a.run.app";

async function askAI() {
  const queryInput = document.getElementById("question-input");
  const responseBox = document.getElementById("response-container");
  const responseText = document.getElementById("response-text");
  const sendBtn = document.getElementById("send-button");

  const query = queryInput.value.trim();
  if (!query) return;

  // UI Feedback: Show loading state
  responseBox.classList.remove("hidden");
  responseBox.style.opacity = "1";
  responseText.innerHTML = '<span class="loading">Joshia\'s assistant is thinking...</span>';
  sendBtn.disabled = true;

  try {
    const response = await fetch(API_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ data: { query: query } }),
    });

    const result = await response.json();

    // Display actual AI response
    // responseText.innerText = result.data.text;
    responseText.innerHTML = marked.parse(result.data.text.replace(/\n\n/g, "<br><br>"));
  } catch (error) {
    console.error("Error: ", error);
    responseText.innerText = "Sorry, I couldn't connect right now. Please try again later!";
  } finally {
    sendBtn.disabled = false;
  }
}

// Allow pressing 'Enter' to send
function handleEnter(event) {
  if (event.key === "Enter") {
    askAI();
  }
}
