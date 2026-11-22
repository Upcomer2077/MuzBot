from _logger import LOGGER
from infra.worker.new_worker import WorkerPipe

TRACK_PIPELINE = WorkerPipe(LOGGER)
"Instance of worker loop"
