import mujoco
import mujoco.viewer
import time

model = mujoco.MjModel.from_xml_path("assets/so_arm100/scene.xml")
data = mujoco.MjData(model)

with mujoco.viewer.launch_passive(model, data) as viewer:

    while viewer.is_running():

        # PAUSE
        time.sleep(2)

        # MOVE 4 actuators
        data.ctrl[0] = 0.5
        data.ctrl[1] = -0.5
        data.ctrl[2] = 0.5
        data.ctrl[3] = -0.5
        data.ctrl[4] = 0.8

        # Let the robot move for 1 second
        start = time.time()
        while time.time() - start < 1:
            mujoco.mj_step(model, data)
            viewer.sync()
            time.sleep(0.01)

        # PAUSE
        time.sleep(2)

        # MOVE THEM BACK
        data.ctrl[0] = -0.5
        data.ctrl[1] = 0.5
        data.ctrl[2] = -0.5
        data.ctrl[3] = 0.5
        data.ctrl[4] = -0.8

        start = time.time()
        while time.time() - start < 1:
            mujoco.mj_step(model, data)
            viewer.sync()
            time.sleep(0.01)
