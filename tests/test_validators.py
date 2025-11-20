import json
import sys
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR = os.path.join(BASE_DIR, 'src')
sys.path.insert(0, SRC_DIR)

from validators.generated_validators import (
    validate_system, 
    validate_interface, 
    validate_qos, 
    validate_security,
    validate_full_config
)

CONFIG_PATH = os.path.join(SRC_DIR, "config", "configData.json")

with open(CONFIG_PATH) as f:
    cfg = json.load(f)

print("\n***SYSTEM **")
print(validate_system(cfg.get("model:system", {})))

print("\n*** INTERFACE ***")
print(validate_interface(cfg.get("model:interface", {})))

print("\n*** QOS***")
print(validate_qos(cfg.get("model:qos", {})))

print("\n***SECURITY***")
print(validate_security(cfg.get("model:security", {})))

print("\n")
print("*"*60)
print("FULL CONFIG VALIDATIO")
print(validate_full_config(cfg))