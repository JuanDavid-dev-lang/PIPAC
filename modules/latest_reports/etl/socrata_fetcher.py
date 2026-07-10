import logging
import time
import requests
import pandas as pd
from typing import Optional

logger = logging.getLogger(__name__)

class SocrataFetcher:
    def __init__(self, dataset_id: str, app_token: Optional[str] = None, base_url: str = 'https://www.datos.gov.co/resource'):
        self.dataset_id = dataset_id
        self.app_token = app_token
        self.base_url = base_url
        self.endpoint = f"{self.base_url}/{self.dataset_id}.json"
        
    def _get_headers(self) -> dict:
        headers = {}
        if self.app_token:
            headers['X-App-Token'] = self.app_token
        return headers

    def _fetch_page(self, limit: int, offset: int, where_clause: Optional[str] = None) -> list[dict]:
        params = {
            '$limit': limit,
            '$offset': offset,
            '$order': ':id'
        }
        if where_clause:
            params['$where'] = where_clause
            
        for attempt in range(3):
            try:
                response = requests.get(self.endpoint, params=params, headers=self._get_headers())
                response.raise_for_status()
                return response.json()
            except Exception as e:
                logger.warning(f"Error fetching page (attempt {attempt+1}): {e}")
                time.sleep(2 ** attempt)
        raise Exception(f"Failed to fetch data from {self.endpoint} after 3 attempts")

    def fetch_all(self, limit: int = 50000) -> pd.DataFrame:
        logger.info(f"Fetching all data for dataset {self.dataset_id}")
        return self._fetch_paginated(limit=limit)

    def fetch_since(self, since_date: str, date_col: str, limit: int = 50000) -> pd.DataFrame:
        logger.info(f"Fetching data for dataset {self.dataset_id} since {since_date}")
        where_clause = f"{date_col} >= '{since_date}'"
        return self._fetch_paginated(limit=limit, where_clause=where_clause)

    def _fetch_paginated(self, limit: int, where_clause: Optional[str] = None) -> pd.DataFrame:
        all_data = []
        offset = 0
        while True:
            logger.info(f"Fetching rows {offset} to {offset+limit}")
            data = self._fetch_page(limit, offset, where_clause)
            if not data:
                break
            all_data.extend(data)
            offset += limit
            if len(data) < limit:
                break
        return pd.DataFrame(all_data)

    def fetch_count(self, where_clause: Optional[str] = None) -> int:
        params = {'$select': 'count(*)'}
        if where_clause:
            params['$where'] = where_clause
        try:
            response = requests.get(self.endpoint, params=params, headers=self._get_headers())
            response.raise_for_status()
            data = response.json()
            if data and isinstance(data, list) and 'count' in data[0]:
                return int(data[0]['count'])
        except Exception as e:
            logger.error(f"Error fetching count: {e}")
        return 0
