from dataclasses import dataclass, field
from typing import Optional

from dataclasses_json import dataclass_json

from src.enum.IdeEnum import Ide


@dataclass_json
@dataclass
class DotHttpConfigDto:
    environment: Optional[str] = 'Development'
    create_environment: Optional[bool] = True
    create_assert: Optional[bool] = True
    used_ide: Optional[Ide] = field(default=Ide.INTELLIJ)

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
