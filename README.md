# GPS Visualization

This adds a small visualization script that reads `output/combined_data.csv` and produces two plots in `output/plots`:

- `scatter_lon_lat.png`: Scatter plot of longitude vs latitude.
- `heatmap_lon_lat.png`: Density heatmap of GPS points using a Gaussian KDE.

Prerequisites
- Python 3.8+ recommended.

Quick setup (PowerShell)

```powershell
# create and activate a virtual environment
python -m venv .venv; .\.venv\Scripts\Activate.ps1

# upgrade pip and install dependencies
python -m pip install --upgrade pip; pip install -r requirements.txt
```

Run

```powershell
python visualize_gps.py
```

Notes
- The script expects `output/combined_data.csv` to exist and contain `Y_WGS84` and `X_WGS84` columns.
- If you have a large dataset, consider subsampling or using a faster density algorithm.
