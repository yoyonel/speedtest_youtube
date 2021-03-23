from __future__ import unicode_literals

import atexit
import io
import re
from contextlib import redirect_stdout
from dataclasses import dataclass, field
from functools import partial
from pprint import pformat
from typing import AnyStr, Match, List, Tuple, Optional

import click
import click_spinner
import timeout_decorator
import typer
import youtube_dl
from click._termui_impl import ProgressBar
from humanfriendly import parse_size
from rich.console import Console
from rich.table import Table

app = typer.Typer()
console = Console()
stdout_capture_streaming = io.StringIO()

regex = r"\[download\][ ]{1,}(?P<percent>\d+(?:\.\d+)?)%[ ]{1,}of[ ]{1,}(?P<total_size>[.0-9]+.iB)[ ]{1,}at[ ]{1,}(?P<dl_rate>[.0-9]+.iB)\/s"


@dataclass
class HookLogger:
    bar: ProgressBar

    dl_rates: List[Tuple[float, float]] = field(init=False, default_factory=list)
    last_percent: float = field(init=False, default=0.0)

    def __post_init__(self):
        self.bar.item_show_func = lambda x: f"download rate: {round((self.dl_rates[-1][1] if self.dl_rates else 0) / (1024 * 1024), 2)} MB/s"

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


def hook_callback(d, logger):
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
            total_size=match.group("totalupdate(_size"),
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


def show_results_in_table(dl_rates: List[Tuple[float, float]]):
    # show results
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Percent")
    table.add_column("Download rate (Mbps)", justify="right")
    for percent, dl_rate in dl_rates:
        table.add_row(str(percent), f"{dl_rate:.2F}")
    console.print()
    console.print(table)


def yt_dl_embed(
        yt_uri: str,
        yt_country: str,
        show_progress_bar: bool,
        show_information: bool,
        timeout_seconds: Optional[float]
) -> HookLogger:
    with typer.progressbar(
            label="Youtube download monitoring",
            bar_template='%(label)s  %(bar)s | %(info)s',
            fill_char=click.style(u'#', fg='green'),
            empty_char=' ',
            length=100,
            file=None if show_progress_bar else "/dev/null"
    ) as bar:
        hook_logger = HookLogger(bar)
        ydl_opts = {
            "format": "best",
            "nopart": True,
            "cachedir": True,
            "progress_with_newline": True,
            "geo_bypass_country": yt_country,
            "outtmpl": "/dev/null",
            'logger': hook_logger,
            'progress_hooks': [partial(hook_callback, logger=hook_logger)],
        }

        @timeout_decorator.timeout(seconds=timeout_seconds)
        def _perform_download():
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                if show_information:
                    info_dict = ydl.extract_info(yt_uri, download=False)
                    typer.echo(pformat(info_dict))
                ydl.download([f'https://www.youtube.com/watch?v={yt_uri}'])

        try:
            _perform_download()
        except timeout_decorator.TimeoutError:
            typer.echo(f"\nTimeout(<={timeout_seconds}): cancel download")
        return hook_logger


@app.command()
def speedtest_youtube(
        yt_uri: str = "8cOJhLM66D4",
        yt_country: str = "FR",
        # yt_dl_options: str = "-f best --no-part --no-cache-dir -o /dev/null --newline --geo-bypass-country",
        show_progress_bar: bool = False,
        show_information: bool = False,
        timeout_seconds: Optional[float] = 10
):
    # yt_dl_cli(yt_uri, yt_country, yt_dl_options)
    hook_logger = yt_dl_embed(yt_uri, yt_country, show_progress_bar, show_information, timeout_seconds)
    show_results_in_table(hook_logger.dl_rates)


if __name__ == '__main__':
    app()
