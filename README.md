BCADM — Constraint‑Aware Decision Module (Updated Architecture)
BCADM is a multi‑constraint, safety‑aware decision module designed for robotics, agent systems, and simulation environments. It evaluates proposed actions, applies deterministic safety clamps, and returns a full action‑contract describing exactly how the environment responded.

The latest update expands BCADM’s architecture to support:

multi‑constraint clamping (corner cases, simultaneous boundary violations)

deterministic safety‑aware decision loop

full action‑contract reporting with intervention metadata

consistent naming and identity across the module and GitHub Action

This makes BCADM suitable for robotics labs, multi‑agent systems, planners, and safety‑critical simulation workflows.

Action‑Contract Output (Updated)
Each simulation step now returns a complete action‑contract containing:

requested – the movement the agent attempted

achieved – the movement executed after clamping

modified – whether the action was changed for safety

violated_rule – last constraint that fired (legacy compatibility)

violated_rules – all constraints that fired (multi‑constraint support)

intervention_time – timestamp of the safety intervention

recovery_state – environment’s safety status

final_pose – resulting position after movement

This expanded contract resolves previous observability gaps and ensures upstream systems never misinterpret clamped actions as fully executed ones.
