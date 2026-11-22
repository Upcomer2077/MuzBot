import asyncio
import os
import random
import time
from random import uniform
from typing import TYPE_CHECKING, Final, cast

import yt_dlp
from ytmusicapi.type_alias import JsonList

from config import CACHE_ROOT_DIR, MAX_PLAYLIST_TRACKS_REQUEST
from helpers.get_ytm_links import get_ytm_video_link
from helpers.time_to_seconds import time_to_seconds
from interfaces.imusictools import IMusicTools
from tools.types import (
    ArtistConcreteEntityInfoDict,
    ArtistInfoDict,
    ArtistsShortInfoDict,
    PlaylistInfoDict,
    SearchResultDict,
)
from tools.YTMusic_client import YT

if TYPE_CHECKING:
    from yt_dlp import _Params


class YTMusicTools(IMusicTools):
    def download_track(self, video_id: str):
        YOUTUBE_URL = get_ytm_video_link(video_id)

        YDL_OPTS: _Params = {
            "format": "bestaudio/best",  # Select the best audio quality available
            "writethumbnail": True,
            "extractor_args": {
                "youtube": {"player_client": ["web_embedded", "web", "tv", "android"]}
            },
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",  # Convert to MP3
                    "preferredquality": "192",  # Audio bitrate (192 kbps)
                },
            ],
            "postprocessor_args": [
                "-threads",
                "2",
                "-vn",
                "-sn",
                "-dn",
            ],
            "no_warnings": True,
            "outtmpl": f"{CACHE_ROOT_DIR}/{video_id}/%(title)s.%(ext)s",
            "sleep_interval": 5,
            "max_sleep_interval": 15,
            "quiet": True,
            "retries": 3,
        }
        self._logger.debug(f"Dl-PID for {video_id}: {os.getpid()}")
        self._logger.info(f"Attempting to download video {video_id}")
        for i in range(3):
            try:
                with yt_dlp.YoutubeDL(YDL_OPTS) as ydl:
                    ydl.download([YOUTUBE_URL])

                self._logger.info(f"Downloaded successfully: {video_id}")
                return True
            except Exception as e:
                self._logger.error(
                    f"Error while downloading video. Attempt: {i + 1}. {e}"
                )
                time.sleep(1)
                continue
        self._logger.warning(f"Download of video {video_id} failed!")
        return False

    async def extract_artist_discography(
        self, artist_id: str, *, top_only=True
    ) -> ArtistInfoDict | None:

        self._logger.debug(f"Extracting info about author {artist_id}")
        try:
            INFO = await asyncio.to_thread(YT.get_artist, artist_id)
        except Exception as e:
            self._logger.error(f"Error in extract_artist_discography: {e}")
            return None
        self._logger.debug(f"Has info about {artist_id}: {bool(INFO)}")
        albums: list[ArtistConcreteEntityInfoDict] = INFO.get("albums", {}).get(
            "results", None
        )

        singles: list[ArtistConcreteEntityInfoDict] = INFO.get("singles", {}).get(
            "results", None
        )

        if not top_only:
            if singles and len(singles):
                if "params" in INFO["singles"] and "browseId" in INFO["singles"]:
                    singles_params: str = INFO["singles"]["params"]
                    try:
                        await asyncio.sleep(uniform(1, 2))

                        MORE_INFO_SINGLES = await asyncio.to_thread(
                            YT.get_artist_albums,
                            INFO["singles"]["browseId"],
                            singles_params,
                        )
                        if len(MORE_INFO_SINGLES):
                            singles: list[ArtistConcreteEntityInfoDict] = [
                                {
                                    "title": i["title"],
                                    "browseId": i["browseId"],
                                    "audioPlaylistId": i["playlistId"],
                                    "order": len(MORE_INFO_SINGLES) - idx,
                                }
                                for idx, i in enumerate(MORE_INFO_SINGLES, start=1)
                            ]
                    except Exception as e:
                        self._logger.error(f"Error in extract_artist_discography: {e}")
                else:
                    try:
                        _singles: list[ArtistConcreteEntityInfoDict] = []
                        for idx, i in enumerate(singles, start=1):
                            await asyncio.sleep(uniform(1, 3))
                            a = await asyncio.to_thread(YT.get_album, i["browseId"])
                            _singles.append(
                                {
                                    "audioPlaylistId": a["audioPlaylistId"],
                                    "browseId": i["browseId"],
                                    "title": a["title"],
                                    "order": len(singles) - idx,
                                }
                            )
                        if len(_singles):
                            singles = _singles
                    except Exception as e:
                        self._logger.error(f"Error in extract_artist_discography: {e}")

            # +======
            if albums and len(albums):
                if "params" in INFO["albums"] and "browseId" in INFO["albums"]:
                    albums_params: str = INFO["albums"]["params"]
                    try:
                        await asyncio.sleep(uniform(1, 2))

                        MORE_INFO_ALBUMS: Final = await asyncio.to_thread(
                            YT.get_artist_albums,
                            INFO["albums"]["browseId"],
                            albums_params,
                        )

                        if len(MORE_INFO_ALBUMS):
                            albums = [
                                {
                                    "title": i["title"],
                                    "browseId": i["browseId"],
                                    "audioPlaylistId": i["playlistId"],
                                    "order": len(MORE_INFO_ALBUMS) - idx,
                                }
                                for idx, i in enumerate(MORE_INFO_ALBUMS, start=1)
                            ]
                    except Exception as e:
                        self._logger.error(f"Error in extract_artist_discography: {e}")
                else:
                    for idx, i in enumerate(albums, start=1):
                        i["order"] = len(albums) - idx

        else:
            if albums and len(albums):
                _albums: list[ArtistConcreteEntityInfoDict] = [
                    {
                        "title": i["title"],
                        "browseId": i["browseId"],
                        "audioPlaylistId": i["audioPlaylistId"],
                        "order": len(albums) - idx,
                    }
                    for idx, i in enumerate(albums, start=1)
                ]
                albums = _albums
            if singles and len(singles):
                try:
                    _singles: list[ArtistConcreteEntityInfoDict] = []
                    for idx, i in enumerate(singles, start=1):
                        await asyncio.sleep(uniform(1, 3))

                        c = await asyncio.to_thread(YT.get_album, i["browseId"])
                        _singles.append(
                            {
                                "audioPlaylistId": c["audioPlaylistId"],
                                "browseId": i["browseId"],
                                "title": c["title"],
                                "order": len(singles) - idx,
                            }
                        )
                    if len(_singles):
                        singles = _singles
                except Exception as e:
                    self._logger.error(f"Error in extract_artist_discography: {e}")

        return ArtistInfoDict(
            albums=albums,
            singles=singles,
            name=INFO["name"],
        )

    async def extract_track_info(self, video_id: str) -> SearchResultDict | None:
        def _extract(
            video_id: str,
        ) -> dict[str, str] | None:
            """Execute synchronous metadata extraction for a video without initiating a download.

            Args:
                video_id: Unique YouTube Music track video identifier.

            Returns:
                A dictionary containing raw track metadata, or None if an exception occurs.
            """

            try:
                self._logger.info(f"Extracting info about video {video_id}")
                return YT.get_song(videoId=video_id).get("videoDetails", None)

            except Exception as e:
                self._logger.error(f"Error while getting {video_id} info: {e}")
                return None

        self._logger.debug(f"Extracting info about {video_id}")

        async with YT.track_lock:
            await asyncio.sleep(random.uniform(1.0, 2.0))
            VIDEO = await asyncio.to_thread(_extract, video_id)

        self._logger.debug(f"Has info about {video_id}: {bool(VIDEO)}")

        if VIDEO:
            title: str = VIDEO.get("title") or "UNKNOWN"
            artist = VIDEO.get("author") or "unknown"
            duration_seconds: int = int(VIDEO.get("lengthSeconds", 0) or 0)

            return SearchResultDict(
                title=title,
                artist=artist,
                video_id=video_id,
                duration=None,
                duration_seconds=duration_seconds,
            )

    async def extract_playlist_info(
        self,
        playlist_id: str,
    ) -> tuple[PlaylistInfoDict, list[SearchResultDict]] | None:

        def _extract(link: str):
            """Execute synchronous metadata extraction for a video without initiating a download.

            Args:
                link: YouTube Music track video link.

            Returns:
                A dictionary containing raw track metadata, or None if an exception occurs.
            """
            try:
                return YT.get_playlist(link, limit=MAX_PLAYLIST_TRACKS_REQUEST)

            except Exception:
                return

        self._logger.debug(f"Extracting info about playlist {playlist_id}")

        async with YT.playlist_lock:
            await asyncio.sleep(random.uniform(1.0, 3.0))
            PLAYLIST = await asyncio.to_thread(_extract, playlist_id)

        self._logger.debug(f"Info about playlist {bool(PLAYLIST)}")
        if PLAYLIST is None or "tracks" not in PLAYLIST:
            return None

        videos: list[SearchResultDict] = []
        info: list = PLAYLIST["tracks"]

        author: str | None = "unknown"
        if playlist_id.startswith("OLAK5uy_"):
            author = ", ".join([a["name"] for a in info[0].get("artists", [])])
        elif playlist_id.startswith(("PL", "RD")):
            author = PLAYLIST.get("author", {}).get("name", None)

        for track in info:
            if not track.get("videoId"):
                continue
            _artists = ", ".join([a["name"] for a in track["artists"]])

            videos.append(
                SearchResultDict(
                    title=track.get("title") or "UNKNOWN",
                    artist=_artists.replace(" - Topic", ""),
                    video_id=track.get("videoId"),
                    duration=track.get("duration"),
                    duration_seconds=track.get("duration_seconds") or 0,
                )
            )
        playlist_title: str | None = PLAYLIST.get("title", None)
        if playlist_title:
            playlist_title = playlist_title.replace("Album - ", "")

        return (
            PlaylistInfoDict(title=playlist_title, id=PLAYLIST["id"], author=author),
            videos,
        )

    async def get_like_pl(self, video_id: str) -> list[SearchResultDict] | None:

        async with YT.rec_lock:
            await asyncio.sleep(uniform(1, 2))
            resp = await asyncio.to_thread(
                YT.get_watch_playlist, videoId=video_id, limit=25
            )

        tracks = resp["tracks"]

        if not tracks or isinstance(tracks, str):
            return None

        result: list[SearchResultDict] = [
            SearchResultDict(
                video_id=i["videoId"],
                title=i["title"],
                duration=i["length"],
                artist=", ".join(a["name"] for a in i["artists"]),
                duration_seconds=time_to_seconds(i["length"]),
            )
            for i in tracks[1:]
        ]

        return result

    async def search_artists_in(self, performer: str) -> list[ArtistsShortInfoDict]:

        resp = await asyncio.to_thread(YT.search, performer, filter="artists", limit=3)

        result: list[ArtistsShortInfoDict] = []

        for p in resp[:15]:
            result.append({"name": p["artist"], "id": p["browseId"]})

        return result

    async def search_track_in(
        self, search_query: str, limit: int = 27 * 2
    ) -> list[SearchResultDict]:

        def _extract(query: str, limit: int):
            RES1 = YT.search(query=query, filter="songs", limit=limit)
            RES2 = YT.search(query=query, filter="videos", limit=limit)

            result: JsonList = []
            for i in range(0, max(len(RES1), len(RES2)), 4):
                chunk1 = RES1[i : i + 4]
                if chunk1:
                    result.extend(chunk1)

                chunk2 = RES2[i : i + 4]
                if chunk2:
                    result.extend(chunk2)

            return result

        self._logger.debug(f"Extracting info query: {search_query}")

        try:
            async with YT.search_lock:
                await asyncio.sleep(1)
                SEARCH_RESULTS = await asyncio.to_thread(_extract, search_query, limit)
            self._logger.debug(f"Found info query: {bool(SEARCH_RESULTS)}")
        except Exception:
            self._logger.critical(f'Can\'t pull info from "{search_query}" query')
            return cast(list[SearchResultDict], [])

        video_ids: list[SearchResultDict] = []

        for item in SEARCH_RESULTS[: max(limit, 1)]:
            title: str = item.get("title") or "Unknown"
            artist = ", ".join([artist["name"] for artist in item.get("artists", [])])
            video_id: str | None = item.get("videoId") or None
            duration: str = item.get("duration") or "0:00"
            duration_seconds: int = item.get("duration_seconds", 0) or 0

            if video_id:
                video_ids.append(
                    SearchResultDict(
                        title=title,
                        artist=artist,
                        video_id=video_id,
                        duration=duration,
                        duration_seconds=duration_seconds,
                    )
                )

        return video_ids
