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
    let userIdToUnmatch = null;

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
                const response = await fetch(`/api/matches/unmatch/${userIdToUnmatch}/`, {
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
                        console.log(`Unmatched user ${userIdToUnmatch}, card removed.`);
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
});