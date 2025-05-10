document.addEventListener('DOMContentLoaded', function() {
    const updateLocationButton = document.getElementById('updateLocationBtn');
    // Django form fields are often prefixed with 'id_'
    const latitudeInput = document.getElementById('id_latitude'); 
    const longitudeInput = document.getElementById('id_longitude');

    // Function to get CSRF token (if you decide to send location via API PATCH)
    function getCsrfToken() {
        const csrfInput = document.querySelector('input[name=csrfmiddlewaretoken]');
        return csrfInput ? csrfInput.value : '';
    }

    if (updateLocationButton) {
        if (navigator.geolocation) {
            updateLocationButton.addEventListener('click', function() {
                updateLocationButton.textContent = 'Fetching Location...';
                updateLocationButton.disabled = true;

                navigator.geolocation.getCurrentPosition(
                    function(position) {
                        const lat = position.coords.latitude;
                        const lon = position.coords.longitude;

                        if (latitudeInput) {
                            latitudeInput.value = lat.toFixed(6); // .toFixed(6) for precision
                        }
                        if (longitudeInput) {
                            longitudeInput.value = lon.toFixed(6);
                        }
                        alert('Location fetched! Remember to save your profile to update.');
                        updateLocationButton.textContent = 'Use My Current Location';
                        updateLocationButton.disabled = false;

                        // OPTIONAL: Send directly to API (requires an API endpoint)
                        /* 
                        const profileApiUrl = '/api/profiles/me/'; // Adjust to your API endpoint
                        fetch(profileApiUrl, {
                            method: 'PATCH',
                            headers: {
                                'Content-Type': 'application/json',
                                'X-CSRFToken': getCsrfToken(), 
                            },
                            body: JSON.stringify({
                                location: { type: "Point", coordinates: [lon, lat] } 
                            })
                        })
                        .then(response => {
                            if (!response.ok) {
                                return response.json().then(err => { throw err; });
                            }
                            return response.json();
                        })
                        .then(data => {
                            console.log('Location updated via API:', data);
                            alert('Location updated successfully via API!');
                        })
                        .catch(error => {
                            console.error('Error updating location via API:', error);
                            alert('Could not update location automatically via API. Please save the form manually.');
                        })
                        .finally(() => {
                            updateLocationButton.textContent = 'Use My Current Location';
                            updateLocationButton.disabled = false;
                        });
                        */
                    }, 
                    function(error) {
                        console.error("Error getting location: ", error);
                        let message = `ERROR(${error.code}): ${error.message}`;
                        if (error.code === 1) { // PERMISSION_DENIED
                            message = "You denied access to your location. Please enable it in your browser settings if you want to use this feature.";
                        } else if (error.code === 2) { // POSITION_UNAVAILABLE
                            message = "Location information is unavailable.";
                        } else if (error.code === 3) { // TIMEOUT
                            message = "The request to get user location timed out.";
                        }
                        alert(message);
                        updateLocationButton.textContent = 'Use My Current Location';
                        updateLocationButton.disabled = false;
                    },
                    { // Options for getCurrentPosition
                        enableHighAccuracy: true,
                        timeout: 10000, // 10 seconds
                        maximumAge: 0 // Force fresh location
                    }
                );
            });
        } else {
            updateLocationButton.textContent = "Geolocation not supported";
            updateLocationButton.disabled = true;
            console.warn("Geolocation is not supported by this browser.");
        }
    } else {
        console.warn("Update location button ('updateLocationBtn') not found.");
    }
});

// Function to get CSRF token (if not already available)
function getCsrfToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]').value;
}
