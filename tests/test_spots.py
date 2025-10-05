"""
Tests for the spots module - core spot functionality and data processing.
"""
import pytest
import pandas as pd
import numpy as np
from datetime import datetime
import pytz
from unittest.mock import Mock, patch

from data.spots import Spot, SpotInfo, SPOTS, find_spot, enrich_input_data, compute_angle, compute_shelter


class TestSpotInfo:
    """Test SpotInfo dataclass."""
    
    def test_spot_info_creation(self):
        """Test SpotInfo creation with different pier values."""
        spot_info = SpotInfo(pier=0)
        assert spot_info.pier == 0
        
        spot_info_neg = SpotInfo(pier=-1)
        assert spot_info_neg.pier == -1
        
        spot_info_pos = SpotInfo(pier=1)
        assert spot_info_pos.pier == 1


class TestSpot:
    """Test Spot class functionality."""
    
    def test_spot_creation(self, mock_spot):
        """Test Spot object creation."""
        assert mock_spot.name == "TestSpot"
        assert mock_spot.lat == 52.474773
        assert mock_spot.long == 4.535204
        assert mock_spot.richting == 290.0
        assert mock_spot.db_name == "ZV"
        assert mock_spot.spot_info.pier == 0
    
    def test_spot_equality(self, mock_spot):
        """Test Spot equality comparison."""
        spot_info = SpotInfo(pier=0)
        same_spot = Spot(
            richting=290.0,
            name="TestSpot",
            lat=52.474773,
            long=4.535204,
            db_name="ZV",
            spot_info=spot_info
        )
        
        different_spot = Spot(
            richting=270.0,
            name="DifferentSpot",
            lat=52.0,
            long=4.0,
            db_name="ZV",
            spot_info=spot_info
        )
        
        assert mock_spot == same_spot
        assert mock_spot != different_spot
    
    @patch('data.spots.surffeedback.load')
    def test_feedback_method(self, mock_load, mock_spot, sample_feedback_data):
        """Test spot feedback method."""
        mock_load.return_value = sample_feedback_data
        
        # Test with only_spot_data=True
        result = mock_spot.feedback(only_spot_data=True)
        assert len(result) >= 0  # Should return filtered data
        
        # Test with only_spot_data=False
        result_all = mock_spot.feedback(only_spot_data=False)
        assert len(result_all) == len(sample_feedback_data)
    
    @patch('data.spots.stormglass.load_data')
    def test_hindcast_input(self, mock_load_data, mock_spot, sample_weather_data):
        """Test _hindcast_input method."""
        mock_load_data.return_value = sample_weather_data
        
        result = mock_spot._hindcast_input()
        
        # Should return enriched data with additional columns
        expected_columns = ['waveOnshore', 'waveSideshore', 'windOnshore', 'windSideshore']
        for col in expected_columns:
            assert col in result.columns
    
    def test_add_spot_info(self, mock_spot, sample_weather_data):
        """Test add_spot_info method."""
        mock_spot.add_spot_info(sample_weather_data)
        
        # Should add pier information
        assert 'pier' in sample_weather_data.columns
        assert sample_weather_data['pier'].iloc[0] == 0


class TestSpotFunctions:
    """Test utility functions in spots module."""
    
    def test_find_spot(self):
        """Test find_spot function."""
        # Test finding existing spot
        spot = find_spot("ZV")
        assert spot.name == "ZV"
        
        # Test finding spot with case insensitive search
        spot_lower = find_spot("zv")
        assert spot_lower.name == "ZV"
        
        # Test finding spot with partial match
        spot_partial = find_spot("schev")
        assert "schev" in spot_partial.name.lower()
        
        # Test non-existent spot
        with pytest.raises(ValueError, match="Spot not found"):
            find_spot("NonExistentSpot")
    
    def test_compute_angle(self):
        """Test compute_angle function."""
        data = pd.Series([0, 90, 180, 270])
        richting = 0
        
        result = compute_angle(data, richting)
        expected = pd.Series([0, 90, 180, 270])
        pd.testing.assert_series_equal(result, expected)
        
        # Test with different richting
        richting = 90
        result = compute_angle(data, richting)
        expected = pd.Series([270, 0, 90, 180])
        pd.testing.assert_series_equal(result, expected)
    
    def test_compute_shelter(self):
        """Test compute_shelter function."""
        # Test angles that should give maximum shelter
        assert compute_shelter(0) == 0.0
        assert compute_shelter(180) == 0.0
        
        # Test angles that should give some shelter
        assert 0 < compute_shelter(10) < 0.4
        assert 0 < compute_shelter(170) < 0.4
        
        # Test angles that should give maximum shelter
        assert compute_shelter(90) == 0.7
    
    def test_enrich_input_data(self, mock_spot, sample_weather_data):
        """Test enrich_input_data function."""
        result = enrich_input_data(sample_weather_data, mock_spot)
        
        # Check that new columns are added
        expected_new_columns = [
            'waveOnshore', 'waveSideshore', 'windOnshore', 'windSideshore',
            'windMagOnShore', 'windMagSideShore', 'shelterWind', 'waveEnergyOnshore',
            'seaRise', 'pier'
        ]
        
        for col in expected_new_columns:
            assert col in result.columns
        
        # Check that original columns are preserved
        original_columns = sample_weather_data.columns.tolist()
        for col in original_columns:
            assert col in result.columns


class TestSPOTS:
    """Test SPOTS list and spot definitions."""
    
    def test_spots_list_not_empty(self):
        """Test that SPOTS list is not empty."""
        assert len(SPOTS) > 0
    
    def test_all_spots_have_required_attributes(self):
        """Test that all spots have required attributes."""
        for spot in SPOTS:
            assert hasattr(spot, 'name')
            assert hasattr(spot, 'lat')
            assert hasattr(spot, 'long')
            assert hasattr(spot, 'richting')
            assert hasattr(spot, 'db_name')
            assert hasattr(spot, 'spot_info')
            
            # Check data types
            assert isinstance(spot.name, str)
            assert isinstance(spot.lat, (int, float))
            assert isinstance(spot.long, (int, float))
            assert isinstance(spot.richting, (int, float))
            assert isinstance(spot.db_name, str)
            assert isinstance(spot.spot_info, SpotInfo)
    
    def test_spot_coordinates_valid(self):
        """Test that spot coordinates are within reasonable bounds."""
        for spot in SPOTS:
            # Latitude should be between -90 and 90
            assert -90 <= spot.lat <= 90
            
            # Longitude should be between -180 and 180
            assert -180 <= spot.long <= 180
            
            # For Dutch spots, latitude should be around 52-53
            if spot.name in ['ZV', 'Schev', 'Noordwijk', 'Ijmuiden', 'Wijk', 'Camperduin']:
                assert 51 <= spot.lat <= 54
                assert 3 <= spot.long <= 6
    
    def test_spot_names_unique(self):
        """Test that spot names are unique."""
        names = [spot.name for spot in SPOTS]
        assert len(names) == len(set(names))
    
    def test_spot_richting_valid(self):
        """Test that spot richting values are valid angles."""
        for spot in SPOTS:
            assert 0 <= spot.richting < 360
