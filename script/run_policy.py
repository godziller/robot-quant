"""Run the ACT policy (ahmedsohail2003/act-so101-pickplace-dr) in the robot-quant MuJoCo scene.

    python script/run_policy.py [--episodes 5] [--seed 123]

Each episode places the block at a random spot inside the spawn region, runs the
policy for 16 s in the viewer, then resets.

Assumes: state = first 6 joint angles (rad), action = 6 absolute joint targets,
cameras "front" and "wrist" in the XML, policy trained at 15 Hz.
"""
import argparse
import time
from pathlib import Path

import mujoco
import mujoco.viewer
import numpy as np
import torch

# HuggingFace Hub repo for inferencing model.
REPO = "ahmedsohail2003/act-so101-pickplace-dr"
# MuJoCo scene XML model path for robot.
XML = Path(__file__).resolve().parents[1] / "assets" / "so_arm100" / "pickplace.xml"

# HZ        Control rate: policy steps per second. Must match the training data (15 fps).
#           Source: training dataset page, "15 fps":
#           https://huggingface.co/datasets/ahmedsohail2003/so101-sim-pickplace-dr
# IMG       Camera image size in pixels (224x224). The policy only accepts this size.
#           Source: model card, "Use" section: observation.images.front / .wrist (1,3,224,224)
#           https://huggingface.co/ahmedsohail2003/act-so101-pickplace-dr
# MAX_STEPS Episode length cap: 240 steps = 16 s at 15 Hz. Not a model requirement, just the
#           upstream author's eval timeout. Safe to change.
HZ, IMG, MAX_STEPS = 15, 224, 240

# Block spawn region (polar, relative to the arm base).
# Like a pizza slice in front of the robot, with the block's center at 0.19-0.27 m from the base and
# the block's face aligned with the gripper. The block is 0.012 m thick, so the block's center is at 0.012 m 
# above the table (z=0.012).
R_RANGE = (0.19, 0.27)                              # metres
THETA_RANGE = np.deg2rad((-20, 35))                 # radians
BLOCK_Z = 0.012


def reset(model, data, rng):
    mujoco.mj_resetData(model, data)
    home = model.key("home")
    data.qpos[:6], data.ctrl[:6] = home.qpos[:6], home.ctrl[:6]

    r, theta = rng.uniform(*R_RANGE), rng.uniform(*THETA_RANGE)
    x, y = r * np.sin(theta), -r * np.cos(theta)
    yaw = 0.5 * np.arctan2(x, -y)                   # align block faces with the gripper
    adr = model.jnt_qposadr[model.joint("block_free").id]
    data.qpos[adr:adr + 7] = [x, y, BLOCK_Z, np.cos(yaw), 0, 0, np.sin(yaw)]
    mujoco.mj_forward(model, data)
    return x, y


def observe(model, data, renderer, device):
    batch = {"observation.state": torch.tensor(data.qpos[:6], dtype=torch.float32, device=device)[None]}
    for name in ("front", "wrist"):
        renderer.update_scene(data, camera=name)
        img = torch.from_numpy(renderer.render().copy()).permute(2, 0, 1).float() / 255.0
        batch[f"observation.images.{name}"] = img[None].to(device)
    return batch


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--episodes", type=int, default=5)
    ap.add_argument("--seed", type=int, default=123)
    args = ap.parse_args()

    from huggingface_hub import snapshot_download
    from lerobot.policies import make_pre_post_processors
    from lerobot.policies.act.modeling_act import ACTPolicy

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    ckpt = snapshot_download(REPO)
    # Load the ACT policy onto the target device in eval mode and instantiate
    # LeRobot's official normalization pre/post-processors for observations and actions.
    policy = ACTPolicy.from_pretrained(ckpt).to(device).eval()
    pre, post = make_pre_post_processors(
        policy_cfg=policy.config,
        pretrained_path=ckpt,
        preprocessor_overrides={"device_processor": {"device": str(device)}},
    )

    model = mujoco.MjModel.from_xml_path(str(XML))  # Load the MuJoCo scene model for the robot and block.
    data = mujoco.MjData(model)     # How the arm is controlled & how observations are retrieved.
    renderer = mujoco.Renderer(model, IMG, IMG)     # Need to match MuJoCos renderers resolution to the policy's expected input image size (224x224).
    rng = np.random.default_rng(args.seed)  # Random number generator for block spawn positions.

    # advance the physics engine forward by this many tiny steps before asking for the next observation.
    substeps = max(1, round(1.0 / (HZ * model.opt.timestep)))

    # Min, max values for each actuators
    lo, hi = model.actuator_ctrlrange.T
    # Tells you whether a given actuator actually enforces those limits (represented as 1s and 0s).
    # This logic safely clamps it to the maximum or minimum bounds before sending it to the simulation, preventing the physics engine from glitching or exploding.
    limited = model.actuator_ctrllimited.astype(bool)

    with mujoco.viewer.launch_passive(model, data) as viewer:
        for ep in range(args.episodes):
            x, y = reset(model, data, rng)
            policy.reset()
            print(f"episode {ep}: block at x={x:+.3f} y={y:+.3f}")

            for step in range(MAX_STEPS):
                if not viewer.is_running():
                    return
                t0 = time.perf_counter()

                # Disables gradient computation for inference, which saves memory and speeds up the forward pass.
                with torch.no_grad():
                    # observe(): captures the current joints angels and camera pixels
                    # pre(): normalizes the observations to match the distribution seen during training
                    # policy.select_action(): runs the forward pass of the ACT policy to get the next action
                    # post(): denormalizes the action to match the original scale of the actuators
                    action = post(policy.select_action(pre(observe(model, data, renderer, device))))
                
                # Translate the model's batched GPU tensor output into a flat CPU NumPy array so MuJoCo can read it
                action = action.squeeze(0).cpu().numpy()

                # Difference between policys action and the current robot joint state. Unit checking.
                if step == 0:
                    print(f"  max |action - state| = {np.abs(action - data.qpos[:6]).max():.3f} (large = units mismatch)")

                # Safely apply the action the the actuators within the lo, hi bounds.
                # data: How we interface with MuJoCo, to impact the physics.            
                data.ctrl[:] = np.where(limited, np.clip(action, lo, hi), action)

                # Advance the physics engine forward by substeps tiny steps before asking for the next observation.
                for _ in range(substeps):
                    mujoco.mj_step(model, data)
                viewer.sync()

                # Pacing control. how long the step in total took. and sleeps for the remaining of the 15HZ time slot.
                time.sleep(max(0.0, 1.0 / HZ - (time.perf_counter() - t0)))

            time.sleep(1.0)


if __name__ == "__main__":
    main()