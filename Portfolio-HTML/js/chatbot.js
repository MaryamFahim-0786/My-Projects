document.addEventListener("DOMContentLoaded", () => {

    const toggle = document.querySelector(".chat-toggle");
    const chatWindow = document.querySelector(".chat-window");
    const closeBtn = document.querySelector(".chat-close");

    const input = document.getElementById("user-input");
    const sendBtn = document.getElementById("send-message");
    const chatBody = document.getElementById("chat-body");

    if (!toggle || !chatWindow || !input || !sendBtn || !chatBody) {
        console.error("Maryam AI: Chatbot elements not found.");
        return;
    }

    // Open chatbot
    toggle.addEventListener("click", () => {
        chatWindow.classList.toggle("active");
        input.focus();
    });

    // Close chatbot
    if (closeBtn) {
        closeBtn.addEventListener("click", () => {
            chatWindow.classList.remove("active");
        });
    }

    // Add message
    function addMessage(message, type) {

        const div = document.createElement("div");

        div.className =
            type === "user"
                ? "user-message"
                : "bot-message";

        div.innerHTML = message;

        chatBody.appendChild(div);

        chatBody.scrollTop = chatBody.scrollHeight;
    }

    // Simple portfolio AI
    function getBotResponse(question) {

        const q = question.toLowerCase();

        if (q.includes("name")) {
            return "My name is Maryam Fahim. I'm an AI Engineer and Full Stack Developer.";
        }

        if (q.includes("skill")) {
            return "Maryam's skills include Python, C++, JavaScript, PHP, React, MERN, HTML, CSS, AI, Machine Learning and Web Development.";
        }

        if (q.includes("project")) {
            return "Maryam has worked on projects including AI platforms, web applications, mobile applications, Java projects and management systems.";
        }

        if (q.includes("ai") || q.includes("artificial intelligence")) {
            return "Maryam is focused on Artificial Intelligence, Machine Learning and building intelligent applications.";
        }

        if (q.includes("education") || q.includes("study")) {
            return "Maryam is a Computer Science student currently in her 7th semester with a CGPA of 3.75.";
        }

        if (q.includes("github")) {
            return "You can find Maryam's projects on GitHub.";
        }

        if (q.includes("contact") || q.includes("email")) {
            return "You can contact Maryam through the Contact section of this portfolio.";
        }

        if (q.includes("hello") || q.includes("hi") || q.includes("hey")) {
            return "Hello! 👋 I'm Maryam AI. Ask me about Maryam's skills, projects, education or experience.";
        }

        return "I'm Maryam AI 🤖. I can answer questions about Maryam's skills, projects, education and professional journey.";
    }

    // Send message
    function sendMessage() {

        const message = input.value.trim();

        if (!message) return;

        addMessage(message, "user");

        input.value = "";

        // Typing delay
        setTimeout(() => {

            const response = getBotResponse(message);

            addMessage(response, "bot");

        }, 500);
    }

    sendBtn.addEventListener("click", sendMessage);

    input.addEventListener("keydown", (event) => {

        if (event.key === "Enter") {
            sendMessage();
        }

    });

});