import os
import platform
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "utils"))

from meshoptimizer import stripify_from_triangles, unstripify_to_triangles


def main():
    size = 3
    triangles = []
    for row in range(size - 1):
        for col in range(size - 1):
            v0 = row * size + col
            v1 = v0 + 1
            v2 = v0 + size
            v3 = v2 + 1
            triangles.append((v0, v2, v1))
            triangles.append((v1, v2, v3))

    vertex_count = size * size
    expected = {frozenset(t) for t in triangles}

    result = stripify_from_triangles(triangles)

    if not result or not result[0]:
        raise SystemExit("stripify returned no strip: %r" % (result,))

    strip = result[0]
    print("triangles  %d in, strip of %d points out" % (len(triangles), len(strip)))

    if max(strip) >= vertex_count or min(strip) < 0:
        raise SystemExit(
            "strip contains out-of-range indices (0..%d expected): %r"
            % (vertex_count - 1, strip)
        )

    produced = unstripify_to_triangles(result)
    if produced != expected:
        raise SystemExit(
            "strip does not reproduce the input triangles\n"
            "  missing: %r\n"
            "  extra:   %r" % (expected - produced, produced - expected)
        )

    print("OK: strip reproduces all %d triangles" % len(expected))


if __name__ == "__main__":
    main()
