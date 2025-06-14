// Initialize map
let map = L.map('map').setView([0, 0], 13);
let markers = L.layerGroup().addTo(map);
let heatmapLayer = null;
let isHeatmapEnabled = false;
let showOnlyVerified = false;

// Custom marker icon for incidents
const incidentIcon = L.icon({
    iconUrl: '/static/img/marker.png.png',
    iconSize: [38, 45], // adjust as needed
    iconAnchor: [19, 45],
    popupAnchor: [0, -40]
});

// Add tile layer
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap contributors'
}).addTo(map);

// Get user's location
if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(
        position => {
            const { latitude, longitude } = position.coords;
            map.setView([latitude, longitude], 13);
            L.marker([latitude, longitude])
                .addTo(map)
                .bindPopup('Your Location')
                .openPopup();
        },
        error => {
            console.error('Error getting location:', error);
        }
    );
}

// Add a toggle button for verified incidents (add this to the DOM if not present)
window.addEventListener('DOMContentLoaded', () => {
    if (!document.getElementById('toggleVerified')) {
        const btn = document.createElement('button');
        btn.id = 'toggleVerified';
        btn.className = 'btn btn-sm btn-outline-primary';
        btn.style.position = 'fixed';
        btn.style.top = '7rem';
        btn.style.right = '2rem';
        btn.style.zIndex = 1001;
        btn.innerHTML = '<i class="bi bi-patch-check"></i> Verified Only';
        document.body.appendChild(btn);
    }
    document.getElementById('toggleVerified').addEventListener('click', function() {
        showOnlyVerified = !showOnlyVerified;
        this.classList.toggle('active', showOnlyVerified);
        fetchIncidents();
    });
});

// Fetch and display incidents
async function fetchIncidents() {
    try {
        const response = await fetch('/api/incidents');
        let incidents = await response.json();
        // Filter for verified if toggle is on
        if (showOnlyVerified) {
            incidents = incidents.filter(i => i.verified);
        }
        
        // Clear existing markers
        markers.clearLayers();
        
        // Create heatmap data
        const heatmapData = incidents.map(incident => [
            incident.latitude || incident.lat,
            incident.longitude || incident.lng,
            1 // intensity
        ]);
        
        // Update heatmap if enabled
        if (isHeatmapEnabled) {
            if (heatmapLayer) {
                map.removeLayer(heatmapLayer);
            }
            heatmapLayer = L.heatLayer(heatmapData, {
                radius: 25,
                blur: 15,
                maxZoom: 10
            }).addTo(map);
        }
        
        // Add markers with custom icon
        incidents.forEach(incident => {
            const marker = L.marker([
                incident.latitude || incident.lat,
                incident.longitude || incident.lng
            ], { icon: incidentIcon })
                .bindPopup(createPopupContent(incident));
            markers.addLayer(marker);
        });
        
        // Update recent incidents list
        updateRecentIncidents(incidents);
    } catch (error) {
        console.error('Error fetching incidents:', error);
    }
}

// Create popup content
function createPopupContent(incident) {
    return `
        <div class="incident-popup">
            <div class="type">${incident.type}</div>
            <div class="time">${new Date(incident.timestamp).toLocaleString()}</div>
            <div class="desc">${incident.description}</div>
            ${incident.image_url ? `<img src="${incident.image_url}" alt="Incident Image">` : ''}
        </div>
    `;
}

// Update recent incidents list
function updateRecentIncidents(incidents) {
    const recentIncidentsContainer = document.getElementById('recentIncidents');
    recentIncidentsContainer.innerHTML = '';
    
    // Sort incidents by timestamp (most recent first)
    const sortedIncidents = [...incidents].sort((a, b) => 
        new Date(b.timestamp) - new Date(a.timestamp)
    );
    
    // Display only the 5 most recent incidents
    sortedIncidents.slice(0, 5).forEach(incident => {
        const incidentElement = document.createElement('a');
        incidentElement.href = '#';
        incidentElement.className = 'list-group-item list-group-item-action';
        incidentElement.innerHTML = `
            <div class="d-flex w-100 justify-content-between">
                <h6 class="mb-1">${incident.type}</h6>
                <small>${new Date(incident.timestamp).toLocaleDateString()}</small>
            </div>
            <p class="mb-1">${incident.description.substring(0, 100)}${incident.description.length > 100 ? '...' : ''}</p>
        `;
        
        // Add click event to center map on incident
        incidentElement.addEventListener('click', (e) => {
            e.preventDefault();
            map.setView([incident.latitude, incident.longitude], 15);
            markers.getLayers().find(m => 
                m.getLatLng().lat === incident.latitude && 
                m.getLatLng().lng === incident.longitude
            )?.openPopup();
        });
        
        recentIncidentsContainer.appendChild(incidentElement);
    });
}

// Toggle heatmap
document.getElementById('toggleHeatmap').addEventListener('click', function() {
    isHeatmapEnabled = !isHeatmapEnabled;
    this.classList.toggle('active');
    fetchIncidents(); // Refresh incidents to update heatmap
});

// Refresh map
document.getElementById('refreshMap').addEventListener('click', function() {
    this.classList.add('rotate');
    fetchIncidents();
    setTimeout(() => this.classList.remove('rotate'), 1000);
});

// Initial fetch
fetchIncidents();

// Refresh incidents every 5 minutes
setInterval(fetchIncidents, 5 * 60 * 1000);
