document.addEventListener('DOMContentLoaded', function() {
    // Map initialization
    var map = L.map('map').setView([20.5937, 78.9629], 5);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19
    }).addTo(map);

    // Custom marker icon
    var incidentIcon = L.icon({
        iconUrl: '/static/img/marker.png', // Add a vibrant marker image in static/img/
        iconSize: [38, 45],
        iconAnchor: [19, 45],
        popupAnchor: [0, -40]
    });

    // Fetch and display incidents
    fetch('/api/incidents')
    .then(res => res.json())
    .then(data => {
        data.forEach(inc => {
            var popupContent = `
                <div class="incident-popup">
                    <div class="type">${inc.type}</div>
                    <div class="time">${inc.time}</div>
                    <div class="desc">${inc.description}</div>
                    ${inc.media ? `<img src="/static/uploads/${inc.media}" alt="Incident media">` : ''}
                </div>
            `;
            var marker = L.marker([inc.lat, inc.lng], {icon: incidentIcon}).addTo(map);
            marker.bindPopup(popupContent);
        });
    });
});