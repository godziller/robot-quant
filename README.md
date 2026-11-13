# robot-quant

Dissertation project investigating whether the throughput–accuracy trade-off observed in NPU-deployed frame classification also applies to **closed-loop robotic control**, and whether **INT8 quantization degrades continuous control more severely than it degrades classification**.

![SO-ARM100 arm in MuJoCo](images/so101.png)

## Status

| Stage | State |
|---|---|
| MuJoCo simulation of the SO-ARM100 arm | Working |
| Scripted demo | Working |
| Policy inference (FP32 baseline) | TODO |
| INT8 quantization | TODO |
| NPU deployment and benchmarking | TODO |

## Repository layout

```
robot-quant/
├── assets/
│   └── so_arm100/          # MuJoCo arm model (vendored, see Attribution)
│       ├── pickplace.xml   # arm + cube + tray: the work-cell used in this project
│       ├── scene.xml       # arm + floor/lighting (not used yet)
│       ├── so_arm100.xml   # the arm model itself
│       ├── assets/         # STL meshes
│       ├── LICENSE
│       └── CHANGELOG.md
├── docs/
│   └── MODEL_SELECTION.md  # why this model/policy was chosen
├── images/                 # README images
├── papers/                 # reference papers (PDF)
├── script/
│   └── test_mujoco.py      # scripted back-and-forth arm demo
├── videos/                 # demo recordings
└── requirements.txt
```

## Setup

Run once from the repository root.

```bash
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\Activate.ps1
python3 -m pip install --upgrade pip
pip install -r requirements.txt
python -c "import mujoco; print('MuJoCo:', mujoco.__version__)"
```

Every later session only needs the `source .venv/bin/activate` line.

## Usage

### Run the scripted demo

```bash
python script/test_mujoco.py
```

Opens the MuJoCo viewer and moves the arm back and forth. Close the viewer window to stop the script.

Demo recording: [videos/MovingMujoco.webm](videos/MovingMujoco.webm)

### Open the work-cell in the interactive viewer

```bash
python -m mujoco.viewer --mjcf=assets/so_arm100/pickplace.xml
```

Opens the SO-ARM100 work-cell: the arm, a cube and a tray.

On macOS, use `mjpython` in place of `python` if the viewer refuses to launch.

### Move the cube

1. **Pause the simulation** with `Space`. The cube is welded to the table while the sim runs, so it can only be repositioned while paused.
2. **Select the cube:** hold `Ctrl` + `Shift` and double left-click it.
3. **Move it:** once the cube turns bright red, hold `Ctrl` + `Shift` and hold the right mouse button while dragging.
4. Press `Space` again to resume the simulation.


#### Viewer controls

| Action | Control |
|---|---|
| Pause / resume physics | `Space` |
| Rotate camera | Left-drag |
| Pan camera | Right-drag |
| Zoom | Scroll wheel |
| Select a body | Double-click |
| Move the arm joints | Right-hand **Control** panel sliders |

## Documentation

- [Model selection](docs/MODEL_SELECTION.md): scoring rubric and candidate comparison. Current provisional pick: [`ahmedsohail2003/act-so101-pickplace-dr`](https://huggingface.co/ahmedsohail2003/act-so101-pickplace-dr) (ACT, simulation-first). NPU latency and INT8 accuracy drop are still to be measured.

## References

Papers kept in [`papers/`](papers/):

- *A Reduction of Imitation Learning and Structured Prediction to No-Regret Online Learning* (DAgger)
- *Quantization and Training of Neural Networks for Efficient Integer-Arithmetic-Only Inference*
- *Quantization-Aware Imitation Learning for Resource-Efficient Robotic Control*

## Attribution

The arm model in `assets/so_arm100/` is vendored from [MuJoCo Menagerie](https://github.com/google-deepmind/mujoco_menagerie) (`trs_so_arm100`), licensed Apache-2.0; see [`assets/so_arm100/LICENSE`](assets/so_arm100/LICENSE).



