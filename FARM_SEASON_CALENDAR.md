# Farm Season Calendar for Norway

A comprehensive garden planning system optimized for Norwegian climate zones, featuring evidence-based companion planting, crop rotation, succession planting, and automated reminders.

---

## 🌱 Overview

The Farm Season Calendar is designed specifically for Norwegian gardeners and farmers, taking into account:

- **Norwegian Climate Zones** (1-8, where 1 is warmest coastal areas and 8 is coldest mountain regions)
- **Short Growing Season** - Optimized planting windows for Norwegian summers
- **Frost Dates** - Crop data includes frost tolerance information
- **Local Varieties** - Pre-configured with popular Norwegian crops

---

## 📋 Features

### 1. Crop Database

Pre-configured with 12+ common crops optimized for Norwegian conditions:

- 🍅 **Tomat (Tomato)** - Best in greenhouse/polytunnel
- 🥕 **Gulrot (Carrot)** - Hardy, suitable for all zones
- 🥗 **Salat (Lettuce)** - Perfect for succession planting
- 🥔 **Potet (Potato)** - Norwegian staple crop
- 🥬 **Kål (Cabbage)** - Frost-tolerant, late season harvest
- 🫛 **Erter (Peas)** - Cold-season crop, nitrogen-fixing
- 🧅 **Løk (Onion)** - Easy to grow and store
- 🥒 **Agurk (Cucumber)** - Warm-season, greenhouse recommended
- 🌶️ **Reddik (Radish)** - Fastest crop (25 days)
- 🍓 **Jordbær (Strawberry)** - Perennial, produces for years
- 🌿 **Basilikum (Basil)** - Warm herb, greenhouse or protected areas
- 🎃 **Squash/Gresskar** - Space-intensive, warm-season crop

Each crop includes:
- Scientific name and family
- Planting and harvest months
- Days to maturity
- Temperature requirements
- Frost tolerance
- Sun and water requirements
- Spacing recommendations
- Growing tips in Norwegian
- Companion planting relationships

### 2. Companion Planting

Built-in companion plant database shows which plants grow well together and which should be kept apart:

**Examples:**
- ✅ **Good Companions:** Tomato + Basil, Carrot + Onion, Beans + Corn
- ❌ **Bad Companions:** Tomato + Potato, Onion + Peas, Fennel + Most vegetables

The system automatically warns you when incompatible crops are planted in the same schedule.

### 3. Crop Rotation Planning

Prevent soil-borne diseases and pest buildup by rotating crops from different families:

**Crop Families:**
- Solanaceae (Nightshade): Tomato, Potato, Pepper
- Brassicaceae (Cabbage): Kale, Cabbage, Radish, Turnip
- Fabaceae (Legume): Peas, Beans
- Cucurbitaceae (Gourd): Cucumber, Squash, Pumpkin
- Apiaceae (Carrot): Carrot, Parsnip, Celery
- Alliaceae (Onion): Onion, Garlic, Leek

The system suggests crops from different families to plant after your current season.

### 4. Succession Planting

Calculate optimal planting intervals for continuous harvest:

**Fast-Growing Crops for Succession:**
- Reddik (Radish): Every 10 days
- Salat (Lettuce): Every 14 days
- Gulrot (Carrot): Every 21 days

Enter start and end dates, and the system calculates all planting dates automatically.

### 5. Garden Plot Management

Define and manage multiple garden areas:

- Track dimensions (meters)
- Record soil type and pH
- Note sun exposure
- Mark drainage quality
- Indicate wind protection
- Track irrigation availability

### 6. Planting Schedules

Create detailed planting schedules for each garden plot:

- Link to specific garden plot
- Set year and season
- Add multiple crops with varieties
- Track planting dates
- Calculate harvest dates automatically
- Update status (Planned → Planted → Growing → Harvested)
- Record actual harvest dates
- Track crop rotation

### 7. Email Reminders

Never miss a planting or harvest window:

- Enable email reminders per schedule
- Configure days before planting (default: 7 days)
- Configure days before harvest (default: 7 days)
- Daily automated checks
- Formatted email with all upcoming tasks

**Email Content Includes:**
- Garden plot name
- Crop and variety
- Days until planting/harvest
- Specific dates

### 8. Shopping Lists

Generate seed and plant shopping lists:

- Based on planting schedule
- Groups by crop and variety
- Shows total quantities needed
- Lists all planting dates
- Helps budget planning

### 9. Weather Integration (yr.no) ⭐ NEW!

Real-time weather data from the Norwegian Meteorological Institute:

- **7-Day Forecast** - Temperature, precipitation, wind, humidity
- **Frost Risk Alerts** - Know when frost is expected to protect crops
- **Planting Advice** - Weather-based recommendations for when to plant
- **Crop-Specific Guidance** - Tailored advice based on crop requirements
- **Garden Plot Weather** - Automatic forecast for your plot's location

**Weather Data Includes:**
- Daily min/max/average temperatures
- Precipitation amounts in mm
- Wind speed in m/s
- Relative humidity percentage
- Weather symbols (clear, cloudy, rain, etc.)

**Smart Features:**
- Warns about frost risk for frost-sensitive crops
- Suggests delaying planting during heavy rain
- Recommends irrigation during dry periods
- Considers crop temperature requirements

---

## 🚀 Getting Started

### Step 1: Define Your Garden Plot

Navigate to: **Assist Tools → Garden Plot → New**

Example:
```
Plot Name: Main Vegetable Garden
Location: Oslo
Norwegian Zone: 3
Plot Type: Raised Bed
Length: 5 meters
Width: 3 meters
Soil Type: Loamy
Sun Exposure: Full Sun (6+ hours)
Drainage: Good
```

### Step 2: Browse Available Crops

Navigate to: **Assist Tools → Crop → List**

Review the pre-configured Norwegian crops or add your own varieties.

### Step 3: Create a Planting Schedule

Navigate to: **Assist Tools → Garden Planting Schedule → New**

Example for Spring 2026:
```
Schedule Name: Spring Garden 2026
Garden Plot: Main Vegetable Garden
Year: 2026
Season: Spring

Planting Items:
1. Tomat (Tomato) - Cherry - Plant: 2026-05-15
2. Salat (Lettuce) - Butterhead - Plant: 2026-04-15
3. Gulrot (Carrot) - Nantes - Plant: 2026-04-20
4. Erter (Peas) - Sugar Snap - Plant: 2026-04-10

Email Reminders: ✓
Reminder Email: your.email@example.com
Days Before Planting: 7
Days Before Harvest: 7
```

The system will:
- Calculate harvest dates based on days to maturity
- Check for companion planting conflicts
- Remind you 7 days before each planting and harvest

### Step 4: Use the API for Advanced Planning

See API endpoints below for programmatic access to all features.

---

## 📡 API Endpoints

All endpoints are accessible via REST API with proper authentication.

### Get Planting Calendar

Get crops suitable for planting in a specific zone and month:

```python
POST /api/method/assist.api.get_planting_calendar
{
    "norwegian_zone": "3",
    "month": "May"
}

Response:
{
    "success": true,
    "crops": [
        {
            "crop_name": "Tomat (Tomato)",
            "crop_family": "Solanaceae (Nightshade)",
            "planting_start_month": "April",
            "planting_end_month": "June",
            "days_to_maturity": 70,
            ...
        },
        ...
    ],
    "count": 8,
    "zone": "3",
    "month": "May"
}
```

### Get Companion Planting Suggestions

Find good and bad companion plants for a specific crop:

```python
POST /api/method/assist.api.get_companion_planting_suggestions
{
    "crop_name": "Tomat (Tomato)"
}

Response:
{
    "success": true,
    "crop": "Tomat (Tomato)",
    "good_companions": [
        {"crop_name": "Basilikum", "crop_family": "Lamiaceae", ...},
        {"crop_name": "Gulrot", "crop_family": "Apiaceae", ...}
    ],
    "bad_companions": [
        {"crop_name": "Kål", "crop_family": "Brassicaceae", ...},
        {"crop_name": "Potet", "crop_family": "Solanaceae", ...}
    ]
}
```

### Get Crop Rotation Suggestions

Get suggestions for what to plant after a specific crop:

```python
POST /api/method/assist.api.get_crop_rotation_suggestions
{
    "garden_plot": "Main Vegetable Garden",
    "previous_crop": "Potet (Potato)"
}

Response:
{
    "success": true,
    "previous_crop": "Potet (Potato)",
    "suggested_crops": [
        // Crops from different families
        {"crop_name": "Kål", "crop_family": "Brassicaceae", ...},
        {"crop_name": "Erter", "crop_family": "Fabaceae", ...}
    ],
    "avoid_crops": [
        // Same family crops to avoid
        {"crop_name": "Tomat", "crop_family": "Solanaceae"}
    ],
    "rotation_tip": "Rotate crops from different families..."
}
```

### Calculate Succession Planting

Calculate multiple planting dates for continuous harvest:

```python
POST /api/method/assist.api.calculate_succession_planting
{
    "crop_name": "Salat (Lettuce)",
    "start_date": "2026-04-01",
    "end_date": "2026-07-31"
}

Response:
{
    "success": true,
    "crop": "Salat (Lettuce)",
    "succession_interval_days": 14,
    "planting_schedule": [
        {
            "planting_number": 1,
            "planting_date": "2026-04-01",
            "expected_harvest_date": "2026-05-16",
            "days_to_maturity": 45
        },
        {
            "planting_number": 2,
            "planting_date": "2026-04-15",
            "expected_harvest_date": "2026-05-30",
            "days_to_maturity": 45
        },
        ...
    ],
    "total_plantings": 8
}
```

### Generate Shopping List

Create a shopping list from a planting schedule:

```python
POST /api/method/assist.api.generate_garden_shopping_list
{
    "schedule_name": "GPS-2026-00001"
}

Response:
{
    "success": true,
    "schedule_name": "GPS-2026-00001",
    "garden_plot": "Main Vegetable Garden",
    "year": 2026,
    "shopping_list": [
        {
            "crop": "Tomat (Tomato)",
            "variety": "Cherry",
            "total_quantity": 6,
            "planting_dates": ["2026-05-15", "2026-06-01"]
        },
        ...
    ],
    "total_crop_types": 8
}
```

### Get Upcoming Tasks

Get planting and harvest tasks for the next X days:

```python
POST /api/method/assist.api.get_upcoming_garden_tasks
{
    "days_ahead": 14
}

Response:
{
    "success": true,
    "days_ahead": 14,
    "planting_tasks": [
        {
            "schedule": "Spring Garden 2026",
            "garden_plot": "Main Vegetable Garden",
            "crop": "Gulrot (Carrot)",
            "variety": "Nantes",
            "date": "2026-04-20",
            "days_until": 5,
            "quantity": 100
        }
    ],
    "harvest_tasks": [
        {
            "schedule": "Spring Garden 2026",
            "garden_plot": "Main Vegetable Garden",
            "crop": "Reddik (Radish)",
            "variety": "French Breakfast",
            "date": "2026-05-10",
            "days_until": 10,
            "quantity": 50
        }
    ],
    "total_tasks": 8
}
```

### Weather Forecast

Get 7-day weather forecast from yr.no:

```python
POST /api/method/assist.api.get_weather_forecast_for_location
{
    "latitude": 59.9139,
    "longitude": 10.7522,
    "days": 7
}

Response:
{
    "success": true,
    "location": {
        "latitude": 59.9139,
        "longitude": 10.7522
    },
    "forecast": [
        {
            "date": "2026-04-15",
            "temperature": {
                "min": 8.5,
                "max": 15.2,
                "avg": 11.8
            },
            "precipitation_mm": 2.5,
            "wind_speed_ms": 4.2,
            "humidity_percent": 75,
            "weather_symbol": "partlycloudy_day"
        },
        ...
    ],
    "source": "yr.no (Norwegian Meteorological Institute)",
    "last_updated": "2026-04-15T06:00:00Z"
}
```

### Frost Risk Check

Check for frost risk in upcoming days:

```python
POST /api/method/assist.api.get_frost_risk_for_location
{
    "latitude": 59.9139,
    "longitude": 10.7522
}

Response:
{
    "success": true,
    "location": {
        "latitude": 59.9139,
        "longitude": 10.7522
    },
    "frost_risk": true,
    "frost_days": [
        {
            "date": "2026-04-18",
            "min_temperature": -2.1,
            "severity": "Light Frost"
        }
    ],
    "message": "Frost expected on 1 days"
}
```

### Planting Weather Advice

Get weather-based planting recommendations:

```python
POST /api/method/assist.api.get_planting_weather_advice_for_location
{
    "latitude": 59.9139,
    "longitude": 10.7522,
    "crop_name": "Tomat (Tomato)"
}

Response:
{
    "success": true,
    "location": {
        "latitude": 59.9139,
        "longitude": 10.7522
    },
    "crop": "Tomat (Tomato)",
    "advice": [
        "Temperature is suitable for planting warm-season crops",
        "Moderate rainfall expected - good conditions for planting"
    ],
    "warnings": [
        "Frost expected on 1 days in the next week - delay planting frost-sensitive crops"
    ],
    "crop_specific_advice": "Tomat (Tomato) is not frost-tolerant - wait until frost risk passes",
    "forecast_summary": {
        "days": 7,
        "avg_temperature": 11.5,
        "total_precipitation_mm": 15.3,
        "frost_days": 1
    }
}
```

### Weather for Garden Plot

Get weather forecast for a garden plot's location:

```python
POST /api/method/assist.api.get_weather_for_garden_plot
{
    "plot_name": "Main Vegetable Garden",
    "days": 7
}

Response:
{
    "success": true,
    "garden_plot": "Main Vegetable Garden",
    "location": {
        "latitude": 59.9139,
        "longitude": 10.7522
    },
    "forecast": [...],
    "source": "yr.no (Norwegian Meteorological Institute)"
}

Note: Garden Plot location must be in "latitude,longitude" format (e.g., "59.9139,10.7522")
```

---

## 🔔 Email Reminders

The system sends daily email reminders automatically via a scheduled task.

**Configuration in `hooks.py`:**
```python
scheduler_events = {
    "daily": [
        "assist.tasks.send_garden_reminders"
    ],
}
```

**Email Format:**
```
Subject: Garden Reminders: Spring Garden 2026

Garden Plot: Main Vegetable Garden

Upcoming Planting Tasks:
• Gulrot (Carrot) (Nantes) - Plant in 5 days (2026-04-20)
• Erter (Peas) (Sugar Snap) - Plant in 3 days (2026-04-18)

Upcoming Harvest Tasks:
• Reddik (Radish) (French Breakfast) - Ready to harvest in 10 days (2026-05-10)
• Salat (Lettuce) (Butterhead) - Ready to harvest in 12 days (2026-05-12)

Good luck with your gardening!
```

---

## 🧪 Testing

Run the test suite:

```bash
# Run farm calendar tests
python -m unittest assist.tests.test_farm_calendar -v

# Run all tests
python -m unittest discover assist/tests -v
```

**Test Coverage:**
- Crop doctype structure
- Garden Plot doctype structure
- Garden Planting Schedule doctype structure
- Norwegian crops fixture validation
- API endpoint availability
- Scheduled task configuration
- Companion planting data integrity
- Norwegian zone validation

---

## 📚 Norwegian Climate Zones

Norway is divided into 8 plant hardiness zones:

| Zone | Description | Example Cities | Average Min Temp |
|------|-------------|----------------|------------------|
| 1 | Warmest coastal | Bergen, Stavanger | -5°C to 0°C |
| 2 | Mild coastal | Oslo coast, Kristiansand | -10°C to -5°C |
| 3 | Moderate inland | Oslo inland, Drammen | -15°C to -10°C |
| 4 | Cold inland | Lillehammer, Hamar | -20°C to -15°C |
| 5 | Mountain valleys | Valdres, Hallingdal | -25°C to -20°C |
| 6 | Cold mountain | Røros, Folldal | -30°C to -25°C |
| 7 | Very cold mountain | Northern inland | -35°C to -30°C |
| 8 | Coldest mountain | High mountains | Below -35°C |

**Tip:** Most vegetables are grown in zones 1-5. Zones 6-8 require greenhouses for most crops.

---

## 💡 Tips for Norwegian Gardening

### Best Practices

1. **Start Early Indoors**
   - Tomatoes, peppers: Start indoors in March-April
   - Plant out after last frost (late May - early June)

2. **Use Season Extenders**
   - Polytunnels and greenhouses essential in zones 4+
   - Row covers for early spring crops
   - Cold frames for fall extension

3. **Choose Short-Season Varieties**
   - Look for "early" or "short season" varieties
   - 60-70 day tomatoes instead of 80-90 day
   - Focus on crops that mature in 60-90 days

4. **Maximize the Growing Season**
   - Start with cold-hardy crops (peas, lettuce, radish) in April
   - Plant warm-season crops (tomato, cucumber) in May-June
   - End with fall crops (kale, cabbage, carrots) harvested in Oct-Nov

5. **Companion Plant Strategically**
   - Tomatoes + Basil (beneficial and saves space)
   - Three Sisters: Corn + Beans + Squash
   - Carrots + Onions (onions deter carrot fly)

6. **Rotate by Family**
   - Never plant same family in same spot two years running
   - 3-4 year rotation ideal
   - Legumes improve soil nitrogen

7. **Use the Calendar**
   - Plan succession plantings of fast crops
   - Set reminders for optimal planting times
   - Track what worked and what didn't for next year

---

## 🤝 Contributing

Want to add more Norwegian crops or improve the data?

1. Edit `assist/fixtures/norwegian_crops.json`
2. Add crop data following the existing format
3. Include Norwegian names and growing tips
4. Test with `python -m unittest assist.tests.test_farm_calendar`
5. Submit a pull request

---

## 📖 Further Reading

- [Norsk Gartnerforbund](https://norskgartnerforbund.no/)
- [Frøsamlere.no](https://frosamlere.no/)
- [Nibio - Norsk institutt for bioøkonomi](https://www.nibio.no/)
- [Companion Planting Research](https://en.wikipedia.org/wiki/Companion_planting)
- [Norwegian Climate Zones](https://www.nibio.no/tema/hage/plantesoner)

---

## 📄 License

MIT License - see [license.txt](license.txt) for details.

---

<div align="center">

Made with ❤️ for Norwegian gardeners 🇳🇴

**God høsting!** (Happy harvesting!)

</div>
