from typing import Iterable

from rich.console import Console
from rich.table import Table

from speedtest_youtube.models.ytdl_sample import YoutubeDownloadSample

console = Console()


def show_results_in_table(samples: Iterable[YoutubeDownloadSample]) -> None:
    # show results
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("% Completion")
    table.add_column("Download rate (Mbps)", justify="right")
    for sample in samples:
        table.add_row(str(sample.percent), f"{sample.dl_rate:.2F}")
    console.print()
    console.print(table)
