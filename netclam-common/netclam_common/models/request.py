from dataclasses import dataclass

PENDING = "PENDING"
COMPLETE = "COMPLETE"

@dataclass
class request:

    id: str
    status: str
    created_time: str
    updated_time: str
