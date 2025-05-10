document.addEventListener('DOMContentLoaded', function () {
    const unmatchModal = document.getElementById('unmatchModal');
    const cancelUnmatchButton = document.getElementById('cancelUnmatch');
    const confirmUnmatchButton = document.getElementById('confirmUnmatch');
    const unmatchButtons = document.querySelectorAll('.unmatch-btn');
    let profileIdToUnmatch = null;

    function getCsrfToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]').value;
    }

    unmatchButtons.forEach(button => {
        button.addEventListener('click', function () {
            profileIdToUnmatch = this.dataset.profileId;
            if (unmatchModal) {
                unmatchModal.style.display = 'flex';
            }
        });
    });

    if (cancelUnmatchButton) {
        cancelUnmatchButton.addEventListener('click', function () {
            if (unmatchModal) {
                unmatchModal.style.display = 'none';
            }
            profileIdToUnmatch = null;
        });
    }

    if (confirmUnmatchButton) {
        confirmUnmatchButton.addEventListener('click', function () {
            if (profileIdToUnmatch) {
                // IMPORTANT: Replace '/api/actions/unmatch/' with your actual unmatch API endpoint
                fetch(`/api/actions/unmatch/${profileIdToUnmatch}/`, { // Assuming endpoint takes profile_id
                    method: 'POST', // Or DELETE, depending on your API design
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCsrfToken(),
                    },
                    // body: JSON.stringify({ profile_id: profileIdToUnmatch }) // If your API expects a body
                })
                .then(response => {
                    if (response.ok) {
                        // Successfully unmatched, remove the match card from the UI or reload
                        console.log('Successfully unmatched with profile ID:', profileIdToUnmatch);
                        // Example: Remove the card (you'll need to adjust selectors)
                        const cardToRemove = document.querySelector(`.match-card button[data-profile-id="${profileIdToUnmatch}"]`).closest('.match-card');
                        if (cardToRemove) {
                            cardToRemove.remove();
                        }
                        window.location.reload(); // Or dynamically update UI
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

    // Close modal if clicked outside the content
    if (unmatchModal) {
        unmatchModal.addEventListener('click', function(event) {
            if (event.target === unmatchModal) {
                unmatchModal.style.display = 'none';
                profileIdToUnmatch = null;
            }
        });
    }
});