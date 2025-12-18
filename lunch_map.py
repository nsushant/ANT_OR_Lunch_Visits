#!/usr/bin/env python3
"""
Lunch Locations Map Visualizer
Creates an interactive map showing lunch locations from markdown files
"""

import re
import json
import requests
from typing import Dict, List, Tuple, Optional

class LocationData:
    def __init__(self):
        self.places = []
        self.lunch_log = []
        
    def parse_places_md(self, content: str) -> List[Dict]:
        """Parse places.md to extract location information"""
        places = []
        current_place = {}
        
        for line in content.split('\n'):
            line = line.strip()
            
            if line.startswith('- Name:'):
                if current_place:
                    places.append(current_place)
                current_place = {'name': line.split(':', 1)[1].strip()}
            elif line.startswith('- Location:'):
                current_place['address'] = line.split(':', 1)[1].strip()
            elif line.startswith('- Cuisine:'):
                current_place['cuisine'] = line.split(':', 1)[1].strip()
            elif line.startswith('- Price range:'):
                current_place['price_range'] = line.split(':', 1)[1].strip()
            elif line.startswith('- Note:'):
                current_place['note'] = line.split(':', 1)[1].strip()
                
        if current_place:
            places.append(current_place)
            
        return places
    
    def parse_lunch_log_md(self, content: str) -> List[Dict]:
        """Parse lunch_log.md to extract visited locations"""
        lunch_entries = []
        
        # Find all date entries
        date_pattern = r'### (\d{4}-\d{2}-\d{2}) — (.+)'
        location_pattern = r'- \*\*Location:\*\* (.+)'
        
        dates = re.findall(date_pattern, content)
        
        for date_str, place_name in dates:
            entry = {
                'date': date_str,
                'name': place_name.strip(),
                'visited': True
            }
            
            # Extract location info
            location_match = re.search(r'### ' + re.escape(date_str) + ' — ' + re.escape(place_name) + r'.*?\n- \*\*Location:\*\* (.+)', content, re.DOTALL)
            if location_match:
                entry['location_description'] = location_match.group(1).strip()
                
            lunch_entries.append(entry)
            
        return lunch_entries
    
    def geocode_address(self, address: str) -> Optional[Tuple[float, float]]:
        """Geocode address using Nominatim (OpenStreetMap)"""
        try:
            # Add Antwerpen, Belgium if not specified
            if "Antwerpen" not in address and "Belgium" not in address:
                full_address = f"{address}, Antwerpen, Belgium"
            else:
                full_address = address
                
            url = f"https://nominatim.openstreetmap.org/search"
            params = {
                'q': full_address,
                'format': 'json',
                'limit': 1,
                'addressdetails': 1
            }
            headers = {
                'User-Agent': 'LunchMap/1.0 (educational purpose)'
            }
            
            response = requests.get(url, params=params, headers=headers, timeout=20)
            response.raise_for_status()
            
            data = response.json()
            if data and len(data) > 0:
                lat = float(data[0]['lat'])
                lon = float(data[0]['lon'])
                return (lat, lon)
                
        except Exception as e:
            print(f"Geocoding failed for '{address}': {e}")
            
        return None
    
    def load_data(self):
        """Load and parse data from markdown files"""
        try:
            with open('places.md', 'r', encoding='utf-8') as f:
                places_content = f.read()
                self.places = self.parse_places_md(places_content)
                
            with open('lunch_log.md', 'r', encoding='utf-8') as f:
                lunch_content = f.read()
                self.lunch_log = self.parse_lunch_log_md(lunch_content)
                
        except FileNotFoundError as e:
            print(f"Error: {e}")
            return False
            
        return True
    
    def geocode_all_locations(self):
        """Geocode all addresses"""
        # Predefined coordinates for known Antwerp locations
        antwerp_coords = {
            'Munji': (51.2214, 4.4010),
            'Tjoung Tjoung': (51.2170, 4.4210),
            'Koffie Dealers': (51.2180, 4.4010),
            'Phiin Cà Phê': (51.2190, 4.4000),
            'Arepa culture Antwerpen 🇻🇪': (51.2150, 4.4050),
            'Afghan Darbar Restaurant': (51.2100, 4.4200),
            'Ovanos': (51.2080, 4.4250)
        }
        
        # Geocode places
        for place in self.places:
            if place['name'] in antwerp_coords:
                place['coordinates'] = antwerp_coords[place['name']]
                print(f"Using predefined coordinates for: {place['name']}")
            elif 'address' in place:
                coords = self.geocode_address(place['address'])
                if coords:
                    place['coordinates'] = coords
                else:
                    print(f"Failed to geocode: {place['name']} - {place['address']}")
        
        # Mark visited places
        visited_names = {entry['name'] for entry in self.lunch_log}
        for place in self.places:
            place['visited'] = place['name'] in visited_names
    
    def generate_map_html(self) -> str:
        """Generate HTML for interactive map"""
        html_template = """
<!DOCTYPE html>
<html>
<head>
    <title>Lunch Locations Map</title>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <script src="https://unpkg.com/leaflet-routing-machine@3.2.12/dist/leaflet-routing-machine.js"></script>
    <link rel="stylesheet" href="https://unpkg.com/leaflet-routing-machine@3.2.12/dist/leaflet-routing-machine.css" />
    
    <style>
        body { margin: 0; padding: 0; font-family: Arial, sans-serif; }
        #map { height: 100vh; width: 100%; }
        .info-panel {
            position: absolute;
            top: 10px;
            right: 10px;
            background: white;
            padding: 10px;
            border-radius: 5px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.3);
            z-index: 1000;
            max-width: 250px;
        }
        .travel-info {
            position: absolute;
            bottom: 20px;
            left: 20px;
            background: white;
            padding: 10px;
            border-radius: 5px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.3);
            z-index: 1000;
            display: none;
        }
        .selection-panel {
            position: absolute;
            bottom: 20px;
            left: 20px;
            background: white;
            padding: 10px;
            border-radius: 5px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.3);
            z-index: 1000;
            max-width: 250px;
        }
    </style>
</head>
<body>
    <div id="map"></div>
    
    <div class="info-panel">
        <h3>Lunch Locations Map</h3>
        <p><span style="color: green;">●</span> Visited locations</p>
        <p><span style="color: blue;">●</span> All other places</p>
        <p><span style="color: red;">●</span> University of Antwerp</p>
    </div>
    
    <div class="selection-panel">
        <p><strong>Click two markers to see travel time</strong></p>
        <button onclick="clearSelection()">Clear Selection</button>
    </div>
    
    <div class="travel-info" id="travelInfo" style="bottom: 120px;">
        <h4>Travel Information</h4>
        <div id="travelDetails"></div>
    </div>

    <script>
        // Initialize map
        const map = L.map('map').setView([51.2054, 4.4132], 13); // Center on Antwerp
        
        // Add tile layer
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors'
        }).addTo(map);
        
        // Location data
        const locations = {locations_data};
        
        // Selected markers for routing
        let selectedMarkers = [];
        let routingControl = null;
        
        // Create custom icons
        const visitedIcon = L.divIcon({
            html: '<div style="background: green; width: 12px; height: 12px; border-radius: 50%; border: 2px solid white; box-shadow: 0 2px 4px rgba(0,0,0,0.3);"></div>',
            iconSize: [16, 16],
            className: 'custom-marker'
        });
        
        const placeIcon = L.divIcon({
            html: '<div style="background: blue; width: 12px; height: 12px; border-radius: 50%; border: 2px solid white; box-shadow: 0 2px 4px rgba(0,0,0,0.3);"></div>',
            iconSize: [16, 16],
            className: 'custom-marker'
        });
        
        const universityIcon = L.divIcon({
            html: '<div style="background: red; width: 12px; height: 12px; border-radius: 50%; border: 2px solid white; box-shadow: 0 2px 4px rgba(0,0,0,0.3);"></div>',
            iconSize: [16, 16],
            className: 'custom-marker'
        });
        
        // Add markers
        locations.forEach(function(location) {
            const icon = location.visited ? visitedIcon : placeIcon;
            
            const marker = L.marker([location.coordinates[0], location.coordinates[1]], {icon: icon})
                .addTo(map);
            
            let popupContent = `<strong>${location.name}</strong><br>`;
            if (location.address) popupContent += `Address: ${location.address}<br>`;
            if (location.cuisine) popupContent += `Cuisine: ${location.cuisine}<br>`;
            if (location.price_range) popupContent += `Price: ${location.price_range}<br>`;
            if (location.visited) popupContent += `<span style="color: green;">✓ Visited</span><br>`;
            if (location.note) popupContent += `Note: ${location.note}`;
            
            marker.bindPopup(popupContent);
            
            // Add click handler for routing
            marker.on('click', function() {
                handleMarkerClick(location, marker);
            });
        });
        
        // Add University of Antwerp marker
        const universityMarker = L.marker([51.2054, 4.4132], {icon: universityIcon})
            .addTo(map)
            .bindPopup('<strong>University of Antwerp</strong><br>Reference Location');
        
        universityMarker.on('click', function() {
            handleMarkerClick({
                name: 'University of Antwerp',
                coordinates: [51.2054, 4.4132]
            }, universityMarker);
        });
        
        function handleMarkerClick(location, marker) {
            if (selectedMarkers.length >= 2) {
                clearSelection();
            }
            
            selectedMarkers.push({
                location: location,
                marker: marker
            });
            
            // Highlight selected marker
            marker._icon.style.border = '3px solid yellow';
            marker._icon.style.width = '16px';
            marker._icon.style.height = '16px';
            
            if (selectedMarkers.length === 2) {
                calculateRoute();
            }
        }
        
        function calculateRoute() {
            if (selectedMarkers.length !== 2) return;
            
            const start = selectedMarkers[0].location.coordinates;
            const end = selectedMarkers[1].location.coordinates;
            
            // Remove existing route
            if (routingControl) {
                map.removeControl(routingControl);
            }
            
            // Add routing control
            routingControl = L.Routing.control({
                waypoints: [
                    L.latLng(start[0], start[1]),
                    L.latLng(end[0], end[1])
                ],
                routeWhileDragging: false,
                addWaypoints: false,
                createMarker: function() { return null; }, // Don't create additional markers
                lineOptions: {
                    styles: [{color: 'red', weight: 4, opacity: 0.7}]
                }
            }).on('routesfound', function(e) {
                const routes = e.routes;
                const summary = routes[0].summary;
                
                // Display travel information
                const travelInfo = document.getElementById('travelInfo');
                const travelDetails = document.getElementById('travelDetails');
                
                travelDetails.innerHTML = `
                    <strong>From:</strong> ${selectedMarkers[0].location.name}<br>
                    <strong>To:</strong> ${selectedMarkers[1].location.name}<br>
                    <strong>Distance:</strong> ${(summary.totalDistance / 1000).toFixed(2)} km<br>
                    <strong>Travel Time:</strong> ${Math.round(summary.totalTime / 60)} minutes
                `;
                
                travelInfo.style.display = 'block';
            }).addTo(map);
        }
        
        function clearSelection() {
            // Reset marker styles
            selectedMarkers.forEach(function(item) {
                item.marker._icon.style.border = '2px solid white';
                item.marker._icon.style.width = '12px';
                item.marker._icon.style.height = '12px';
            });
            
            selectedMarkers = [];
            
            // Remove route
            if (routingControl) {
                map.removeControl(routingControl);
                routingControl = null;
            }
            
            // Hide travel info
            document.getElementById('travelInfo').style.display = 'none';
        }
    </script>
</body>
</html>
        """
        
        # Prepare location data for JavaScript
        locations_data = json.dumps([place for place in self.places if 'coordinates' in place])
        
        return html_template.replace('{locations_data}', locations_data)
    
    def create_map(self, output_file: str = 'lunch_map.html'):
        """Main method to create the map"""
        print("Loading location data...")
        if not self.load_data():
            return False
            
        print("Geocoding addresses...")
        self.geocode_all_locations()
        
        print("Generating map HTML...")
        html_content = self.generate_map_html()
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
            
        print(f"Map created successfully! Open {output_file} in your browser.")
        return True

if __name__ == "__main__":
    locator = LocationData()
    locator.create_map()