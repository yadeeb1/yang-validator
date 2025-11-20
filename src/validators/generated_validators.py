
import os
import json
import libyang

BASE = os.path.dirname(os.path.abspath(__file__))
YANG_DIR = os.path.join(os.path.dirname(BASE), "yang")

ctx = libyang.Context(YANG_DIR)
ctx.load_module("model")

_MINIMAL_STUBS = {
    "system": {"hostname": "stub", "max-sessions": 1000},
    "interface": {"name": "eth0", "ip-address": "10.0.0.1", "subnet-mask": "255.255.255.0"},
    "qos": {},
    "security": {}
}

def _validate_container(container, data):
    try:
        full_config = {}
        for c in _MINIMAL_STUBS:
            if c == container:
                full_config["model:" + c] = data
            else:
                full_config["model:" + c] = _MINIMAL_STUBS[c]
        
        json_data = json.dumps(full_config)
        node = ctx.parse_data_mem(json_data, "json", strict=True)
        node.validate()
        
        return {"valid": True, "errors": []}
    except Exception as e:
        error_msg = str(e)
        container_path = "model:" + container
        if container in error_msg or container_path in error_msg:
            return {"valid": False, "errors": [error_msg]}
        return {"valid": False, "errors": [error_msg]}

def validate_full_config(config_data):
    try:
        json_data = json.dumps(config_data)
        node = ctx.parse_data_mem(json_data, "json", strict=True)
        node.validate()
        return {"valid": True, "errors": []}
    except Exception as e:
        return {"valid": False, "errors": [str(e)]}


def validate_system(data):
    return _validate_container("system", data)


def validate_interface(data):
    return _validate_container("interface", data)


def validate_qos(data):
    return _validate_container("qos", data)


def validate_security(data):
    return _validate_container("security", data)
