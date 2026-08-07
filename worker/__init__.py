from worker.new_worker import WorkerPipe
from worker.worker import PlaylistQueueManager

PLAYLIST_QUEUE = PlaylistQueueManager()
TRACK_PIPELINE = WorkerPipe()
