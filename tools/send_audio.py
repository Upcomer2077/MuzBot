from aiogram.types import FSInputFile, MaybeInaccessibleMessageUnion


def answer_audio_cached(
    message: MaybeInaccessibleMessageUnion,
    *,
    audio_file: str,
):
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
    return message.answer_audio(
        audio=audio_file,
        thumbnail=thumb_file,
        title=title,
        performer=artist,
    )
