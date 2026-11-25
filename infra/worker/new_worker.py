from infra.tools.MusicTools import MT
from interfaces.iworkerpipe import IWorkerPipeline


class WorkerPipe(IWorkerPipeline):
    def download_track(self, track_id: str):
        return MT.download_track(track_id)
