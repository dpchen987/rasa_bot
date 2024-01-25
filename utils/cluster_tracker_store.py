# sentinel_tracker_store.py 对应type  'sentinel_tracker_store.RedisSentinelTrackerStore'
import contextlib
import itertools
import json
import logging
import os
import time
from sys import getsizeof as getsize
from time import sleep
from typing import (
    Any,
    Callable,
    Dict,
    Iterable,
    Iterator,
    List,
    Optional,
    Text,
    Union,
    TYPE_CHECKING,
    Generator,
)

from boto3.dynamodb.conditions import Key
from pymongo.collection import Collection

import rasa.core.utils as core_utils
import rasa.shared.utils.cli
import rasa.shared.utils.common
import rasa.shared.utils.io
from rasa.shared.core.constants import ACTION_LISTEN_NAME
from rasa.core.brokers.broker import EventBroker
from rasa.core.constants import (
    POSTGRESQL_SCHEMA,
    POSTGRESQL_MAX_OVERFLOW,
    POSTGRESQL_POOL_SIZE,
)
from rasa.utils.endpoints import EndpointConfig
from rasa.shared.core.conversation import Dialogue
from rasa.shared.core.domain import Domain
from rasa.shared.core.events import SessionStarted
from rasa.shared.core.trackers import (
    ActionExecuted,
    DialogueStateTracker,
    EventVerbosity,
)
from rediscluster import RedisCluster
from rasa.core.tracker_store import TrackerStore, SerializedTrackerAsText

logger = logging.getLogger(__name__)

DEFAULT_REDIS_TRACKER_STORE_KEY_PREFIX = "tracker:"


class RedisClusterTrackerStore(TrackerStore, SerializedTrackerAsText):
    """Stores conversation history in RedisSentinel"""
    def __init__(
        self,
        domain: Domain,
        host: Text,
        port: int,
        db: int = 0,
        password: Optional[Text] = None,
        startup_nodes: Dict[Text, Any] = None,
        event_broker: Optional[EventBroker] = None,
        record_exp: Optional[float] = None,
        key_prefix: Optional[Text] = None,
        **kwargs: Dict[Text, Any],
        ):
        self.startup_nodes = startup_nodes
        self.record_exp = record_exp
        logger.info(f"startup nodes: {startup_nodes} ")

        if self.startup_nodes:
            self.red = RedisCluster(startup_nodes=self.startup_nodes, decode_responses=True)
        else:
            self.red = RedisCluster(
                host=host,
                port=port,
                decode_responses=True)

        self.key_prefix = DEFAULT_REDIS_TRACKER_STORE_KEY_PREFIX
        if key_prefix:
            logger.debug(f"Setting non-default redis key prefix: '{key_prefix}'.")
            self._set_key_prefix(key_prefix)
        super().__init__(domain, event_broker, **kwargs)

    def _set_key_prefix(self, key_prefix: Text) -> None:
        if isinstance(key_prefix, str) and key_prefix.isalnum():
            self.key_prefix = key_prefix + ":" + DEFAULT_REDIS_TRACKER_STORE_KEY_PREFIX
        else:
            logger.warning(
                f"Omitting provided non-alphanumeric redis key prefix: '{key_prefix}'. "
                f"Using default '{self.key_prefix}' instead.")

    def _get_key_prefix(self) -> Text:
        return self.key_prefix

    async def save(
        self, tracker: DialogueStateTracker, timeout: Optional[float] = None
    ) -> None:
        """Saves the current conversation state."""
        await self.stream_events(tracker)

        if not timeout and self.record_exp:
            timeout = self.record_exp

        stored = self.red.get(self.key_prefix + tracker.sender_id)

        if stored is not None:
            prior_tracker = self.deserialise_tracker(tracker.sender_id, stored)

            tracker = self._merge_trackers(prior_tracker, tracker)

        serialised_tracker = self.serialise_tracker(tracker)
        self.red.set(
            self.key_prefix + tracker.sender_id, serialised_tracker, ex=timeout
        )

    async def retrieve(self, sender_id: Text) -> Optional[DialogueStateTracker]:
        """Retrieves tracker for the latest conversation session.

        The Redis key is formed by appending a prefix to sender_id.

        Args:
            sender_id: Conversation ID to fetch the tracker for.

        Returns:
            Tracker containing events from the latest conversation sessions.
        """
        return await self._retrieve(sender_id, fetch_all_sessions=False)

    async def retrieve_full_tracker(
        self, sender_id: Text
    ) -> Optional[DialogueStateTracker]:
        """Retrieves tracker for all conversation sessions.

        The Redis key is formed by appending a prefix to sender_id.

        Args:
            sender_id: Conversation ID to fetch the tracker for.

        Returns:
            Tracker containing events from all conversation sessions.
        """
        return await self._retrieve(sender_id, fetch_all_sessions=True)

    async def _retrieve(
        self, sender_id: Text, fetch_all_sessions: bool
    ) -> Optional[DialogueStateTracker]:
        """Returns tracker matching sender_id.

        Args:
            sender_id: Conversation ID to fetch the tracker for.
            fetch_all_sessions: Whether to fetch all sessions or only the last one.
        """
        stored = self.red.get(self.key_prefix + sender_id)

        if stored is None:
            logger.info(f"Could not find tracker for conversation ID '{sender_id}'.")
            return None

        tracker = self.deserialise_tracker(sender_id, stored)
        if fetch_all_sessions:
            return tracker

        # only return the last session
        multiple_tracker_sessions = (
            rasa.shared.core.trackers.get_trackers_for_conversation_sessions(tracker)
        )

        if 0 <= len(multiple_tracker_sessions) <= 1:
            return tracker

        return multiple_tracker_sessions[-1]

    async def keys(self) -> Iterable[Text]:
        """Returns keys of the Redis Tracker Store."""
        return self.red.keys(self.key_prefix + "*")

    @staticmethod
    def _merge_trackers(
        prior_tracker: DialogueStateTracker, tracker: DialogueStateTracker
    ) -> DialogueStateTracker:
        """Merges two trackers.

        Args:
            prior_tracker: Tracker containing events from the previous conversation
                sessions.
            tracker: Tracker containing events from the current conversation session.
        """
        if not prior_tracker.events:
            return tracker

        last_event_timestamp = prior_tracker.events[-1].timestamp
        past_tracker = tracker.travel_back_in_time(target_time=last_event_timestamp)

        if past_tracker.events == prior_tracker.events:
            return tracker

        merged = tracker.init_copy()
        for new_event in tracker.events:
            merged.update(new_event)

        # merged.update_with_events(
        #     list(prior_tracker.events), override_timestamp=False, domain=None
        # )
        #
        # for new_event in tracker.events:
        #     # Event subclasses implement `__eq__` method that make it difficult
        #     # to compare events. We use `as_dict` to compare events.
        #     flag = True
        #     new_event_dict = new_event.as_dict()
        #     for existing_event in merged.events:
        #         if new_event_dict == existing_event.as_dict():
        #             flag = False
        #             continue
        #
        #     if flag:
        #         merged.update(new_event)
        #
        #     if all(
        #         [
        #             new_event.as_dict() != existing_event.as_dict()
        #             for existing_event in merged.events
        #         ]
        #     ):
        #         merged.update(new_event)

        return merged
