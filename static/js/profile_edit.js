// In a relevant JS file, e.g., static/js/profile_edit.js
document.addEventListener('DOMContentLoaded', function() {
    const updateLocationButton = document.getElementById('updateLocationBtn');
    const latitudeInput = document.getElementById('id_latitude'); // Assuming your form field ID
    const longitudeInput = document.getElementById('id_longitude'); // Assuming your form field ID

    if (updateLocationButton && navigator.geolocation) {
        updateLocationButton.addEventListener('click', function() {
            navigator.geolocation.getCurrentPosition(function(position) {
                const lat = position.coords.latitude;
                const lon = position.coords.longitude;

                if (latitudeInput && longitudeInput) {
                    latitudeInput.value = lat.toFixed(6);
                    longitudeInput.value = lon.toFixed(6);
                    alert('Location fetched! Save your profile to update.');
                }

                // OR, send directly to the API to update location
                // This would require an API endpoint that accepts PATCH requests to update location
                // For example, your UserProfileDetailView API
                /*
                fetch('/api/profiles/me/', { // Adjust to your API profile update endpoint
                    method: 'PATCH',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCsrfToken(), // You'll need a getCsrfToken function
                    },
                    body: JSON.stringify({
                        location: { type: "Point", coordinates: [lon, lat] }
                    })
                })
                .then(response => response.json())
                .then(data => {
                    console.log('Location updated via API:', data);
                    alert('Location updated successfully!');
                })
                .catch(error => {
                    console.error('Error updating location via API:', error);
                    alert('Could not update location automatically.');
                });
                */

            }, function(error) {
                console.error("Error getting location: ", error);
                alert(`ERROR(${error.code}): ${error.message}`);
            });
        });
    } else if (updateLocationButton) {
        updateLocationButton.textContent = "Geolocation is not supported by this browser.";
        updateLocationButton.disabled = true;
    }
});

// Function to get CSRF token (if not already available)
function getCsrfToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]').value;
}
