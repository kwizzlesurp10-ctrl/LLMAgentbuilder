
import json
import os
import datetime
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field, asdict

PRESETS_FILE = os.path.join(os.path.dirname(__file__), "presets", "presets.json")

@dataclass
class AgentConfig:
    provider: str
    model: str
    system_prompt: str
    example_task: str
    tools: List[Dict[str, Any]] = field(default_factory=list)
    enable_multi_step: bool = False
    swarm_config: Optional[Dict[str, Any]] = None

@dataclass
class AgentPreset:
    id: str
    name: str
    version: str
    description: str
    config: AgentConfig
    created_at: str
    updated_at: str

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AgentPreset':
        config_data = data.get("config", {})
        return cls(
            id=data.get("id"),
            name=data.get("name"),
            version=data.get("version"),
            description=data.get("description"),
            config=AgentConfig(**config_data),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at")
        )

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class PresetManager:
    def __init__(self, presets_file: str = PRESETS_FILE):
        self.presets_file = presets_file
        self.presets: List[AgentPreset] = self._load_presets()

    def _load_presets(self) -> List[AgentPreset]:
        if not os.path.exists(self.presets_file):
            return []
        try:
            with open(self.presets_file, 'r') as f:
                data = json.load(f)
                return [AgentPreset.from_dict(item) for item in data]
        except Exception as e:
            print(f"Error loading presets: {e}")
            return []

    def list_presets(self) -> List[AgentPreset]:
        return self.presets

    def get_preset(self, name_or_id: str) -> Optional[AgentPreset]:
        for preset in self.presets:
            if preset.id == name_or_id or preset.name.lower() == name_or_id.lower():
                return preset
        return None

    def save_presets(self):
        data = [preset.to_dict() for preset in self.presets]
        os.makedirs(os.path.dirname(self.presets_file), exist_ok=True)
        with open(self.presets_file, 'w') as f:
            json.dump(data, f, indent=2)

    def add_preset(self, preset: AgentPreset):
        # Check if exists and update or append
        existing = self.get_preset(preset.id)
        if existing:
            self.presets.remove(existing)
        self.presets.append(preset)
        self.save_presets()

    def create_preset_from_args(self, name: str, description: str, args: Any) -> AgentPreset:
        now = datetime.datetime.utcnow().isoformat() + "Z"
        config = AgentConfig(
            provider=args.provider,
            model=args.model or "claude-3-5-sonnet-20241022", # Default fallback
            system_prompt=args.prompt,
            example_task=args.task,
            tools=[], # Tool support from CLI args is complex, keeping empty for simple creation
            enable_multi_step=False
        )
        return AgentPreset(
            id=f"{name.lower()}-v1",
            name=name,
            version="1.0.0",
            description=description,
            config=config,
            created_at=now,
            updated_at=now
        )
