document.addEventListener('DOMContentLoaded', function() {
    // Debug info
    console.log('Matches page initialized');
    
    // Check authentication
    const isAuthenticated = document.querySelector('.container').dataset.userAuthenticated === 'true';
    if (!isAuthenticated) {
        console.warn('User not authenticated');
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

    // Modal functionality
    const unmatchModal = document.getElementById('unmatchModal');
    const cancelUnmatchBtn = document.getElementById('cancelUnmatch');
    const confirmUnmatchBtn = document.getElementById('confirmUnmatch');
    let userIdToUnmatch = null;

    // Initialize unmatch buttons
    document.querySelectorAll('.unmatch-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            userIdToUnmatch = this.dataset.userId;
            if (unmatchModal) unmatchModal.style.display = 'flex';
        });
    });

    // Modal event listeners
    if (cancelUnmatchBtn) {
        cancelUnmatchBtn.addEventListener('click', () => {
            if (unmatchModal) unmatchModal.style.display = 'none';
        });
    }

    if (confirmUnmatchBtn) {
        confirmUnmatchBtn.addEventListener('click', async () => {
            if (!userIdToUnmatch) return;
            
            try {
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
                    if (card) card.remove();
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

    // Filter form submission
    const filterForm = document.getElementById('discoveryFilterForm');
    if (filterForm) {
        filterForm.addEventListener('submit', function(e) {
            e.preventDefault();
            // Add any filter logic here if needed
            this.submit();
        });
    }
});