"""
The "autoload" module of scaict_uwu module.
This makes our life easier to deal with the complex Python import hell.
WARN: Do NOT write `import scaict` or `from scaict_uwu import` in any
`src/scaict_uwu/*.py` file to prevent cyclic import.
"""

from scaict_uwu.core.config import (
    Config,
    ConfigFactory,
    ConfigNames,
    ConfigSchema,
)
from scaict_uwu.core.user import (
    User,
    UserFactory,
)
from scaict_uwu.libs.language import (
    LanguageTag,
    LanguageTagFactory,
    LanguageUtils,
    SystemMessage,
)
from scaict_uwu.libs.services import (
    CannotReplaceActiveServiceError,
    NoSuchServiceError,
    Service,
    ServiceAlreadyDefinedError,
    ServiceContainer,
)
from scaict_uwu.maintenance.maintenance import (
    MaintenanceScript,
    MaintenanceParameters,
)
from scaict_uwu.maintenance.scripts import (
    MaintenanceScriptUpdate,
)
