import bpy, math, random
from mathutils import Vector

random.seed(17)
bpy.ops.wm.read_factory_settings(use_empty=True)

def mat(name, color, rough=.8, emission=None):
    m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True
    bs=m.node_tree.nodes.get('Principled BSDF'); bs.inputs['Base Color'].default_value=(*color,1); bs.inputs['Roughness'].default_value=rough
    if emission:
        bs.inputs['Emission Color'].default_value=(*emission,1); bs.inputs['Emission Strength'].default_value=.18
    return m

rock=mat('Sinai limestone',(0.19,.16,.11),.94); sand=mat('Red Sea sand',(.34,.26,.16),1); coral=mat('Coral',(.37,.12,.075),.72,(.12,.025,.012))

# A traversable canyon: irregular floor with two steep, eroded walls.
N=72; size=28; verts=[]; faces=[]
for y in range(N):
    py=(y/(N-1)-.5)*size
    for x in range(N):
        px=(x/(N-1)-.5)*size
        channel=math.exp(-(px/3.8)**4)
        shelves=(1-channel)*(4.3+1.6*math.sin(py*.22+px*.34))
        noise=.45*math.sin(px*1.15+math.sin(py*.3))+0.22*math.sin(py*1.7+px*.4)
        z=-4.4+shelves+noise
        verts.append((px,py,z))
for y in range(N-1):
    for x in range(N-1):
        a=y*N+x; faces.extend(((a,a+1,a+N+1,a+N),(a+1,a+2 if x+2<N else a+1,a+N+1,a+N+1))) if False else faces.append((a,a+1,a+N+1,a+N))
mesh=bpy.data.meshes.new('Canyon terrain'); mesh.from_pydata(verts,[],faces); mesh.materials.append(rock)
terrain=bpy.data.objects.new('Canyon terrain',mesh); bpy.context.collection.objects.link(terrain)
bev=terrain.modifiers.new('Weathered edges','BEVEL'); bev.width=.08; bev.segments=2

for i in range(95):
    x=random.choice((-1,1))*random.uniform(4.2,13); y=random.uniform(-13,13); z=random.uniform(-3.2,1.5)
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=random.uniform(.18,.85),location=(x,y,z))
    o=bpy.context.object; o.name='Rock'; o.scale=(random.uniform(.8,2.2),random.uniform(.7,1.7),random.uniform(.45,1.15)); o.rotation_euler=[random.random()*2 for _ in range(3)]; o.data.materials.append(rock)

for i in range(34):
    side=random.choice((-1,1)); x=side*random.uniform(4.4,9.5); y=random.uniform(-11,11); z=random.uniform(-2.7,.2)
    branches=random.randint(3,7)
    for b in range(branches):
        h=random.uniform(.18,.72); bpy.ops.mesh.primitive_cone_add(vertices=7,radius1=.055,radius2=.018,depth=h,location=(x+random.uniform(-.18,.18),y+random.uniform(-.18,.18),z+h/2))
        c=bpy.context.object;c.name='Coral';c.rotation_euler=(random.uniform(-.35,.35),random.uniform(-.35,.35),random.random());c.data.materials.append(coral)

# Water volume and soft sun shafts.
bpy.ops.mesh.primitive_cube_add(size=2,location=(0,0,3)); water=bpy.context.object; water.name='Water volume'; water.scale=(18,18,8)
vm=bpy.data.materials.new('Water haze'); vm.use_nodes=True; nt=vm.node_tree; nt.nodes.clear(); out=nt.nodes.new('ShaderNodeOutputMaterial'); vol=nt.nodes.new('ShaderNodeVolumePrincipled'); vol.inputs['Color'].default_value=(.015,.16,.19,1); vol.inputs['Density'].default_value=.018; vol.inputs['Anisotropy'].default_value=.35; nt.links.new(vol.outputs['Volume'],out.inputs['Volume']); water.data.materials.append(vm)
bpy.ops.object.light_add(type='AREA',location=(-4,-4,9)); sun=bpy.context.object; sun.data.energy=1700; sun.data.shape='DISK'; sun.data.size=7; sun.data.color=(.58,.88,1)

bpy.ops.object.camera_add(location=(0,-16,-.5)); cam=bpy.context.object; cam.data.lens=28; cam.data.sensor_width=32
def look(obj,target): obj.rotation_euler=(Vector(target)-obj.location).to_track_quat('-Z','Y').to_euler()
look(cam,(0,1,-1.2)); bpy.context.scene.camera=cam
world=bpy.data.worlds.new('Deep water'); bpy.context.scene.world=world; world.use_nodes=True; world.node_tree.nodes['Background'].inputs['Color'].default_value=(.002,.035,.055,1); world.node_tree.nodes['Background'].inputs['Strength'].default_value=.18

scene=bpy.context.scene; scene.render.engine='BLENDER_EEVEE'; scene.render.resolution_x=960; scene.render.resolution_y=600; scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'; scene.render.filepath='/root/.openclaw/workspace/deepdive/assets/underwater-canyon-preview.png'; scene.render.film_transparent=False
scene.view_settings.look='AgX - Medium High Contrast'; scene.render.image_settings.color_mode='RGBA'
bpy.ops.wm.save_as_mainfile(filepath='/root/.openclaw/workspace/deepdive/assets/underwater-canyon.blend')
bpy.ops.render.render(write_still=True)
