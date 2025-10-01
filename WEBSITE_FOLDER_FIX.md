# Website Folder Fix Summary

## Problem
The `website_folder` variable was not defined in `data/plotting.py`, causing import errors in `data/webtables.py` when trying to write table files to disk.

## Root Cause
- `data/webtables.py` was importing `website_folder` from `data/plotting.py`
- `website_folder` was only defined in `data/plotting_html.py` with a hardcoded path
- The import was failing because the variable didn't exist in the expected location

## Solution
1. **Added `website_folder` definition to `data/plotting.py`**:
   ```python
   # Define website folder for Django site
   website_folder = Path(__file__).resolve().parents[1] / "site"
   ```

2. **Uncommented the `save_to_web` function** in `data/plotting.py`:
   ```python
   def save_to_web(spot_name):
       plt.savefig(website_folder / f"{spot_name}.png")
   ```

## Result
- `website_folder` now correctly points to `D:\persoonlijk\magicnorthseaweed\site`
- The path exists and contains the expected `tables/` and `tables_widget/` subdirectories
- All imports in `data/webtables.py` now work correctly
- The Django site structure is properly supported

## Files Modified
- `data/plotting.py`: Added `website_folder` definition and uncommented `save_to_web` function

## Verification
```bash
cd data
python -c "from plotting import website_folder; print('website_folder:', website_folder); print('exists:', website_folder.exists())"
# Output: website_folder: D:\persoonlijk\magicnorthseaweed\site
#         exists: True
```

The fix ensures that when `web_update_silent.py` runs and calls functions like `webtables.write_table_per_day()` and `webtables.write_simple_table()`, the files are written to the correct Django site directory structure.
