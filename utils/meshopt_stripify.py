import ctypes
import numpy as np
import os.path


# Load Mesh Optimizer DLL
meshopt = ctypes.CDLL(os.path.join(os.path.dirname(__file__), "meshoptimizer.dll"))

# Index buffers shared with meshoptimizer are arrays of unsigned int. Numpy's own
# np.uint is 64 bit wide from numpy 2.0 onwards, including on Windows where it used
# to be 32, so the width has to be stated rather than inferred: a mismatch makes the
# library read and write half-indices and produces garbage strip points.
INDEX_DTYPE = np.uint32

def stripify(triangles, vertex_count):
    """Stripify triangles, optimizing for the vertex cache."""

    points = [vertex for triangle in triangles for vertex in triangle]
    point_count = len(points)

    # Optimize the vertex cache for strips
    cached_points = cache_vertices(points, point_count, vertex_count)
    cached_point_count = len(cached_points)

    # Compute worst case size of output strips
    strip_bound = meshopt_stripify_bound(cached_point_count)

    # Stripify and stitch triangle points
    strips = meshopt_stripify(cached_points, cached_point_count, strip_bound, vertex_count)

    # Return the nested list of strips with one element
    return [strips.tolist()]

def cache_vertices(points, point_count, vertex_count):
    return meshopt_optimize_vertex_cache_strip(points, point_count, vertex_count).tolist()

# Vertex Cache Function Params
meshopt.meshopt_optimizeVertexCacheStrip.restype = None # Void
meshopt.meshopt_optimizeVertexCacheStrip.argtypes = [
    ctypes.POINTER(ctypes.c_uint),    # Output indices
    ctypes.POINTER(ctypes.c_uint),    # Input indices
    ctypes.c_size_t,                  # Index count
    ctypes.c_size_t,                  # Vertex count
]

def meshopt_optimize_vertex_cache_strip(points, point_count, vertex_count):
    output_array = np.zeros(point_count, dtype=INDEX_DTYPE)
    points_array = np.array(points, dtype=INDEX_DTYPE).flatten()
    array_size = ctypes.c_size_t(point_count)
    vertices_size = ctypes.c_size_t(vertex_count)

    meshopt.meshopt_optimizeVertexCacheStrip(
        output_array.ctypes.data_as(ctypes.POINTER(ctypes.c_uint)),
        points_array.ctypes.data_as(ctypes.POINTER(ctypes.c_uint)),
        array_size,
        vertices_size
    )

    return output_array

# Stripify Function Params
meshopt.meshopt_stripify.restype = ctypes.c_size_t # Returns size_t
meshopt.meshopt_stripify.argtypes = [
    ctypes.POINTER(ctypes.c_uint),    # Output indices
    ctypes.POINTER(ctypes.c_uint),    # Input indices
    ctypes.c_size_t,                  # Index count
    ctypes.c_size_t,                  # Vertex count
    ctypes.c_uint                     # Restart Index
]

def meshopt_stripify(points, points_count, strip_bound, vertex_count):
    output_array = np.zeros(strip_bound, dtype=INDEX_DTYPE)
    points_array = np.array(points, dtype=INDEX_DTYPE).flatten()
    points_size = ctypes.c_size_t(points_count)
    vertices_size = ctypes.c_size_t(vertex_count)
    restart_index = ctypes.c_uint(0)

    strip_size = meshopt.meshopt_stripify(
        output_array.ctypes.data_as(ctypes.POINTER(ctypes.c_uint)),
        points_array.ctypes.data_as(ctypes.POINTER(ctypes.c_uint)),
        points_size,
        vertices_size,
        restart_index
    )

    return output_array[:strip_size]

# Stripify Bound Function Params
meshopt.meshopt_stripifyBound.restype = ctypes.c_size_t
meshopt.meshopt_stripifyBound.argtypes = [
    ctypes.c_size_t,                       # Index count
]

def meshopt_stripify_bound(points_count):
    points_size = ctypes.c_size_t(points_count)

    strip_bound = meshopt.meshopt_stripifyBound(points_size)

    return strip_bound