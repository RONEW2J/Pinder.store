document.addEventListener('DOMContentLoaded', function () {
    const unmatchModal = document.getElementById('unmatchModal');
    const cancelUnmatchButton = document.getElementById('cancelUnmatch');
    const confirmUnmatchButton = document.getElementById('confirmUnmatch');
    const unmatchButtons = document.querySelectorAll('.unmatch-btn');
    let profileIdToUnmatch = null;

    // Updated filter elements
    const discoveryFilterForm = document.getElementById('discoveryFilterForm'); // The <form> element
    const citySelect = document.getElementById('city'); // The <select> for cities
    // Interest checkboxes will be handled by querying the form
    const profilesGrid = document.getElementById('profilesGrid');

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

    function fetchProfiles(cityId = '', interestIds = []) {
        if (!profilesGrid) {
            console.warn('Profiles grid not found on this page.');
            return;
        }
        
        profilesGrid.innerHTML = '<p style="text-align:center; padding: 20px;">Loading profiles...</p>';

        // Construct API URL with new filters
        const params = new URLSearchParams();
        if (cityId) {
            params.append('city', cityId);
        }
        interestIds.forEach(id => {
            params.append('interests', id);
        });

        const queryString = params.toString();
        const apiUrl = `/api/v1/profiles/all/${queryString ? '?' + queryString : ''}`;
        console.log('Fetching profiles from:', apiUrl);

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
                profilesGrid.innerHTML = '<p style="text-align:center; padding: 20px;">No new profiles found matching your criteria. Try adjusting your filters!</p>';
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
                                : '/static/images/default_avatar.png'; 
        
        const cityText = profile.city && profile.city.name
                       ? `<p class="match-location"><i class="fas fa-map-marker-alt"></i> ${profile.city.name}</p>`
                           : '';

        const card = document.createElement('div');
        card.className = 'match-card'; // Or your specific class for discovered profiles
        card.innerHTML = `
            <div class="match-photo" style="background-image: url('${profilePhotoUrl}')">
                <div class="match-actions">
                    <button class="btn like-btn" data-user-id="${profile.user_id || user.id}"><i class="fas fa-heart"></i> Like</button>
                    <button class="btn pass-btn" data-user-id="${profile.user_id || user.id}"><i class="fas fa-times"></i> Pass</button>
                </div>
            </div>
            <div class="match-info">
                <h3>${user.first_name || user.username || 'User'}, ${profile.age || 'N/A'}</h3>
                ${cityText} 
                <!-- You can add interests here if desired -->
            </div>
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

    // --- Filters for Profile Discovery (AJAX) ---
    if (discoveryFilterForm && profilesGrid) {
        discoveryFilterForm.addEventListener('submit', function(event) {
            event.preventDefault();
            
            const selectedCityId = citySelect ? citySelect.value : '';
            const selectedInterestIds = Array.from(discoveryFilterForm.querySelectorAll('input[name="interests"]:checked'))
                                           .map(checkbox => checkbox.value);
            
            fetchProfiles(selectedCityId, selectedInterestIds);

            // Optional: Update URL query parameters without full page reload
            const currentUrl = new URL(window.location);
            currentUrl.searchParams.delete('city'); // Clear existing
            if (selectedCityId) currentUrl.searchParams.set('city', selectedCityId);
            currentUrl.searchParams.delete('interests'); // Clear existing
            selectedInterestIds.forEach(id => currentUrl.searchParams.append('interests', id));
            window.history.pushState({}, '', currentUrl.toString());
        });

        // Initial fetch on page load using current URL parameters or defaults
        const initialUrlParams = new URLSearchParams(window.location.search);
        const initialCityId = initialUrlParams.get('city') || '';
        const initialInterestIds = initialUrlParams.getAll('interests') || [];
        fetchProfiles(initialCityId, initialInterestIds);
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