import os
from pyang import repository, context

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
YANG_DIR = os.path.join(BASE_DIR, "yang")
MODEL_PATH = os.path.join(YANG_DIR, "model.yang")
VALIDATORS_OUT = os.path.join(BASE_DIR, "validators", "generated_validators.py")


def parse_yang(model_path: str):
    repo = repository.FileRepository(os.path.dirname(model_path))
    ctx = context.Context(repo)

    with open(model_path) as f:
        text = f.read()

    module = ctx.add_module(os.path.basename(model_path), text)
    ctx.validate()

    if module is None:
        raise RuntimeError("Invalid YANG file")

    module_name = module.arg
    containers = [s.arg for s in module.substmts if s.keyword == "container"]

    return module_name, containers


def generate_validators(model_path=MODEL_PATH, out_path=VALIDATORS_OUT):
    module_name, containers = parse_yang(model_path)

    code = f'''
import os
import json
import libyang

BASE = os.path.dirname(os.path.abspath(__file__))
YANG_DIR = os.path.join(os.path.dirname(BASE), "yang")

ctx = libyang.Context(YANG_DIR)
ctx.load_module("{module_name}")

_MINIMAL_STUBS = {{
    "system": {{"hostname": "stub", "max-sessions": 1000}},
    "interface": {{"name": "eth0", "ip-address": "10.0.0.1", "subnet-mask": "255.255.255.0"}},
    "qos": {{}},
    "security": {{}}
}}

def _validate_container(container, data):
    try:
        full_config = {{}}
        for c in _MINIMAL_STUBS:
            if c == container:
                full_config["{module_name}:" + c] = data
            else:
                full_config["{module_name}:" + c] = _MINIMAL_STUBS[c]
        
        json_data = json.dumps(full_config)
        node = ctx.parse_data_mem(json_data, "json", strict=True)
        node.validate()
        
        return {{"valid": True, "errors": []}}
    except Exception as e:
        error_msg = str(e)
        container_path = "{module_name}:" + container
        if container in error_msg or container_path in error_msg:
            return {{"valid": False, "errors": [error_msg]}}
        return {{"valid": False, "errors": [error_msg]}}

def validate_full_config(config_data):
    try:
        json_data = json.dumps(config_data)
        node = ctx.parse_data_mem(json_data, "json", strict=True)
        node.validate()
        return {{"valid": True, "errors": []}}
    except Exception as e:
        return {{"valid": False, "errors": [str(e)]}}
'''

    for c in containers:
        code += f'''

def validate_{c}(data):
    return _validate_container("{c}", data)
'''

    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    with open(out_path, "w") as f:
        f.write(code)

    print(f"Generated {len(containers)} validators")


if __name__ == "__main__":
    generate_validators()