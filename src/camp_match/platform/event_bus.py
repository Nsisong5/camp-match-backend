from camp_match.platform.in_memory_event_bus import InMemoryEventBus

_event_bus = InMemoryEventBus()

def get_event_bus() -> InMemoryEventBus:
    return _event_bus
