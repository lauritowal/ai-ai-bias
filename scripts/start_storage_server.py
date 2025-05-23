import scripts_common_setup

from interlab.context import FileStorage

from storage import cache_friendly_file_storage

storage = cache_friendly_file_storage
storage.start_server()