
Bruce Constraint‑Aware Decision Module (BCADM)
BCADM is a multi‑constraint, safety‑aware decision module designed for robotics, agent systems, and simulation environments. It evaluates proposed actions, scores the requested pose, applies deterministic boundary‑aware clamping, and returns a full safety‑aware action‑contract describing exactly how the environment responded.

BCADM is built for environments where agents interact with hard boundaries, safety constraints, and deterministic clamping rules. It is suitable for robotics labs, multi‑agent planners, simulation workflows, and safety‑critical systems.

Updated Architecture (OmniLink‑Aligned)
The latest update incorporates OmniLink’s scoring recommendations and expands BCADM’s architecture to support:

Requested‑pose scoring  
The score reflects the agent’s intent, not the clamped result.

Boundary‑target = 5.0  
The wall is the explicit attractor in the score landscape.

Amplified boundary‑seek (1.2× overshoot)  
Boundary‑seek aggressively drives the agent toward the constraint edge.

Weakened center‑bias + expanded probe range  
Encourages outward exploration and reduces center dominance.

Pressure term (overshoot reward)  
Requested poses beyond the wall score higher than staying at the wall, enabling continuous pressure behavior.

Friction decay (stillness penalty)  
Remaining stationary at the wall reduces score over time, preventing deadlock.

Multi‑constraint clamping  
Supports corner cases and simultaneous boundary violations.

Deterministic safety‑aware decision loop  
Every step produces a consistent, reproducible action‑contract.

Full intervention metadata  
Includes violated rules, clamped axes, and intervention timestamps.

Consistent naming and identity across module + GitHub Action  
Matches the published BCADM action metadata.

Action‑Contract Output (Updated)
Each simulation step returns a complete multi‑constraint action‑contract containing:

requested — the movement the agent attempted (used for scoring)

achieved — the movement executed after clamping

modified — whether the action was changed for safety

violated_rule — last constraint that fired (legacy compatibility)

violated_rules — all constraints that fired

intervention_time — timestamp of the safety intervention

recovery_state — safety status and clamped axes

final_pose — resulting position after movement

This expanded contract resolves previous observability gaps and ensures upstream systems never misinterpret clamped actions as fully executed ones. Scoring the requested pose also makes the printed score reflect the agent’s intent rather than the clamped outcome, matching OmniLink’s analysis.

GitHub Action Metadata
BCADM includes a GitHub Action for running simulation loops inside CI/CD pipelines.

yaml
name: "Bruce Constraint‑Aware Decision Module (BCADM)"
description: "Runs the BCADM multi‑constraint simulation loop, evaluates requested poses, applies boundary‑aware clamping, and outputs full safety‑aware action‑contracts."
author: "Bruce"

inputs:
  steps:
    description: "Number of simulation steps to run (each step produces a full multi‑constraint action‑contract with requested, achieved, clamped, violated-rules, intervention-time, and recovery-state fields)"
    required: false
    default: "10"

runs:
  using: "docker"
  image: "Dockerfile"

branding:
  icon: "cpu"
  color: "blue"
Usage Example
Run a 50‑step BCADM simulation:

bash
python bcadm_simulation.py
Each step prints:

current state

chosen action

full action‑contract

requested‑pose score

Why BCADM Exists
BCADM provides a transparent, deterministic, and fully observable safety‑aware decision module. It is designed for environments where:

agents must interact with hard boundaries

safety constraints must be enforced deterministically

upstream systems require full visibility into clamping behavior

requested‑pose scoring is necessary for accurate intent modeling

BCADM’s architecture ensures that every action is traceable, every clamp is recorded, and every intervention is observable.
