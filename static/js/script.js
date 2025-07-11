document.addEventListener("DOMContentLoaded", () => {
    const chatWindow = document.getElementById("chat-window");
    const chatForm = document.getElementById("chat-form");
    const messageInput = document.getElementById("message-input");
    const typingIndicator = document.getElementById("typing-indicator");

    let chatHistory = [];
    let userIntroduced = false;

    // Animación de entrada para los mensajes
    function addMessageToUI(sender, message) {
        const messageElement = document.createElement("div");
        messageElement.classList.add(
            "message",
            sender === "user" ? "user-message" : "assistant-message",
            "fade-in"
        );
        messageElement.textContent = message;
        chatWindow.appendChild(messageElement);

        // Desplazar automáticamente al final
        chatWindow.scrollTop = chatWindow.scrollHeight;
    }

    // Mensaje de bienvenida inicial
    function showWelcome() {
        addMessageToUI(
            "assistant",
            "👋 ¡Hola! Soy tu entrevistador técnico de Data Science. ¿Puedes presentarte antes de comenzar la entrevista?"
        );
    }

    // Función para manejar el envío del formulario
    const handleSendMessage = async (event) => {
        event.preventDefault();
        const userMessage = messageInput.value.trim();

        if (!userMessage) return;

        addMessageToUI("user", userMessage);
        messageInput.value = "";

        // Si el usuario aún no se ha presentado
        if (!userIntroduced) {
            userIntroduced = true;
            typingIndicator.style.display = "flex";
            try {
                const response = await fetch("/chat", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        message: userMessage,
                        history: []
                    }),
                });
                const data = await response.json();
                addMessageToUI("assistant", data.message);
                chatHistory.push({ role: "user", content: userMessage });
                chatHistory.push({ role: "assistant", content: data.message });
            } catch {
                addMessageToUI("assistant", "Ha ocurrido un error al iniciar la entrevista.");
            } finally {
                typingIndicator.style.display = "none";
            }
            return;
        }

        // Añadir mensaje del usuario al historial
        chatHistory.push({ role: "user", content: userMessage });
        typingIndicator.style.display = "flex";

        try {
            const response = await fetch("/chat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    message: userMessage,
                    history: chatHistory.slice(0, -1)
                }),
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            const assistantMessage = data.message;

            addMessageToUI("assistant", assistantMessage);
            chatHistory.push({ role: "assistant", content: assistantMessage });

        } catch (error) {
            console.error("Error al contactar la API:", error);
            addMessageToUI("assistant", "Lo siento, ha ocurrido un error. Por favor, inténtalo de nuevo.");
        } finally {
            typingIndicator.style.display = "none";
        }
    };

    chatForm.addEventListener("submit", handleSendMessage);

    // Mostrar bienvenida al cargar
    showWelcome();
});