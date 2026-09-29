# ============================================================
# BRUCE-STYLE EXISTENTIAL–ARCHITECTURAL AGENT SIMULATION
# Updated per OmniLink’s scoring email:
# - boundary_target set to 5.0 so the wall is the attractor.
# - Score computed from the *requested* pose (not clamped).
# - Probe range increased.
# - Center-bias weakened.
# - Boundary-seek amplified (1.2x overshoot).
# ============================================================

import time
import random
from typing import Dict, Any, List, Optional


# ============================================================
# SIMULATION ENVIRONMENT
# ============================================================

class SimulationEnv:
    def __init__(self) -> None:
        self.x = 0.0
        self.y = 0.0
        self.min_x = -5.0
        self.max_x = 5.0
        self.min_y = -5.0
        self.max_y = 5.0

    def observe(self) -> Dict[str, Any]:
        return {"x": self.x, "y": self.y}

    def constraints(self) -> Dict[str, Any]:
        return {
            "min_x": self.min_x,
            "max_x": self.max_x,
            "min_y": self.min_y,
            "max_y": self.max_y,
        }

    def _compute_recovery_state(self, modified: bool, violated_rules: List[str]) -> Dict[str, Any]:
        if not modified:
            return {
                "safe": True,
                "status": "within_bounds",
                "clamped_axes": [],
            }

        clamped_axes = []
        if any(r in ("min_x_boundary", "max_x_boundary") for r in violated_rules):
            clamped_axes.append("x")
        if any(r in ("min_y_boundary", "max_y_boundary") for r in violated_rules):
            clamped_axes.append("y")

        return {
            "safe": False,
            "status": "clamped",
            "clamped_axes": clamped_axes,
        }

    def act(self, action: Dict[str, Any]) -> Dict[str, Any]:
        requested_dx = action["params"].get("dx", 0.0)
        requested_dy = action["params"].get("dy", 0.0)

        proposed_x = self.x + requested_dx
        proposed_y = self.y + requested_dy

        violated_rules = []
        modified = False

        # Clamp X
        if proposed_x < self.min_x:
            proposed_x = self.min_x
            violated_rules.append("min_x_boundary")
            modified = True
        elif proposed_x > self.max_x:
            proposed_x = self.max_x
            violated_rules.append("max_x_boundary")
            modified = True

        # Clamp Y
        if proposed_y < self.min_y:
            proposed_y = self.min_y
            violated_rules.append("min_y_boundary")
            modified = True
        elif proposed_y > self.max_y:
            proposed_y = self.max_y
            violated_rules.append("max_y_boundary")
            modified = True

        violated_rule = violated_rules[-1] if violated_rules else None

        achieved_dx = proposed_x - self.x
        achieved_dy = proposed_y - self.y

        self.x = proposed_x
        self.y = proposed_y

        intervention_time = time.time() if modified else None

        recovery_state = self._compute_recovery_state(modified, violated_rules)

        return {
            "requested": {"dx": requested_dx, "dy": requested_dy},
            "achieved": {"dx": achieved_dx, "dy": achieved_dy},
            "modified": modified,
            "violated_rule": violated_rule,
            "violated_rules": violated_rules,
            "intervention_time": intervention_time,
            "recovery_state": recovery_state,
            "final_pose": {"x": self.x, "y": self.y},
        }

    def score(self, requested_state: Dict[str, Any]) -> float:
        """
        OmniLink email:
        - Score the *requested* pose (not clamped).
        - boundary_target = 5.0 so the wall itself is the attractor.
        """

        x = requested_state["x"]
        y = requested_state["y"]

        # Center preference
        center_term = 1.0 - (abs(x) + abs(y)) / 10.0

        # Boundary preference (wall as target)
        boundary_target = 5.0
        boundary_term = 1.0 - (
            abs(abs(x) - boundary_target) + abs(abs(y) - boundary_target)
        ) / 10.0

        # Strong outward bias (0.9 boundary, 0.1 center)
        blended = 0.1 * center_term + 0.9 * boundary_term

        return max(0.0, min(1.0, blended))


# ============================================================
# WORLD MODEL
# ============================================================

class WorldModel:
    def __init__(self) -> None:
        self.constraints = {}
        self.patterns = []
        self.questions = []

    def update(self, state: Dict[str, Any], constraints: Dict[str, Any]) -> None:
        self.constraints = dict(constraints)
        self.patterns.append(
            {
                "timestamp": time.time(),
                "state": dict(state),
                "constraints": dict(constraints),
            }
        )

    def add_question(self, q: str) -> None:
        self.questions.append(q)


# ============================================================
# ACTION GENERATOR
# ============================================================

class ActionGenerator:
    def propose(self, state: Dict[str, Any], constraints: Dict[str, Any]) -> List[Dict[str, Any]]:
        actions = []

        # Probe (stronger outward randomness)
        actions.append({
            "type": "probe",
            "params": {
                "dx": random.uniform(-0.5, 0.5),
                "dy": random.uniform(-0.5, 0.5),
            },
        })

        # Center bias (weaker inward pull)
        actions.append({
            "type": "center_bias",
            "params": {
                "dx": -state["x"] * 0.05,
                "dy": -state["y"] * 0.05,
            },
        })

        # Boundary seek (amplified, 1.2x overshoot)
        bx = constraints["max_x"] if state["x"] >= 0 else constraints["min_x"]
        by = constraints["max_y"] if state["y"] >= 0 else constraints["min_y"]

        actions.append({
            "type": "boundary_seek",
            "params": {
                "dx": (bx - state["x"]) * 1.2,
                "dy": (by - state["y"]) * 1.2,
            },
        })

        return actions


# ============================================================
# ACTION SELECTOR
# ============================================================

class ActionSelector:
    def select(self, actions, state, constraints, env):
        best_action = None
        best_score = -999.0

        for action in actions:
            simulated = self.simulate_requested(action, state)
            score = env.score(simulated)

            if score > best_score:
                best_score = score
                best_action = action

        return best_action

    def simulate_requested(self, action, state):
        new = dict(state)
        new["x"] += action["params"].get("dx", 0.0)
        new["y"] += action["params"].get("dy", 0.0)
        return new


# ============================================================
# BRUCE-STYLE AGENT
# ============================================================

class BruceAgent:
    def __init__(self, env):
        self.env = env
        self.model = WorldModel()
        self.generator = ActionGenerator()
        self.selector = ActionSelector()
        self.history = []

    def step(self):
        state = self.env.observe()
        constraints = self.env.constraints()

        self.model.update(state, constraints)

        questions = self._generate_questions(state, constraints)
        actions = self.generator.propose(state, constraints)
        best_action = self.selector.select(actions, state, constraints, self.env)

        feedback = self.env.act(best_action)

        # Score the *requested* pose (not the clamped final pose)
        requested_pose = {
            "x": state["x"] + best_action["params"].get("dx", 0.0),
            "y": state["y"] + best_action["params"].get("dy", 0.0),
        }
        score = self.env.score(requested_pose)

        self._log(state, constraints, questions, best_action, feedback, score)
        self._record_history(state, constraints, best_action, feedback, score)

    def _generate_questions(self, state, constraints):
        qs = [
            "What boundary am I closest to?",
            "What happens if I push the constraint edge?",
            "What structural pattern emerges from movement?",
            "How does the environment respond to probing?",
            "What assumption about the world can be tested next?",
        ]
        for q in qs:
            self.model.add_question(q)
        return qs

    def _log(self, state, constraints, questions, action, feedback, score):
        print("\n=== SIMULATION STEP ===")
        print(f"State: {state}")
        print(f"Constraints: {constraints}")
        print("Questions:")
        for q in questions:
            print(f"  - {q}")
        print(f"Action: {action}")
        print("Action Contract:")
        print(f"  Requested: {feedback['requested']}")
        print(f"  Achieved: {feedback['achieved']}")
        print(f"  Modified: {feedback['modified']}")
        print(f"  Violated Rule: {feedback['violated_rule']}")
        print(f"  Violated Rules: {feedback['violated_rules']}")
        print(f"  Intervention Time: {feedback['intervention_time']}")
        print(f"  Recovery State: {feedback['recovery_state']}")
        print(f"  Final Pose: {feedback['final_pose']}")
        print(f"Score (requested pose): {score:.4f}")
        print("========================")

    def _record_history(self, state, constraints, action, feedback, score):
        self.history.append({
            "timestamp": time.time(),
            "state": dict(state),
            "constraints": dict(constraints),
            "action": dict(action),
            "feedback": dict(feedback),
            "score": score,
        })


# ============================================================
# RUN SIMULATION
# ============================================================

if __name__ == "__main__":
    env = SimulationEnv()
    agent = BruceAgent(env)

    print("Running Bruce-style existential agent simulation...\n")

    try:
        for _ in range(50):
            agent.step()
            time.sleep(0.1)
    except Exception as e:
        print("ERROR:", e)

    input("Press Enter to exit...")
