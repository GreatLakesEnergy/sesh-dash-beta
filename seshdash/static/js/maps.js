L.mapbox.accessToken = 'pk.eyJ1IjoiYXRpbGV2IiwiYSI6IjYxNDcxZWM4ZjE1NDYzYzgzNjU0OTEzYjI4NDI1YzRiIn0.zqkFtrbhpNbeTNiIqTxBZQ';

var lat = site[0]['fields']['latitude']; 
var lon = site[0]['fields']['longitude'];
var map = L.mapbox.map('map', 'mapbox.streets')
    .setView([lat, lon], 9);

// L.marker is a low-level marker constructor in Leaflet.
L.marker([lat, lon], {
    icon: L.mapbox.marker.icon({
        'marker-size': 'medium',
        'marker-symbol': 'building',
        'marker-color': '#1087bf'
    })
}).addTo(map);


