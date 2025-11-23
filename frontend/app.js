
    const chatBox = document.getElementById("chatBox");
    const input = document.getElementById("messageInput");
    const sendBtn = document.getElementById("sendBtn");

    function appendMessage(text, sender) {
        const msg = document.createElement("div");
        msg.className = sender === "user" ? "message user" : "message bot";

        const avatar = sender === "user" ? "🧑" : "🤖";

        msg.innerHTML = `
            <div class="avatar">${avatar}</div>
            <div class="bubble">${text}</div>
        `;

        chatBox.appendChild(msg);
        chatBox.scrollTop = chatBox.scrollHeight;
    }

    async function sendMessage() {
        const text = input.value.trim();
        if (!text) return;

        appendMessage(text, "user");
        input.value = "";

        try {
            const res = await fetch("http://127.0.0.1:8000/chat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ session_id: "user123", message: text })
            });

            const data = await res.json();
            appendMessage(data.reply, "bot");

        } catch (error) {
            appendMessage("⚠️ Failed to reach backend server", "bot");
        }
    }

    sendBtn.onclick = sendMessage;

    input.addEventListener("keypress", function(e) {
        if (e.key === "Enter") {
            sendMessage();
        }
    });

