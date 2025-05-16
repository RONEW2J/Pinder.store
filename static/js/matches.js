document.addEventListener('DOMContentLoaded', function() {
    // Debug info
    console.log('Matches page initialized');

    // Check authentication
    const container = document.querySelector('.container');
    const isAuthenticated = container && container.dataset.userAuthenticated === 'true';

    if (!isAuthenticated) {
        console.warn('User not authenticated or container not found.');
        return;
    }

    // Debug: Log all match cards
    const matchCards = document.querySelectorAll('.match-card');
    console.log(`Found ${matchCards.length} match cards`);
    matchCards.forEach(card => {
        console.log('Match card:', {
            id: card.dataset.profileId,
            visible: card.offsetParent !== null
        });
    });

    // --- Existing Unmatch Modal functionality ---
    const unmatchModal = document.getElementById('unmatchModal');
    const cancelUnmatchBtn = document.getElementById('cancelUnmatch');
    const confirmUnmatchBtn = document.getElementById('confirmUnmatch');
    userIdToUnmatch = this.dataset.profileId; // Rename variable for clarity if you prefer, e.g., profileIdToUnmatch

    // Initialize unmatch buttons
    document.querySelectorAll('.unmatch-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            userIdToUnmatch = this.dataset.userId;
            if (unmatchModal) {
                unmatchModal.style.display = 'flex';
            }
        });
    });

    // Modal event listeners
    if (cancelUnmatchBtn) {
        cancelUnmatchBtn.addEventListener('click', () => {
            if (unmatchModal) unmatchModal.style.display = 'none';
            userIdToUnmatch = null; // Reset on cancel
        });
    }

    if (confirmUnmatchBtn) {
        confirmUnmatchBtn.addEventListener('click', async () => {
            if (!userIdToUnmatch) return;

            try {
                // Ensure CSRF token is available
                const response = await fetch(`/api/actions/unmatch/${userIdToUnmatch}/`, { // Change the URL part if you renamed userIdToUnmatch
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                        'Content-Type': 'application/json'
                    }
                });

                if (response.ok) {
                    // Remove the match card
                    const card = document.querySelector(`.match-card[data-profile-id="${userIdToUnmatch}"]`);
                    if (card) {
                        card.remove();
                        console.log(`Unmatched profile ${userIdToUnmatch}, card removed.`);
                    }
                } else {
                    throw new Error('Unmatch failed');
                }
            } catch (error) {
                console.error('Unmatch error:', error);
                alert('Failed to unmatch. Please try again.');
            } finally {
                if (unmatchModal) unmatchModal.style.display = 'none';
                userIdToUnmatch = null;
            }
        });
    }

    // Close modal when clicking outside
    if (unmatchModal) {
        unmatchModal.addEventListener('click', (e) => {
            if (e.target === unmatchModal) {
                unmatchModal.style.display = 'none';
            }
        });
    }

    // --- Existing Filter form submission ---
    const filterForm = document.getElementById('discoveryFilterForm');
    if (filterForm) {
        filterForm.addEventListener('submit', function(e) {
            e.preventDefault();
            // Add any filter logic here if needed
            this.submit();
        });
    }

    // --- New Slideshow Functionality for Discovery Profiles ---
    const slideshowContainer = document.getElementById('profilesSlideshow');
    if (slideshowContainer) {
        const slides = slideshowContainer.querySelectorAll('.discovery-slide');
        const prevButton = document.getElementById('prevProfile');
        const nextButton = document.getElementById('nextProfile');
        let currentSlideIndex = 0;

        function showSlide(index) {
            slides.forEach((slide, i) => {
                slide.classList.remove('active');
                slide.style.display = 'none'; // Ensure only active is block
                if (i === index) {
                    slide.classList.add('active');
                    slide.style.display = 'block';
                }
            });
        }

        function updateButtonStates() {
            if (!prevButton || !nextButton) return;
            // Optional: Disable prev/next if at start/end and not looping
            // prevButton.disabled = currentSlideIndex === 0;
            // nextButton.disabled = currentSlideIndex === slides.length - 1;
        }

        if (slides.length > 0) {
            showSlide(currentSlideIndex);
            updateButtonStates();
        } else {
            // Hide controls if no discovery profiles
            if (prevButton) prevButton.style.display = 'none';
            if (nextButton) nextButton.style.display = 'none';
            console.log('No discovery slides found.');
        }

        if (prevButton) {
            prevButton.addEventListener('click', () => {
                if (slides.length === 0) return;
                currentSlideIndex = (currentSlideIndex > 0) ? currentSlideIndex - 1 : slides.length - 1; // Loop to end
                showSlide(currentSlideIndex);
                updateButtonStates();
            });
        }

        if (nextButton) {
            nextButton.addEventListener('click', () => {
                if (slides.length === 0) return;
                currentSlideIndex = (currentSlideIndex < slides.length - 1) ? currentSlideIndex + 1 : 0; // Loop to start
                showSlide(currentSlideIndex);
                updateButtonStates();
            });
        }

        // Event listeners for Like/Pass buttons within the slideshow
        slideshowContainer.addEventListener('click', async (event) => {
            const likeButton = event.target.closest('.like-btn');
            const passButton = event.target.closest('.pass-btn');
            const targetUserId = likeButton?.dataset.userId || passButton?.dataset.userId;

            if (!targetUserId) return;

            let action = '';
            if (likeButton) action = 'like';
            if (passButton) action = 'pass';

            if (action) {
                console.log(`Discovery Action: ${action}, User ID: ${targetUserId}`);
                // TODO: Implement API call to record the swipe/action for discovery profiles
                // This would be different from unmatching.
                // Example:
                // try {
                //     const response = await fetch(`/api/actions/swipe/`, { /* ... API call details ... */ });
                //     const result = await response.json();
                //     if (response.ok) {
                //         console.log(`Discovery swipe ${action} successful:`, result);
                //         // Remove the current slide and advance
                //         const currentSlideElement = slides[currentSlideIndex];
                //         currentSlideElement.remove(); // Or hide and mark as swiped
                //         // Re-evaluate slides NodeList or manage an array of active slides
                //         // Then call nextButton.click() or similar logic to advance
                //     } else { /* ... error handling ... */ }
                // } catch (error) { /* ... error handling ... */ }

                // For now, as a placeholder, just advance to the next slide after an action
                // This is a simplified advancement and doesn't handle removing the swiped card yet.
                // Proper implementation would remove the card and then decide the next index.
                if (nextButton) {
                    nextButton.click();
                }
            }
        });
    } else {
        console.log('Slideshow container (#profilesSlideshow) not found.');
    }
    
    const slides = document.querySelectorAll('.discovery-slide');
    const prevBtn = document.getElementById('prevProfile');
    const nextBtn = document.getElementById('nextProfile');
    let currentIndex = 0;

    function showSlide(index) {
        slides.forEach((slide, i) => {
            slide.style.display = i === index ? 'block' : 'none';
        });
    }

    if (slides.length > 0) {
        showSlide(0);
        
        if (nextBtn) {
            nextBtn.addEventListener('click', () => {
                currentIndex = (currentIndex + 1) % slides.length;
                showSlide(currentIndex);
            });
        }
        
        if (prevBtn) {
            prevBtn.addEventListener('click', () => {
                currentIndex = (currentIndex - 1 + slides.length) % slides.length;
                showSlide(currentIndex);
            });
        }
    } else {
        if (prevBtn) prevBtn.style.display = 'none';
        if (nextBtn) nextBtn.style.display = 'none';
    }

    const cardsContainer = document.querySelector('.cards-container');
    if (cardsContainer) {
        let currentCard = cardsContainer.querySelector('.swipe-card:last-child'); // Начинаем с верхней карточки (последней в DOM по вашей верстке)
        let nextCard = currentCard ? currentCard.previousElementSibling : null;

        function initSwipeCards() {
            const swipeCards = document.querySelectorAll('.swipe-card');
            swipeCards.forEach((card, index) => {
                // Показываем только несколько верхних карт для стека
                if (index < swipeCards.length - 3) { // Показываем 3 карты, остальные скрыты
                    card.style.display = 'none';
                } else {
                    card.style.zIndex = swipeCards.length - index;
                    card.style.transform = `scale(<span class="math-inline">\{1 \- \(swipeCards\.length \- 1 \- index\) \* 0\.05\}\) translateY\(</span>{(swipeCards.length - 1 - index) * 10}px)`;
                    card.style.opacity = 1 - (swipeCards.length - 1 - index) * 0.1;
                }

                const hammer = new Hammer(card);
                hammer.on('panstart', () => {
                    card.classList.add('dragging');
                });

                hammer.on('panmove', (ev) => {
                    if (ev.deltaX === 0) return;
                    if (ev.center.x === 0 && ev.center.y === 0) return;

                    card.style.transition = 'none'; // Убираем анимацию во время перетаскивания
                    const xMulti = ev.deltaX / 10; // Коэффициент поворота
                    const yMulti = ev.deltaY / 80; // Меньшее влияние на Y
                    const rotate = xMulti * yMulti;

                    card.style.transform = `translate(${ev.deltaX}px, <span class="math-inline">\{ev\.deltaY\}px\) rotate\(</span>{rotate}deg)`;

                    // Показываем индикаторы лайка/дизлайка
                    if (ev.deltaX > 0) {
                        card.querySelector('.like-indicator')?.style.opacity = Math.abs(ev.deltaX) / card.offsetWidth * 2;
                        card.querySelector('.nope-indicator')?.style.opacity = 0;
                    } else {
                        card.querySelector('.nope-indicator')?.style.opacity = Math.abs(ev.deltaX) / card.offsetWidth * 2;
                        card.querySelector('.like-indicator')?.style.opacity = 0;
                    }
                });

                hammer.on('panend', (ev) => {
                    card.classList.remove('dragging');
                    card.style.transition = 'transform 0.5s ease-out, opacity 0.5s ease-out'; // Возвращаем плавную анимацию

                    const moveOutWidth = document.body.clientWidth;
                    const keep = Math.abs(ev.deltaX) < 80 || Math.abs(ev.velocityX) < 0.3;

                    if (keep) {
                        card.style.transform = `scale(<span class="math-inline">\{1 \- \(swipeCards\.length \- 1 \- index\) \* 0\.05\}\) translateY\(</span>{(swipeCards.length - 1 - index) * 10}px)`;
                        card.querySelector('.like-indicator')?.style.opacity = 0;
                        card.querySelector('.nope-indicator')?.style.opacity = 0;
                    } else {
                        const endX = Math.max(Math.abs(ev.velocityX) * moveOutWidth, moveOutWidth);
                        const toX = ev.deltaX > 0 ? endX : -endX;
                        const endY = Math.abs(ev.velocityY) * moveOutWidth;
                        const toY = ev.deltaY > 0 ? endY : -endY;
                        const xMulti = ev.deltaX / 80;
                        const yMulti = ev.deltaY / 100;
                        const rotate = xMulti * yMulti;

                        card.style.transform = `translate(${toX}px, <span class="math-inline">\{toY \+ ev\.deltaY\}px\) rotate\(</span>{rotate}deg)`;
                        card.style.opacity = 0;

                        const action = ev.deltaX > 0 ? 'like' : 'pass';
                        handleSwipeAction(card.dataset.profileId, action);
                        removeCardFromStack(card);
                    }
                });
            });
        }

        function removeCardFromStack(cardElement) {
            setTimeout(() => {
                cardElement.remove();
                updateCardStackVisuals();
                if (document.querySelectorAll('.swipe-card').length === 0) {
                    showNoMoreProfilesMessage();
                }
            }, 500); // Должно совпадать с длительностью анимации улетания
        }

        function updateCardStackVisuals() {
            const remainingCards = document.querySelectorAll('.swipe-card');
            remainingCards.forEach((card, index) => {
                // Обновляем стили для оставшихся карточек, чтобы создать эффект стека
                // Индексы идут от самой нижней к самой верхней
                const reversedIndex = remainingCards.length - 1 - index; // Индекс от верха (0 - верхняя)
                card.style.zIndex = remainingCards.length - reversedIndex;
                card.style.transform = `scale(<span class="math-inline">\{1 \- reversedIndex \* 0\.05\}\) translateY\(</span>{reversedIndex * 10}px)`;
                card.style.opacity = 1 - reversedIndex * 0.1;
                if (reversedIndex >= 3) { // Скрываем карты глубже 3-й
                    card.style.opacity = 0;
                    card.style.display = 'none';
                } else {
                    card.style.display = 'block';
                }
            });
        }

        function showNoMoreProfilesMessage() {
            const swipeContainer = document.querySelector('.swipe-container');
            if (swipeContainer && !document.querySelector('.no-profiles')) {
                const noProfilesMessage = document.createElement('div');
                noProfilesMessage.classList.add('no-profiles');
                noProfilesMessage.innerHTML = '<p>No new profiles to discover right now. Try adjusting your filters or check back later!</p>';
                swipeContainer.appendChild(noProfilesMessage);
                document.querySelector('.swipe-buttons').style.display = 'none';
            }
        }

        async function handleSwipeAction(profileId, action) {
            console.log(`Swiped ${action} on profile ${profileId}`);
            // TODO: Implement API call to record the swipe/action for discovery profiles
            try {
                const response = await fetch(`/api/swipe/<span class="math-inline">\{profileId\}/</span>{action}/`, { // Пример URL
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                        'Content-Type': 'application/json'
                    },
                });
                const result = await response.json();
                if (response.ok) {
                    console.log(`Swipe ${action} successful:`, result);
                    if (result.match) {
                        // Показать Match Success Modal
                        showMatchSuccessModal(result.user_profile_image, result.matched_profile_image, result.matched_profile_name);
                    }
                } else {
                    console.error('Swipe action failed:', result);
                    // Возможно, вернуть карточку или показать ошибку
                }
            } catch (error) {
                console.error('Error during swipe action:', error);
            }
        }

        // Кнопки Like/Pass
        const likeBtn = document.getElementById('likeBtn');
        const passBtn = document.getElementById('passBtn');

        if (likeBtn) {
            likeBtn.addEventListener('click', () => {
                const currentCard = document.querySelector('.swipe-card:last-child'); // Верхняя карта
                if (currentCard) {
                    currentCard.classList.add('swiping-right');
                    handleSwipeAction(currentCard.dataset.profileId, 'like');
                    removeCardFromStack(currentCard);
                }
            });
        }
        if (passBtn) {
            passBtn.addEventListener('click', () => {
                 const currentCard = document.querySelector('.swipe-card:last-child'); // Верхняя карта
                if (currentCard) {
                    currentCard.classList.add('swiping-left');
                    handleSwipeAction(currentCard.dataset.profileId, 'pass');
                    removeCardFromStack(currentCard);
                }
            });
        }

        // Инициализация при загрузке
        if (document.querySelectorAll('.swipe-card').length > 0) {
            initSwipeCards();
            updateCardStackVisuals(); // Для корректного начального отображения
        } else {
            showNoMoreProfilesMessage();
        }
    }
});