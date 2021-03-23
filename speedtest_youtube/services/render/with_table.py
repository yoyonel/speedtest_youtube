from typing import List, Tuple

from rich.console import Console
from rich.table import Table

console = Console()


def show_results_in_table(dl_rates: List[Tuple[float, float]]):
    # show results
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Percent")
    table.add_column("Download rate (Mbps)", justify="right")
    for percent, dl_rate in dl_rates:
        table.add_row(str(percent), f"{dl_rate:.2F}")
    console.print()
    console.print(table)
