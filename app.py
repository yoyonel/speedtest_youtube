from __future__ import unicode_literals

import atexit

import io
from contextlib import redirect_stdout
from dataclasses import dataclass, field

import youtube_dl
from humanfriendly import parse_size


@dataclass(frozen=True)
class YoutubeDownloadSample:
    percent: int
    dl_rate: float
    total_size: int = field(repr=False)

    @staticmethod
    def from_match_re(match):
        return YoutubeDownloadSample(
            percent=match.group("percent"),
            total_size=match.group("total_size"),
            # https://humanfriendly.readthedocs.io/en/latest/api.html?highlight=format_size#humanfriendly.parse_size
            dl_rate=round(parse_size(match.group("dl_rate")) / 1024 / 1024, 2),
        )

    def __repr__(self):
        return f"{self.percent} {self.dl_rate}"


stdout_capture_streaming = io.StringIO()


def yt_dl_capture_exit():
    stdout_yt_dl = stdout_capture_streaming.getvalue()

    import re
    # https://www.regular-expressions.info/named.html
    # https://regex101.com/r/q0fbm4/2
    regex = r"\[download\][ ]{1,}(?P<percent>\d+(?:\.\d+)?)%[ ]{1,}of[ ]{1,}(?P<total_size>[.0-9]+.iB)[ ]{1,}at[ ]{1,}(?P<dl_rate>[.0-9]+.iB)\/s"
    matches = re.finditer(regex, stdout_yt_dl, re.MULTILINE)

    results = map(YoutubeDownloadSample.from_match_re, matches)
    for result in results:
        print(result)


# https://docs.python.org/3/library/atexit.html
atexit.register(yt_dl_capture_exit)


def main():
    with redirect_stdout(stdout_capture_streaming):
        yt_uri = "8cOJhLM66D4"
        yt_country = "FR"
        argv = f"-f best --no-part --no-cache-dir -o /dev/null --newline --geo-bypass-country {yt_country} https://youtu.be/{yt_uri}"

        youtube_dl.main(argv.split())


if __name__ == '__main__':
    main()
