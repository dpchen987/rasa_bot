import logging
import json
from typing import Text, Optional

from rasa.core.lock import TicketLock
from rasa.core.lock_store import LockStore
from rasa.utils.endpoints import EndpointConfig

from rediscluster import RedisCluster

logger = logging.getLogger(__name__)


class RedisClusterLockStore(LockStore):
    def __init__(self, endpoint_config: EndpointConfig) -> None:
        self.startup_nodes = endpoint_config.kwargs['startup_nodes']
        self.key_prefix = endpoint_config.kwargs['key_prefix']
        logger.info(f"startup nodes: {self.startup_nodes} ")
        logger.info(f"key_prefix nodes: {self.key_prefix} ")
        self.client = RedisCluster(startup_nodes=self.startup_nodes, decode_responses=True)
        super().__init__()

    def lock_key(self, conversation_id: Text) -> Text:
        return self.key_prefix + conversation_id

    def get_lock(self, conversation_id: Text) -> Optional[TicketLock]:
        serialised_lock = self.client.get(self.lock_key(conversation_id))
        if serialised_lock:
            return TicketLock.from_dict(json.loads(serialised_lock))

    def delete_lock(self, conversation_id: Text) -> None:
        deletion_successful = self.client.delete(self.lock_key(conversation_id))
        self._log_deletion(conversation_id, deletion_successful)

    def save_lock(self, lock: TicketLock) -> None:
        self.client.set(self.lock_key(lock.conversation_id), lock.dumps())