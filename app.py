from __future__ import unicode_literals

import atexit
import io
import re
from contextlib import redirect_stdout
from dataclasses import dataclass, field
from functools import partial
from pprint import pformat
from typing import AnyStr, Match, List

import click_spinner
import typer
import youtube_dl
from click._termui_impl import ProgressBar
from humanfriendly import parse_size

app = typer.Typer()
stdout_capture_streaming = io.StringIO()

regex = r"\[download\][ ]{1,}(?P<percent>\d+(?:\.\d+)?)%[ ]{1,}of[ ]{1,}(?P<total_size>[.0-9]+.iB)[ ]{1,}at[ ]{1,}(?P<dl_rate>[.0-9]+.iB)\/s"


@dataclass(frozen=True)
class YoutubeDownloadSample:
    """
    (Data)Class to grab youtube-dl download sample
    """
    percent: int
    dl_rate: float
    total_size: int = field(repr=False)

    @staticmethod
    def from_match_re(match: Match[AnyStr]):
        return YoutubeDownloadSample(
            percent=int(float(match.group("percent"))),
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
    for yt_dl_sample in map(YoutubeDownloadSample.from_match_re, matches):
        typer.echo(yt_dl_sample)


def yt_dl_cli(yt_uri: str, yt_country: str, yt_dl_options: str):
    argv = f"{yt_dl_options} {yt_country} https://youtu.be/{yt_uri}"
    with redirect_stdout(stdout_capture_streaming):
        with click_spinner.spinner():
            # https://docs.python.org/3/library/atexit.html
            atexit.register(yt_dl_capture_exit)
            youtube_dl.main(argv.split())


# last_percent_dl = 0


def yt_dl_embed(
        yt_uri: str,
        yt_country: str,
        show_progress_bar: bool,
        show_information: bool
):
    @dataclass
    class MyLogger:
        bar: ProgressBar

        dl_rates: List[float] = field(init=False, default_factory=list)
        last_percent: float = field(init=False, default=0.0)

        def debug(self, msg):
            # matches = re.finditer(regex, msg, re.MULTILINE)
            # for yt_dl_sample in (YoutubeDownloadSample.from_match_re(match) for match in matches):
            #     self.bar.update(yt_dl_sample.percent - self._last_percent)
            #     self._last_percent = yt_dl_sample.percent
            #     self.dl_rates.append(yt_dl_sample.dl_rate)
            # typer.echo('\r' + msg, nl=False)
            pass

        def warning(self, msg):
            pass

        def error(self, msg):
            typer.echo(msg)

    def my_hook(d, logger):
        status = d.get("status")
        if status == "downloading":
            speed_rate = d["speed"]
            if speed_rate:
                percent_dl = float(d["_percent_str"].split("%")[0])
                diff_percent_dl = percent_dl - logger.last_percent
                logger.last_percent = percent_dl
                logger.bar.update(diff_percent_dl)
                logger.dl_rates.append((percent_dl, speed_rate))
        elif status == "finished":
            # typer.echo(pformat(logger.dl_rates))
            pass

    with typer.progressbar(label="youtube-dl % completion", length=100, file=None if show_progress_bar else "/dev/null") as bar:
        my_logger = MyLogger(bar)
        ydl_opts = {
            "format": "best",
            "nopart": True,
            "cachedir": True,
            "progress_with_newline": True,
            "geo_bypass_country": yt_country,
            "outtmpl": "/dev/null",
            'logger': my_logger,
            'progress_hooks': [partial(my_hook, logger=my_logger)],
        }
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            if show_information:
                info_dict = ydl.extract_info(yt_uri, download=False)
                typer.echo(pformat(info_dict))
            ydl.download([f'https://www.youtube.com/watch?v={yt_uri}'])
        # show results
        typer.echo(pformat(my_logger.dl_rates))


@app.command()
def speedtest_youtube(
        yt_uri: str = "8cOJhLM66D4",
        yt_country: str = "FR",
        # yt_dl_options: str = "-f best --no-part --no-cache-dir -o /dev/null --newline --geo-bypass-country",
        show_progress_bar: bool = False,
        show_information: bool = False,
):
    # yt_dl_cli(yt_uri, yt_country, yt_dl_options)
    yt_dl_embed(yt_uri, yt_country, show_progress_bar, show_information)


if __name__ == '__main__':
    app()
