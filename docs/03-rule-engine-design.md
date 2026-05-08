# Rule Engine Design

The rule engine does not predict price movement. It checks whether a proposed action violates the user's predefined discipline.

## Rule Outputs

- `BLOCKED`: hard violation. The system records why the action should not proceed.
- `WARN`: action may proceed, but risk is logged.
- `PASS`: no material discipline issue found.

## Initial Rule Set

- Position overweight.
- No evidence trade.
- Emotional averaging down.
- Earnings bet.
- FOMO trade.
- Thesis drift.
- Review required.

The MVP intentionally keeps these rules deterministic. AI may help write explanations, but the final result comes from the rule engine.

