from dataclasses import dataclass, field
from pprint import pformat
from typing import List, Optional, Dict

import click
import timeout_decorator
import typer
import youtube_dl
from click._termui_impl import ProgressBar

from speedtest_youtube.models.ytdl_sample import YoutubeDownloadSample


@dataclass
class ProgressHook:
    bar: ProgressBar

    dl_samples: List[YoutubeDownloadSample] = field(init=False, default_factory=list)
    last_percent: float = field(init=False, default=0.0)

    def __post_init__(self):
        # function hook for progress bar
        self.bar.item_show_func = lambda x: f"download rate: {round((self.dl_samples[-1].dl_rate if self.dl_samples else 0) / (1024 * 1024), 2)} MB/s"

    def hook_callback(self, hook_progress_status: Dict) -> None:
        process_hook = self
        status = hook_progress_status.get("status")
        if status == "downloading":
            speed_rate = hook_progress_status.get("speed")
            if speed_rate:
                percent_dl = float(hook_progress_status["_percent_str"].split("%")[0])
                diff_percent_dl = percent_dl - process_hook.last_percent
                process_hook.last_percent = percent_dl
                process_hook.bar.update(diff_percent_dl)
                process_hook.dl_samples.append(YoutubeDownloadSample(percent_dl, speed_rate, hook_progress_status.get("downloaded_bytes")))
        # elif status == "finished":
        #     pass


@dataclass
class HookLogger:
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


def using_embedded(
        yt_uri: str,
        yt_country: str,
        show_progress_bar: bool,
        show_information: bool,
        timeout_seconds: Optional[float]
) -> ProgressHook:
    with typer.progressbar(
            label="Youtube download monitoring",
            bar_template='%(label)s  %(bar)s | %(info)s',
            fill_char=click.style(u'#', fg='green'),
            empty_char=' ',
            length=100,
            file=None if show_progress_bar else "/dev/null"
    ) as bar:
        hook_logger = HookLogger()
        progress_hook = ProgressHook(bar)
        ydl_opts = {
            "format": "best",
            "nopart": True,
            "cachedir": True,
            "progress_with_newline": True,
            "geo_bypass_country": yt_country,
            "outtmpl": "/dev/null",
            'logger': hook_logger,
            'progress_hooks': [progress_hook.hook_callback]
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
            typer.echo(f"\nTimeout: benchmarking exceed {timeout_seconds}s -> cancel")
        return progress_hook
