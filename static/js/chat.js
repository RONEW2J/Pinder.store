document.addEventListener('DOMContentLoaded', function() {
    // Получаем данные пользователя
    const currentUserId = document.body.dataset.userId;
    const messagesContainer = document.getElementById('messagesContainer');
    const messageForm = document.getElementById('messageForm');

    // WebSocket соединение
    const pathParts = window.location.pathname.split('/');
    const conversationId = pathParts.find(part => !isNaN(parseInt(part)));
    
    if (conversationId) {
        const wsScheme = window.location.protocol === "https:" ? "wss" : "ws";
        const chatSocket = new WebSocket(
            `${wsScheme}://${window.location.host}/ws/chat/${conversationId}/`
        );

        // Обработка новых сообщений
        chatSocket.onmessage = function(e) {
            const data = JSON.parse(e.data);
            const isCurrentUser = data.sender_id == currentUserId;
            
            const messageHTML = `
                <div class="message ${isCurrentUser ? 'sent' : 'received'}">
                    <div class="message-content">
                        <p>${data.content}</p>
                        <span class="message-time">
                            ${new Date(data.timestamp).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}
                        </span>
                    </div>
                </div>
            `;
            
            messagesContainer.insertAdjacentHTML('beforeend', messageHTML);
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        };

        // Отправка сообщений
        if (messageForm) {
            messageForm.addEventListener('submit', function(e) {
                e.preventDefault();
                const messageInput = this.querySelector('input[name="content"]');
                const message = messageInput.value.trim();
                
                if (message && chatSocket.readyState === WebSocket.OPEN) {
                    chatSocket.send(JSON.stringify({
                        'message': message,
                        'sender_id': currentUserId
                    }));
                    messageInput.value = '';
                }
            });
        }
    }

    // Поиск в списке бесед
    const searchInput = document.getElementById('conversationSearch');
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            const term = this.value.toLowerCase();
            document.querySelectorAll('.conversation-item').forEach(item => {
                const name = item.querySelector('h3').textContent.toLowerCase();
                item.style.display = name.includes(term) ? '' : 'none';
            });
        });
    }
});