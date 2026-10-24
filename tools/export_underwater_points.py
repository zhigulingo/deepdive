import bpy
import math
import random
import struct
from pathlib import Path
from mathutils import Vector


POINTS = 240_000
SEED = 7319
OUT = Path(bpy.path.abspath("//underwater-canyon.points"))
EXCLUDE = {"camera", "water volume"}


def material_color(obj, polygon):
    if not obj.material_slots:
        return (0.22, 0.48, 0.42)
    index = min(polygon.material_index, len(obj.material_slots) - 1)
    mat = obj.material_slots[index].material
    if not mat:
        return (0.22, 0.48, 0.42)
    color = mat.diffuse_color[:3]
    if mat.use_nodes and mat.node_tree:
        node = mat.node_tree.nodes.get("Principled BSDF")
        if node and "Base Color" in node.inputs:
            color = node.inputs["Base Color"].default_value[:3]
    return tuple(max(0.0, min(1.0, float(c))) for c in color)


random.seed(SEED)
depsgraph = bpy.context.evaluated_depsgraph_get()
triangles = []
total_area = 0.0

for source in bpy.context.scene.objects:
    if source.type != "MESH" or source.name.lower() in EXCLUDE or source.hide_render:
        continue
    obj = source.evaluated_get(depsgraph)
    mesh = obj.to_mesh()
    mesh.calc_loop_triangles()
    matrix = obj.matrix_world
    normal_matrix = matrix.to_3x3().inverted().transposed()
    for tri in mesh.loop_triangles:
        a, b, c = (matrix @ mesh.vertices[i].co for i in tri.vertices)
        area = ((b - a).cross(c - a)).length * 0.5
        if area < 1e-8:
            continue
        normal = (normal_matrix @ tri.normal).normalized()
        color = material_color(source, mesh.polygons[tri.polygon_index])
        total_area += area
        triangles.append((total_area, a.copy(), b.copy(), c.copy(), normal.copy(), color))
    obj.to_mesh_clear()

if not triangles:
    raise RuntimeError("No renderable mesh triangles found")

OUT.parent.mkdir(parents=True, exist_ok=True)
points = []
mins = Vector((float("inf"),) * 3)
maxs = Vector((float("-inf"),) * 3)

for _ in range(POINTS):
    target = random.random() * total_area
    lo, hi = 0, len(triangles) - 1
    while lo < hi:
        mid = (lo + hi) // 2
        if triangles[mid][0] < target:
            lo = mid + 1
        else:
            hi = mid
    _, a, b, c, normal, color = triangles[lo]
    r1, r2 = random.random(), random.random()
    root = math.sqrt(r1)
    point = (1.0 - root) * a + root * (1.0 - r2) * b + root * r2 * c
    for axis in range(3):
        mins[axis] = min(mins[axis], point[axis])
        maxs[axis] = max(maxs[axis], point[axis])
    points.append((point, normal, color))

extent = max(maxs[i] - mins[i] for i in range(3)) or 1.0
with OUT.open("wb") as out:
    out.write(b"DPGS")
    out.write(struct.pack("<I", len(points)))
    out.write(struct.pack("<6f", *mins, *maxs))
    for point, normal, color in points:
        packed_pos = [round((point[i] - mins[i]) / max(1e-9, maxs[i] - mins[i]) * 65535) for i in range(3)]
        packed_normal = [round((normal[i] * 0.5 + 0.5) * 255) for i in range(3)]
        # Lift the procedural materials slightly so underwater relief stays readable.
        packed_color = [round((0.08 + 0.92 * (c ** (1 / 2.2))) * 255) for c in color]
        size = max(1, min(255, round(1650 / math.sqrt(POINTS) * 255 / extent)))
        out.write(struct.pack("<3H3B3BB", *packed_pos, *packed_normal, *packed_color, size))

print(f"Wrote {len(points):,} points to {OUT}")
print(f"Bounds: {tuple(round(v, 3) for v in mins)} .. {tuple(round(v, 3) for v in maxs)}")
