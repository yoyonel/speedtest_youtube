import atexit
import io
import re
from contextlib import redirect_stdout
from dataclasses import dataclass, field
from typing import Match, AnyStr, Optional

import click_spinner
import timeout_decorator
import typer
import youtube_dl
from humanfriendly import parse_size

from speedtest_youtube.services.render.with_table import show_results_in_table

regex = r"\[download\][ ]{1,}(?P<percent>\d+(?:\.\d+)?)%[ ]{1,}of[ ]{1,}(?P<total_size>[.0-9]+.iB)[ ]{1,}at[ ]{1,}(?P<dl_rate>[.0-9]+.iB)\/s"
stdout_capture_streaming = io.StringIO()


@dataclass(frozen=True)
class YoutubeDownloadSample:
    """
    (Data)Class to grab youtube-dl download sample
    """
    percent: float
    dl_rate: float
    total_size: int = field(repr=False)

    @staticmethod
    def from_match_re(match: Match[AnyStr]):
        return YoutubeDownloadSample(
            percent=float(match.group("percent")),
            total_size=match.group("total_size"),
            # https://humanfriendly.readthedocs.io/en/latest/api.html?highlight=format_size#humanfriendly.parse_size
            dl_rate=round(parse_size(match.group("dl_rate")) / 1024 / 1024, 2) * 8,
        )

    def __repr__(self):
        return f"{self.percent} {self.dl_rate}"


def yt_dl_capture_exit():
    yt_dl_stdout = stdout_capture_streaming.getvalue()
    # https://www.regular-expressions.info/named.html
    # https://regex101.com/r/q0fbm4/2
    matches = re.finditer(regex, yt_dl_stdout, re.MULTILINE)
    # for yt_dl_sample in map(YoutubeDownloadSample.from_match_re, matches):
    #     typer.echo(yt_dl_sample)
    show_results_in_table([(yt_dl_sample.percent, yt_dl_sample.dl_rate) for yt_dl_sample in map(YoutubeDownloadSample.from_match_re, matches)])


def yt_dl_cli(
        yt_uri: str,
        yt_country: str,
        yt_dl_options: str,
        timeout_seconds: Optional[float]
):
    argv = f"{yt_dl_options} {yt_country} https://youtu.be/{yt_uri}"
    with redirect_stdout(stdout_capture_streaming) as capture:
        with click_spinner.spinner():
            # https://docs.python.org/3/library/atexit.html
            atexit.register(yt_dl_capture_exit)

            @timeout_decorator.timeout(seconds=timeout_seconds)
            def _call_youtube_dl():
                youtube_dl.main(argv.split())

            try:
                _call_youtube_dl()
            except timeout_decorator.TimeoutError:
                typer.echo("Timeout")
                atexit.unregister(yt_dl_capture_exit)
    yt_dl_capture_exit()
