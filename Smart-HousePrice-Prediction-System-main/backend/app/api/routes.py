from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os
import json
import re
import httpx

from app.core.config import GROQ_API_KEY
from app.agents.planner_agent import PlannerAgent
from app.services.geocoding import geocode_or_default
from app.storage.crud import get_cached, save_cached


class RawTextPayload(BaseModel):
    text: str

router = APIRouter()
planner = PlannerAgent()


@router.get("/health")
def health():
    return {"status": "ok"}


@router.post("/search")
def search(payload: dict):
    """
    Expected payload:
    {
      "location": { "lat": 34.05, "lon": -118.24 },
      "features": ["near hospitals", "safe", "cheap"],
      "city": "Chennai",
      "area_name": "Iyyapanthangal"
    }
    """
    location = payload.get("location", {})
    features = payload.get("features", [])

    # Debug log
    print(f"[Search] Incoming payload: {payload}")

    # Create cache key
    lat = location.get("lat")
    lon = location.get("lon")
    if lat is None or lon is None:
        print(f"[Search] Error: Latitude or Longitude missing in payload: {payload}")
        raise HTTPException(status_code=400, detail="Latitude / Longitude required")
    
    location_key = f"{lat:.6f},{lon:.6f}"
    
    # Convert features to list of strings for caching
    feature_strings = [str(f) for f in features]

    # Check database cache
    try:
        cached_record = get_cached(location_key, feature_strings)
        if cached_record:
            print(f"[Search] Cache hit for {location_key}")
            return getattr(cached_record, "result_json", cached_record)
    except Exception as e:
        print(f"[Search] Cache check failed (skipping cache): {e}")

    # Run planner
    results = planner.run(payload)

    # Save to cache
    try:
        save_cached(location_key, feature_strings, results)
    except Exception as e:
        print(f"[Search] Cache save failed: {e}")
    
    return results


@router.post("/parse")
def parse_input(payload: RawTextPayload):
    """
    Converts raw text into structured JSON via LLM.
    Falls back to geocoding if LLM fails.
    """
    text = payload.text.strip()

    # Use direct API call to Groq to bypass library version issues
    api_key = GROQ_API_KEY.strip() if GROQ_API_KEY else None
    if api_key:
        try:
            import requests
            url = "https://api.groq.com/openai/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            prompt = (
                "You are a real estate assistant. Convert this user request into a JSON object. \n"
                "JSON format: {\"location\": {\"lat\": null, \"lon\": null, \"city\": \"city name\", \"area\": \"area name\"}, \"features\": []}\n"
                "User Request: " + text
            )

            request_data = {
                "model": "llama-3.3-70b-versatile",
                "messages": [{"role": "user", "content": prompt}]
            }

            resp = requests.post(url, headers=headers, json=request_data, timeout=10)
            resp.raise_for_status()
            
            chat_data = resp.json()
            content = chat_data["choices"][0]["message"]["content"]
            
            # Extract JSON
            parsed = None
            match = re.search(r'\{.*\}', content, re.DOTALL)
            if match:
                try:
                    parsed = json.loads(match.group(0))
                except Exception:
                    pass
            
            if not parsed:
                parsed = json.loads(content)
            
            # If lat/lon are null, try to geocode the city or text
            loc = parsed.get("location", {})
            if loc.get("lat") is None:
                city_name = loc.get("city") or loc.get("area") or text
                coords = geocode_or_default(city_name)
                if coords["lat"] is not None:
                    parsed["location"] = coords

            # Ensure city and area are at the top level for the planner
            parsed["city"] = loc.get("city") or ""
            parsed["area_name"] = loc.get("area") or ""

            print(f"[Groq-Direct] Parsed: {parsed}")
            return parsed

        except Exception as e:
            print(f"Groq direct API error: {e}")
            coords = geocode_or_default(text)
            return {
                "location": coords,
                "features": [text],
                "city": text,
                "area_name": ""
            }

    # Fallback
    coords = geocode_or_default(text)
    return {
        "location": coords,
        "features": [text],
        "city": text,
        "area_name": ""
    }