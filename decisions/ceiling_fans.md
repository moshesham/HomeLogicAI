# Decision Template: Ceiling Fans

> *Use this before you visit a showroom, call a supplier, or approve a contractor's selection.*

---

## The Problem Most Homeowners Don't See

Ceiling fans are sold on aesthetics. Almost no showroom floor display tells you the CFM rating, the motor type, or the noise level. You will spend $200–$800 on a fan and never know if it actually moves air efficiently — until summer arrives and it's too late to return it.

This template changes that.

---

## What to Ask (Before You Buy)

### Motor & Efficiency
- [ ] Is this motor **AC or DC**? *(DC = up to 70% more efficient, quieter, and longer-lasting)*
- [ ] What is the **CFM (Cubic Feet per Minute)** rating at the highest speed?
- [ ] What is the **CFM efficiency rating** (CFM per watt)?
- [ ] Is the motor covered by a **separate warranty** from the fixture warranty?

### Airflow & Blade Performance
- [ ] What is the **blade pitch** (angle in degrees)?
- [ ] What is the **blade span** (diameter) in inches?
- [ ] Is this rated for **indoor, outdoor-damp, or outdoor-wet** locations?
- [ ] Is it **UL listed** for the environment it will be installed in?

### Installation
- [ ] What is the **minimum ceiling height** required for this model?
- [ ] Does it come with a **downrod**, and what length?
- [ ] Is it compatible with my existing **wall switch** or will I need a new one?
- [ ] Does the **remote/smart control** work with my home automation system? *(e.g., Alexa, Google Home)*

### Aesthetics & Practicality
- [ ] What is the **light kit included**, and what bulb base does it use? *(E26/GU24)*
- [ ] Is the **blade reversible** for summer/winter operation?
- [ ] What is the **noise rating** in dB at high speed?

---

## Critical Attributes Checklist

Use this to compare products side by side. Fill in for each fan you're considering.

| Attribute | Minimum Standard | Product A | Product B |
|---|---|---|---|
| Motor Type | DC preferred | | |
| CFM (high speed) | ≥ 5,000 for rooms >200 sq ft | | |
| CFM/Watt | ≥ 75 | | |
| Blade Pitch | 12–15° | | |
| Blade Span | Match room size* | | |
| Noise Level | < 40 dB | | |
| Motor Warranty | ≥ 5 years | | |
| Wet/Damp Rated | Required for covered porch | | |
| Smart Compatible | Per your setup | | |

> **Room-to-Fan sizing guide:**
> - Up to 75 sq ft → 29–36 in blade span
> - 76–144 sq ft → 36–42 in blade span
> - 145–225 sq ft → 44–50 in blade span
> - 226–400 sq ft → 50–54 in blade span
> - 400+ sq ft → 60+ in blade span (or two fans)

---

## Hidden Costs & Technical Blind Spots

### 💡 Wiring & Permit Surprises
Adding a new ceiling fan where there is no existing wiring requires:
1. A new circuit or a shared circuit (if load allows)
2. A permit in most jurisdictions
3. An electrical inspection

**Ask your contractor**: *"Is there an existing junction box rated for a fan (not just a light)?"* Standard light boxes are rated for 35 lbs. Fan-rated boxes must support 150 lbs and dynamic load.

### 💡 CFM vs. "Airflow Feel"
High CFM is meaningless if the fan is mounted too high. The ideal mounting height for airflow is **7–9 feet** from the floor to blade. In rooms with 10+ ft ceilings, use a longer downrod — not just the shortest available.

### 💡 DC Motor ≠ Always Quieter
Some cheap DC motors hum at certain speeds due to poor PWM (pulse-width modulation) controllers. Ask for a demo at the showroom before buying.

### 💡 Smart Fan Compatibility
Not all smart fans work with all platforms. Confirm:
- Does it require a proprietary hub?
- Does it support your wiring (2-wire vs. 3-wire)?
- Will it work with your existing smart dimmer switch? (Many won't.)

### 💡 The "Energy Star" Trap
Energy Star certification for fans only requires the motor+light system to meet efficiency standards *together*. A fan without a light kit may not be tested. Check the CFM/watt spec directly.

---

## Standards Reference

Per `standards.json`:
- DC motor preferred
- CFM ≥ 5,000 for rooms > 200 sq ft
- Blade pitch: 12–15°
- Noise: < 40 dB
- Motor warranty: ≥ 5 years

---

## Related Vault Category

Products captured for this category are saved in: `vault/fans/`

Run a comparison with:
```bash
python compare/compare.py --folder vault/fans
```
