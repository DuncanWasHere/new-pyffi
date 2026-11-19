"""
Stripify functions for meshoptimizer.
"""

import ctypes
from typing import Optional
import numpy as np

from . import optimize_vertex_cache_strip
from ._loader import lib


def stripify(indices: np.ndarray, index_count: Optional[int] = None, vertex_count: Optional[int] = None) -> np.ndarray:
    """
    Converts a triangle list to triangle strip, stitching strips using degenerate triangles.

    Args:
        indices: numpy array of index data
        index_count: number of indices (optional, derived from indices if not provided)
        vertex_count: number of vertices (optional, derived from vertices if not provided)

    Returns:
        Stripified index data

    Raises:
        ValueError: if parameters are invalid or would cause excessive memory allocation
        RuntimeError: if stripifying fails
    """
    # Convert indices to numpy array if it's not already
    indices = np.asarray(indices, dtype=np.uint32)

    # Derive index_count if not provided
    if index_count is None:
        index_count = len(indices)

    # Derive vertex_count if not provided
    if vertex_count is None:
        vertex_count = np.max(indices) + 1

    # Optimize vertex cache for strips
    optimized_indices = np.zeros(index_count, dtype=np.uint32)
    optimize_vertex_cache_strip(optimized_indices, indices, index_count, vertex_count)

    # Use degenerate triangles
    restart_index = ctypes.c_uint(0)

    # Calculate destination size
    bound = lib.meshopt_stripifyBound(index_count)

    # Allocate destination
    destination = np.zeros(bound, dtype=np.uint32)

    # Call C function
    result_size = lib.meshopt_stripify(
        destination.ctypes.data_as(ctypes.POINTER(ctypes.c_uint)),
        optimized_indices.ctypes.data_as(ctypes.POINTER(ctypes.c_uint)),
        index_count,
        vertex_count,
        restart_index
    )

    if result_size == 0:
        raise RuntimeError("Failed to stripify")

    return destination[:result_size]


def stripify_from_triangles(triangles: list[tuple[int]]) -> list[list[int]]:
    indices = np.asarray([index for triangle in triangles for index in triangle], dtype=np.uint32)
    return [stripify(indices).tolist()]


def unstripify(indices: np.ndarray, index_count: Optional[int] = None) -> np.ndarray:
    """
    Converts a triangle strip to a triangle list.

    Args:
        indices: numpy array of index data
        index_count: number of indices (optional, derived from indices if not provided)

    Returns:
        Triangulated index data

    Raises:
        ValueError: if parameters are invalid or would cause excessive memory allocation
        RuntimeError: if unstripifying fails
    """
    # Convert indices to numpy array if it's not already
    indices = np.asarray(indices, dtype=np.uint32)

    # Derive index_count if not provided
    if index_count is None:
        index_count = len(indices)

    # Use degenerate triangles
    restart_index = ctypes.c_uint(0)

    # Calculate destination size
    bound = lib.meshopt_unstripifyBound(index_count)

    # Allocate destination
    destination = np.zeros(bound, dtype=np.uint32)

    # Call C function
    result_size = lib.meshopt_unstripify(
        destination.ctypes.data_as(ctypes.POINTER(ctypes.c_uint)),
        indices.ctypes.data_as(ctypes.POINTER(ctypes.c_uint)),
        index_count,
        restart_index
    )

    if result_size == 0:
        raise RuntimeError("Failed to unstripify")

    return destination[:result_size]


def unstripify_to_triangles(indices: list[list[int]], index_count: Optional[int] = None) -> list[tuple[int, ...]]:
    triangle_indices = unstripify(np.asarray(indices[0], dtype=np.uint32), index_count)
    return [tuple(int(index) for index in triangle_indices[i:i + 3]) for i in range(0, triangle_indices.size, 3)]
