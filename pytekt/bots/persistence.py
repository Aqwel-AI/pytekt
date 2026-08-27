"""
Durable Persistence & Database Integration for PyTekt Bots.
Provides bot.db backed by pytekt.db document collections for persistent FSM states,
session data, long-term facts, and role assignments across restarts.
"""

from __future__ import annotations

import logging
import time
from typing import Any, Dict, List, Optional, Union

logger = logging.getLogger("pytekt.bots.persistence")


class BotDB:
    """
    Database persistence layer for PyTekt Bots wrapping pytekt.db collections.

    Parameters
    ----------
    source : str, Connection, or Dict[str, Any]
        Database connection URL (e.g. 'sqlite:///./bot.db') or connection dict.
    """

    def __init__(self, source: Union[str, Any] = "sqlite:///./bot.db") -> None:
        from pytekt.db import connect

        if isinstance(source, (str, dict)):
            self.conn = connect(source)
        else:
            self.conn = source

    # ------------------------------------------------------------------
    # Persistent FSM States & Session Data
    # ------------------------------------------------------------------

    def set_state(self, fsm_key: str, state: str, ttl: float = 0.0) -> None:
        """Save active FSM state with optional expiration timestamp."""
        now = time.time()
        expires_at = (now + ttl) if ttl > 0 else 0.0

        if not state:
            self.clear_state(fsm_key)
            return

        try:
            col = self.conn.collection("pytekt_fsm_state")
            existing = col.find_one(fsm_key=fsm_key)
            if existing:
                col.update({"fsm_key": fsm_key}, {"state": state, "expires_at": expires_at, "updated_at": now})
            else:
                col.insert({"fsm_key": fsm_key, "state": state, "expires_at": expires_at, "updated_at": now})
        except Exception as e:
            logger.error("DB error in set_state: %s", e)

    def get_state(self, fsm_key: str) -> str:
        """Retrieve active FSM state, returning empty string if expired or not set."""
        try:
            col = self.conn.collection("pytekt_fsm_state")
            doc = col.find_one(fsm_key=fsm_key)
            if not doc:
                return ""

            expires_at = float(doc.get("expires_at") or 0.0)
            if expires_at > 0 and time.time() > expires_at:
                self.clear_state(fsm_key)
                return ""
            return str(doc.get("state") or "")
        except Exception as e:
            logger.error("DB error in get_state: %s", e)
            return ""

    def clear_state(self, fsm_key: str) -> None:
        """Clear active FSM state."""
        try:
            col = self.conn.collection("pytekt_fsm_state")
            col.delete(fsm_key=fsm_key)
        except Exception as e:
            logger.error("DB error in clear_state: %s", e)

    def set_data(self, fsm_key: str, data_key: str, data_val: str, ttl: float = 0.0) -> None:
        """Save session key-value pair."""
        now = time.time()
        expires_at = (now + ttl) if ttl > 0 else 0.0

        try:
            col = self.conn.collection("pytekt_fsm_data")
            existing = col.find_one(fsm_key=fsm_key, data_key=data_key)
            if existing:
                col.update({"fsm_key": fsm_key, "data_key": data_key}, {"data_val": str(data_val), "expires_at": expires_at})
            else:
                col.insert({"fsm_key": fsm_key, "data_key": data_key, "data_val": str(data_val), "expires_at": expires_at})
        except Exception as e:
            logger.error("DB error in set_data: %s", e)

    def get_data(self, fsm_key: str, data_key: str) -> str:
        """Get session value by key."""
        try:
            col = self.conn.collection("pytekt_fsm_data")
            doc = col.find_one(fsm_key=fsm_key, data_key=data_key)
            if not doc:
                return ""

            expires_at = float(doc.get("expires_at") or 0.0)
            if expires_at > 0 and time.time() > expires_at:
                col.delete(fsm_key=fsm_key, data_key=data_key)
                return ""
            return str(doc.get("data_val") or "")
        except Exception as e:
            logger.error("DB error in get_data: %s", e)
            return ""

    def get_all_data(self, fsm_key: str) -> Dict[str, str]:
        """Get all active session data for an FSM key."""
        try:
            col = self.conn.collection("pytekt_fsm_data")
            docs = col.find(fsm_key=fsm_key)
            res = {}
            now = time.time()
            for d in docs:
                exp = float(d.get("expires_at") or 0.0)
                if exp > 0 and now > exp:
                    continue
                k = d.get("data_key")
                if k is not None:
                    res[str(k)] = str(d.get("data_val") or "")
            return res
        except Exception as e:
            logger.error("DB error in get_all_data: %s", e)
            return {}

    def clear_data(self, fsm_key: str) -> None:
        """Clear all session data for an FSM key."""
        try:
            col = self.conn.collection("pytekt_fsm_data")
            col.delete(fsm_key=fsm_key)
        except Exception as e:
            logger.error("DB error in clear_data: %s", e)

    # ------------------------------------------------------------------
    # Persistent AI Long-Term Facts
    # ------------------------------------------------------------------

    def remember_fact(self, chat_id: str, fact: str) -> None:
        """Persist an explicit long-term fact."""
        try:
            col = self.conn.collection("pytekt_chat_facts")
            if not col.find_one(chat_id=chat_id, fact=fact):
                col.insert({"chat_id": chat_id, "fact": fact, "created_at": time.time()})
        except Exception as e:
            logger.error("DB error in remember_fact: %s", e)

    def get_facts(self, chat_id: str) -> List[str]:
        """Get all stored long-term facts for a chat/user."""
        try:
            col = self.conn.collection("pytekt_chat_facts")
            docs = col.find(chat_id=chat_id)
            return [str(d["fact"]) for d in docs if "fact" in d]
        except Exception as e:
            logger.error("DB error in get_facts: %s", e)
            return []

    def forget_facts(self, chat_id: str) -> None:
        """Wipe long-term facts for a chat."""
        try:
            col = self.conn.collection("pytekt_chat_facts")
            col.delete(chat_id=chat_id)
        except Exception as e:
            logger.error("DB error in forget_facts: %s", e)

    # ------------------------------------------------------------------
    # Persistent User Roles & Access Control
    # ------------------------------------------------------------------

    def grant_role(self, chat_id: str, user_id: str, role: str) -> None:
        """Assign a role to a user in a chat."""
        r = role.lower().strip()
        uid = str(user_id)
        try:
            col = self.conn.collection("pytekt_user_roles")
            if not col.find_one(chat_id=chat_id, user_id=uid, role=r):
                col.insert({"chat_id": chat_id, "user_id": uid, "role": r, "granted_at": time.time()})
        except Exception as e:
            logger.error("DB error in grant_role: %s", e)

    def revoke_role(self, chat_id: str, user_id: str, role: str) -> None:
        """Remove a role assignment from a user."""
        r = role.lower().strip()
        uid = str(user_id)
        try:
            col = self.conn.collection("pytekt_user_roles")
            col.delete(chat_id=chat_id, user_id=uid, role=r)
        except Exception as e:
            logger.error("DB error in revoke_role: %s", e)

    def get_roles(self, chat_id: str, user_id: str) -> List[str]:
        """Get all active roles for a user in a chat."""
        uid = str(user_id)
        try:
            col = self.conn.collection("pytekt_user_roles")
            docs = col.find(user_id=uid)
            roles = []
            for d in docs:
                if d.get("chat_id") in (chat_id, "*") and "role" in d:
                    roles.append(str(d["role"]))
            return roles
        except Exception as e:
            logger.error("DB error in get_roles: %s", e)
            return []
