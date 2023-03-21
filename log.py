from pathlib import Path
from Logger import Logger


_FILENAME = "log.md"
_DIR = Path("logs")


logger = Logger()
logger.createLog(_DIR, _FILENAME)
with open(Path(_DIR / _FILENAME), "w") as file:
    file.write('```python\n')