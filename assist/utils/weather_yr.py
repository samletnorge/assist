"""
Weather integration with yr.no (Norwegian Meteorological Institute)

This module provides functions to fetch weather data from yr.no's LocationForecast API.
API documentation: https://api.met.no/weatherapi/locationforecast/2.0/documentation

Note: The API requires a User-Agent header identifying the application.
"""

import frappe
import requests
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta


def get_weather_forecast(latitude: float, longitude: float, days: int = 7) -> Dict[str, Any]:
    """
    Get weather forecast from yr.no for a specific location.
    
    Args:
        latitude: Latitude coordinate (e.g., 59.9139 for Oslo)
        longitude: Longitude coordinate (e.g., 10.7522 for Oslo)
        days: Number of days to forecast (default: 7, max: 10)
    
    Returns:
        Dictionary with weather forecast data including:
        - Temperature (air_temperature)
        - Precipitation (precipitation_amount)
        - Wind speed (wind_speed)
        - Humidity (relative_humidity)
        - Symbol code (weather symbol)
    """
    try:
        # yr.no API endpoint
        url = "https://api.met.no/weatherapi/locationforecast/2.0/compact"
        
        # Required User-Agent header (as per API terms of service)
        headers = {
            "User-Agent": "Assist-ERPNext/1.0 (https://github.com/samletnorge/assist; kontakt@drivstoffapp.no)"
        }
        
        params = {
            "lat": latitude,
            "lon": longitude
        }
        
        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        # Parse the forecast data
        forecast = parse_yr_forecast(data, days)
        
        return {
            "success": True,
            "location": {
                "latitude": latitude,
                "longitude": longitude
            },
            "forecast": forecast,
            "source": "yr.no (Norwegian Meteorological Institute)",
            "last_updated": data.get("properties", {}).get("meta", {}).get("updated_at")
        }
        
    except requests.exceptions.RequestException as e:
        frappe.log_error(f"yr.no API error: {str(e)}", "Weather API Error")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to fetch weather data from yr.no"
        }
    except Exception as e:
        frappe.log_error(f"Weather parsing error: {str(e)}", "Weather Parsing Error")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to parse weather data"
        }


def parse_yr_forecast(data: Dict, days: int) -> List[Dict[str, Any]]:
    """
    Parse yr.no forecast data into a simplified format.
    
    Args:
        data: Raw API response from yr.no
        days: Number of days to include
    
    Returns:
        List of daily forecast summaries
    """
    timeseries = data.get("properties", {}).get("timeseries", [])
    
    if not timeseries:
        return []
    
    # Group by date and aggregate
    daily_forecasts = {}
    cutoff_date = datetime.now() + timedelta(days=days)
    
    for entry in timeseries:
        time_str = entry.get("time")
        if not time_str:
            continue
        
        forecast_time = datetime.fromisoformat(time_str.replace('Z', '+00:00'))
        
        # Only include forecasts within the requested days
        if forecast_time > cutoff_date:
            break
        
        date_key = forecast_time.date().isoformat()
        
        if date_key not in daily_forecasts:
            daily_forecasts[date_key] = {
                "date": date_key,
                "temperatures": [],
                "precipitation": [],
                "wind_speeds": [],
                "humidity": [],
                "symbols": []
            }
        
        instant = entry.get("data", {}).get("instant", {}).get("details", {})
        next_1_hours = entry.get("data", {}).get("next_1_hours", {})
        next_6_hours = entry.get("data", {}).get("next_6_hours", {})
        
        # Collect temperature
        if "air_temperature" in instant:
            daily_forecasts[date_key]["temperatures"].append(instant["air_temperature"])
        
        # Collect precipitation
        precip_details = next_1_hours.get("details", {}) or next_6_hours.get("details", {})
        if "precipitation_amount" in precip_details:
            daily_forecasts[date_key]["precipitation"].append(precip_details["precipitation_amount"])
        
        # Collect wind speed
        if "wind_speed" in instant:
            daily_forecasts[date_key]["wind_speeds"].append(instant["wind_speed"])
        
        # Collect humidity
        if "relative_humidity" in instant:
            daily_forecasts[date_key]["humidity"].append(instant["relative_humidity"])
        
        # Collect weather symbol
        symbol = next_1_hours.get("summary", {}).get("symbol_code") or next_6_hours.get("summary", {}).get("symbol_code")
        if symbol:
            daily_forecasts[date_key]["symbols"].append(symbol)
    
    # Aggregate daily data
    result = []
    for date_key in sorted(daily_forecasts.keys()):
        day = daily_forecasts[date_key]
        
        temps = day["temperatures"]
        precip = day["precipitation"]
        winds = day["wind_speeds"]
        humid = day["humidity"]
        symbols = day["symbols"]
        
        summary = {
            "date": date_key,
            "temperature": {
                "min": round(min(temps), 1) if temps else None,
                "max": round(max(temps), 1) if temps else None,
                "avg": round(sum(temps) / len(temps), 1) if temps else None
            },
            "precipitation_mm": round(sum(precip), 1) if precip else 0,
            "wind_speed_ms": round(sum(winds) / len(winds), 1) if winds else None,
            "humidity_percent": round(sum(humid) / len(humid), 0) if humid else None,
            "weather_symbol": max(set(symbols), key=symbols.count) if symbols else None
        }
        
        result.append(summary)
    
    return result


def get_frost_risk(latitude: float, longitude: float) -> Dict[str, Any]:
    """
    Check for frost risk in the upcoming days.
    
    Args:
        latitude: Latitude coordinate
        longitude: Longitude coordinate
    
    Returns:
        Dictionary with frost risk assessment
    """
    try:
        forecast_data = get_weather_forecast(latitude, longitude, days=7)
        
        if not forecast_data.get("success"):
            return forecast_data
        
        frost_days = []
        for day in forecast_data.get("forecast", []):
            temp = day.get("temperature", {})
            min_temp = temp.get("min")
            
            if min_temp is not None and min_temp <= 0:
                frost_days.append({
                    "date": day["date"],
                    "min_temperature": min_temp,
                    "severity": "Hard Frost" if min_temp <= -5 else "Light Frost"
                })
        
        return {
            "success": True,
            "location": forecast_data.get("location"),
            "frost_risk": len(frost_days) > 0,
            "frost_days": frost_days,
            "message": f"Frost expected on {len(frost_days)} days" if frost_days else "No frost expected in the next 7 days"
        }
        
    except Exception as e:
        frappe.log_error(f"Frost risk check error: {str(e)}", "Frost Risk Error")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to check frost risk"
        }


def get_planting_weather_advice(latitude: float, longitude: float, crop_name: str = None) -> Dict[str, Any]:
    """
    Get weather-based planting advice for a location.
    
    Args:
        latitude: Latitude coordinate
        longitude: Longitude coordinate
        crop_name: Optional crop name for specific advice
    
    Returns:
        Dictionary with planting advice based on weather conditions
    """
    try:
        forecast_data = get_weather_forecast(latitude, longitude, days=7)
        
        if not forecast_data.get("success"):
            return forecast_data
        
        advice = []
        warnings = []
        
        forecast = forecast_data.get("forecast", [])
        if not forecast:
            return {
                "success": False,
                "message": "No forecast data available"
            }
        
        # Check current and upcoming conditions
        today = forecast[0] if forecast else {}
        next_week = forecast[:7]
        
        # Temperature checks
        avg_temp = today.get("temperature", {}).get("avg")
        if avg_temp is not None:
            if avg_temp < 5:
                warnings.append("Temperature is below 5°C - too cold for most warm-season crops")
            elif avg_temp >= 10:
                advice.append("Temperature is suitable for planting warm-season crops")
        
        # Frost checks
        frost_count = sum(1 for day in next_week if day.get("temperature", {}).get("min", 100) <= 0)
        if frost_count > 0:
            warnings.append(f"Frost expected on {frost_count} days in the next week - delay planting frost-sensitive crops")
        else:
            advice.append("No frost expected - safe to plant frost-sensitive crops")
        
        # Precipitation checks
        total_precip = sum(day.get("precipitation_mm", 0) for day in next_week)
        if total_precip > 50:
            warnings.append(f"Heavy rain expected ({total_precip}mm this week) - soil may be too wet for planting")
        elif total_precip < 5:
            advice.append("Low rainfall expected - ensure adequate watering after planting")
        else:
            advice.append("Moderate rainfall expected - good conditions for planting")
        
        # Crop-specific advice
        crop_advice = None
        if crop_name:
            try:
                crop = frappe.get_doc("Crop", crop_name)
                min_temp = crop.min_temperature_celsius or 0
                frost_tolerant = crop.frost_tolerant
                
                if not frost_tolerant and frost_count > 0:
                    crop_advice = f"{crop_name} is not frost-tolerant - wait until frost risk passes"
                elif avg_temp and avg_temp < min_temp:
                    crop_advice = f"{crop_name} prefers temperatures above {min_temp}°C - current conditions may slow growth"
                else:
                    crop_advice = f"Weather conditions are suitable for planting {crop_name}"
            except:
                pass
        
        return {
            "success": True,
            "location": forecast_data.get("location"),
            "crop": crop_name,
            "advice": advice,
            "warnings": warnings,
            "crop_specific_advice": crop_advice,
            "forecast_summary": {
                "days": len(next_week),
                "avg_temperature": round(sum(d.get("temperature", {}).get("avg", 0) for d in next_week) / len(next_week), 1) if next_week else None,
                "total_precipitation_mm": round(total_precip, 1),
                "frost_days": frost_count
            }
        }
        
    except Exception as e:
        frappe.log_error(f"Planting weather advice error: {str(e)}", "Weather Advice Error")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to generate planting advice"
        }
