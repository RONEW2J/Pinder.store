document.addEventListener('DOMContentLoaded', function () {
    const unmatchModal = document.getElementById('unmatchModal');
    const cancelUnmatchButton = document.getElementById('cancelUnmatch');
    const confirmUnmatchButton = document.getElementById('confirmUnmatch');
    const unmatchButtons = document.querySelectorAll('.unmatch-btn');
    let profileIdToUnmatch = null;

    const distanceFilterForm = document.getElementById('distanceFilterForm');
    const radiusSlider = document.getElementById('search_radius_km'); // Assuming this is your range slider
    const radiusDisplay = document.getElementById('radiusValueDisplay'); // Assuming this displays the slider value
    const profilesGrid = document.getElementById('profilesGrid'); // Use ID for more specific targeting

    function getCsrfToken() {
        // A more robust way to get the CSRF token, especially if the input isn't always present
        const csrfInput = document.querySelector('input[name=csrfmiddlewaretoken]');
        if (csrfInput) {
            return csrfInput.value;
        }
        console.warn('CSRF token input not found.');
        return ''; // Fallback or handle error
    }

    unmatchButtons.forEach(button => {
        button.addEventListener('click', function () {
            profileIdToUnmatch = this.dataset.profileId;
            if (unmatchModal) {
                unmatchModal.style.display = 'flex';
            }
        });
    });

    function fetchProfiles(radiusKm = '50') { // Pass radius as an argument, default to 50
        if (!profilesGrid) {
            console.warn('Profiles grid not found on this page.');
            return;
        }
        
        const apiUrl = `/api/profiles/?radius_km=${encodeURIComponent(radiusKm)}`;
        profilesGrid.innerHTML = '<p style="text-align:center; padding: 20px;">Loading profiles...</p>';

        fetch(apiUrl, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                // 'X-CSRFToken': getCsrfToken(), // CSRF token is not needed for GET requests
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
                const fragment = document.createDocumentFragment();
                data.results.forEach(profileData => {
                    const card = createProfileCard(profileData);
                    if (card) {
                        fragment.appendChild(card);
                    }
                });
                profilesGrid.appendChild(fragment);
                // Add event listeners for new like/pass buttons after they are added to the DOM
                setupSwipeActionButtons();
            } else {
                profilesGrid.innerHTML = '<p style="text-align:center; padding: 20px;">No new profiles found matching your criteria. Try expanding your search radius!</p>';
            }
        })
        .catch(error => {
            console.error('Error fetching profiles:', error);
            profilesGrid.innerHTML = '<p style="text-align:center; padding: 20px;">Could not load profiles. Please try again later.</p>';
        });
    }

    function createProfileCard(profile) {
        // Ensure profile.user is an object with expected properties
        const user = profile.user || {}; 
        const profilePhotoUrl = (profile.photos && profile.photos.length > 0 && profile.photos[0].image) 
                                ? profile.photos[0].image 
                                : '/static/images/default_avatar.png'; // Ensure this path is correct
        
        const distanceText = (profile.distance !== null && profile.distance !== undefined)
                           ? `<p class="match-location"><i class="fas fa-map-marker-alt"></i> ~ ${parseFloat(profile.distance).toFixed(1)} km away</p>` 
                           : '';

        const card = document.createElement('div');
        card.className = 'match-card'; // Or your specific class for discovered profiles
        card.innerHTML = `
            <div class="match-photo" style="background-image: url('${profilePhotoUrl}')">
                <div class="match-actions">
                    <button class="btn like-btn" data-user-id="${user.id || profile.user_id}"><i class="fas fa-heart"></i> Like</button>
                    <button class="btn pass-btn" data-user-id="${user.id || profile.user_id}"><i class="fas fa-times"></i> Pass</button>
                </div>
            </div>
            <div class="match-info">
                <h3>${user.first_name || user.username || 'User'}, ${profile.age || 'N/A'}</h3>
                ${distanceText}
            }
        })
        .catch(error => {
            console.error('Error fetching profiles:', error);
            profilesGrid.innerHTML = '<p>Could not load profiles. Please try again later.</p>';
        });
    }
        `;
        return card;
    }

    function setupSwipeActionButtons() {
        document.querySelectorAll('.like-btn, .pass-btn').forEach(button => {
            // Remove existing event listeners to prevent duplicates if this function is called multiple times
            const newButton = button.cloneNode(true);
            button.parentNode.replaceChild(newButton, button);

            newButton.addEventListener('click', function() {
                const userId = this.dataset.userId;
                const action = this.classList.contains('like-btn') ? 'like' : 'pass';
                console.log(`${action} user ${userId}`);
                // TODO: Implement API call for swipe action
                // fetch(`/api/actions/swipe/`, {
                //     method: 'POST',
                //     headers: {
                //         'Content-Type': 'application/json',
                //         'X-CSRFToken': getCsrfToken(),
                //     },
                //     body: JSON.stringify({ target_user_id: userId, action: action })
                // })
                // .then(response => response.json())
                // .then(data => {
                //     console.log('Swipe action response:', data);
                //     if (data.match_status) { // Or however your API indicates a new match
                //         alert("It's a match!");
                //     }
                //     // Remove card from UI
                //     this.closest('.match-card').remove();
                // })
                // .catch(error => console.error('Swipe action error:', error));
            });
        });
    }

    // --- Distance Filter for Profile Discovery (AJAX) ---
    if (radiusSlider && profilesGrid) { // Check for slider specifically
        radiusSlider.addEventListener('input', function() {
            if (radiusDisplay) radiusDisplay.textContent = this.value;
        });
        radiusSlider.addEventListener('change', function() { // 'change' event fires when user releases mouse
            fetchProfiles(this.value);
            // Optional: Update URL query parameter without full reload
            // const currentUrl = new URL(window.location);
            // currentUrl.searchParams.set('radius_km', this.value);
            // window.history.pushState({}, '', currentUrl);
        });
        // Initial fetch on page load using the slider's current value
        fetchProfiles(radiusSlider.value);

    } else if (distanceFilterForm && profilesGrid) { // Fallback for simple form submission
        distanceFilterForm.addEventListener('submit', function(event) {
            event.preventDefault();
            const radiusKmInput = document.getElementById('radius_km'); // Assuming this is the ID of the input field in the form
            const radiusKm = radiusKmInput ? radiusKmInput.value : '50';
            fetchProfiles(radiusKm);
        });
        // Initial fetch for form based
        const initialRadiusInput = document.getElementById('radius_km');
        const initialRadius = initialRadiusInput ? initialRadiusInput.value : '50';
        fetchProfiles(initialRadius);
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
                // Assuming profileIdToUnmatch is the ID of the *other user* or the *match object ID*
                // Adjust endpoint and data based on your API
                fetch(`/api/matches/unmatch/${profileIdToUnmatch}/`, { // Example endpoint
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
                        // This selector might need to be more specific if profileIdToUnmatch is not a user_id
                        const cardToRemove = document.querySelector(`.match-card button[data-user-id="${profileIdToUnmatch}"]`)?.closest('.match-card');
                        if (cardToRemove) cardToRemove.remove();
                        else window.location.reload(); // Fallback to reload if card not found for dynamic removal

                    } else {
                        response.json().then(err => console.error('Unmatch error details:', err)).catch(() => {});
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
    // Initial setup for any swipe buttons already on the page (if any, for existing matches)
    // setupSwipeActionButtons();
});