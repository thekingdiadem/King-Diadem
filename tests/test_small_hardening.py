"""ฟังก์ชันเล็กที่เคยพังเมื่อได้ค่าผิดชนิด หรือ DB_PATH เป็นชื่อไฟล์เปล่าๆ"""
import importlib

from AI_KERNEL.living_water import get_response_guidance
from GLOBAL_NODE.node_model import GlobalNode


def test_guidance_with_dict_falls_back_to_clear():
    assert get_response_guidance({})["signal"] == "CLEAR"
    assert get_response_guidance(["CRISIS"])["halt_logic"] is False


def test_remove_node_with_unhashable_location():
    assert GlobalNode().remove_node({}) is False


def test_node_registry_fallback_with_bare_filename(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("DB_PATH", "bare.db")
    nr = importlib.import_module("NETWORK.node_registry")
    import builtins
    real_import = builtins.__import__

    def no_db(name, *a, **k):
        if name == "DATABASE.db":
            raise ImportError
        return real_import(name, *a, **k)
    monkeypatch.setattr(builtins, "__import__", no_db)
    nr._conn().close()
    assert (tmp_path / "bare.db").exists()
