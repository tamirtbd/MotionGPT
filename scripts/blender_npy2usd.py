import bpy
import numpy as np
from sys import argv
from mathutils import Matrix

humanml3d_joints = [ 'root', 'RH', 'LH', 'BP', 'RK', 'LK', 'BT', 'RMrot', 'LMrot', 'BLN', 'RF', 'LF', 'BMN', 'RSI', 'LSI', 'BUN', 'RS', 'LS', 'RE', 'LE', 'RW', 'LW' ]
smplh_joints = 'pelvis, right_hip, left_hip, spine1, right_knee, left_knee, spine3, right_ankle, left_ankle, neck, right_foot, left_foot, jaw, right_collar, left_collar, head, right_shoulder, left_shoulder, right_elbow, left_elbow, right_wrist, left_wrist'.split(', ')

# Get Numpy File Path from cli keyword arguments
clean_argv = argv[5:]
nargs = len(clean_argv)

apairs = np.array(clean_argv).reshape((int(nargs/2), 2))
args = {k.replace('-',''): v for k, v in apairs}
print(args)

fp = args['npy_pose_file_path']
a = np.load(fp)

# Select skeleton
C = bpy.context
skel = bpy.data.objects['SMPLX-male']
skel.select_set(True)

# Minor transformations on poses
aroot = a[[0], 0]
aroot[:, 1] = -aroot[:, 1]

# Create keyframes for each of the next frames
for i, f in enumerate( a ):
    n = i+1
    
    for r, name in zip( f, smplh_joints ):
        pb = skel.pose.bones[name]
        rotmat = Matrix( r )
        rotmat = rotmat.inverted()
        quat = rotmat.to_quaternion()
        quat.x *= -1
        
        pb.rotation_quaternion = quat
        pb.keyframe_insert('rotation_quaternion', frame=n)

# Final adjustments to orient character    
bpy.ops.transform.rotate(value=3.14159, orient_axis='X', orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', constraint_axis=(True, False, False), mirror=False, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False, snap=False, snap_elements={'INCREMENT'}, use_snap_project=False, snap_target='CLOSEST', use_snap_self=True, use_snap_edit=True, use_snap_nonedit=True, use_snap_selectable=False)
bpy.ops.transform.rotate(value=3.14159, orient_axis='Z', orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', constraint_axis=(False, False, True), mirror=False, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False, snap=False, snap_elements={'INCREMENT'}, use_snap_project=False, snap_target='CLOSEST', use_snap_self=True, use_snap_edit=True, use_snap_nonedit=True, use_snap_selectable=False)
bpy.ops.transform.translate(value=(-0, -0, -0.357846), orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', constraint_axis=(False, False, True), mirror=False, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False, snap=False, snap_elements={'INCREMENT'}, use_snap_project=False, snap_target='CLOSEST', use_snap_self=True, use_snap_edit=True, use_snap_nonedit=True, use_snap_selectable=False)

# Export USD
export_path = args['export_path']

bpy.ops.wm.usd_export(filepath=export_path, export_animation=True, export_normals=False, export_materials=False, export_shapekeys=True)
