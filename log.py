from pathlib import Path
from Logger import Logger
from consts import DATA_DIRECTORY


_FILENAME = "log.md"
_DIR = Path(DATA_DIRECTORY)


logger = Logger()
logger.createLog(_DIR, _FILENAME)
with open(Path(_DIR / _FILENAME), "w") as file:
    file.write('```python\n')