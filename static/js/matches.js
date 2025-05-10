document.addEventListener('DOMContentLoaded', function () {
    const unmatchModal = document.getElementById('unmatchModal');
    const cancelUnmatchButton = document.getElementById('cancelUnmatch');
    const confirmUnmatchButton = document.getElementById('confirmUnmatch');
    const unmatchButtons = document.querySelectorAll('.unmatch-btn');
    let profileIdToUnmatch = null;

    const distanceFilterForm = document.getElementById('distanceFilterForm');
    const profilesGrid = document.querySelector('.matches-grid'); // Assuming this is where profiles are listed

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

     // --- Distance Filter for Profile Discovery (AJAX) ---
    if (distanceFilterForm && profilesGrid) {
        distanceFilterForm.addEventListener('submit', function(event) {
            event.preventDefault(); // Prevent default GET submission
            fetchProfiles();
        });

        // Initial fetch on page load
        fetchProfiles();
    }

    function fetchProfiles() {
        const radiusKmInput = document.getElementById('radius_km');
        const radiusKm = radiusKmInput ? radiusKmInput.value : '50'; // Default if input not found
        
        // Add other filters here if needed (e.g., age, interests from other inputs)
        const apiUrl = `/api/profiles/?radius_km=${encodeURIComponent(radiusKm)}`;

        profilesGrid.innerHTML = '<p>Loading profiles...</p>'; // Show loading state

        fetch(apiUrl, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken(), // May not be needed for GET, but good practice if session is involved
                // Add Authorization header if your API requires it
                // 'Authorization': `Bearer ${your_jwt_token}`
            }
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            profilesGrid.innerHTML = ''; // Clear previous profiles or loading message
            if (data.results && data.results.length > 0) {
                data.results.forEach(profile => {
                    // Assuming 'profile.photos[0].image' gives the primary photo URL
                    // and 'profile.user' is the username string. Adjust based on your ProfileSerializer.
                    const profilePhotoUrl = profile.photos && profile.photos.length > 0 ? profile.photos[0].image : '/static/images/default_avatar.png';
                    const cardHtml = `
                        <div class="match-card">
                            <img src="${profilePhotoUrl}" alt="${profile.user}'s photo">
                            <h3>${profile.user}</h3>
                            <p>Age: ${profile.age || 'N/A'}</p>
                            ${profile.distance ? `<p>Distance: ${parseFloat(profile.distance).toFixed(1)} km</p>` : ''}
                            <div class="match-actions">
                                <button class="btn like-btn" data-profile-id="${profile.user_id}">Like</button> {# Assuming user_id is available for swipe action #}
                                <button class="btn pass-btn" data-profile-id="${profile.user_id}">Pass</button>
                            </div>
                        </div>
                    `;
                    profilesGrid.insertAdjacentHTML('beforeend', cardHtml);
                });
                // Add event listeners for new like/pass buttons here
            } else {
                profilesGrid.innerHTML = '<p>No profiles found matching your criteria. Try expanding your search!</p>';
            }
        })
        .catch(error => {
            console.error('Error fetching profiles:', error);
            profilesGrid.innerHTML = '<p>Could not load profiles. Please try again later.</p>';
        });
    }

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