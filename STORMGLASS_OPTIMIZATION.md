# StormGlass API Optimization

This document explains the optimized StormGlass API usage system that intelligently manages API keys to maximize efficiency and prevent quota exhaustion.

## 🎯 Problem Solved

**Before:** Random key selection led to:
- Uneven API usage across keys
- Some keys hitting limits while others were unused
- No tracking of daily quotas
- Risk of exhausting all keys early in the day
- No visibility into API usage patterns

**After:** Intelligent key rotation provides:
- ✅ Even distribution of API calls across all keys
- ✅ Each key used up to exactly 10 times per day
- ✅ Persistent usage tracking across application restarts
- ✅ Automatic daily quota reset
- ✅ Real-time usage monitoring
- ✅ Fallback mechanisms when keys are exhausted
- ✅ Works in both development and production environments

## 🏗️ Architecture

### Core Components

1. **`StormGlassApiManager`** (`data/stormglass_api_manager.py`)
   - Manages all 6 API keys intelligently
   - Tracks daily usage per key
   - Implements least-used-first rotation
   - Persists usage data to JSON file
   - Thread-safe for concurrent access

2. **Modified `stormglass.py`**
   - Replaced random key selection with optimized manager
   - Extracts usage information from API responses
   - Improved error handling and logging

3. **Usage Monitor** (`data/stormglass_usage_monitor.py`)
   - CLI tool for monitoring API usage
   - Visual usage bars and status indicators
   - Export functionality for analysis

4. **Test Suite** (`test_stormglass_optimization.py`)
   - Validates optimization functionality
   - Simulates API usage patterns

## 📊 Usage Information Extraction

The system automatically extracts usage information from StormGlass API responses:

```json
{
  "meta": {
    "cost": 1,           // API calls consumed by this request
    "dailyQuota": 10,    // Daily limit for this key
    "requestCount": 3    // Total requests made today with this key
  }
}
```

This information is used to:
- Update internal usage counters
- Validate quota limits
- Track actual vs. expected usage

## 🔄 Key Rotation Algorithm

### Selection Strategy
1. **Filter Available Keys**: Only consider keys with remaining quota
2. **Sort by Usage**: Prefer least-used keys first
3. **Consider Recency**: Among equally-used keys, prefer least recently used
4. **Automatic Reset**: Daily counters reset at midnight

### Example Rotation Pattern
```
Day 1:
Key_0: [████████░░] 8/10 requests
Key_1: [██████░░░░] 6/10 requests  ← Next selected
Key_2: [██████████] 10/10 requests (exhausted)
Key_3: [████░░░░░░] 4/10 requests
Key_4: [██░░░░░░░░] 2/10 requests
Key_5: [░░░░░░░░░░] 0/10 requests
```

## 💾 Persistent Storage

Usage data is stored in `data/stormglass/api_usage.json`:

```json
{
  "key_0": {
    "key": "1feeb6a8-5bc9-11ee-a26f-0242ac130002-1feeb702-5bc9-11ee-a26f-0242ac130002",
    "daily_quota": 10,
    "requests_today": 3,
    "last_reset_date": "2025-10-02",
    "last_used": "2025-10-02T14:30:15.123456",
    "total_requests": 127
  }
}
```

This ensures:
- Usage tracking survives application restarts
- Historical data is preserved
- Daily resets work correctly across deployments

## 🛠️ Usage Examples

### Basic Integration
```python
from data.stormglass_api_manager import get_api_manager

# Get optimized API manager
manager = get_api_manager()

# Make an API request (automatically selects best key)
json_data, key_id = manager.make_request(
    'https://api.stormglass.io/v2/weather/point',
    params={'lat': 52.47, 'lng': 4.53, 'params': 'waveHeight'}
)

print(f"Used key: {key_id}")
```

### Monitor Usage
```bash
# Show current usage status
python data/stormglass_usage_monitor.py

# Export usage data for analysis
python data/stormglass_usage_monitor.py export

# Reset usage data (for testing)
python data/stormglass_usage_monitor.py reset
```

### Test the System
```bash
# Run basic functionality tests
python test_stormglass_optimization.py

# Simulate API usage patterns
python test_stormglass_optimization.py simulate
```

## 📈 Benefits

### Efficiency Gains
- **60 API calls per day** (6 keys × 10 calls) vs. random usage
- **Even distribution** prevents early exhaustion
- **Automatic rotation** maximizes available quota

### Reliability Improvements
- **Graceful degradation** when keys are exhausted
- **Persistent tracking** survives restarts
- **Thread-safe** for concurrent forecast generation

### Monitoring & Debugging
- **Real-time visibility** into API usage
- **Historical tracking** for usage analysis
- **Clear error messages** when limits are reached

### Production Ready
- **Environment agnostic** (works in development and production)
- **No configuration required** (uses existing API keys)
- **Backward compatible** with existing code

## 🚨 Error Handling

### When All Keys Are Exhausted
```
Exception: All API keys have reached their daily limit. Please wait until tomorrow.
```

### When API Request Fails
```
Exception: Request failed with key key_2: HTTPSConnectionPool timeout
```

### Automatic Recovery
- Daily quotas reset automatically at midnight
- Failed requests don't consume quota
- System continues with remaining available keys

## 🔧 Configuration

### Default Settings
- **Daily Quota**: 10 requests per key (from API response)
- **Total Keys**: 6 keys
- **Storage Location**: `data/stormglass/api_usage.json`
- **Reset Time**: Midnight (based on system timezone)

### Customization
The system can be customized by modifying `StormGlassApiManager`:
- Change storage location
- Adjust quota limits
- Add new API keys
- Modify rotation algorithm

## 📊 Monitoring Dashboard

The usage monitor provides a visual dashboard:

```
StormGlass API Usage Summary
============================================================
Date: 2025-10-02 14:30:15
Total API Keys: 6
Keys Available: 4
Total Requests Today: 23/60
Remaining Requests: 37

Individual Key Status:
------------------------------------------------------------
✅ key_0: [████████░░░░░░░░░░░░] 8/10
    Last used: 14:25:30 | Total: 127 requests
✅ key_1: [██████░░░░░░░░░░░░░░] 6/10
    Last used: 14:20:15 | Total: 98 requests
❌ key_2: [████████████████████] 10/10
    Last used: 14:30:00 | Total: 156 requests
✅ key_3: [████░░░░░░░░░░░░░░░░] 4/10
    Last used: 13:45:22 | Total: 89 requests
```

## 🚀 Deployment

### For Development
No changes required - the system automatically detects and uses the optimized API manager.

### For Production
1. Ensure `data/stormglass/` directory exists and is writable
2. The usage tracking file will be created automatically
3. Monitor usage with the provided CLI tools

### For Docker/Railway
The system works seamlessly in containerized environments:
- Usage data persists in the container filesystem
- Daily resets work correctly with container timezone
- No external dependencies required

## 📝 Migration Notes

### From Old System
- **No code changes required** in existing forecast generation
- **Automatic migration** from random to optimized selection
- **Backward compatible** with all existing functionality

### Benefits Immediate
- Optimization takes effect immediately
- No warm-up period required
- Existing cache files remain valid

This optimization ensures your StormGlass API usage is maximally efficient, reliable, and observable, providing the foundation for consistent surf forecast generation.
