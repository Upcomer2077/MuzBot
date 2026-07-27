from aiogram.types import FSInputFile, MaybeInaccessibleMessageUnion


def answer_audio_cached(
    message: MaybeInaccessibleMessageUnion,
    *,
    audio_file: str,
):
    """Send an audio file to the user using an existing Telegram file ID.

    Args:
        message: The incoming Telegram message object.
        audio_file: The unique Telegram file identifier string.

    Returns:
        An awaitable Telegram message object containing the sent audio.
    """
    return message.answer_audio(
        audio=audio_file,
    )


def answer_audio(
    message: MaybeInaccessibleMessageUnion,
    *,
    audio_file: FSInputFile,
    thumb_file: FSInputFile | None,
    title: str,
    artist: str,
):
    """Upload and send a local audio file to the user with specific metadata and thumbnail.

    Args:
        message: The incoming Telegram message object.
        audio_file: The local filesystem input file pointer for the audio track.
        thumb_file: The local filesystem input file pointer for the album art, or None.
        title: The track title name string.
        artist: The track performer name string.

    Returns:
        An awaitable Telegram message object containing the sent audio.
    """
    return message.answer_audio(
        audio=audio_file,
        thumbnail=thumb_file,
        title=title,
        performer=artist,
    )
