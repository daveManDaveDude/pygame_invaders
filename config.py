"""
Configuration module loading constants from JSON file.
"""
import json
import os

_CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'config.json')
try:
    with open(_CONFIG_PATH) as _f:
        _cfg = json.load(_f)
except Exception as _e:
    raise RuntimeError(f"Failed to load configuration file: {_CONFIG_PATH}: {_e}")

# Expose keys as module-level variables
globals().update(_cfg)

__all__ = list(_cfg.keys())