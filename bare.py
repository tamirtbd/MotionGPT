import torch
import numpy as np
from pathlib import Path
import pytorch_lightning as pl
from scipy.spatial.transform import Rotation as RRR

from mGPT.render.pyrender.hybrik_loc2rot import HybrIKJointsToRotmat
from mGPT.data.build_data import build_data
from mGPT.models.build_model import build_model
from mGPT.config import parse_args

from os import environ

def export_pose_data(data, name, output_data_dir):
    output_path = Path(output_data_dir)
    if (output_data_dir is not None) and output_path.exists():
        # EXPORT CONTROL POINT DATA
        cpfp = output_path.joinpath(f'{name}_control_points.npy')
        np.save(cpfp, data)

        if len(data.shape) == 4:
            data = data[0]

        data = data - data[0, 0]
        pose_generator = HybrIKJointsToRotmat()
        pose = pose_generator(data)
        pose = np.concatenate([
            pose,
            np.stack([np.stack([np.eye(3)] * pose.shape[0], 0)] * 2, 1)
        ], 1)

        r = RRR.from_rotvec(np.array([np.pi, 0.0, 0.0]))
        pose[:, 0] = np.matmul(r.as_matrix().reshape(1, 3, 3), pose[:, 0])

        posefp = output_path.joinpath(f'{name}_pose.npy')
        np.save(posefp, pose)


cfg = parse_args(phase="webui")  # parse config file
cfg.FOLDER = 'cache'
output_dir = Path(cfg.FOLDER) # TODO: CHANGE TO PARAM OR OTHER FOLDER
output_dir.mkdir(parents=True, exist_ok=True)
pl.seed_everything(cfg.SEED_VALUE)
if cfg.ACCELERATOR == "gpu":
    device = torch.device("cuda")
else:
    device = torch.device("cpu")
datamodule = build_data(cfg, phase="test")

model = build_model(cfg, datamodule)
state_dict = torch.load(cfg.TEST.CHECKPOINTS, map_location="cpu")["state_dict"]
model.load_state_dict(state_dict)
model.to(device)

motion_length, motion_token_string = 0, ''

from sys import argv
npairs = len(argv) - 1

apairs = np.array(argv[1:]).reshape((int(npairs/2), 2))
args = { k[2:]:v for k,v in apairs }

input  = args['prompt'] # 'a person is standing upright then sits cross legged'
prompt = model.lm.placeholder_fulfill(input, motion_length, motion_token_string, "")
batch  = { "length": [motion_length], "text": [prompt] }

outputs = model(batch, task="t2m")
out_lengths = outputs["length"][0]
out_joints = outputs["joints"][:out_lengths].detach().cpu().numpy()

output_dir = args['output_dir']

export_pose_data(out_joints, input, output_dir)