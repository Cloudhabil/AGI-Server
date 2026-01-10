"""
GPIA Communication Bridge: Bidirectional IPC between Gardener and Main Agent

Implements a lightweight, file-based message queue for real-time communication.
Works across platforms without additional dependencies.

Message Flow:
  Gardener → GPIA: Classification requests, organization events, stats
  GPIA → Gardener: Commands, quality feedback, configuration updates

Architecture:
- Message queue: data/ipc/messages/
- Inbox (Gardener → GPIA): data/ipc/messages/to_gpia/
- Outbox (GPIA → Gardener): data/ipc/messages/to_gardener/
- Lock-free atomic writes using temp files + rename
"""

import json
import time
from pathlib import Path
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum
import threading
import uuid


class MessageType(Enum):
    """Message types for GPIA-Gardener communication"""
    # Gardener → GPIA
    CLASSIFICATION_REQUEST = "classification_request"
    ARTIFACT_DISCOVERED = "artifact_discovered"
    ARTIFACT_ORGANIZED = "artifact_organized"
    STATS_UPDATE = "stats_update"
    ERROR_REPORT = "error_report"

    # GPIA → Gardener
    CLASSIFY_ARTIFACT = "classify_artifact"
    ORGANIZE_COMMAND = "organize_command"
    SCAN_DIRECTORY = "scan_directory"
    UPDATE_CONFIG = "update_config"
    SHUTDOWN = "shutdown"


@dataclass
class Message:
    """IPC message structure"""
    id: str
    type: MessageType
    timestamp: str
    payload: Dict[Any, Any]
    sender: str
    priority: int = 0  # Higher = more urgent

    def to_dict(self):
        return {
            **asdict(self),
            'type': self.type.value
        }

    @staticmethod
    def from_dict(data: Dict) -> 'Message':
        return Message(
            id=data['id'],
            type=MessageType(data['type']),
            timestamp=data['timestamp'],
            payload=data['payload'],
            sender=data['sender'],
            priority=data.get('priority', 0)
        )


class MessageQueue:
    """
    Atomic file-based message queue.
    Thread-safe, lock-free using atomic rename.
    """

    def __init__(self, queue_dir: Path):
        self.queue_dir = queue_dir
        self.queue_dir.mkdir(parents=True, exist_ok=True)

    def send(self, message: Message):
        """Send a message atomically"""
        # Write to temp file first
        temp_file = self.queue_dir / f".tmp_{message.id}"
        final_file = self.queue_dir / f"{message.id}.json"

        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump(message.to_dict(), f, indent=2)

        # Atomic rename
        temp_file.replace(final_file)

    def receive(self, delete: bool = True) -> Optional[Message]:
        """Receive next message (FIFO by timestamp)"""
        messages = sorted(self.queue_dir.glob("*.json"))

        if not messages:
            return None

        msg_file = messages[0]

        try:
            with open(msg_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                message = Message.from_dict(data)

            if delete:
                msg_file.unlink()

            return message

        except Exception as e:
            print(f"[BRIDGE] Error reading message {msg_file}: {e}")
            return None

    def receive_all(self, delete: bool = True) -> List[Message]:
        """Receive all pending messages"""
        messages = []
        while True:
            msg = self.receive(delete)
            if msg is None:
                break
            messages.append(msg)
        return messages

    def count(self) -> int:
        """Count pending messages"""
        return len(list(self.queue_dir.glob("*.json")))


class GPIABridge:
    """
    Bidirectional communication bridge between Gardener and GPIA.

    Usage:
        # Gardener side
        bridge = GPIABridge(root, sender="gardener")
        bridge.send_to_gpia(MessageType.ARTIFACT_DISCOVERED, {...})

        # GPIA side
        bridge = GPIABridge(root, sender="gpia")
        bridge.send_to_gardener(MessageType.CLASSIFY_ARTIFACT, {...})
        bridge.listen_from_gardener(callback)
    """

    def __init__(self, root: Path, sender: str):
        self.root = Path(root)
        self.sender = sender

        # Setup queues
        ipc_dir = self.root / "data" / "ipc" / "messages"
        self.to_gpia = MessageQueue(ipc_dir / "to_gpia")
        self.to_gardener = MessageQueue(ipc_dir / "to_gardener")

        # Listener thread
        self._listener_thread = None
        self._listener_active = False
        self._callbacks: Dict[MessageType, List[Callable]] = {}

    def send_to_gpia(self, msg_type: MessageType, payload: Dict):
        """Send message from Gardener to GPIA"""
        message = Message(
            id=str(uuid.uuid4()),
            type=msg_type,
            timestamp=datetime.now().isoformat(),
            payload=payload,
            sender=self.sender
        )
        self.to_gpia.send(message)

    def send_to_gardener(self, msg_type: MessageType, payload: Dict):
        """Send message from GPIA to Gardener"""
        message = Message(
            id=str(uuid.uuid4()),
            type=msg_type,
            timestamp=datetime.now().isoformat(),
            payload=payload,
            sender=self.sender
        )
        self.to_gardener.send(message)

    def receive_from_gpia(self, delete: bool = True) -> Optional[Message]:
        """Receive message from GPIA (called by Gardener)"""
        return self.to_gardener.receive(delete)

    def receive_from_gardener(self, delete: bool = True) -> Optional[Message]:
        """Receive message from Gardener (called by GPIA)"""
        return self.to_gpia.receive(delete)

    def register_callback(self, msg_type: MessageType, callback: Callable):
        """Register callback for specific message type"""
        if msg_type not in self._callbacks:
            self._callbacks[msg_type] = []
        self._callbacks[msg_type].append(callback)

    def listen_from_gardener(self, poll_interval: float = 1.0):
        """
        Start listening to Gardener messages in background.
        Dispatches to registered callbacks.
        """
        if self._listener_active:
            return

        self._listener_active = True
        self._listener_thread = threading.Thread(
            target=self._listener_loop,
            args=(self.to_gpia, poll_interval),
            daemon=True
        )
        self._listener_thread.start()

    def listen_from_gpia(self, poll_interval: float = 1.0):
        """
        Start listening to GPIA messages in background.
        Dispatches to registered callbacks.
        """
        if self._listener_active:
            return

        self._listener_active = True
        self._listener_thread = threading.Thread(
            target=self._listener_loop,
            args=(self.to_gardener, poll_interval),
            daemon=True
        )
        self._listener_thread.start()

    def _listener_loop(self, queue: MessageQueue, poll_interval: float):
        """Background listener loop"""
        print(f"[BRIDGE] Listener started (polling every {poll_interval}s)")

        while self._listener_active:
            try:
                messages = queue.receive_all(delete=True)

                for message in messages:
                    # Dispatch to callbacks
                    callbacks = self._callbacks.get(message.type, [])
                    for callback in callbacks:
                        try:
                            callback(message)
                        except Exception as e:
                            print(f"[BRIDGE] Callback error for {message.type}: {e}")

            except Exception as e:
                print(f"[BRIDGE] Listener error: {e}")

            time.sleep(poll_interval)

    def stop_listening(self):
        """Stop background listener"""
        self._listener_active = False
        if self._listener_thread:
            self._listener_thread.join(timeout=5.0)

    def get_stats(self) -> Dict:
        """Get bridge statistics"""
        return {
            'to_gpia_pending': self.to_gpia.count(),
            'to_gardener_pending': self.to_gardener.count(),
            'listener_active': self._listener_active,
            'registered_callbacks': {
                msg_type.value: len(callbacks)
                for msg_type, callbacks in self._callbacks.items()
            }
        }


# Convenience functions for common operations

def notify_gpia_artifact_discovered(bridge: GPIABridge, artifact_path: str, classification: str):
    """Notify GPIA that a new artifact was discovered"""
    bridge.send_to_gpia(
        MessageType.ARTIFACT_DISCOVERED,
        {
            'artifact_path': artifact_path,
            'classification': classification,
            'timestamp': datetime.now().isoformat()
        }
    )


def notify_gpia_artifact_organized(bridge: GPIABridge, artifact_path: str,
                                     source: str, destination: str, classification: str):
    """Notify GPIA that an artifact was organized"""
    bridge.send_to_gpia(
        MessageType.ARTIFACT_ORGANIZED,
        {
            'artifact_path': artifact_path,
            'source': source,
            'destination': destination,
            'classification': classification,
            'timestamp': datetime.now().isoformat()
        }
    )


def request_gpia_classification(bridge: GPIABridge, artifact_path: str,
                                  signature: str, size: int) -> str:
    """
    Request GPIA to classify an artifact.
    Returns message ID for tracking.
    """
    msg_id = str(uuid.uuid4())
    bridge.send_to_gpia(
        MessageType.CLASSIFICATION_REQUEST,
        {
            'request_id': msg_id,
            'artifact_path': artifact_path,
            'signature': signature,
            'size': size,
            'timestamp': datetime.now().isoformat()
        }
    )
    return msg_id


def send_gardener_stats(bridge: GPIABridge, stats: Dict):
    """Send Gardener statistics to GPIA"""
    bridge.send_to_gpia(
        MessageType.STATS_UPDATE,
        {
            'stats': stats,
            'timestamp': datetime.now().isoformat()
        }
    )


def command_gardener_scan(bridge: GPIABridge, directory: str):
    """Command Gardener to scan a directory"""
    bridge.send_to_gardener(
        MessageType.SCAN_DIRECTORY,
        {
            'directory': directory,
            'timestamp': datetime.now().isoformat()
        }
    )


if __name__ == "__main__":
    # Test mode
    print("GPIA Bridge - Test Mode\n")

    root = Path(__file__).parent.parent

    # Simulate Gardener
    print("[Gardener] Sending test message to GPIA...")
    gardener_bridge = GPIABridge(root, sender="gardener")
    notify_gpia_artifact_discovered(
        gardener_bridge,
        "test_skill.py",
        "SKILL_SYNTHESIZED"
    )

    # Simulate GPIA
    print("[GPIA] Receiving message from Gardener...")
    gpia_bridge = GPIABridge(root, sender="gpia")
    message = gpia_bridge.receive_from_gardener()

    if message:
        print(f"[GPIA] Received: {message.type.value}")
        print(f"        Payload: {message.payload}")
        print("\nBridge test successful!")
    else:
        print("[GPIA] No message received")
