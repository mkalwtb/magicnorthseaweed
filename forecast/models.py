from django.db import models


class WeatherData(models.Model):
    """Store historical weather data from Stormglass API"""
    location_name = models.CharField(max_length=100)
    latitude = models.FloatField()
    longitude = models.FloatField()
    timestamp = models.DateTimeField()
    
    # Weather parameters
    wave_direction = models.FloatField(null=True, blank=True)
    wave_period = models.FloatField(null=True, blank=True)
    wave_height = models.FloatField(null=True, blank=True)
    wind_speed = models.FloatField(null=True, blank=True)
    wind_direction = models.FloatField(null=True, blank=True)
    current_speed = models.FloatField(null=True, blank=True)
    wind_wave_height = models.FloatField(null=True, blank=True)
    sea_level = models.FloatField(null=True, blank=True)
    
    # Computed fields
    wave_onshore = models.FloatField(null=True, blank=True)
    wind_onshore = models.FloatField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['location_name', 'timestamp']
        indexes = [
            models.Index(fields=['location_name', 'timestamp']),
            models.Index(fields=['timestamp']),
        ]


class SurfRating(models.Model):
    """Store surf rating predictions"""
    location_name = models.CharField(max_length=100)
    timestamp = models.DateTimeField()
    
    # Rating predictions
    rating = models.FloatField(null=True, blank=True)
    hoog = models.FloatField(null=True, blank=True)
    clean = models.FloatField(null=True, blank=True)
    krachtig = models.FloatField(null=True, blank=True)
    stijl = models.FloatField(null=True, blank=True)
    stroming = models.FloatField(null=True, blank=True)
    windy = models.FloatField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['location_name', 'timestamp']
        indexes = [
            models.Index(fields=['location_name', 'timestamp']),
        ]


class AlertLog(models.Model):
    """Store email alert history"""
    timestamp = models.DateTimeField()
    spot = models.CharField(max_length=100)
    rating = models.IntegerField()
    email = models.EmailField()
    alert_timestamp = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['timestamp']),
            models.Index(fields=['spot']),
        ]


class SurfFeedback(models.Model):
    """Store user surf feedback data"""
    timestamp = models.DateTimeField()
    spot = models.CharField(max_length=100)
    rating = models.IntegerField()
    # Add other feedback fields as needed
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['timestamp']),
            models.Index(fields=['spot']),
        ]


class BuoyData(models.Model):
    """Store buoy measurement data"""
    buoy_name = models.CharField(max_length=100)
    timestamp = models.DateTimeField()
    
    # Buoy parameters - add fields as needed based on your data
    wave_height = models.FloatField(null=True, blank=True)
    wave_period = models.FloatField(null=True, blank=True)
    wind_speed = models.FloatField(null=True, blank=True)
    # Add other buoy measurement fields
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['buoy_name', 'timestamp']
        indexes = [
            models.Index(fields=['buoy_name', 'timestamp']),
        ]


class SiteCache(models.Model):
    """Store cached website content"""
    cache_key = models.CharField(max_length=255, unique=True)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    
    class Meta:
        indexes = [
            models.Index(fields=['cache_key']),
            models.Index(fields=['expires_at']),
        ]
