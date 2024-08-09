const chatInput = document.querySelector("#chat-input");
const sendButton = document.querySelector("#send-btn");
const chatContainer = document.querySelector(".chat-container");
const themeButton = document.querySelector("#theme-btn");
const deleteButton = document.querySelector("#delete-btn");

const initialInputHeight = chatInput.scrollHeight;
const animationDuration = 1500; // Duration of the typing animation in milliseconds

const loadDataFromLocalStorage = () => {
    const themeColor = localStorage.getItem("themeColor");
    document.body.classList.toggle("light-mode", themeColor === "light_mode");
    themeButton.innerText = document.body.classList.contains("light-mode") ? "dark_mode" : "light_mode";

    const defaultText = `<div class="default-text">
                            <h1>E.D.I.T.H</h1>
                            <p><b>Educational Dialogue-based Intelligent Tutoring Helper</b><br>Start a conversation and explore the power of AI.<br> Your chat history will be displayed here.</p>
                        </div>`;
                        
    chatContainer.innerHTML = localStorage.getItem("all-chats") || defaultText;
    chatContainer.scrollTo(0, chatContainer.scrollHeight);
};

const createChatElement = (content, className) => {
    const chatDiv = document.createElement("div");
    chatDiv.classList.add("chat", className);
    chatDiv.innerHTML = content;
    return chatDiv;
};

const showTypingAnimation = () => {
    const html = `<div class="chat-content typing-animation" style="padding: 0px 600px 0px 0px;">
                    <div class="chat-details">
                        <img src="images/chatbot.jpg" alt="chatbot-img">
                        <div class="typing-animation">
                            <div class="typing-dot" style="--delay: 0.2s"></div>
                            <div class="typing-dot" style="--delay: 0.3s"></div>
                            <div class="typing-dot" style="--delay: 0.4s"></div>
                        </div>
                    </div>
                </div>`;
    const incomingChatDiv = createChatElement(html, "incoming");
    chatContainer.appendChild(incomingChatDiv);
    chatContainer.scrollTo(0, chatContainer.scrollHeight);
    return incomingChatDiv;
};

const handleOutgoingChat = async () => {
    const selectedCategory = document.querySelector('.box.selected .category-btn');
    const userText = chatInput.value.trim();
    if (!userText) return;

    chatInput.value = "";
    chatInput.style.height = `${initialInputHeight}px`;

    const html = `<div class="chat-content">
                    <div class="chat-details">
                        <img src="images/user.jpg" alt="user-img">
                        <p>${userText}</p>
                    </div>
                </div>`;

    const outgoingChatDiv = createChatElement(html, "outgoing");
    chatContainer.querySelector(".default-text")?.remove();
    chatContainer.appendChild(outgoingChatDiv);
    chatContainer.scrollTo(0, chatContainer.scrollHeight);

    const incomingChatDiv = showTypingAnimation();
// Inside your handleOutgoingChat() function, after checking for selected category
const firstUserMessage = userText.trim();
if (firstUserMessage && !slidingMenu.querySelector('.menu-item')) {
    addMenuButton(firstUserMessage);
}

    setTimeout(async () => {
        if (selectedCategory && selectedCategory.innerText === "Counselling") {
            try {
                const response = await fetch("/api/chat", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({ message: userText })
                });
                const data = await response.json();
                const botText = data.response;
                incomingChatDiv.remove(); // Remove typing animation
                const botChat = createChatElement(`
                    <div class="chat-details bot">
                        <img src="images/chatbot.jpg" alt="chatbot-img">
                        <p>${botText}</p>
                    </div>`, "incoming");
                chatContainer.appendChild(botChat);
                chatContainer.scrollTo(0, chatContainer.scrollHeight);
                localStorage.setItem("all-chats", chatContainer.innerHTML);
            } catch (error) {
                incomingChatDiv.remove(); // Remove typing animation
                const errorChat = createChatElement(`
                    <div class="chat-details bot error">
                        <p>Oops! Something went wrong while retrieving the response. Please try again.</p>
                    </div>`, "incoming");
                chatContainer.appendChild(errorChat);
                chatContainer.scrollTo(0, chatContainer.scrollHeight);
                console.error("Error:", error);
            }
        } else if (selectedCategory && selectedCategory.innerText === "College Prediction") {
            let data = { userText };
            if (userText.includes("10th")) {
                const percentage = parseFloat(prompt("Enter your percentage: "));
                data = { standard: '10th', percentage };
            } else if (userText.includes("12th")) {
                const choice = prompt("Enter your choice (engineering/doctor): ");
                const percentage = parseFloat(prompt("Enter your percentage: "));
                const cet_percentile = parseFloat(prompt("Enter your CET percentile: "));
                if (choice === 'engineering') {
                    const jee_percentile = parseFloat(prompt("Enter your JEE percentile: "));
                    data = { standard: '12th', choice, percentage, cet_percentile, jee_percentile };
                } else if (choice === 'doctor') {
                    const neet_marks = parseFloat(prompt("Enter your NEET marks: "));
                    data = { standard: '12th', choice, percentage, cet_percentile, neet_marks };
                } else {
                    alert("Invalid choice. Please enter 'engineering' or 'doctor'.");
                    incomingChatDiv.remove(); // Remove typing animation
                    return;
                }
            } else {
                alert("Invalid standard. Please enter '10th' or '12th'.");
                incomingChatDiv.remove(); // Remove typing animation
                return;
            }

            try {
                const response = await fetch('/check-eligibility', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                });
                const result = await response.json();
                incomingChatDiv.remove(); // Remove typing animation
                const incomingChatResponse = createChatElement(`
                    <div class="chat-content">
                        <div class="chat-details">
                            <img src="images/chatbot.jpg" alt="chatbot-img">
                            <p>${result.message}</p>
                        </div>
                    </div>`, "incoming");

                chatContainer.appendChild(incomingChatResponse);
                chatContainer.scrollTo(0, chatContainer.scrollHeight);

                if (result.colleges) {
                    result.colleges.forEach(college => {
                        const collegeDiv = createChatElement(`
                            <div class="chat-content">
                                <div class="chat-details">
                                    <p>${college}</p>
                                </div>
                            </div>`, "incoming");
                        chatContainer.appendChild(collegeDiv);
                        chatContainer.scrollTo(0, chatContainer.scrollHeight);
                    });
                }

                localStorage.setItem("all-chats", chatContainer.innerHTML);
            } catch (error) {
                incomingChatDiv.remove(); // Remove typing animation
                const errorChat = createChatElement(`
                    <div class="chat-details bot error">
                        <p>Oops! Something went wrong while retrieving the response. Please try again.</p>
                    </div>`, "incoming");
                chatContainer.appendChild(errorChat);
                chatContainer.scrollTo(0, chatContainer.scrollHeight);
                console.error("Error:", error);
            }
        } else {
            incomingChatDiv.remove(); // Remove typing animation
        }
    }, animationDuration);
};

deleteButton.addEventListener("click", () => {
    if (confirm("Are you sure you want to delete all the chats?")) {
        localStorage.removeItem("all-chats");
        loadDataFromLocalStorage();
    }
});

themeButton.addEventListener("click", () => {
    document.body.classList.toggle("light-mode");
    localStorage.setItem("themeColor", themeButton.innerText);
    themeButton.innerText = document.body.classList.contains("light-mode") ? "dark_mode" : "light_mode";
});

chatInput.addEventListener("input", () => {
    chatInput.style.height = `${initialInputHeight}px`;
    chatInput.style.height = `${chatInput.scrollHeight}px`;
});

chatInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey && window.innerWidth > 800) {
        e.preventDefault();
        handleOutgoingChat();
    }
});

document.querySelectorAll('.box').forEach(function(box) {
    box.addEventListener('click', function() {
        document.querySelectorAll('.box').forEach(function(box) {
            box.classList.remove('selected');
        });
        this.classList.add('selected');
        chatContainer.innerHTML = '';
        if (this.textContent.trim() === 'Counselling') {
            startCounselling();
        } else if (this.textContent.trim() === 'College Prediction') {
            startCollegePrediction();
        }
    });
});

const startCounselling = () => {
    const botChat = createChatElement(`
        <div class="chat-details bot" style="padding: 0px 0px 0px 0px;">
            <img src="images/chatbot.jpg" alt="chatbot-img">
            <p>Hey! How can I help you?</p>
        </div>`, "incoming");
    chatContainer.appendChild(botChat);
    chatContainer.scrollTo(0, chatContainer.scrollHeight);
};

const startCollegePrediction = () => {
    const botChat = createChatElement(`
        <div class="chat-details bot" style="padding: 0px 600px 0px 0px;">
            <img src="images/chatbot.jpg" alt="chatbot-img">
            <p>Enter your standard (10th or 12th)</p>
        </div>`, "incoming");
    chatContainer.appendChild(botChat);
    chatContainer.scrollTo(0, chatContainer.scrollHeight);
};

loadDataFromLocalStorage();
sendButton.addEventListener("click", handleOutgoingChat);
