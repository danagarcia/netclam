from dataclasses import dataclass

@dataclass
class MetricConfig:

    namespace: str
    subsystem: str
    enabled: bool