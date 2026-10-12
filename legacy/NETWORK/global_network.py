# NETWORK/global_network.py
# KING DIADEM — Global Network
# redirect ไป global_chat.py — ไม่ duplicate store อีกต่อไป

from NETWORK.global_chat import (
    add_chat     as add_message,   # backward compat
    get_chat     as get_messages,
    count_messages,
    clear_old_messages,
)

__all__ = ["add_message", "get_messages", "count_messages", "clear_old_messages"]
