import bpy
bpy.ops.preferences.addon_install(filepath='/home/MotionGPT/blender-animation-retargeting-stable.zip')
bpy.ops.preferences.addon_enable(module='blender-animation-retargeting-stable')
bpy.ops.wm.save_userpref()