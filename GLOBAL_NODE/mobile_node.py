# GLOBAL_NODE/mobile_node.py — เดิมชื่อ mobile.nood.py (มีจุดในชื่อ → import เป็นโมดูลไม่ได้)
from GLOBAL_NODE.network_sync import sync_node


def mobile_report(location, food, risk):

    node_data = {
        "food_score": food,
        "risk_score": risk
    }

    world = sync_node(location, node_data)

    return world
