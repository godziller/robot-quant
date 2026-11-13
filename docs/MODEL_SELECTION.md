# Model selection for robot-quant

My recommended simulation-first pick is **`ahmedsohail2003/act-so101-pickplace-dr`**, which scores 88 out of 100 on the rubric below (rubric v4, audited 31 October 2026). It ties F on points and is preferred for this project because it includes a reproducible MuJoCo work-cell, public LeRobot checkpoint, domain-randomized data, and a documented 18/20 (90%) nominal result. This is model-card evidence, not an independent reproduction. The exact SO-101 MJCF match, target-NPU latency, and INT8 accuracy drop remain to be measured.

The project is a control experiment: does INT8 quantization hurt closed-loop SO-101 control more than it hurts frame classification? To answer that I need a model with a working FP32 baseline, a size that fits on an NPU, and enough public evidence to reproduce it. A MuJoCo scene would also help, because then I don't have to rebuild the camera setup from scratch.

## Rubric

Each model has to pass four gates first. Models that pass are then scored from 1 to 5 on seven weighted criteria, which add up to 100 points. Weighted points = (score / 5) × weight.

Scores marked with an asterisk are estimates, not measurements. The Speed and Quantization columns are estimates throughout: no audited upstream page reports target-NPU p95 latency or measured INT8 accuracy degradation. No upstream page proves that this project can reproduce an FP32 baseline locally; that remains validation work.

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

Sizes, configurations, licences and reported results come from upstream model cards/APIs and linked projects, checked on 31 October 2026. Reported performance is not independently reproduced here.

| Label | Model | Type | Size | Training environment | Cameras | Reported results |
| --- | --- | --- | --- | --- | --- | --- |
| F | [ddduk/so101_act35_real_sim_v1](https://huggingface.co/ddduk/so101_act35_real_sim_v1) | ACT | 34.2M | MuJoCo (official SO-101 MJCF) + real (103 real episodes, 48 sim copies) | Top + wrist, 640×480 @ 30 fps | MuJoCo closed loop 8/8; 7/8 under ±6 mm stress; chunk MAE 3.81° real, 1.07° sim |
| K | [ahmedsohail2003/act-so101-pickplace-dr](https://huggingface.co/ahmedsohail2003/act-so101-pickplace-dr) | ACT | 51.6M | MuJoCo SO-ARM100/Menagerie work-cell with visual and physics domain randomization | Front + wrist, 224×224 | 18/20 (90%) nominal; 87%, 87%, 87%, 100% over 15-episode DR sweeps |
| G | [omiya239532/so101_act_cotrain](https://huggingface.co/omiya239532/so101_act_cotrain) | ACT | 51.7M | Genesis sim pretrain + 10 real episodes | World + wrist, 640×480 @ 30 fps | Real arm 85% (17/20), against 25% (5/20) without sim pretraining |
| A | [sahilapage/act_so101_pick_block_bowl](https://huggingface.co/sahilapage/act_so101_pick_block_bowl) | ACT | 51.7M | Real | Wrist + external, 640×480 | One real rollout, no metrics |
| H | [imhari/so101_sim_act](https://huggingface.co/imhari/so101_sim_act) | ACT | 51.7M | Simulation (simulator not named) | Up + side, 320×240 | None |
| B | [vimanyutaneja/so101-plush-pick](https://huggingface.co/vimanyutaneja/so101-plush-pick) | ACT | ~52M claimed | Real (30 demos claimed) | Top + wrist, 640×480 @ 30 fps claimed | No quantitative result; no public checkpoint files found |
| J | [binhpham/sim_so101_cubes_act](https://huggingface.co/binhpham/sim_so101_cubes_act) | ACT | 34.2M | Simulation (simulator not named) | Not documented | None |
| I | [szk1ck/so101-pickplace-sim-mujoco](https://huggingface.co/szk1ck/so101-pickplace-sim-mujoco) | ACT | 51.7M | Name suggests MuJoCo, not confirmed | Not documented | None |
| C | [r2owb0/act1](https://huggingface.co/r2owb0/act1) | ACT | ~200 MB weights | Real | Dual camera | None |
| D | [dobri420/smolvla-so101-pick-cube](https://huggingface.co/dobri420/pick-cube-smolvla-so101) | SmolVLA | ~450M | Real | Three views | 89% grab rate (72/81) on real arm |
| E | [Project-IRA Pi0.5 V7](https://huggingface.co/Project-IRA/TPSoSe2026_Pi05_LeRobot_SO101_Finetuning_V7_Full_V2) | Pi0.5 | Not stated | Real | `wrist_left` 640×480 + `desk_view` 800×600 | Operator observations only; no formal success rate |

**Left out of the scoring**

- `lerobot/smolvla_base`: it's a base model with no task training.
- `pr0tos/act_sim_stack_033`: the card doesn't give the size, simulator or cameras, and its evaluation example uses `so100_follower`.

## Scores and weighted totals

Scores are out of 5. The weight for each criterion is in brackets.

| Model | Accuracy (25) | Speed (20) | Quantization (20) | Evidence (15) | Sim assets (10) | Fit (5) | Licence (5) | Total (100) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| K (ahmedsohail2003 ACT-DR) | 4 | 5* | 4* | 5 | 5 | 4 | 5 | 88 |
| F (ddduk ACT) | 4 | 5 | 4 | 5 | 4 | 4 | 5 | 88 |
| G (omiya239532 ACT) | 4 | 5 | 4 | 4 | 3 | 4 | 5 | 83 |
| A (sahilapage ACT) | 3 | 5 | 4 | 4 | 2 | 4 | 5 | 76 |
| H (imhari ACT) | 2 | 5 | 4 | 4 | 3 | 3 | 5 | 72 |
| B (vimanyutaneja ACT) | — | — | — | — | — | — | — | **Ineligible: no public checkpoint** |
| J (binhpham ACT) | 2 | 5 | 4 | 3 | 3 | 3 | 5 | 69 |
| I (szk1ck ACT) | 2 | 5 | 4 | 3 | 3 | 2 | 5 | 68 |
| C (r2owb0 ACT) | 2 | 5 | 4 | 3 | 1 | 4 | 5 | 66 |
| D (dobri420 SmolVLA) | 5 | 2 | 2 | 4 | 1 | 3 | 5 | 63 |
| E (Project-IRA Pi0.5) | 3 | 1* | 1* | 2 | 1 | 3 | 1 | 31 |

### Why model K is ahead

K is the strongest simulation-first candidate: its project includes the MuJoCo work-cell, camera definitions, data-generation code, ACT training recipe and public checkpoint. Its model card reports 18/20 (90%) nominal success and 87%, 87%, 87% and 100% across its 15-episode domain-randomization sweeps. It ties F under this rubric; K is preferred only as a simulation-first tie-break, not as evidence that it will outperform F on a real arm.

### Sensitivity check

I have not rerun the sensitivity analysis after the upstream audit. Any sensitivity result must use the corrected 18/20 K result, exclude B, and retain the asterisks for estimated speed and quantization.

## Caveats and things to check

- **Camera poses.** F's card says the camera exposure, viewpoint, ordering and resolution have to match how the data was collected, but it doesn't give the camera extrinsics. I need to look in the `configs/` and `deployment/` folders of F's repo. If they contain camera poses or scene files, F's simulation assets score goes up to 5. If not, I'll measure the poses myself and write them down.
- **MJCF match.** F uses the "official SO-101 MJCF". I need to check that it matches `assets/robotstudio_so101` before assuming the scene carries over.
- **Sim versus real.** F's card warns that simulation results and offline metrics don't tell you how the model will do on a real robot.
- **K.** The linked project is explicitly simulation-only. Its model card provides an `ACTPolicy.from_pretrained` path and reports 18/20 nominal success. Apache-2.0 is verified, but the model uses the MuJoCo Menagerie SO-ARM100 description, so I must compare it with `assets/robotstudio_so101` before treating it as an SO-101 drop-in.
- **G.** It was trained in Genesis, not MuJoCo, but it's the only model here with a measured real-arm success rate (20 trials).
- **H.** Its rollout example uses 640×480 cameras even though it was trained at 320×240.
- **C.** Its card mentions a SmolVLA base model even though it describes an ACT policy.
- **B.** The upstream page currently exposes only a README; no public weights/config were found, so it fails the public-weights and `from_pretrained` gates until uploaded.
- **E.** The checkpoint is CC-BY-SA-4.0, so it receives licence score 1 under this rubric; its model card reports qualitative operator observations, not a formal success rate.
- **Versions.** I should pin `lerobot` in `requirements.txt`. F, H and B all state version 0.6.1.

## Fallback: generate my own simulation data

If none of these models work out, [so101-nexus](https://github.com/johnsutor/so101-nexus) is a MuJoCo environment library for the SO-101. It has six tasks, writes LeRobot v3 datasets, is Apache-2.0 and is still in beta. I could use it to generate training data in a scene where I control the cameras. I haven't checked it against `robotstudio_so101` yet.

## Keeping this file up to date

1. Freeze the weights and anchors before evaluating any model.
2. Add new candidates to the Candidates table with the date I checked them.
3. Score them in the scores table and recalculate the totals (score / 5 × weight).
4. Swap the estimated speed and quantization scores for measured ones.

