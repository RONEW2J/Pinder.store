document.addEventListener('DOMContentLoaded', function () {
    // Modal elements
    const unmatchModal = document.getElementById('unmatchModal');
    const cancelUnmatchButton = document.getElementById('cancelUnmatch');
    const confirmUnmatchButton = document.getElementById('confirmUnmatch');
    let profileIdToUnmatch = null;

    // Profile discovery and filtering elements
    const discoveryFilterForm = document.getElementById('discoveryFilterForm');
    const citySelect = document.getElementById('city');
    const profilesGrid = document.getElementById('profilesGrid');

    // --- Helper Functions ---
    function getCsrfToken() {
        const csrfInput = document.querySelector('input[name=csrfmiddlewaretoken]');
        if (csrfInput) {
            return csrfInput.value;
        }
        console.warn('CSRF token input not found.');
        return ''; // Fallback or handle error
    }

    function getAuthToken() {
        // Check both localStorage and sessionStorage for token
        return localStorage.getItem('accessToken') || sessionStorage.getItem('accessToken');
    }

    // --- Event Listeners for Unmatch Buttons ---
    document.querySelectorAll('.unmatch-btn').forEach(button => {
        button.addEventListener('click', function () {
            profileIdToUnmatch = this.dataset.profileId;
            if (unmatchModal) {
                unmatchModal.style.display = 'flex';
            }
        });
    });

    // --- Profile Fetching and Display ---
    function fetchProfiles(cityId = '', interestIds = []) {
        if (!profilesGrid) {
            console.warn('Profiles grid not found on this page.');
            return;
        }
        
        profilesGrid.innerHTML = '<p class="loading-message">Loading profiles...</p>';

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

        const token = getAuthToken();
        const headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        };

        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        } else {
            console.warn('No authentication token found for fetching profiles.');
            profilesGrid.innerHTML = '<p class="error-message">Please log in to view profiles.</p>';
            return Promise.reject('Unauthorized');
        }

        fetch(apiUrl, {
            method: 'GET',
            headers: headers
        })
        .then(response => {
            if (response.status === 401) {
                profilesGrid.innerHTML = '<p class="error-message">Session expired. Please log in again.</p>';
                // Consider redirecting to login page
                throw new Error('Unauthorized');
            }
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            profilesGrid.innerHTML = ''; // Clear loading message
            if (data.results && data.results.length > 0) {
                const fragment = document.createDocumentFragment();
                data.results.forEach(profileData => {
                    const card = createProfileCard(profileData);
                    if (card) {
                        fragment.appendChild(card);
                    }
                });
                profilesGrid.appendChild(fragment);
            } else {
                profilesGrid.innerHTML = '<p class="info-message">No profiles found matching your criteria. Try adjusting filters.</p>';
            }
        })
        .catch(error => {
            console.error('Error fetching profiles:', error);
            if (error.message !== 'Unauthorized') {
                profilesGrid.innerHTML = '<p class="error-message">Could not load profiles. Please try again.</p>';
            }
        });
    }

    function createProfileCard(profile) {
        const user = profile.user || {}; 
        const profilePhotoUrl = (profile.photos && profile.photos.length > 0 && profile.photos[0].image) 
                                ? profile.photos[0].image 
                                : '/static/images/default_avatar.png'; 
        
        const cityText = profile.city && profile.city.name
                       ? `<p class="match-location"><i class="fas fa-map-marker-alt"></i> ${profile.city.name}</p>`
                       : '';

        const card = document.createElement('div');
        card.className = 'match-card';
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
                ${profile.bio ? `<p class="match-bio">${profile.bio}</p>` : ''}
            </div>
        `;
        return card;
    }

    // --- Event Delegation for Swipe Actions ---
    if (profilesGrid) {
        profilesGrid.addEventListener('click', function(event) {
            const button = event.target.closest('.like-btn, .pass-btn');
            if (!button) return;

            const userId = button.dataset.userId;
            const action = button.classList.contains('like-btn') ? 'like' : 'pass';
            console.log(`${action} user ${userId}`);

            const token = getAuthToken();
            const headers = {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken()
            };
            
            if (token) {
                headers['Authorization'] = `Bearer ${token}`;
            } else {
                alert('Please log in to perform this action');
                return;
            }

            fetch(`/api/actions/swipe/`, {
                method: 'POST',
                headers: headers,
                body: JSON.stringify({ 
                    target_user_id: userId, 
                    action: action 
                })
            })
            .then(response => {
                if (!response.ok) throw new Error('Action failed');
                return response.json();
            })
            .then(data => {
                if (data.match) {
                    // Show match notification
                    alert(`It's a match with ${data.matched_user_name}!`);
                }
                // Remove the card
                button.closest('.match-card').remove();
            })
            .catch(error => {
                console.error('Swipe action error:', error);
                alert('Action failed. Please try again.');
            });
        });
    }

    // --- Profile Discovery Filters ---
    if (discoveryFilterForm && profilesGrid) {
        discoveryFilterForm.addEventListener('submit', function(event) {
            event.preventDefault();
            
            const selectedCityId = citySelect ? citySelect.value : '';
            const selectedInterestIds = Array.from(discoveryFilterForm.querySelectorAll('input[name="interests"]:checked'))
                                           .map(checkbox => checkbox.value);
            
            fetchProfiles(selectedCityId, selectedInterestIds);

            // Update URL without reload
            const currentUrl = new URL(window.location);
            currentUrl.searchParams.delete('city');
            if (selectedCityId) currentUrl.searchParams.set('city', selectedCityId);
            currentUrl.searchParams.delete('interests');
            selectedInterestIds.forEach(id => currentUrl.searchParams.append('interests', id));
            window.history.pushState({}, '', currentUrl.toString());
        });

        // Initial fetch with URL params
        const initialUrlParams = new URLSearchParams(window.location.search);
        const initialCityId = initialUrlParams.get('city') || '';
        const initialInterestIds = initialUrlParams.getAll('interests') || [];
        fetchProfiles(initialCityId, initialInterestIds);
    }

    // --- Unmatch Modal Logic ---
    if (confirmUnmatchButton) {
        confirmUnmatchButton.addEventListener('click', function () {
            if (!profileIdToUnmatch) return;

            const token = getAuthToken();
            const headers = {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken()
            };
            
            if (token) {
                headers['Authorization'] = `Bearer ${token}`;
            } else {
                alert('Please log in to perform this action');
                return;
            }

            fetch(`/api/matches/unmatch/${profileIdToUnmatch}/`, {
                method: 'POST',
                headers: headers
            })
            .then(response => {
                if (response.ok) {
                    // Remove card or reload
                    const card = document.querySelector(`[data-profile-id="${profileIdToUnmatch}"]`)?.closest('.match-card');
                    if (card) card.remove();
                    else window.location.reload();
                } else {
                    throw new Error('Unmatch failed');
                }
            })
            .catch(error => {
                console.error('Unmatch error:', error);
                alert('Failed to unmatch. Please try again.');
            })
            .finally(() => {
                if (unmatchModal) unmatchModal.style.display = 'none';
                profileIdToUnmatch = null;
            });
        });
    }

    if (cancelUnmatchButton) {
        cancelUnmatchButton.addEventListener('click', function () {
            if (unmatchModal) unmatchModal.style.display = 'none';
            profileIdToUnmatch = null;
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

    // Add CSS for messages
    const style = document.createElement('style');
    style.textContent = `
        .loading-message, .info-message, .error-message { 
            text-align: center; 
            padding: 20px; 
            margin: 20px 0;
        }
        .error-message { color: #dc3545; }
        .info-message { color: #17a2b8; }
    `;
    document.head.appendChild(style);
});