document.addEventListener('DOMContentLoaded', function () {
    const messagesContainer = document.getElementById('messagesContainer');
    const messageInput = document.getElementById('messageInput');
    const messageForm = document.getElementById('messageForm');
    const sendButton = document.getElementById('sendButton'); // Assuming you might want to disable it
    const conversationSearchInput = document.getElementById('conversationSearch');

    const unmatchModal = document.getElementById('unmatchModal');
    const cancelUnmatchButton = document.getElementById('cancelUnmatch');
    const confirmUnmatchButton = document.getElementById('confirmUnmatch');
    const unmatchButtonInView = document.querySelector('.conversation-view .unmatch-btn'); // Specific to active chat
    let profileIdToUnmatch = null;

    let chatSocket = null;

    function getCsrfToken() {
        const csrfTokenEl = document.querySelector('[name=csrfmiddlewaretoken]');
        return csrfTokenEl ? csrfTokenEl.value : null;
    }

    function scrollToBottom() {
        if (messagesContainer) {
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }
    }

    // Initialize scroll on page load if there's an active conversation
    if (messagesContainer && document.querySelector('.conversation-view .conversation-header')) {
        scrollToBottom();
    }

    // --- WebSocket Setup ---
    // Extract conversation ID. This assumes the ID is in the URL path like /chat/123/
    // Or, you can pass it via a data attribute in your HTML.
    const pathParts = window.location.pathname.split('/');
    const conversationId = pathParts.find(part => !isNaN(parseInt(part))); // A simple way to find numeric ID in path

    if (conversationId && document.querySelector('.conversation-view .conversation-header')) { // Only connect if a conversation is active
        const wsScheme = window.location.protocol === "https:" ? "wss" : "ws";
        // IMPORTANT: Ensure this matches your `apps.matches.routing.websocket_urlpatterns`
        chatSocket = new WebSocket(
            `${wsScheme}://${window.location.host}/ws/chat/${conversationId}/`
        );

        chatSocket.onopen = function (e) {
            console.log('Chat socket connected');
        };

        chatSocket.onmessage = function (e) {
            const data = JSON.parse(e.data);
            console.log('Message received:', data);

            // Assuming data has: sender_username, content, timestamp, sender_id
            // And you have a global `currentUserId` or can infer from message styling
            // For simplicity, we'll assume `data.sender_id` helps determine if it's "sent" or "received"
            // You'll need to pass the current user's ID to the template or JS
            const currentUserId = window.currentUserId; // You need to set this variable, e.g., in a <script> tag in your base.html or chat.html

            const messageDiv = document.createElement('div');
            messageDiv.classList.add('message');
            if (data.sender_id === currentUserId) {
                messageDiv.classList.add('sent');
            } else {
                messageDiv.classList.add('received');
            }

            const messageContentDiv = document.createElement('div');
            messageContentDiv.classList.add('message-content');

            const p = document.createElement('p');
            p.textContent = data.content;

            const timeSpan = document.createElement('span');
            timeSpan.classList.add('message-time');
            timeSpan.textContent = new Date(data.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

            messageContentDiv.appendChild(p);
            messageContentDiv.appendChild(timeSpan);
            messageDiv.appendChild(messageContentDiv);

            if (messagesContainer) {
                messagesContainer.appendChild(messageDiv);
                scrollToBottom();
            }
        };

        chatSocket.onclose = function (e) {
            console.error('Chat socket closed unexpectedly');
        };

        chatSocket.onerror = function (err) {
            console.error('WebSocket encountered error: ', err.message, 'Closing socket');
            chatSocket.close();
        };
    }

    // --- Sending Messages ---
    if (messageForm) {
        messageForm.addEventListener('submit', function (e) {
            e.preventDefault();
            const message = messageInput.value.trim();
            if (message && chatSocket && chatSocket.readyState === WebSocket.OPEN) {
                chatSocket.send(JSON.stringify({
                    'message': message
                }));
                messageInput.value = ''; // Clear input
            }
        });
    }

    // --- Conversation Search ---
    if (conversationSearchInput) {
        conversationSearchInput.addEventListener('input', function () {
            const searchTerm = this.value.toLowerCase();
            const conversationItems = document.querySelectorAll('.conversations-list .conversation-item');
            conversationItems.forEach(item => {
                const name = item.querySelector('.conversation-details h3').textContent.toLowerCase();
                const preview = item.querySelector('.conversation-preview p').textContent.toLowerCase();
                if (name.includes(searchTerm) || preview.includes(searchTerm)) {
                    item.style.display = '';
                } else {
                    item.style.display = 'none';
                }
            });
        });
    }

    // --- Unmatch Functionality (similar to matches.js but specific to active chat) ---
    if (unmatchButtonInView) {
        unmatchButtonInView.addEventListener('click', function () {
            profileIdToUnmatch = this.dataset.profileId;
            if (unmatchModal) unmatchModal.style.display = 'flex';
        });
    }

    if (cancelUnmatchButton) {
        cancelUnmatchButton.addEventListener('click', function () {
            if (unmatchModal) unmatchModal.style.display = 'none';
            profileIdToUnmatch = null;
        });
    }

    if (confirmUnmatchButton) {
        confirmUnmatchButton.addEventListener('click', function () {
            if (profileIdToUnmatch) {
                // IMPORTANT: Replace '/api/actions/unmatch/' with your actual unmatch API endpoint
                fetch(`/api/actions/unmatch/${profileIdToUnmatch}/`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCsrfToken(),
                    },
                })
                .then(response => {
                    if (response.ok) {
                        console.log('Successfully unmatched with profile ID:', profileIdToUnmatch);
                        // Redirect to matches page or update UI to show no active conversation
                        window.location.href = "{% url 'matches' %}"; // Django template tag won't work here, use actual URL
                    } else {
                        console.error('Failed to unmatch.');
                        alert('Failed to unmatch. Please try again.');
                    }
                })
                .finally(() => {
                    if (unmatchModal) unmatchModal.style.display = 'none';
                    profileIdToUnmatch = null;
                });
            }
        });
    }

    if (unmatchModal) {
        unmatchModal.addEventListener('click', function(event) {
            if (event.target === unmatchModal) {
                unmatchModal.style.display = 'none';
                profileIdToUnmatch = null;
            }
        });
    }
});