BCADM — Constraint‑Aware Decision Module (Updated Architecture)
BCADM is a multi‑constraint, safety‑aware decision module for robotics, agent systems, and simulation environments. It evaluates proposed actions, scores the requested pose, applies deterministic boundary‑aware clamping, and returns a full action‑contract describing exactly how the environment responded.

The latest update incorporates OmniLink’s scoring recommendations and expands BCADM’s architecture to support:

requested‑pose scoring (not the clamped final pose)

boundary‑target = 5.0, making the wall the explicit attractor

amplified boundary‑seek with 1.2× overshoot

weakened center‑bias and expanded probe range

multi‑constraint clamping (corner cases, simultaneous boundary violations)

deterministic safety‑aware decision loop

full action‑contract reporting with intervention metadata

consistent naming and identity across the module and GitHub Action

This update aligns BCADM with OmniLink’s replay behavior and makes the module suitable for robotics labs, multi‑agent planners, simulation workflows, and safety‑critical environments.

Action‑Contract Output (Updated)
Each simulation step now returns a complete multi‑constraint action‑contract containing:

requested — the movement the agent attempted (used for scoring)

achieved — the movement executed after clamping

modified — whether the action was changed for safety

violated_rule — the last constraint that fired (legacy compatibility)

violated_rules — all constraints that fired (multi‑constraint support)

intervention_time — timestamp of the safety intervention

recovery_state — environment’s safety status and clamped axes

final_pose — the resulting position after movement

This expanded contract resolves previous observability gaps and ensures upstream systems never misinterpret clamped actions as fully executed ones. Scoring the requested pose also makes the printed score reflect the agent’s intent rather than the clamped outcome, matching OmniLink’s analysis.
