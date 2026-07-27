import re

YTM_REGEX = re.compile(
    r"(?:https?:\/\/)?music\.youtube\.com/watch\?.*v=([a-zA-Z0-9_\-]{11})"
)
YTM_VID_REGEX = re.compile(
    r"v=([a-zA-Z0-9_\-]{11})",
)
