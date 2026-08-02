import os
import platform
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "utils"))

import meshopt_stripify


def triangles_from_strip(strip):
    triangles = set()
    for i in range(len(strip) - 2):
        a, b, c = strip[i], strip[i + 1], strip[i + 2]
        if a == b or b == c or a == c:
            continue
        triangles.add(frozenset((a, b, c)))
    return triangles


def main():
    print("python     %s" % sys.version.split()[0])
    print("platform   %s" % sys.platform)
    print("machine    %s" % platform.machine())
    print("library    %s" % meshopt_stripify.MESHOPT_LIBRARY)
    print("loaded     %s" % meshopt_stripify.meshopt._name)

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

    result = meshopt_stripify.stripify(triangles, vertex_count)

    if not result or not result[0]:
        raise SystemExit("stripify returned no strip: %r" % (result,))

    strip = result[0]
    print("triangles  %d in, strip of %d points out" % (len(triangles), len(strip)))

    if max(strip) >= vertex_count or min(strip) < 0:
        raise SystemExit(
            "strip contains out-of-range indices (0..%d expected): %r"
            % (vertex_count - 1, strip)
        )

    produced = triangles_from_strip(strip)
    if produced != expected:
        raise SystemExit(
            "strip does not reproduce the input triangles\n"
            "  missing: %r\n"
            "  extra:   %r" % (expected - produced, produced - expected)
        )

    print("OK: strip reproduces all %d triangles" % len(expected))


if __name__ == "__main__":
    main()
