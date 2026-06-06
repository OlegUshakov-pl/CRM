import re
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional


@dataclass
class CommandContext:
    user: Any
    text: str
    intent: str
    params: Dict[str, Any] = field(default_factory=dict)
    session: Any = None


@dataclass
class CommandResult:
    ok: bool = True
    message: str = ''
    needs_confirmation: bool = False
    confirmation_text: str = ''
    payload: Dict[str, Any] = field(default_factory=dict)
    actions: List[Dict[str, Any]] = field(default_factory=list)
    undoable: bool = False
    undo_token: Optional[str] = None
    error: str = ''

    def to_dict(self) -> Dict[str, Any]:
        return {
            'ok': self.ok,
            'message': self.message,
            'needs_confirmation': self.needs_confirmation,
            'confirmation_text': self.confirmation_text,
            'payload': self.payload,
            'actions': self.actions,
            'undoable': self.undoable,
            'undo_token': self.undo_token,
            'error': self.error,
        }


Handler = Callable[[CommandContext], 'CommandResult']


class CommandRegistry:
    def __init__(self):
        self._handlers: Dict[str, Handler] = {}
        self._patterns: List[tuple] = []
        self._descriptions: Dict[str, str] = {}

    def register(self, intent: str, patterns: List[str], handler: Handler, description: str = ''):
        self._handlers[intent] = handler
        compiled = [(re.compile(p, re.IGNORECASE | re.UNICODE), intent) for p in patterns]
        self._patterns.extend(compiled)
        if description:
            self._descriptions[intent] = description

    def descriptions(self) -> Dict[str, str]:
        return dict(self._descriptions)

    def match(self, text: str) -> Optional[str]:
        text = (text or '').strip()
        if not text:
            return None
        for pattern, intent in self._patterns:
            if pattern.search(text):
                return intent
        return None

    def handle(self, intent: str, context: CommandContext) -> 'CommandResult':
        handler = self._handlers.get(intent)
        if not handler:
            return CommandResult(ok=False, error=f'Unknown intent: {intent}')
        return handler(context)

    def extract_params(self, text: str, groups: Dict[str, str]) -> Dict[str, Any]:
        result: Dict[str, Any] = {}
        for key, value in groups.items():
            if value is None:
                continue
            v = value.strip()
            if key in ('date', 'due_date', 'start_date'):
                from datetime import date, datetime, timedelta
                v_low = v.lower()
                if v_low in ('сегодня', 'today', 'now'):
                    result[key] = date.today().isoformat()
                    continue
                if v_low in ('завтра', 'tomorrow'):
                    result[key] = (date.today() + timedelta(days=1)).isoformat()
                    continue
                if v_low in ('послезавтра', 'day after tomorrow'):
                    result[key] = (date.today() + timedelta(days=2)).isoformat()
                    continue
                for fmt in ('%Y-%m-%d', '%d.%m.%Y', '%d/%m/%Y', '%d-%m-%Y'):
                    try:
                        result[key] = datetime.strptime(v, fmt).date().isoformat()
                        break
                    except ValueError:
                        continue
                else:
                    result[key] = v
                continue
            if key in ('quantity', 'qty', 'кол-во', 'кол_во'):
                try:
                    result[key] = float(v.replace(',', '.'))
                except ValueError:
                    result[key] = v
                continue
            if key in ('price', 'unit_price'):
                try:
                    result[key] = float(v.replace(',', '.').replace(' ', ''))
                except ValueError:
                    result[key] = v
                continue
            result[key] = v
        return result


command_registry = CommandRegistry()
