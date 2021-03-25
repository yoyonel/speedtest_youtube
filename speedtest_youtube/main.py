from __future__ import unicode_literals

from typing import Optional

import typer

from speedtest_youtube.services.render.with_table import show_results_in_table
from speedtest_youtube.services.youtube_dl.embedded import yt_dl_embed
from speedtest_youtube.services.youtube_dl.external import yt_dl_cli

app = typer.Typer()


@app.command()
def speedtest_youtube(
        yt_uri: str = "8cOJhLM66D4",
        yt_country: str = "FR",
        show_progress_bar: bool = False,
        show_information: bool = False,
        timeout_seconds: Optional[float] = 10
):
    process_hook = yt_dl_embed(yt_uri, yt_country, show_progress_bar, show_information, timeout_seconds)
    show_results_in_table(process_hook.dl_samples)


@app.command()
def speedtest_youtube_external(
        yt_uri: str = "8cOJhLM66D4",
        yt_country: str = "FR",
        yt_dl_options: str = "-f best --no-part --no-cache-dir -o /dev/null --newline --geo-bypass-country",
        timeout_seconds: Optional[float] = 10
):
    yt_dl_cli(yt_uri, yt_country, yt_dl_options, timeout_seconds)


if __name__ == '__main__':
    app()
