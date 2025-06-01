import json

import config
import os

def get_conf():
    if config.mode == config.mode_worker:
        return _get_config_worker()
    if config.mode == config.mode_buyer:
        return _get_config_buyer()
    return {}

def set_conf():
    pass

def _get_config_worker():
    pass

def _get_config_buyer():
    fn = config.config_json

    if not os.path.isfile(fn):
        raise f"file not found: {fn}"

    with open(fn, "r", encoding="utf-8") as f:
        data = json.load(f)


    if not isinstance(data, dict) or "autobuy" not in data:
        raise f"error parse json: no autobuy key"

    autobuy = data["autobuy"]

    res = dir()
    for short, full_name in config.short_to_full.items():
        item = autobuy.get(full_name)
        if not item:
            continue
        price = float(item.get("buyPrice"))
        if not isinstance(price, (int, float)):
            continue
        res[short]= (price // 100_000) /10



