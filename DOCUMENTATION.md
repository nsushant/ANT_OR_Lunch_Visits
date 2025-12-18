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

The script uses **batch geocoding** to efficiently convert addresses to coordinates:

```python
# Batch processes all unique addresses at once
# "Oude Koornmarkt 68, 2000 Antwerpen" → (51.218929, 4.4002575)
# "Breydelstraat 16, 2018 Antwerpen" → (51.218665, 4.419126)
# etc.
```

**Batch Geocoding Benefits:**
- **Reduced API calls**: Processes unique addresses once, then reuses results
- **Better reliability**: Includes proper error handling and retry logic
- **Progress tracking**: Shows which address is being processed
- **Faster execution**: Minimizes network requests
- **Automatic caching**: Results stored during batch process for reuse

**Technical Details:**
- Automatically adds "Antwerpen, Belgium" if not present
- Uses OpenStreetMap's Nominatim service with 1.5-second delays
- Handles failed addresses gracefully (falls back to Antwerp center)
- Collects all unique addresses first, then processes them sequentially

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
    Extract unique addresses
        ↓
    Batch geocode → Get coordinates
        ↓
    Cache results & assign to places
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
Starting batch geocoding for 7 unique addresses...
Geocoding 1/7: Oude Koornmarkt 68, 2000 Antwerpen
  ✓ Success: (51.218929, 4.4002575)
Geocoding 2/7: Breydelstraat 16, 2018 Antwerpen
  ✓ Success: (51.218665, 4.419126)
...
Batch geocoding completed. 7 successful, 0 failed.
Assigned coordinates: Munji -> (51.218929, 4.4002575)
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
- Network timeouts (graceful fallback to Antwerp center coordinates)
- Rate limit respect (1.5-second delays between API calls)
- Batch processing continues even if individual addresses fail

## Geocoding Improvements

**Before (Individual Geocoding):**
- Each restaurant geocoded separately
- Multiple network requests for same addresses
- Susceptible to timeout failures
- No progress tracking

**After (Batch Geocoding):**
- All unique addresses processed once
- Results cached and reused
- Better error handling and recovery
- Progress tracking during processing
- Reduced API load and faster execution

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

## Maintenance

**Adding New Restaurants:**
1. Add restaurant details to `places.md`
2. Run `python3 lunch_map.py`
3. New addresses will be automatically geocoded in the next batch

**Performance:**
- Subsequent runs are faster when addresses don't change
- Batch processing minimizes network requests
- Only new/unique addresses trigger API calls

**Verification:**
- Run `python3 verify_coordinates.py` to check coordinate accuracy
- Compare map locations against known addresses in Antwerp