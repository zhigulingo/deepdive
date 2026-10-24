"""Open underwater-canyon.blend, then run this file from Blender's Scripting workspace."""
import bpy, json, math
from pathlib import Path
from mathutils import Vector

VIEWS = 180
WIDTH, HEIGHT = 960, 600
SAMPLES = 32

scene = bpy.context.scene
blend_path = Path(bpy.data.filepath)
if not blend_path.name:
    raise RuntimeError("Save/open underwater-canyon.blend before running this script")
out = blend_path.parent / "underwater_dataset"
images = out / "images"
images.mkdir(parents=True, exist_ok=True)

# Blender 4.2 renamed EEVEE to EEVEE Next; try the current id first and retain 4.0 compatibility.
try:
    scene.render.engine = 'BLENDER_EEVEE_NEXT'
except TypeError:
    scene.render.engine = 'BLENDER_EEVEE'
scene.render.resolution_x, scene.render.resolution_y = WIDTH, HEIGHT
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'
scene.render.image_settings.color_mode = 'RGB'
scene.render.film_transparent = False
scene.render.image_settings.color_depth = '8'
if hasattr(scene, 'eevee') and hasattr(scene.eevee, 'taa_render_samples'):
    scene.eevee.taa_render_samples = SAMPLES

cam = scene.camera
cam.data.lens = 28
cam.data.sensor_width = 32
target = Vector((0, 0, -1.1))
frames = []

def matrix_rows(m):
    # Blender camera-to-world uses OpenGL camera axes, which transforms.json expects.
    return [[float(m[r][c]) for c in range(4)] for r in range(4)]

for i in range(VIEWS):
    t = i / VIEWS
    # Three gently varying orbits cover the canyon floor and both walls.
    angle = -math.pi * .62 + t * math.pi * 2.25
    radius = 13.5 + 2.2 * math.sin(t * math.pi * 4)
    cam.location = (math.sin(angle) * radius, -math.cos(angle) * radius, -0.2 + 3.8 * math.sin(t * math.pi * 2.0) ** 2)
    aim = target + Vector((1.6 * math.sin(t * math.pi * 6), 2.4 * math.sin(t * math.pi * 2), .45 * math.cos(t * math.pi * 4)))
    cam.rotation_euler = (aim - cam.location).to_track_quat('-Z', 'Y').to_euler()
    name = f"frame_{i:04d}"
    scene.render.filepath = str(images / f"{name}.png")
    bpy.ops.render.render(write_still=True)
    frames.append({"file_path": f"images/{name}.png", "transform_matrix": matrix_rows(cam.matrix_world)})
    print(f"SPLAT DATASET {i + 1}/{VIEWS}")

camera_angle_x = 2 * math.atan(cam.data.sensor_width / (2 * cam.data.lens))
payload = {
    "camera_model": "OPENCV",
    "camera_angle_x": camera_angle_x,
    "fl_x": WIDTH / (2 * math.tan(camera_angle_x / 2)),
    "fl_y": WIDTH / (2 * math.tan(camera_angle_x / 2)),
    "cx": WIDTH / 2,
    "cy": HEIGHT / 2,
    "w": WIDTH,
    "h": HEIGHT,
    "frames": frames,
}
(out / "transforms.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
(out / "README.txt").write_text(
    f"Deepdive synthetic underwater dataset\n{VIEWS} PNG images at {WIDTH}x{HEIGHT}\nCamera poses: transforms.json\n",
    encoding="utf-8",
)
print(f"DONE: {out}")
