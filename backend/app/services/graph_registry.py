"""Graph registry for mapping evaluation modes to graph builders."""

import threading
from typing import Callable, Dict

from app.models.graph import ReactFlowGraph, Graph3DPayload

GraphBuilder2D = Callable[[str], ReactFlowGraph]
GraphBuilder3D = Callable[[str, list | None], Graph3DPayload]

_builders_2d: Dict[str, GraphBuilder2D] = {}
_builders_3d: Dict[str, GraphBuilder3D] = {}
_lock = threading.Lock()


class GraphRegistry:
    @classmethod
    def register_2d(cls, mode: str, builder: GraphBuilder2D) -> None:
        with _lock:
            _builders_2d[mode] = builder

    @classmethod
    def register_3d(cls, mode: str, builder: GraphBuilder3D) -> None:
        with _lock:
            _builders_3d[mode] = builder

    @classmethod
    def get_2d_builder(cls, mode: str) -> GraphBuilder2D:
        if mode not in _builders_2d:
            raise ValueError(f"Unsupported mode: {mode}")
        return _builders_2d[mode]

    @classmethod
    def get_3d_builder(cls, mode: str) -> GraphBuilder3D:
        if mode not in _builders_3d:
            raise ValueError(f"Unsupported mode: {mode}")
        return _builders_3d[mode]

    @classmethod
    def supported_modes(cls) -> list[str]:
        return list(_builders_2d.keys())

    @classmethod
    def is_supported(cls, mode: str) -> bool:
        return mode in _builders_2d

    @classmethod
    def clear(cls) -> None:
        with _lock:
            _builders_2d.clear()
            _builders_3d.clear()
