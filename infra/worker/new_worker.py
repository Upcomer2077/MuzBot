from interfaces.iworkerpipe import IWorkerPipeline


class WorkerPipe(IWorkerPipeline):
    def download_track(self, track_id: str):
        return self._MT.download_track(track_id)
