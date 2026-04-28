# Decision Template: Kitchen Hardware

> *Use this before ordering pulls, knobs, hinges, or faucet hardware for any kitchen or bathroom renovation.*

---

## The Problem Most Homeowners Don't See

Kitchen hardware is one of the highest-touch surfaces in the home. Most homeowners choose hardware based on aesthetics — brushed gold looks nice, matte black is on-trend. What they miss is that **finish durability**, **material quality**, and **dimensional accuracy** are what determine whether your hardware still looks good in 5 years or starts flaking, pitting, and loosening within 18 months.

This template ensures you choose for longevity, not just looks.

---

## What to Ask (Before You Buy)

### Dimensions (Most Critical — Measure First)
- [ ] What is the **center-to-center (CTC) measurement** of existing holes?
  *(Common sizes: 3" / 76mm, 3.75" / 96mm, 5" / 128mm, 6.25" / 160mm)*
- [ ] Are the new cabinets **metric or imperial**? *(Imported IKEA-style = metric)*
- [ ] What is the **projection** (how far the pull sticks out from the face)?
- [ ] Will the pull clear the **drawer box** when the drawer is fully open?

### Material & Construction
- [ ] Is this **solid brass**, zinc alloy, or plastic-core?
- [ ] Is the finish **PVD** (Physical Vapor Deposition) or traditional plating?
- [ ] Does it come with matching **screws**? What thread size and length?
- [ ] Are replacement screws available if I install thicker drawer fronts?

### Finish & Durability
- [ ] Is there a **lifetime finish warranty**?
- [ ] Is the finish rated for **wet environments** (under-sink, dishwasher adjacent)?
- [ ] What is the **ASTM B117** salt spray test rating? *(High-quality hardware should pass 1000+ hours)*

### Hinges (If Applicable)
- [ ] What is the **overlay** (full overlay, half overlay, inset)?
- [ ] Is the hinge **soft-close**?
- [ ] What is the **hinge cup diameter**? (European standard = 35mm)
- [ ] Can the hinge be adjusted in 3 axes (height, depth, lateral)?

### Faucet Hardware
- [ ] What is the **hole configuration** (single hole, 3-hole 4-inch spread, 3-hole 8-inch spread)?
- [ ] What is the **flow rate (GPM)** — check against local water conservation codes?
- [ ] Is it compatible with **1/4-turn ceramic disc cartridges**? *(More durable than ball valves)*

---

## Critical Attributes Checklist

| Attribute | Minimum Standard | Product A | Product B |
|---|---|---|---|
| Material | Solid brass or 304 SS | | |
| Finish Type | PVD preferred | | |
| Finish Warranty | Lifetime | | |
| CTC Measurement | Matches your cabinets | | |
| Projection Clearance | Clears drawer box | | |
| Screw Included | Yes, correct length | | |
| Wet Location Rated | Required near sink | | |
| ASTM B117 (salt spray) | ≥ 500 hrs minimum | | |

---

## Hidden Costs & Technical Blind Spots

### 💡 The CTC Measurement Trap
This is the #1 mistake in hardware installation. If you order 96mm pulls and your cabinet has 76mm holes, you need to either:
- Drill new holes (visible on the cabinet face), or
- Return everything and reorder

**Always measure existing holes before ordering.** Use a digital caliper, not a tape measure.

### 💡 PVD vs. Traditional Plating
Traditional chrome/nickel plating scratches and eventually peels. PVD finish bonds at the molecular level — it's essentially permanent. You'll pay 20–40% more, but most manufacturers back it with a lifetime warranty that covers finish, not just mechanics.

If a company won't offer a lifetime finish warranty, that tells you something about the quality.

### 💡 Screw Length Math
Standard cabinet drawer fronts are ¾" (19mm) thick. Standard pulls come with 1" (25mm) screws. If you have thick slab fronts (1" or more), you need longer screws — and they usually aren't in the box.

Buy extra screws in the correct thread pitch before installation day.

### 💡 "Matching" Hardware Across Brands
Different manufacturers' "brushed nickel" or "matte black" rarely match perfectly. If you mix brands in the same kitchen, do a side-by-side in person before ordering everything.

### 💡 Hinge Adjustment After Installation
All European-style cabinet hinges are 3-way adjustable *if* you buy the correct plates. If a contractor installs non-adjustable hinges, there is no way to fix a crooked door without removing the hinge entirely. Specify **3-way adjustable Blum or Hettich** hinges by name.

### 💡 The "Commercial Grade" Upsell
Commercial-grade hardware is rated for 50,000+ open/close cycles. For a kitchen cabinet, you'll realistically do 20–40 cycles per day — so residential grade (10,000–25,000 cycles) is sufficient. Don't overpay for commercial grade on standard cabinet doors.

---

## Standards Reference

Per `standards.json`:
- Tier 1 materials: solid brass, 304 stainless steel
- Preferred finish: PVD
- Finish warranty: lifetime required
- Common CTC sizes: 64mm, 76mm, 96mm, 128mm, 160mm

---

## Related Vault Category

Products captured for this category are saved in: `vault/hardware/`

Run a comparison with:
```bash
python compare/compare.py --folder vault/hardware
```
