from dataclasses import dataclass, field
from typing import Optional

from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class DotHttpConfigDto:
    environment: Optional[str] = 'Development'
    create_environment: Optional[bool] = True
    create_assert: Optional[bool] = True
    create_response_comment: Optional[bool] = True
    write_params_in_url: Optional[bool] = True
    """If True, writes params within the URL. In regards to dothttp doc it should be False, but IntelliJ cannot 
    handle it."""

    def __getitem__(self, item):
        return getattr(self, item)


@dataclass_json
@dataclass
class ConfigDto:
    base_url: str
    ip: Optional[str] = None
    dothttp: Optional[DotHttpConfigDto] = field(default_factory=DotHttpConfigDto)

    def __getitem__(self, item):
        return getattr(self, item)
