# engine/rule_loader.py
import json
from pathlib import Path
from typing import List
from engine.rule_models import SubsidyRule, ConflictRule

class RuleLoader:
    _subsidy: List[SubsidyRule] = []
    _conflict: List[ConflictRule] = []

    @classmethod
    def load(cls, cfg_dir: Path = Path("config")):
        cls._subsidy = [
            SubsidyRule(**r)
            for r in json.loads((cfg_dir / "subsidy_rules.json").read_text(encoding="utf-8"))
        ]
        cls._conflict = [
            ConflictRule(**r)
            for r in json.loads((cfg_dir / "conflict_rules.json").read_text(encoding="utf-8"))
        ]

    @classmethod
    def reload(cls):
        cls.load()  # 运行时可随时调用

    @classmethod
    def subsidy_rules(cls) -> List[SubsidyRule]:
        return cls._subsidy

    @classmethod
    def conflict_rules(cls) -> List[ConflictRule]:
        return cls._conflict