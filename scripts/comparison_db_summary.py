import scripts_common_setup

import logging
from pathlib import Path

from llm_comparison.comparison_storage import (db_stats,
                                               get_comparison_results_db)
from llm_comparison.llm_comparison import COMPARISON_STORAGE_DB_FILENAME
from storage import cache_friendly_file_storage

if __name__ == "__main__":
    db = get_comparison_results_db(
        Path(cache_friendly_file_storage.directory) / COMPARISON_STORAGE_DB_FILENAME
    )
    logging.info(db_stats(db))