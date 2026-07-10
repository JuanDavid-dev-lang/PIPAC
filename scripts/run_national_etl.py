import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from modules.latest_reports.etl.pipeline import LatestReportsPipeline

if __name__ == "__main__":
    print("Starting ETL pipeline for national data (limiting to 100k for demonstration)...")
    pipeline = LatestReportsPipeline(PROJECT_ROOT)
    
    # We will only run 'hurtos_modalidades' for this demo to save time and memory.
    # We patch fetch_all temporarily to use a smaller limit for training
    from modules.latest_reports.etl.socrata_fetcher import SocrataFetcher
    original_fetch_all = SocrataFetcher.fetch_all
    def mock_fetch_all(self, limit=50000):
        return original_fetch_all(self, limit=50000)
    
    SocrataFetcher.fetch_all = mock_fetch_all
    
    results = pipeline.run_full(['hurtos_modalidades'])
    print(f"Pipeline results: {results}")
