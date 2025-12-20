#!/usr/bin/env python3
"""
Lunch Locations Map Visualizer
Creates an interactive map showing lunch locations from markdown files
"""

import re
import json
import time
from typing import Dict, List, Tuple, Optional
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter

class LocationData:
    def __init__(self):
        self.places = []
        self.lunch_log = []
        self.geocoded_cache = {}  # Cache for batch geocoded addresses
        # Initialize geopy geocoder 
        self.geolocator = Nominatim(user_agent="LunchMap/1.0 (educational purpose)")
        self.geocode = RateLimiter(self.geolocator.geocode, min_delay_seconds=1)
        
        # Minimal fallback coordinates for essential locations only
        self.fallback_coordinates = {
            'University of Antwerp - Stadscampus': (51.2229654, 4.4102137)
        }
        
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
            elif line.startswith('- pics:'):
                current_place['pics'] = line.split(':', 1)[1].strip()
                
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
    
    def get_images_from_directory(self, pics_dir: str) -> List[str]:
        """Get list of images from the pics directory"""
        import os
        
        if not pics_dir or not os.path.exists(pics_dir):
            return []
        
        supported_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
        images = []
        
        try:
            for filename in sorted(os.listdir(pics_dir)):
                ext = os.path.splitext(filename)[1].lower()
                if ext in supported_extensions:
                    # Store relative path for HTML
                    images.append(os.path.join(pics_dir, filename))
        except Exception as e:
            print(f"Error reading directory {pics_dir}: {e}")
        
        return images
    
    def geocode_address(self, address: str) -> Optional[Tuple[float, float]]:
        """Get coordinates for address (from cache or fallback)"""
        # First check if we have fallback coordinates
        if address in self.fallback_coordinates:
            return self.fallback_coordinates[address]
        
        # Check if we have geocoded this address already
        if address in self.geocoded_cache:
            return self.geocoded_cache[address]
        
        # If geocoding failed during batch processing, use default
        return (51.2054, 4.4132)  # Center of Antwerp
    
    def batch_geocode_addresses(self, addresses: List[str]) -> Dict[str, Tuple[float, float]]:
        """Batch geocode all unique addresses at once"""
        print(f"Starting batch geocoding for {len(addresses)} unique addresses...")
        
        geocoded_results = {}
        failed_addresses = []
        
        for i, address in enumerate(addresses):
            if address in self.fallback_coordinates:
                print(f"Using fallback coordinates for: {address}")
                geocoded_results[address] = self.fallback_coordinates[address]
                continue
                
            try:
                # Add Antwerpen, Belgium if not specified
                if "Antwerpen" not in address and "Belgium" not in address:
                    full_address = f"{address}, Antwerpen, Belgium"
                else:
                    full_address = address
                
                print(f"Geocoding {i+1}/{len(addresses)}: {address}")
                
                # Use rate limiter for batch processing to be safe
                location = self.geocode(full_address)
                
                if location:
                    geocoded_results[address] = (location.latitude, location.longitude)
                    print(f"  ✓ Success: ({location.latitude}, {location.longitude})")
                else:
                    failed_addresses.append(address)
                    print(f"  ✗ Failed: No results found")
                    
                # Add delay between requests to respect rate limits
                time.sleep(1.5)  # Slightly longer delay for reliability
                
            except Exception as e:
                failed_addresses.append(address)
                print(f"  ✗ Error: {e}")
                # Add extra delay after errors
                time.sleep(2)
        
        # Handle failed addresses with default coordinates
        for address in failed_addresses:
            print(f"Using default Antwerp coordinates for failed address: {address}")
            geocoded_results[address] = (51.2054, 4.4132)
        
        print(f"Batch geocoding completed. {len(geocoded_results) - len(failed_addresses)} successful, {len(failed_addresses)} failed.")
        return geocoded_results
    
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
        """Geocode all addresses using batch processing"""
        # Collect all unique addresses
        unique_addresses = []
        for place in self.places:
            if 'address' in place and place['address'] not in unique_addresses:
                unique_addresses.append(place['address'])
        
        # Batch geocode all unique addresses
        self.geocoded_cache = self.batch_geocode_addresses(unique_addresses)
        
        # Assign coordinates to places
        for place in self.places:
            if 'address' in place:
                coords = self.geocode_address(place['address'])
                if coords:
                    place['coordinates'] = coords
                    print(f"Assigned coordinates: {place['name']} -> {coords}")
                else:
                    print(f"Failed to assign coordinates: {place['name']} - {place['address']}")
            else:
                print(f"No address found for: {place['name']}")
            
            # Process images if pics field exists
            if 'pics' in place:
                images = self.get_images_from_directory(place['pics'])
                if images:
                    place['images'] = images
                    print(f"Found {len(images)} image(s) for {place['name']}")
        
        # Mark visited places
        visited_names = {entry['name'] for entry in self.lunch_log}
        for place in self.places:
            place['visited'] = place['name'] in visited_names
    
    def generate_map_html(self) -> str:
        """Generate HTML for interactive map"""
        # Load images for University of Antwerp
        ua_images = self.get_images_from_directory('images/UA')
        print(f"Found {len(ua_images)} image(s) for University of Antwerp")
        
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
            top: 60px;
            left: 10px;
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
            right: 20px;
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
        .popup-image-gallery {
            margin-top: 10px;
            max-width: 300px;
        }
        .popup-image-gallery img {
            width: 100%;
            height: auto;
            border-radius: 4px;
            margin-bottom: 8px;
            display: none;
            cursor: pointer;
        }
        .popup-image-gallery img.active {
            display: block;
        }
        .popup-gallery-controls {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-top: 8px;
        }
        .popup-nav-btn {
            background: #4CAF50;
            color: white;
            border: none;
            padding: 6px 10px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 12px;
        }
        .popup-nav-btn:hover {
            background: #45a049;
        }
        .popup-counter {
            font-size: 12px;
            color: #666;
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
    
    <div class="travel-info" id="travelInfo">
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
        
        // Close pinned popups when clicking on the map (not on a marker)
        map.on('click', function() {
            closeAllPinnedPopups();
        });
        
        // Store gallery states for each marker
        const galleryStates = new Map();
        
        // Track pinned popups (clicked to stay open)
        const pinnedMarkers = new Set();
        let isHoveringPopup = false;
        
        // Function to convert markdown links to HTML
        function markdownLinksToHtml(text) {
            if (!text) return text;
            // Convert markdown links [text](url) to HTML <a> tags
            return text.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank">$1</a>');
        }
        
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
            if (location.note) popupContent += `Note: ${markdownLinksToHtml(location.note)}`;
            
            // Add image gallery to popup if images exist
            if (location.images && location.images.length > 0) {
                const galleryId = 'gallery-' + location.name.replace(/[^a-zA-Z0-9]/g, '-');
                galleryStates.set(galleryId, 0); // Initialize at first image
                
                popupContent += `<div class="popup-image-gallery" id="${galleryId}">`;
                location.images.forEach((imgPath, index) => {
                    popupContent += `<img src="${imgPath}" class="${index === 0 ? 'active' : ''}" alt="Image ${index + 1}">`;
                });
                
                if (location.images.length > 1) {
                    popupContent += `<div class="popup-gallery-controls">`;
                    popupContent += `<button class="popup-nav-btn" onclick="navigatePopupGallery('${galleryId}', -1)">← Prev</button>`;
                    popupContent += `<span class="popup-counter" id="${galleryId}-counter">1 / ${location.images.length}</span>`;
                    popupContent += `<button class="popup-nav-btn" onclick="navigatePopupGallery('${galleryId}', 1)">Next →</button>`;
                    popupContent += `</div>`;
                }
                popupContent += `</div>`;
            }
            
            marker.bindPopup(popupContent, {
                closeOnClick: false,
                autoClose: false,
                closeButton: true
            });
            
            // Show popup on hover
            marker.on('mouseover', function() {
                marker.openPopup();
            });
            
            // Close popup when mouse leaves (with delay to check if moving to popup)
            marker.on('mouseout', function() {
                setTimeout(function() {
                    // Only close if not hovering popup and not pinned
                    if (!isHoveringPopup && !pinnedMarkers.has(marker)) {
                        marker.closePopup();
                    }
                }, 100);
            });
            
            // Pin popup on click (keep it open)
            marker.on('click', function(e) {
                pinnedMarkers.add(marker);
                marker.openPopup();
                handleMarkerClick(location, marker);
            });
            
            // Setup popup event listeners when popup opens
            marker.on('popupopen', function() {
                const popupElement = marker.getPopup().getElement();
                
                popupElement.addEventListener('mouseenter', function() {
                    isHoveringPopup = true;
                });
                
                popupElement.addEventListener('mouseleave', function() {
                    isHoveringPopup = false;
                    // Close popup if not pinned
                    if (!pinnedMarkers.has(marker)) {
                        marker.closePopup();
                    }
                });
                
                // Add double-click handler to images
                const images = popupElement.querySelectorAll('.popup-image-gallery img');
                images.forEach(function(img) {
                    img.addEventListener('dblclick', function() {
                        window.open(img.src, '_blank');
                    });
                });
            });
            
            // Unpin when popup closes
            marker.on('popupclose', function() {
                pinnedMarkers.delete(marker);
            });
        });
        
        // Add University of Antwerp Stadscampus marker
        const uaImages = {ua_images_data};
        let uaPopupContent = '<strong>University of Antwerp - Stadscampus</strong><br>Prinsstraat 13, 2000 Antwerpen';
        
        // Add image gallery to UA popup if images exist
        if (uaImages && uaImages.length > 0) {
            const galleryId = 'gallery-UA';
            galleryStates.set(galleryId, 0);
            
            uaPopupContent += `<div class="popup-image-gallery" id="${galleryId}">`;
            uaImages.forEach((imgPath, index) => {
                uaPopupContent += `<img src="${imgPath}" class="${index === 0 ? 'active' : ''}" alt="Image ${index + 1}">`;
            });
            
            if (uaImages.length > 1) {
                uaPopupContent += `<div class="popup-gallery-controls">`;
                uaPopupContent += `<button class="popup-nav-btn" onclick="navigatePopupGallery('${galleryId}', -1)">← Prev</button>`;
                uaPopupContent += `<span class="popup-counter" id="${galleryId}-counter">1 / ${uaImages.length}</span>`;
                uaPopupContent += `<button class="popup-nav-btn" onclick="navigatePopupGallery('${galleryId}', 1)">Next →</button>`;
                uaPopupContent += `</div>`;
            }
            uaPopupContent += `</div>`;
        }
        
        const universityMarker = L.marker([51.2229654, 4.4102137], {icon: universityIcon})
            .addTo(map)
            .bindPopup(uaPopupContent, {
                closeOnClick: false,
                autoClose: false,
                closeButton: true
            });
        
        // Show popup on hover
        universityMarker.on('mouseover', function() {
            universityMarker.openPopup();
        });
        
        // Close popup when mouse leaves (with delay)
        universityMarker.on('mouseout', function() {
            setTimeout(function() {
                if (!isHoveringPopup && !pinnedMarkers.has(universityMarker)) {
                    universityMarker.closePopup();
                }
            }, 100);
        });
        
        // Pin on click
        universityMarker.on('click', function() {
            pinnedMarkers.add(universityMarker);
            universityMarker.openPopup();
            handleMarkerClick({
                name: 'University of Antwerp - Stadscampus',
                coordinates: [51.2229654, 4.4102137]
            }, universityMarker);
        });
        
        // Setup popup hover handling
        universityMarker.on('popupopen', function() {
            const popupElement = universityMarker.getPopup().getElement();
            
            popupElement.addEventListener('mouseenter', function() {
                isHoveringPopup = true;
            });
            
            popupElement.addEventListener('mouseleave', function() {
                isHoveringPopup = false;
                if (!pinnedMarkers.has(universityMarker)) {
                    universityMarker.closePopup();
                }
            });
            
            // Add double-click handler to images
            const images = popupElement.querySelectorAll('.popup-image-gallery img');
            images.forEach(function(img) {
                img.addEventListener('dblclick', function() {
                    window.open(img.src, '_blank');
                });
            });
        });
        
        // Unpin when popup closes
        universityMarker.on('popupclose', function() {
            pinnedMarkers.delete(universityMarker);
        });
        
        function closeAllPinnedPopups() {
            // Close all pinned popups and clear the set
            pinnedMarkers.forEach(function(marker) {
                marker.closePopup();
            });
            pinnedMarkers.clear();
        }
        
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
            
            // Close all pinned popups when showing a route
            closeAllPinnedPopups();
            
            const start = selectedMarkers[0].location.coordinates;
            const end = selectedMarkers[1].location.coordinates;
            
            // Remove existing route
            if (routingControl) {
                map.removeControl(routingControl);
            }
            
            // Add routing control for walking
            routingControl = L.Routing.control({
                waypoints: [
                    L.latLng(start[0], start[1]),
                    L.latLng(end[0], end[1])
                ],
                routeWhileDragging: false,
                addWaypoints: false,
                createMarker: function() { return null; }, // Don't create additional markers
                router: L.Routing.osrmv1({
                    serviceUrl: 'https://routing.openstreetmap.de/routed-foot/route/v1'
                }),
                lineOptions: {
                    styles: [{color: 'red', weight: 4, opacity: 0.7}]
                }
            }).on('routesfound', function(e) {
                const routes = e.routes;
                const summary = routes[0].summary;
                
                // Calculate walking time for faster walking speed (brisk pace: 6.0 km/h = 100 m/min)
                const walkingSpeedMetersPerMinute = 100;
                const walkingTimeMinutes = Math.ceil(summary.totalDistance / walkingSpeedMetersPerMinute);
                
                // Display travel information
                const travelInfo = document.getElementById('travelInfo');
                const travelDetails = document.getElementById('travelDetails');
                
                travelDetails.innerHTML = `
                    <strong>From:</strong> ${selectedMarkers[0].location.name}<br>
                    <strong>To:</strong> ${selectedMarkers[1].location.name}<br>
                    <strong>Distance:</strong> ${(summary.totalDistance / 1000).toFixed(2)} km<br>
                    <strong>Walking Time:</strong> ${walkingTimeMinutes} minutes<br>
                    <small>(brisk 6.0 km/h walking speed)</small>
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
        
        function navigatePopupGallery(galleryId, direction) {
            const gallery = document.getElementById(galleryId);
            if (!gallery) return;
            
            const images = gallery.querySelectorAll('img');
            const counter = document.getElementById(galleryId + '-counter');
            
            // Find current active image
            let currentIndex = 0;
            images.forEach((img, index) => {
                if (img.classList.contains('active')) {
                    currentIndex = index;
                    img.classList.remove('active');
                }
            });
            
            // Calculate new index
            currentIndex += direction;
            if (currentIndex < 0) currentIndex = images.length - 1;
            if (currentIndex >= images.length) currentIndex = 0;
            
            // Show new image
            images[currentIndex].classList.add('active');
            
            // Update counter
            if (counter) {
                counter.textContent = `${currentIndex + 1} / ${images.length}`;
            }
        }
    </script>
</body>
</html>
        """
        
        # Prepare location data for JavaScript
        locations_data = json.dumps([place for place in self.places if 'coordinates' in place])
        ua_images_data = json.dumps(ua_images)
        
        return html_template.replace('{locations_data}', locations_data).replace('{ua_images_data}', ua_images_data)
    
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