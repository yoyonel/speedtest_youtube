from dataclasses import dataclass, field
from functools import partial
from pprint import pformat
from typing import List, Tuple, Optional

import click
import timeout_decorator
import typer
import youtube_dl
from click._termui_impl import ProgressBar


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
