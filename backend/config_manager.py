from __future__ import annotations

import json
import os
import re
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlparse

DEFAULT_CONFIG: Dict[str, Any] = {
    "schema_version": 1,
    "ui": {
        "title": "JD-Mobile",
        "default_view": "packages",
    },
    "instances": [
        {
            "id": "primary",
            "name": "Primary",
            "enabled": True,
            "providers": {
                "primary": {
                    "type": "local",
                    "base_url": "",        # set during setup
                    "timeout_ms": 800,
                },
                "fallback": {
                    "type": "myjd",
                    "enabled": False,
                    "email": "",
                    "password": "",
                    "device_name": "",
                },
            },
        }
    ],
    "active_instance_id": "primary",
    "behavior": {
        "prefer_primary": True,
        "failover_on_unreachable": False,
    },
}

ID_RE = re.compile(r"^[a-z0-9][a-z0-9\-]{0,63}$")

@dataclass
class ConfigLoadResult:
    ok: bool
    config: Dict[str, Any]
    errors: List[str]
    needs_setup: bool
    path: str

def _deep_merge(dst: Dict[str, Any], src: Dict[str, Any]) -> Dict[str, Any]:
    for k, v in src.items():
        if isinstance(v, dict) and isinstance(dst.get(k), dict):
            dst[k] = _deep_merge(dst[k], v)
        else:
            dst[k] = v
    return dst

def _is_valid_http_url(u: str) -> bool:
    try:
        p = urlparse(u)
        return p.scheme in ("http", "https") and bool(p.netloc)
    except Exception:
        return False

def _normalize_base_url(u: str) -> str:
    return (u or "").strip().rstrip("/")

def _ensure_dir(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

class ConfigManager:
    def __init__(self, config_path: Optional[str] = None):
        env_path = os.environ.get("JD_MOBILE_CONFIG_PATH", "").strip()
        self.path = Path(config_path or env_path or "/app/config/config.json")

    def load(self) -> ConfigLoadResult:
        errors: List[str] = []
        cfg: Dict[str, Any] = json.loads(json.dumps(DEFAULT_CONFIG))  # deep copy

        if self.path.exists():
            try:
                raw = self.path.read_text(encoding="utf-8")
                user_cfg = json.loads(raw)
                if isinstance(user_cfg, dict):
                    cfg = _deep_merge(cfg, user_cfg)
                else:
                    errors.append("Config root must be a JSON object.")
            except json.JSONDecodeError as e:
                errors.append(f"Config JSON parse error: {e}")
            except Exception as e:
                errors.append(f"Failed to read config: {e}")
        else:
            errors.append("Config file not found (first run).")

        norm_errors, needs_setup = self._normalize_and_validate(cfg)
        errors.extend(norm_errors)

        ok = (not needs_setup) and (len([e for e in errors if not e.lower().startswith("config file not found")]) == 0)

        return ConfigLoadResult(ok=ok, config=cfg, errors=errors, needs_setup=needs_setup, path=str(self.path))

    def save(self, cfg: Dict[str, Any]) -> Tuple[bool, List[str]]:
        errors, needs_setup = self._normalize_and_validate(cfg)
        if needs_setup:
            errors.append("Refusing to save: config still requires setup (missing required fields).")
            return False, errors

        try:
            _ensure_dir(self.path)
            data = json.dumps(cfg, indent=2, sort_keys=True)
            with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False, dir=str(self.path.parent)) as tf:
                tf.write(data)
                tf.flush()
                os.fsync(tf.fileno())
                tmp_name = tf.name
            os.replace(tmp_name, self.path)
            return True, []
        except Exception as e:
            return False, [f"Failed to save config: {e}"]

    def get_active_instance(self, cfg: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        inst_id = str(cfg.get("active_instance_id") or "").strip()
        for inst in (cfg.get("instances") or []):
            if isinstance(inst, dict) and inst.get("id") == inst_id:
                return inst
        return None

    def _normalize_and_validate(self, cfg: Dict[str, Any]) -> Tuple[List[str], bool]:
        errors: List[str] = []
        needs_setup = False

        # schema_version
        sv = cfg.get("schema_version", 1)
        if not isinstance(sv, int) or sv < 1:
            errors.append("schema_version must be an integer >= 1.")
            cfg["schema_version"] = 1

        # ui defaults
        if not isinstance(cfg.get("ui"), dict):
            cfg["ui"] = {}
        cfg["ui"] = _deep_merge(json.loads(json.dumps(DEFAULT_CONFIG["ui"])), cfg["ui"])
        if not cfg["ui"].get("title"):
            cfg["ui"]["title"] = "JD-Mobile"

        # behavior defaults
        if not isinstance(cfg.get("behavior"), dict):
            cfg["behavior"] = {}
        cfg["behavior"] = _deep_merge(json.loads(json.dumps(DEFAULT_CONFIG["behavior"])), cfg["behavior"])

        # instances
        instances = cfg.get("instances")
        if not isinstance(instances, list) or len(instances) == 0:
            errors.append("instances must be a non-empty array.")
            cfg["instances"] = json.loads(json.dumps(DEFAULT_CONFIG["instances"]))
            instances = cfg["instances"]
            needs_setup = True

        seen_ids = set()
        for idx, inst in enumerate(instances):
            if not isinstance(inst, dict):
                errors.append(f"instances[{idx}] must be an object.")
                needs_setup = True
                continue

            inst_id = str(inst.get("id") or "").strip()
            if not inst_id or not ID_RE.match(inst_id):
                errors.append(f"instances[{idx}].id is invalid (lowercase letters/numbers/hyphens, 1-64 chars).")
                needs_setup = True
                inst_id = f"instance-{idx+1}"
                inst["id"] = inst_id

            if inst_id in seen_ids:
                errors.append(f"Duplicate instance id '{inst_id}'.")
                needs_setup = True
            seen_ids.add(inst_id)

            name = str(inst.get("name") or "").strip()
            if not name:
                inst["name"] = inst_id

            if not isinstance(inst.get("enabled"), bool):
                inst["enabled"] = True

            if not isinstance(inst.get("providers"), dict):
                inst["providers"] = {}
            inst["providers"] = _deep_merge(json.loads(json.dumps(DEFAULT_CONFIG["instances"][0]["providers"])), inst["providers"])

            primary = inst["providers"].get("primary", {})
            if not isinstance(primary, dict):
                inst["providers"]["primary"] = json.loads(json.dumps(DEFAULT_CONFIG["instances"][0]["providers"]["primary"]))
                primary = inst["providers"]["primary"]

            ptype = str(primary.get("type") or "").strip().lower()
            if ptype not in ("local", "myjd"):
                errors.append(f"instances[{idx}].providers.primary.type must be 'local' or 'myjd'.")
                primary["type"] = "local"
                ptype = "local"

            if ptype == "local":
                base_url = _normalize_base_url(primary.get("base_url", ""))
                primary["base_url"] = base_url
                if not base_url:
                    needs_setup = True
                    errors.append(f"instances[{idx}] primary local base_url is not set.")
                elif not _is_valid_http_url(base_url):
                    needs_setup = True
                    errors.append(f"instances[{idx}] primary local base_url is not a valid http(s) URL: '{base_url}'")

                tmo = primary.get("timeout_ms", 800)
                if not isinstance(tmo, int) or tmo < 100 or tmo > 60000:
                    errors.append(f"instances[{idx}].providers.primary.timeout_ms must be 100..60000.")
                    primary["timeout_ms"] = 800

            fallback = inst["providers"].get("fallback", {})
            if not isinstance(fallback, dict):
                inst["providers"]["fallback"] = json.loads(json.dumps(DEFAULT_CONFIG["instances"][0]["providers"]["fallback"]))
                fallback = inst["providers"]["fallback"]

            ftype = str(fallback.get("type") or "").strip().lower()
            if ftype and ftype != "myjd":
                errors.append(f"instances[{idx}].providers.fallback.type must be 'myjd' when set.")
                fallback["type"] = "myjd"
            if not isinstance(fallback.get("enabled"), bool):
                fallback["enabled"] = False

        active_id = str(cfg.get("active_instance_id") or "").strip()
        if not active_id:
            cfg["active_instance_id"] = instances[0].get("id", "primary")
            active_id = cfg["active_instance_id"]

        if active_id not in seen_ids:
            errors.append(f"active_instance_id '{active_id}' does not match any instance.")
            cfg["active_instance_id"] = instances[0].get("id", "primary")
            needs_setup = True

        if not any(isinstance(i, dict) and i.get("enabled") for i in instances):
            errors.append("At least one instance must be enabled.")
            if isinstance(instances[0], dict):
                instances[0]["enabled"] = True
            needs_setup = True

        return errors, needs_setup
