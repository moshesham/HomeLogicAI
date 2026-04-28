# Decision Template: Lighting

> *Use this before selecting any light fixture — pendants, recessed, under-cabinet, or sconces.*

---

## The Problem Most Homeowners Don't See

Lighting is the single renovation element most homeowners regret. Not because of the fixture style — but because the light *quality* is wrong. Colors look off. The room feels clinical or dingy. Food on the counter looks gray. Skin tones in the bathroom look green.

These problems are almost never caused by the fixture. They're caused by buying the wrong light *source*. This template teaches you how to specify light correctly.

---

## What to Ask (Before You Buy)

### Color Quality (The Most Important Specs Nobody Mentions)
- [ ] What is the **CRI (Color Rendering Index)**?
  *(Scale of 0–100. Below 80 = colors look distorted. Kitchens and baths: require ≥ 90)*
- [ ] What is the **CCT (Correlated Color Temperature)** in Kelvin?
  *(2700K = warm/amber, 3000K = warm white, 4000K = neutral, 5000K+ = cool/daylight)*
- [ ] Does the bulb/LED use **binning control**? *(Higher-end fixtures specify ≤ 3-step MacAdam ellipse to prevent color variation between bulbs in the same room)*
- [ ] Is the color temperature **consistent across the full dimming range**?
  *(Cheap LEDs shift orange when dimmed — called "color temperature shift")*

### Efficiency & Longevity
- [ ] What is the **lumen output** (total brightness)?
- [ ] What is the **lumens-per-watt** efficiency rating?
- [ ] What is the rated **L70 lifespan** (hours until light output drops to 70%)?
  *(Look for ≥ 25,000 hours for recessed/fixed LED)*

### Dimming Compatibility
- [ ] Is the fixture **dimmable**?
- [ ] What **dimmer brands/models** is it compatible with? *(Always ask for the compatibility list)*
- [ ] What is the **minimum dim level** before the light flickers or turns off?

### Recessed Lighting Specifics
- [ ] What is the **housing type** (new construction vs. remodel/retrofit)?
- [ ] What is the **IC rating** — is it safe for insulated ceilings? *(IC-rated = insulation contact approved)*
- [ ] What is the **airtight rating**? *(AT-rated seals against air infiltration — reduces HVAC loss)*
- [ ] What **beam angle** does the trim produce? *(Narrow = 25° spotlight, Wide = 60° flood)*
- [ ] What is the **trim diameter** and does it match existing holes?

### Smart Lighting
- [ ] Does it require a **neutral wire** at the switch location?
- [ ] Is it compatible with your **home automation platform**?
- [ ] Does it support **scenes and schedules** without an internet connection?

---

## Critical Attributes Checklist

| Attribute | Minimum Standard | Product A | Product B |
|---|---|---|---|
| CRI | ≥ 90 (kitchens/baths) | | |
| Color Temperature | 2700–3000K living, 3000–4000K work | | |
| Lumens (total) | Match room needs* | | |
| Lumens per Watt | ≥ 80 lm/W | | |
| L70 Lifespan | ≥ 25,000 hours | | |
| Dimmable | Yes (confirm dimmer compat.) | | |
| IC-Rated | Required if attic above | | |
| Airtight (AT) | Preferred | | |
| Warranty | ≥ 3 years (LED driver) | | |

> **Lumen needs by room type:**
> - Kitchen general: 3,000–4,500 lm total
> - Kitchen task (under cabinet): 300–500 lm per linear foot
> - Bathroom vanity: 1,500–3,000 lm (shadow-free from sides, not above)
> - Bedroom: 1,000–2,000 lm general
> - Living room: 1,500–3,000 lm general

---

## Hidden Costs & Technical Blind Spots

### 💡 CRI: The Spec That Changes Everything
CRI measures how accurately a light source renders the colors of objects compared to natural sunlight (CRI 100).

- **CRI 80**: Standard. Acceptable for hallways, closets, garages.
- **CRI 90**: Good. Recommended for kitchens, living rooms, and bathrooms.
- **CRI 95+**: Excellent. Used in photography studios, makeup applications, and high-end retail.

**Why it matters in the kitchen**: At CRI 80, raw chicken and ripe tomatoes look nearly identical in color. At CRI 90+, the difference is clearly visible. This isn't aesthetic — it's a food safety issue.

### 💡 Color Temperature and Perceived Room Size
Warmer light (2700K) makes a room feel smaller and cozier. Cooler light (4000K+) makes it feel larger and more clinical. In open-plan spaces with multiple zones, mixing color temperatures creates a jarring effect. Decide on one CCT for each open zone.

### 💡 The Dimmer Compatibility Problem
Most LED retrofit bulbs list "dimmable" on the box. What they don't tell you: there are over 200 different dimmer models on the market, and many LEDs are only compatible with 10–30 of them.

**Solution**: Before installing smart dimmers or LED dimmers, download the fixture's compatibility list from the manufacturer and confirm your dimmer model is on it. Or use the Lutron or Leviton compatibility finders.

### 💡 Recessed Lighting "Holes" Are Permanent
Once you cut holes for recessed cans in a finished ceiling, they're there forever. If you change your mind about layout or decide you want pendants instead, the holes remain.

Before cutting: mock up the layout with painter's tape on the ceiling. Live with it for 48 hours before finalizing the plan.

### 💡 The Neutral Wire Requirement
Most older homes were wired for standard (non-smart) switches, which don't have a neutral wire at the switch box. Most smart dimmers require a neutral wire. Before specifying smart lighting throughout:
1. Have an electrician verify neutral wire presence at each switch location.
2. Or choose "no-neutral" smart dimmers (Lutron Caseta works without neutral).

### 💡 Under-Cabinet Light Placement
Under-cabinet lights should be positioned at the *front edge* of the upper cabinet — not at the back. Rear placement creates harsh shadows from your hands while you're working on the counter.

---

## Standards Reference

Per `standards.json`:
- CRI ≥ 90 for kitchens/bathrooms
- Color temperature: 2700–3000K for living spaces, 3000–4000K for task areas
- Lumens per watt: ≥ 80 lm/W
- Dimming compatible: preferred
- Warranty: ≥ 3 years (LED driver)

---

## Related Vault Category

Products captured for this category are saved in: `vault/lighting/`

Run a comparison with:
```bash
python compare/compare.py --folder vault/lighting
```
