from django.http import HttpResponse, Http404
from django.shortcuts import render
from django.utils.safestring import mark_safe
import re
import json

import os
import sys
from pathlib import Path

# Ensure the project's root is on sys.path so data.* modules import correctly
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
DATA_DIR = PROJECT_ROOT / 'data'
if str(DATA_DIR) not in sys.path:
    sys.path.insert(0, str(DATA_DIR))

# Import existing domain logic after path fix
from data.spots import SPOTS
from data.webtables import weekoverzicht, table_per_day, table_html, table_html_simple
from data.models import MODELS
from backend.data_processor import get_processor


def _get_spot_by_name(spot_name: str):
    for spot in SPOTS:
        if spot.name.lower() == spot_name.lower():
            return spot
    return None


def home(request):
    return render(request, 'forecast/home.html', {})


def week_overview(request):
    try:
        processor = get_processor()
        content = processor.get_forecast_data()
        html = content.get('week_overview', '')
        if request.GET.get('plain') == '1':
            html = _sanitize_embedded_html(html)
            return HttpResponse(html)
        return render(request, 'forecast/embed.html', { 'content': mark_safe(html) })
    except Exception as e:
        error_html = f"<p>Error loading week overview: {str(e)}</p>"
        if request.GET.get('plain') == '1':
            return HttpResponse(error_html)
        return render(request, 'forecast/embed.html', { 'content': mark_safe(error_html) })


def spot_table(request, spot_name: str):
    try:
        processor = get_processor()
        content = processor.get_forecast_data()
        
        if spot_name not in content.get('spot_tables', {}):
            spot = _get_spot_by_name(spot_name)
            if spot is None:
                raise Http404("Spot not found")
            # Return error message if spot data not available
            error_html = f"<p>Forecast data for {spot_name} is currently being updated. Please try again in a few minutes.</p>"
            if request.GET.get('plain') == '1':
                return HttpResponse(error_html)
            return render(request, 'forecast/embed.html', { 'content': mark_safe(error_html) })
        
        html = content['spot_tables'].get(spot_name, '')
        if request.GET.get('plain') == '1':
            html = _sanitize_embedded_html(html)
            return HttpResponse(html)
        return render(request, 'forecast/embed.html', { 'content': mark_safe(html) })
    except Exception as e:
        error_html = f"<p>Error loading forecast for {spot_name}: {str(e)}</p>"
        if request.GET.get('plain') == '1':
            return HttpResponse(error_html)
        return render(request, 'forecast/embed.html', { 'content': mark_safe(error_html) })


def spot_widget(request, spot_name: str):
    try:
        processor = get_processor()
        content = processor.get_forecast_data()
        
        if spot_name not in content.get('spot_widgets', {}):
            spot = _get_spot_by_name(spot_name)
            if spot is None:
                raise Http404("Spot not found")
            # Return error message if spot data not available
            error_html = f"<p>Widget data for {spot_name} is currently being updated.</p>"
            return render(request, 'forecast/embed.html', { 'content': mark_safe(error_html) })
        
        html = content['spot_widgets'].get(spot_name, '')
        return render(request, 'forecast/embed.html', { 'content': mark_safe(html) })
    except Exception as e:
        error_html = f"<p>Error loading widget for {spot_name}: {str(e)}</p>"
        return render(request, 'forecast/embed.html', { 'content': mark_safe(error_html) })


def _sanitize_embedded_html(html) -> str:
    # Ensure html is a string
    if html is None:
        return ""
    if not isinstance(html, str):
        html = str(html)
    
    # Remove <head>...</head>
    html = re.sub(r"<head[\s\S]*?</head>", "", html, flags=re.IGNORECASE)
    # Remove wrapping <body> tags
    html = re.sub(r"</?body[^>]*>", "", html, flags=re.IGNORECASE)
    # Trim stray whitespace
    return html.strip()


def health_check(request):
    """Health check endpoint for monitoring"""
    return HttpResponse("OK", status=200)


def cache_status(request):
    """Get cache status information"""
    processor = get_processor()
    status = processor.get_cache_status()
    return HttpResponse(
        json.dumps(status, indent=2),
        content_type='application/json'
    )


def api_usage_status(request):
    """Get API usage status information"""
    processor = get_processor()
    status = processor.get_api_usage_status()
    return HttpResponse(
        json.dumps(status, indent=2),
        content_type='application/json'
    )


def refresh_cache(request):
    """Manually refresh the forecast cache"""
    try:
        processor = get_processor()
        data = processor.get_forecast_data(force_refresh=True)
        spots_count = len(data.get('spots_processed', []))
        return HttpResponse(
            f"Cache refreshed successfully. Updated {spots_count} spots.",
            status=200
        )
    except Exception as e:
        return HttpResponse(
            f"Error refreshing cache: {str(e)}",
            status=500
        )

# Create your views here.
