document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded - initializing swipe functionality');
    
    // Debugging helper
    function debugLog(message, obj = null) {
        if (obj) {
            console.log(`[Debug] ${message}:`, obj);
        } else {
            console.log(`[Debug] ${message}`);
        }
    }

    // Основной класс для работы со свайпами в стиле Tinder
    class TinderSwipe {
        constructor(options) {
            debugLog('TinderSwipe constructor called', options);
            
            // DOM элементы
            this.cardsContainer = document.querySelector(options.cardsContainerSelector || '.cards-container');
            this.likeButton = document.querySelector(options.likeButtonSelector || '.like-btn');
            this.passButton = document.querySelector(options.passButtonSelector || '.pass-btn');
            this.swipeContainer = document.querySelector(options.swipeContainerSelector || '.swipe-container');
            
            // Log DOM elements for debugging
            debugLog('Cards container found:', this.cardsContainer);
            debugLog('Like button found:', this.likeButton);
            debugLog('Pass button found:', this.passButton);
            debugLog('Swipe container found:', this.swipeContainer);
            
            // Настройки
            this.threshold = options.threshold || 100; // Минимальное расстояние свайпа для срабатывания
            this.rotationAngle = options.rotationAngle || 10; // Угол поворота при свайпе
            this.animationSpeed = options.animationSpeed || 400; // Длительность анимации в мс
            this.maxVisibleCards = options.maxVisibleCards || 3; // Количество видимых карточек в стеке
            
            // Состояние
            this.cards = [];
            this.currentCardIndex = 0;
            this.userIdToSwipe = null;
            
            // API настройки
            this.apiEndpoint = options.apiEndpoint || '/api/swipe';
            this.csrfTokenSelector = options.csrfTokenSelector || '[name=csrfmiddlewaretoken]';
            
            // Инициализация
            this.initializeCards();
            this.bindEvents();
        }
        
        // Получение всех карточек и настройка их начального положения
        initializeCards() {
            if (!this.cardsContainer) {
                debugLog('ERROR: Cards container not found!');
                return;
            }
            
            this.cards = Array.from(this.cardsContainer.querySelectorAll('.swipe-card'));
            debugLog(`Found ${this.cards.length} cards for swiping`);
            
            if (this.cards.length === 0) {
                this.showNoMoreProfiles();
                return;
            }
            
            // Make sure the first card is visible and positioned correctly
            this.cards.forEach((card, index) => {
                if (index === 0) {
                    card.classList.add('active-card');
                    card.style.display = 'block';
                    card.style.zIndex = 10;
                    card.style.transform = '';
                    card.style.opacity = 1;
                } else if (index < this.maxVisibleCards) {
                    card.style.display = 'block';
                    card.style.zIndex = 10 - index;
                    card.style.transform = `scale(${1 - index * 0.05}) translateY(${index * 10}px)`;
                    card.style.opacity = 1 - index * 0.2;
                } else {
                    card.style.display = 'none';
                }
            });
            
            // Update swipe button states
            this.updateButtons();
        }
        
        // Enable/disable swipe buttons based on card availability
        updateButtons() {
            const hasCards = this.currentCardIndex < this.cards.length;
            
            if (this.likeButton) {
                this.likeButton.disabled = !hasCards;
                this.likeButton.classList.toggle('disabled', !hasCards);
            }
            
            if (this.passButton) {
                this.passButton.disabled = !hasCards;
                this.passButton.classList.toggle('disabled', !hasCards);
            }
            
            if (!hasCards) {
                this.showNoMoreProfiles();
            }
        }
        
        // Привязка событий к элементам
        bindEvents() {
            // Кнопки лайка и пропуска
            if (this.likeButton) {
                debugLog('Adding click event to like button');
                this.likeButton.addEventListener('click', (e) => {
                    debugLog('Like button clicked');
                    e.preventDefault();
                    if (!this.likeButton.disabled) {
                        this.handleButtonAction('like');
                    }
                });
            } else {
                debugLog('ERROR: Like button not found');
            }
            
            if (this.passButton) {
                debugLog('Adding click event to pass button');
                this.passButton.addEventListener('click', (e) => {
                    debugLog('Pass button clicked');
                    e.preventDefault();
                    if (!this.passButton.disabled) {
                        this.handleButtonAction('pass');
                    }
                });
            } else {
                debugLog('ERROR: Pass button not found');
            }
            
            // Обработка свайпов для каждой карточки
            this.cards.forEach(card => this.initializeCardSwipe(card));
        }
        
        // Настройка свайпа для карточки используя Hammer.js
        initializeCardSwipe(card) {
            // Проверяем доступность Hammer.js
            if (typeof Hammer === 'undefined') {
                console.error('Hammer.js не загружен! Свайпы не будут работать.');
                return;
            }
            
            const hammer = new Hammer(card);
            hammer.get('pan').set({ direction: Hammer.DIRECTION_ALL });
            
            // События Hammer для обработки свайпов
            hammer.on('panstart', () => {
                // Only handle swipe for the active card
                if (!card.classList.contains('active-card')) return;
                
                card.classList.add('dragging');
                card.style.transition = 'none'; // Убираем transition для плавного следования за пальцем
            });
            
            hammer.on('panmove', (event) => {
                // Only handle swipe for the active card
                if (!card.classList.contains('active-card')) return;
                
                this.handlePanMove(card, event);
            });
            
            hammer.on('panend', (event) => {
                // Only handle swipe for the active card
                if (!card.classList.contains('active-card')) return;
                
                this.handlePanEnd(card, event);
            });
        }
        
        // Обработка движения при свайпе
        handlePanMove(card, event) {
            // Игнорируем некорректные события
            if (event.deltaX === 0 || (event.center.x === 0 && event.center.y === 0)) return;
            
            // Расчет трансформации
            const xMulti = event.deltaX / 80; // Коэффициент для эффекта поворота
            const yMulti = event.deltaY / 200; // Меньшее влияние на вертикальную ось
            const rotation = xMulti * 10; // Ограничиваем угол поворота
            
            // Применение трансформации
            card.style.transform = `translate(${event.deltaX}px, ${event.deltaY}px) rotate(${rotation}deg)`;
            
            // Показываем индикаторы лайка/пропуска
            this.updateSwipeIndicators(card, event.deltaX);
        }
        
        // Обработка окончания свайпа
        handlePanEnd(card, event) {
            card.classList.remove('dragging');
            card.style.transition = `transform ${this.animationSpeed / 1000}s ease-out`;
            
            // Проверяем, был ли свайп достаточно сильным для действия
            const moveOutWidth = document.body.clientWidth;
            const triggeredAction = Math.abs(event.deltaX) > this.threshold || Math.abs(event.velocityX) > 0.5;
            
            if (triggeredAction) {
                // Определяем направление свайпа
                const action = event.deltaX > 0 ? 'like' : 'pass';
                
                // Вычисляем конечную позицию для анимации "улетания"
                const xPos = event.deltaX > 0 ? moveOutWidth * 1.5 : -moveOutWidth * 1.5;
                const yPos = event.deltaY;
                const rotation = event.deltaX * 0.1; // Увеличиваем вращение при улетании
                
                // Применяем анимацию улетания
                card.style.transform = `translate(${xPos}px, ${yPos}px) rotate(${rotation}deg)`;
                card.classList.add(`swiping-${action === 'like' ? 'right' : 'left'}`);
                
                // Обрабатываем действие (лайк/пропуск)
                this.handleSwipeAction(card, action);
            } else {
                // Возвращаем карточку на место, если свайп был недостаточным
                this.resetCardPosition(card);
            }
            
            // Скрываем индикаторы в любом случае
            this.hideSwipeIndicators(card);
        }
        
        // Обработка нажатия на кнопки лайка/пропуска
        handleButtonAction(action) {
            debugLog(`Button action: ${action}`);
            
            const currentCard = this.getCurrentCard();
            if (!currentCard) {
                debugLog('No current card found');
                return;
            }
            
            debugLog('Processing current card', currentCard);
            currentCard.style.transition = `transform ${this.animationSpeed / 1000}s ease-out`;
            
            // Применяем класс анимации в зависимости от действия
            currentCard.classList.add(action === 'like' ? 'swiping-right' : 'swiping-left');
            
            // Задаем конечную позицию для анимации
            const moveOutWidth = document.body.clientWidth;
            const xPos = action === 'like' ? moveOutWidth * 1.5 : -moveOutWidth * 1.5;
            const rotation = action === 'like' ? this.rotationAngle : -this.rotationAngle;
            
            currentCard.style.transform = `translate(${xPos}px, 0) rotate(${rotation}deg)`;
            
            // Обрабатываем действие
            this.handleSwipeAction(currentCard, action);
        }
        
        // Get the current active card
        getCurrentCard() {
            if (this.currentCardIndex < this.cards.length) {
                return this.cards[this.currentCardIndex];
            }
            return null;
        }
        
        // Логика обработки действия свайпа
        handleSwipeAction(card, action) {
            const profileId = card.dataset.profileId;
            debugLog(`Swipe ${action} for profile ${profileId}`);
            
            if (!profileId) {
                debugLog('ERROR: profile ID not found on card element');
                return;
            }
            
            // Remove active class
            card.style.display = 'none';
    
            // Increment current card index
            this.currentCardIndex++;
            
            // Update card stack
            this.updateCardStackAfterSwipe();
            
            // Send API request
            this.sendSwipeRequest(profileId, action);
            
            // Check if we're out of cards
            if (this.currentCardIndex >= this.cards.length) {
                this.showNoMoreProfiles();
            }
        }
        
        // Update card stack after a swipe action
        updateCardStackAfterSwipe() {
            // Update the visible cards
            this.cards.forEach((card, index) => {
                const relativeIndex = index - this.currentCardIndex;
                
                if (relativeIndex === 0) {
                    // Make next card active
                    card.classList.add('active-card');
                    card.style.display = 'block';
                    card.style.zIndex = 10;
                    card.style.transform = '';
                    card.style.opacity = 1;
                } else if (relativeIndex > 0 && relativeIndex < this.maxVisibleCards) {
                    // Position background cards
                    card.style.display = 'block';
                    card.style.zIndex = 10 - relativeIndex;
                    card.style.transform = `scale(${1 - relativeIndex * 0.05}) translateY(${relativeIndex * 10}px)`;
                    card.style.opacity = 1 - relativeIndex * 0.2;
                } else {
                    card.style.display = 'none';
                }
            });
            
            // Update button states
            this.updateButtons();
        }
        
        // Отправка запроса на сервер о свайпе
        async sendSwipeRequest(profileId, action) {
            debugLog(`Sending API request for profile ${profileId}, action: ${action}`);
            
            try {
                const csrfToken = document.querySelector(this.csrfTokenSelector)?.value;
                if (!csrfToken) {
                    console.error('CSRF token not found. Selector:', this.csrfTokenSelector);
                    return;
                }
                
                // Adjust the API endpoint to match your actual backend URL pattern
                // This should match the URL pattern in your Django urls.py
                const apiUrl = `/api/swipe/${profileId}/${action}/`;
                debugLog(`API URL: ${apiUrl}`);
                
                const response = await fetch(apiUrl, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': csrfToken,
                        'Content-Type': 'application/json'
                    }
                });
                
                if (!response.ok) {
                    throw new Error(`HTTP error! Status: ${response.status}`);
                }
                
                const result = await response.json();
                debugLog(`Swipe ${action} successfully recorded:`, result);
                
                // Проверяем на совпадение (match)
                if (result.match) {
                    this.showMatchSuccessModal(result);
                }
            } catch (error) {
                console.error('Error sending swipe action:', error);
            }
        }
        
        // Показать модальное окно при совпадении
        showMatchSuccessModal(matchData) {
            debugLog('Showing match modal with data:', matchData);
            
            const matchModal = document.getElementById('matchSuccessModal');
            if (!matchModal) {
                debugLog('ERROR: Match modal not found');
                return;
            }
            
            // Set the matched user's name
            const nameElement = document.getElementById('matchName');
            if (nameElement && matchData.matched_profile_name) {
                nameElement.textContent = matchData.matched_profile_name;
            }
            
            // Set profile images
            if (matchData.user_profile_image) {
                const userPic = matchModal.querySelector('.user-pic');
                if (userPic) {
                    userPic.style.backgroundImage = `url(${matchData.user_profile_image})`;
                }
            }
            
            if (matchData.matched_profile_image) {
                const matchPic = matchModal.querySelector('.match-pic');
                if (matchPic) {
                    matchPic.style.backgroundImage = `url(${matchData.matched_profile_image})`;
                }
            }
            
            // Configure buttons
            const keepSwipingBtn = document.getElementById('keepSwiping');
            const sendMessageBtn = document.getElementById('sendMessage');
            
            if (keepSwipingBtn) {
                keepSwipingBtn.onclick = () => {
                    matchModal.style.display = 'none';
                };
            }
            
            if (sendMessageBtn && matchData.conversation_id) {
                sendMessageBtn.onclick = () => {
                    window.location.href = `/matches/chat/${matchData.conversation_id}/`;
                };
            }
            
            // Show the modal
            matchModal.style.display = 'flex';
        }
        
        // Сброс позиции карточки после неполного свайпа
        resetCardPosition(card) {
            card.style.transform = '';
        }
        
        // Обновление индикаторов свайпа (LIKE/NOPE)
        updateSwipeIndicators(card, deltaX) {
            const likeIndicator = card.querySelector('.like-indicator');
            const nopeIndicator = card.querySelector('.nope-indicator');
            
            if (!likeIndicator || !nopeIndicator) return;
            
            // Вычисляем прозрачность индикаторов в зависимости от силы свайпа
            const opacity = Math.min(Math.abs(deltaX) / 100, 1);
            
            if (deltaX > 0) {
                likeIndicator.style.opacity = opacity;
                nopeIndicator.style.opacity = 0;
            } else {
                likeIndicator.style.opacity = 0;
                nopeIndicator.style.opacity = opacity;
            }
        }
        
        // Скрытие индикаторов свайпа
        hideSwipeIndicators(card) {
            const likeIndicator = card.querySelector('.like-indicator');
            const nopeIndicator = card.querySelector('.nope-indicator');
            
            if (likeIndicator) likeIndicator.style.opacity = 0;
            if (nopeIndicator) nopeIndicator.style.opacity = 0;
        }
        
        // Показать сообщение об отсутствии профилей
        showNoMoreProfiles() {
            if (!this.swipeContainer) return;
            
            // Проверяем, не отображается ли уже сообщение
            if (!this.swipeContainer.querySelector('.no-profiles')) {
                const noProfilesMessage = document.createElement('div');
                noProfilesMessage.classList.add('no-profiles');
                noProfilesMessage.innerHTML = `
                    <p>Профили закончились</p>
                    <p>Попробуйте изменить параметры поиска или загляните позже</p>
                `;
                
                // Clear out any existing cards
                if (this.cardsContainer) {
                    this.cardsContainer.style.display = 'none';
                }
                
                this.swipeContainer.appendChild(noProfilesMessage);
                
                // Скрываем кнопки управления
                if (this.likeButton && this.likeButton.parentElement) {
                    this.likeButton.parentElement.style.display = 'none';
                }
            }
        }
    }
    
    // Инициализация
    try {
        // Check for required elements before initializing
        const cardsContainer = document.querySelector('.cards-container');
        const likeBtn = document.getElementById('likeBtn');
        const passBtn = document.getElementById('passBtn');
        
        if (!cardsContainer) {
            console.error('Cards container not found. Make sure the selector matches your HTML structure.');
        }
        if (!likeBtn) {
            console.error('Like button not found. Make sure it has id="likeBtn".');
        }
        if (!passBtn) {
            console.error('Pass button not found. Make sure it has id="passBtn".');
        }
        
        if (cardsContainer && likeBtn && passBtn) {
            window.tinderSwipe = new TinderSwipe({
                cardsContainerSelector: '.cards-container',
                likeButtonSelector: '#likeBtn',
                passButtonSelector: '#passBtn',
                swipeContainerSelector: '.swipe-container',
                apiEndpoint: '/api/swipe', // Updated to match your likely API pattern
                threshold: 100,
                rotationAngle: 15,
                animationSpeed: 400,
                maxVisibleCards: 3
            });
            
            debugLog('Tinder-like swipe functionality successfully initialized');
        } else {
            console.error('Failed to initialize TinderSwipe - missing required elements');
        }
    } catch (e) {
        console.error('Error initializing Tinder swipes:', e);
    }
    
    // Обработка модального окна при "совпадении" (match)
    const matchSuccessModal = document.getElementById('matchSuccessModal');
    if (matchSuccessModal) {
        // Set up keep swiping button
        const keepSwipingBtn = document.getElementById('keepSwiping');
        if (keepSwipingBtn) {
            keepSwipingBtn.addEventListener('click', () => {
                matchSuccessModal.style.display = 'none';
            });
        }
        
        // Закрытие при клике вне модального окна
        matchSuccessModal.addEventListener('click', (e) => {
            if (e.target === matchSuccessModal) {
                matchSuccessModal.style.display = 'none';
            }
        });
    } else {
        console.warn('Match success modal not found in DOM');
    }
    
    // Обработка модального окна при "отмене совпадения" (unmatch)
    const unmatchModal = document.getElementById('unmatchModal');
    let userIdToUnmatch = null;
    
    if (unmatchModal) {
        // Initialize unmatch buttons
        document.querySelectorAll('.unmatch-btn').forEach(btn => {
            btn.addEventListener('click', function() {
                userIdToUnmatch = this.dataset.userId;
                unmatchModal.style.display = 'flex';
                console.log(`Unmatch modal shown for user ID: ${userIdToUnmatch}`);
            });
        });
        
        // Handle modal buttons
        const cancelBtn = unmatchModal.querySelector('#cancelUnmatch');
        const confirmBtn = unmatchModal.querySelector('#confirmUnmatch');
        
        if (cancelBtn) {
            cancelBtn.addEventListener('click', () => {
                unmatchModal.style.display = 'none';
                userIdToUnmatch = null;
            });
        }
        
        if (confirmBtn) {
            confirmBtn.addEventListener('click', async () => {
                if (!userIdToUnmatch) return;
                
                try {
                    const response = await fetch(`/api/actions/unmatch/${userIdToUnmatch}/`, {
                        method: 'POST',
                        headers: {
                            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                            'Content-Type': 'application/json'
                        }
                    });
                    
                    if (response.ok) {
                        // Find and remove card from DOM
                        const matchCards = document.querySelectorAll('.match-card');
                        for (const card of matchCards) {
                            if (card.querySelector(`.unmatch-btn[data-user-id="${userIdToUnmatch}"]`)) {
                                card.remove();
                                console.log(`Unmatched profile ${userIdToUnmatch}`);
                                break;
                            }
                        }
                    } else {
                        throw new Error('Failed to unmatch');
                    }
                } catch (error) {
                    console.error('Error unmatching:', error);
                    alert('Failed to unmatch. Please try again.');
                } finally {
                    unmatchModal.style.display = 'none';
                    userIdToUnmatch = null;
                }
            });
        }
        
        // Close when clicking outside modal
        unmatchModal.addEventListener('click', (e) => {
            if (e.target === unmatchModal) {
                unmatchModal.style.display = 'none';
            }
        });
    } else {
        console.warn('Unmatch modal not found in DOM');
    }
});