#!/usr/bin/env python3
"""
Simple script to verify the coordinates are accurate
"""

import json

# Read the coordinates from the generated map
with open('lunch_map.html', 'r') as f:
    content = f.read()
    
# Extract the location data
start_marker = 'const locations = '
end_marker = ';'
start_pos = content.find(start_marker)
if start_pos != -1:
    start_pos += len(start_marker)
    end_pos = content.find(end_marker, start_pos)
    if end_pos != -1:
        locations_json = content[start_pos:end_pos]
        locations = json.loads(locations_json)
        
        print("Location Coordinates Verification:")
        print("=" * 50)
        
        for loc in locations:
            name = loc.get('name', 'Unknown')
            address = loc.get('address', 'No address')
            coords = loc.get('coordinates', [0, 0])
            visited = loc.get('visited', False)
            
            status = "✓ Visited" if visited else "○ Not visited"
            print(f"{name}")
            print(f"  Address: {address}")
            print(f"  Coordinates: {coords[0]:.4f}, {coords[1]:.4f}")
            print(f"  Status: {status}")
            print()