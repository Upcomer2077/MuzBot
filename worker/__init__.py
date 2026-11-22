from _logger import LOGGER
from worker.new_worker import WorkerPipe

TRACK_PIPELINE = WorkerPipe(LOGGER)
"Instance of worker loop"
