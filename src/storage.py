from interlab.context import FileStorage

# use this folder for context artifacts instead of generic "logs"
# to enable using those logs in a cache-like way to retrieve recent
# results of successful LLM queries with similar params.
CACHE_FRIENDLY_FILE_STORAGE_DIR = "context_cache"
cache_friendly_file_storage = FileStorage(CACHE_FRIENDLY_FILE_STORAGE_DIR)
