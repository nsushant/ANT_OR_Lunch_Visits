# Lunch Locations Map - How It Works

## Overview

The `lunch_map.py` script creates an interactive HTML map displaying lunch locations from markdown files. It automatically converts addresses to coordinates, shows which restaurants you've visited, and provides routing between locations.

## Files Required

- `places.md` - Contains restaurant information (name, address, cuisine, price, notes)
- `lunch_log.md` - Contains visit history with dates and locations
- Generates: `lunch_map.html` - Interactive web map

## How the Code Works

### 1. Reading Data

The script reads two markdown files:

**places.md format:**
```markdown
- Name: Munji
- Location: Oude Koornmarkt 68, 2000 Antwerpen
- Cuisine: Middle Eastern 
- Price range: $
- Note: Place only serves falafel wraps.
```

**lunch_log.md format:**
```markdown
### 2024-01-15 — Munji
- **Location:** Oude Koornmarkt 68, 2000 Antwerpen
Visit details...
```

### 2. Converting Addresses to Coordinates

The script uses the **geopy** library to automatically convert street addresses to latitude/longitude coordinates:

```python
# Takes "Oude Koornmarkt 68, 2000 Antwerpen"
# Returns: (51.218929, 4.4002575)
```

- Automatically adds "Antwerpen, Belgium" if not present
- Uses OpenStreetMap's Nominatim service
- Includes rate limiting (1 second delay) to respect API limits

### 3. Creating the Map

The script generates a complete HTML file with:

**Mapping Libraries:**
- **Leaflet.js** - Interactive map display
- **Leaflet Routing Machine** - Route calculation and display
- **OpenStreetMap** - Map tiles

**Marker Types:**
- 🟢 **Green circles** - Visited restaurants (from lunch_log.md)
- 🔵 **Blue circles** - Unvisited restaurants (from places.md)
- 🔴 **Red circle** - University of Antwerp (Stadscampus)

### 4. Interactive Features

**Click Actions:**
1. Click any marker to select it (gets yellow border)
2. Click a second marker to create a route between them
3. Route appears as red line with travel info
4. Information panel shows in bottom-right corner

**Travel Information:**
- Route visualization on map
- Distance in kilometers
- Estimated travel time in minutes
- Clear Selection button to reset

### 5. Data Flow

```
places.md + lunch_log.md
        ↓
    Parse data
        ↓
    Geocode addresses → Get coordinates
        ↓
    Generate HTML + JavaScript
        ↓
    lunch_map.html → Open in browser
```

## Usage

**Run the script:**
```bash
python3 lunch_map.py
```

**Output:**
```
Loading location data...
Geocoding addresses...
Geocoded: Munji -> (51.218929, 4.4002575)
Geocoded: Tjoung Tjoung -> (51.2186649, 4.4191256)
...
Generating map HTML...
Map created successfully! Open lunch_map.html in your browser.
```

## Dependencies

**Python packages:**
- `geopy` - Converts addresses to coordinates

**Web libraries (loaded automatically):**
- Leaflet.js for mapping
- Leaflet Routing Machine for directions

## Error Handling

The script handles common issues:
- Missing markdown files
- Failed geocoding (continues with other locations)
- Network errors (tries each address individually)

## Map Features

**Interactive Elements:**
- Click markers to select for routing
- Hover markers to see restaurant details
- Travel info panel appears bottom-right
- Responsive design works on different screen sizes

**Restaurant Information:**
- Name, address, cuisine type
- Price range and notes
- Visit status (visited/unvisited)

This system automatically keeps your map updated - just add new restaurants to `places.md` or new visits to `lunch_log.md` and run the script again!