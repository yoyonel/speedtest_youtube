from dataclasses import dataclass, field
from typing import Match, AnyStr

from humanfriendly import parse_size


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
