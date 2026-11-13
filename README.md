# robot-quant
This dissertation investigates whether the throughput–accuracy trade-off observed in NPU-deployed frame classification also applies to closed-loop robotic control, and whether INT8 quantization degrades continuous control more severely than it degrades classification

# running mujoco

## Run the scripted demo

Create and activate the virtual environment, install the dependencies, and run
the Python script from the repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install --upgrade pip
pip install -r requirements.txt
python script/test_mujoco.py
```

The script opens the MuJoCo viewer and moves the SO-101 arm back and forth.
Close the viewer to stop the script.

### Demo video

[Watch the scripted MuJoCo demo](videos/MovingMujoco.webm)

<video src="videos/MovingMujoco.webm" controls width="640"></video>

## Open MuJoCo manually

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install --upgrade pip
pip install -r requirements.txt
python -c "import mujoco; print('MuJoCo:', mujoco.__version__)"
python -m mujoco.viewer --mjcf=assets/robotstudio_so101/scene.xml
```

![SO-101 Arm](images/so101.png)
