# Model selection for robot-quant

My provisional pick is **`ddduk/so101_act35_real_sim_v1`**, which scored 88 out of 100 on the rubric below (rubric v2, scored 24 October 2026). It stays provisional until I've measured latency and INT8 accuracy drop on the target NPU for the top three models.

The project is a control experiment: does INT8 quantization hurt closed-loop SO-101 control more than it hurts frame classification? To answer that I need a model with a working FP32 baseline, a size that fits on an NPU, and enough public evidence to reproduce it. A MuJoCo scene would also help, because then I don't have to rebuild the camera setup from scratch.

## Rubric (v2)

Each model has to pass four gates first. Models that pass are then scored from 1 to 5 on seven weighted criteria, which add up to 100 points. Weighted points = (score / 5) × weight.

**Gates (pass or fail)**

1. Takes SO-101 state as input and outputs 6-DOF actions (5 arm joints + gripper).
2. Weights are public and the licence allows research use.
3. Loads with LeRobot's `from_pretrained`.
4. I can reproduce an FP32 baseline myself.

**Criteria**

| Criterion | Weight | 5 points | 3 points | 1 point |
| --- | --- | --- | --- | --- |
| Task accuracy | 25 | Quantitative success of 80% or more over 50+ trials | Qualitative successful hardware rollout | No task-ready checkpoint |
| Inference speed | 20 | p95 policy call ≤ 50 ms on target | ≤ 250 ms | > 1 s |
| Quantization suitability | 20 | INT8 accuracy drop ≤ 2 points (measured) | Small model, export path untested | Multi-billion-parameter VLA |
| Evidence and reproducibility | 15 | Public dataset, training config and quantitative evaluation | Dataset or config partly missing | Qualitative claims only |
| Simulation assets | 10 | Ships with a MuJoCo scene, camera config or poses | Sim-trained, but not MuJoCo (or simulator not stated) | Real-world only, cameras undocumented |
| Fit to SO-101 arm | 5 | Verified in my setup | Cameras undocumented, three cameras, or custom processors | Incompatible state or action space |
| Licence | 5 | Apache-2.0 or MIT | Licence not seen, or inherited terms | Unclear or restrictive |

A 2 or a 4 means somewhere between the two nearest anchors. These are the specific anchors I used:

- **Simulation assets, 4:** validated in MuJoCo with an SO-101 model, but the camera poses or scene file aren't confirmed as included. **2:** real-world only, but camera names and resolution are documented.
- **Fit, 4:** same 6-DOF state and action space, with one or two documented cameras. **2:** the model card contradicts itself (for example, it uses a different robot type in its examples).
- **Accuracy, 4:** quantitative evidence, but with fewer than 50 trials or in simulation only.

The speed and quantization scores are estimates based on model size and architecture. I'll replace them with real benchmark numbers once I have them.

## Candidates

Sizes and results come from the model cards, checked on 24 October 2026.

| Label | Model | Type | Size | Training environment | Cameras | Reported results |
| --- | --- | --- | --- | --- | --- | --- |
| F | [ddduk/so101_act35_real_sim_v1](https://huggingface.co/ddduk/so101_act35_real_sim_v1) | ACT | 34.2M | MuJoCo (official SO-101 MJCF) + real (103 real episodes, 48 sim copies) | Top + wrist, 640×480 @ 30 fps | MuJoCo closed loop 8/8; 7/8 under ±6 mm stress; chunk MAE 3.81° real, 1.07° sim |
| G | [omiya239532/so101_act_cotrain](https://huggingface.co/omiya239532/so101_act_cotrain) | ACT | 51.7M | Genesis sim pretrain + 10 real episodes | World + wrist, 640×480 @ 30 fps | Real arm 85% (17/20), against 25% (5/20) without sim pretraining |
| A | [sahilapage/act_so101_pick_block_bowl](https://huggingface.co/sahilapage/act_so101_pick_block_bowl) | ACT | 51.7M | Real | Wrist + external, 640×480 | One real rollout, no metrics |
| H | [imhari/so101_sim_act](https://huggingface.co/imhari/so101_sim_act) | ACT | 51.7M | Simulation (simulator not named) | Up + side, 320×240 | None |
| B | [vimanyutaneja/so101-plush-pick](https://huggingface.co/vimanyutaneja/so101-plush-pick) | ACT | ~52M | Real (30 demos) | Overhead + wrist, 640×480 | None seen |
| J | [binhpham/sim_so101_cubes_act](https://huggingface.co/binhpham/sim_so101_cubes_act) | ACT | 34.2M | Simulation (simulator not named) | Not documented | None |
| I | [szk1ck/so101-pickplace-sim-mujoco](https://huggingface.co/szk1ck/so101-pickplace-sim-mujoco) | ACT | 51.7M | Name suggests MuJoCo, not confirmed | Not documented | None |
| C | [r2owb0/act1](https://huggingface.co/r2owb0/act1) | ACT | ~200 MB weights | Real | Dual camera | None |
| D | [dobri420/smolvla-so101-pick-cube](https://huggingface.co/dobri420/pick-cube-smolvla-so101) | SmolVLA | ~450M | Real | Three views | 89% grab rate (72/81) on real arm |
| E | [Project-IRA Pi0.5 V7](https://huggingface.co/Project-IRA/TPSoSe2026_Pi05_LeRobot_SO101_Finetuning_V7_Full_V2) | Pi0.5 | Not stated (largest here) | Real | Not stated | Operator-observed only |

**Left out of the scoring**

- `lerobot/smolvla_base`: it's a base model with no task training.
- `pr0tos/act_sim_stack_033`: the card doesn't give the size, simulator or cameras, and its evaluation example uses `so100_follower`.

## Scores and weighted totals

Scores are out of 5. The weight for each criterion is in brackets.

| Model | Accuracy (25) | Speed (20) | Quantization (20) | Evidence (15) | Sim assets (10) | Fit (5) | Licence (5) | Total (100) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| F (ddduk ACT) | 4 | 5 | 4 | 5 | 4 | 4 | 5 | 88 |
| G (omiya239532 ACT) | 4 | 5 | 4 | 4 | 3 | 4 | 5 | 83 |
| A (sahilapage ACT) | 3 | 5 | 4 | 4 | 2 | 4 | 5 | 76 |
| H (imhari ACT) | 2 | 5 | 4 | 4 | 3 | 3 | 5 | 72 |
| B (vimanyutaneja ACT) | 3 | 5 | 4 | 3 | 2 | 4 | 3 | 71 |
| J (binhpham ACT) | 2 | 5 | 4 | 3 | 3 | 3 | 5 | 69 |
| I (szk1ck ACT) | 2 | 5 | 4 | 3 | 3 | 2 | 5 | 68 |
| C (r2owb0 ACT) | 2 | 5 | 4 | 3 | 1 | 4 | 5 | 66 |
| D (dobri420 SmolVLA) | 5 | 2 | 2 | 4 | 1 | 3 | 5 | 63 |
| E (Project-IRA Pi0.5) | 3 | 1 | 1 | 2 | 1 | 3 | 3 | 37 |

### Why model F is ahead

F is the only candidate that has a public training config, a quantitative evaluation and MuJoCo validation all together. At 34.2M parameters it's also the smallest model with all three. It finishes 5 points ahead of G.

### Sensitivity check

I tried raising the accuracy weight to 40 points, taking 12.5 points each from speed and quantization. F still comes first on 86.5, G is second on 81.5, and D moves up to third on 72. Whenever I quote these results I should say which weights I used.

## Caveats and things to check

- **Camera poses.** F's card says the camera exposure, viewpoint, ordering and resolution have to match how the data was collected, but it doesn't give the camera extrinsics. I need to look in the `configs/` and `deployment/` folders of F's repo. If they contain camera poses or scene files, F's simulation assets score goes up to 5. If not, I'll measure the poses myself and write them down.
- **MJCF match.** F uses the "official SO-101 MJCF". I need to check that it matches `assets/robotstudio_so101` before assuming the scene carries over.
- **Sim versus real.** F's card warns that simulation results and offline metrics don't tell you how the model will do on a real robot.
- **G.** It was trained in Genesis, not MuJoCo, but it's the only model here with a measured real-arm success rate (20 trials).
- **H.** Its rollout example uses 640×480 cameras even though it was trained at 320×240.
- **C.** Its card mentions a SmolVLA base model even though it describes an ACT policy.
- **Licences.** I couldn't find the licences for B and E.
- **Versions.** I should pin `lerobot` in `requirements.txt`. F, H and B all state version 0.6.1.

## Fallback: generate my own simulation data

If none of these models work out, [so101-nexus](https://github.com/johnsutor/so101-nexus) is a MuJoCo environment library for the SO-101. It has six tasks, writes LeRobot v3 datasets, is Apache-2.0 and is still in beta. I could use it to generate training data in a scene where I control the cameras. I haven't checked it against `robotstudio_so101` yet.

## Keeping this file up to date

1. Freeze the weights and anchors before evaluating any model.
2. Add new candidates to the Candidates table with the date I checked them.
3. Score them in the scores table and recalculate the totals (score / 5 × weight).
4. Swap the estimated speed and quantization scores for measured ones.
