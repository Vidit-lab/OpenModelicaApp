# The simulated model

Two tanks connected by a pipe. Tank 1 has a constant inflow and a valve that opens at `t = 5 s`; tank 2 collects whatever leaves tank 1 and has no outlet.

```
Tank 1:  der(h₁) = (Qin − Qo) / A        Qo = 0        if t ≤ 5
                                         Qo = √h₁      otherwise
Tank 2:  der(h₂) = Qo / A
```

| Parameter | Value | Meaning |
|---|---|---|
| `Qin` | 2 | inflow into tank 1 |
| `A` | 1 | cross-section area (both tanks) |
| `V` | 10 | tank 2 volume, used for residence time |

## Resulting behaviour

| Phase | Tank 1 | Tank 2 |
|---|---|---|
| `t ≤ 5` | rises linearly, `h₁ = 2t` | flat at 0 — valve shut |
| `t > 5` | drains toward equilibrium `h₁ = 4` | fills steadily, slope → 2 |

Mass is conserved exactly: `h₁ + h₂ = 2t` at all times.

The connector `FlowConnect` declares `Real F`, not `flow Real F`, so `connect()` emits an equality rather than a sum-to-zero: `tank2.Q1 = tank1.Qo` exactly. It is a signal connector, not a physical one.
