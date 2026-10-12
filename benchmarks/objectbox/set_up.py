import shutil

# Start fresh: remove the DB (and its model JSON) before models.py opens the store
shutil.rmtree("/tmp/objectbox-bench", ignore_errors=True)

import models  # noqa: E402,F401
