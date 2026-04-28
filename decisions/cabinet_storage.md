# Decision Template: Cabinet Storage

> *Use this before selecting pull-out shelves, drawer organizers, lazy Susans, or any internal cabinet storage system.*

---

## The Problem Most Homeowners Don't See

Interior cabinet storage is almost never discussed during a renovation. Contractors install the cabinets, and the homeowner later discovers the pull-outs sag, the drawers bind, or the organizer blocks the door from fully opening. By the time this is discovered, the contractor is gone and the cabinets are installed.

Specify your storage systems *before* cabinets are ordered — many must be factory-installed or require specific cabinet box dimensions.

---

## What to Ask (Before You Buy)

### Weight Capacity
- [ ] What is the **maximum weight capacity** of the pull-out?
  *(Under-sink and pantry items — especially canned goods — can easily exceed 50 lbs per shelf)*
- [ ] Is the weight rating for the **shelf surface** or the **slide mechanism**?
  *(These are sometimes rated separately)*
- [ ] Does the rating apply when **fully extended** or only when partially extended?

### Slide Quality & Extension
- [ ] Are the slides **full-extension** (100% access to contents) or partial extension?
- [ ] Are they **undermount** (hidden) or **side-mount**?
- [ ] Do they have **soft-close** dampening?
- [ ] What is the slide **width rating**? *(Slides must match the interior cabinet width)*

### Spatial Efficiency
- [ ] What is the **usable interior depth** of the cabinet vs. total depth?
  *(Factory cabinets often waste 4–6 inches behind the face frame)*
- [ ] What is the **usable height** per shelf level, accounting for pull-out box height?
- [ ] Does the pull-out allow for **adjustable shelf heights**?
- [ ] Will a **lazy Susan** conflict with the door hinges or adjacent drawers?

### Material & Construction
- [ ] Is the pull-out box **solid wood, plywood, or wire frame**?
- [ ] Is the coating **rated for wet/under-sink environments**? *(Especially important for epoxy-coated wire)*
- [ ] What is the **joint type** on wood pull-outs? *(Dovetail = strongest; stapled = weakest)*

### Installation
- [ ] Can this be **retrofit** into existing cabinets, or does it require factory installation?
- [ ] What is the **minimum cabinet interior width** required?
- [ ] Are mounting brackets and hardware **included**?

---

## Critical Attributes Checklist

| Attribute | Minimum Standard | Product A | Product B |
|---|---|---|---|
| Weight Capacity | ≥ 100 lbs (pantry/pots) | | |
| Extension Type | Full-extension (100%) | | |
| Slide Type | Undermount preferred | | |
| Soft-Close | Yes | | |
| Box Material | Plywood or solid wood | | |
| Wet Zone Rating | Required under sink | | |
| Joint Type | Dovetail preferred | | |
| Fits Cabinet Width | Verified before ordering | | |
| Warranty | ≥ 1 year (lifetime on slides) | | |

---

## Spatial Volume Calculation Guide

Before ordering, calculate the actual usable volume of each cabinet:

```
Usable Width  = Cabinet Interior Width − Slide Allowance (typically 1–2 in total)
Usable Depth  = Cabinet Interior Depth − Face Frame Depth (typically 1.5–2 in)
Usable Height = Cabinet Interior Height − Pull-out Box Height − Clearance (typically 0.5 in)

Usable Volume = Usable Width × Usable Depth × Usable Height
```

> **Example:** A 24-inch base cabinet with 23" interior width, 22" usable depth (24" total − 2" frame), and 5" pull-out box height:
> - Usable Width: 23" − 1" (slides) = 22"
> - Volume: 22" × 22" × 5" = 2,420 cubic inches per pull-out level

Compare this across products to see what you're actually getting.

---

## Hidden Costs & Technical Blind Spots

### 💡 "Full-Extension" Is Not Always 100%
Some manufacturers call 3/4 extension (75%) "full extension." Ask specifically: *"Does the slide allow 100% access to the rear of the cabinet?"*

True full-extension slides let you see and reach the back wall of the cabinet. This matters enormously for under-sink storage and deep pantry cabinets.

### 💡 The Weight Rating Lie
Pull-out weight ratings are tested *empty and level*. Once you have canned goods stacked at the front of the shelf and the pull-out is fully extended, leverage forces on the slide increase dramatically.

A 75 lb rated slide loaded at the front with 40 lbs will feel like it's carrying 100 lbs. Choose slides rated well above your anticipated load.

### 💡 Soft-Close Is Not Standard
Even on expensive cabinets, soft-close pull-outs are often an upsell. Specify it explicitly. Slamming drawers and pull-outs will loosen cabinet boxes over time, especially if the box is particleboard.

### 💡 Cabinet Box Material vs. Door Material
Most homeowners see the door and assume the entire cabinet is the same quality. The box (the carcass behind the door) is often particleboard even on expensive cabinet lines.

**Ask specifically**: *"What material is the cabinet box — plywood or particleboard?"*

Particleboard cabinets in wet zones (under-sink, near dishwasher) will swell and fail. Plywood is the correct choice.

### 💡 Lazy Susan Clearance
Corner lazy Susans require the corner cabinet to have a specific interior dimension and door opening clearance. If the adjacent cabinet is too close to the corner, the Susan won't rotate fully.

Measure corner clearances *before* ordering. Get the manufacturer's minimum opening specification in writing.

### 💡 Retrofit vs. Factory Installation
Most after-market pull-outs are designed for retrofit (installing into existing cabinets). However, some premium systems (like Rev-A-Shelf with full-access frames) require different cabinet dimensions than standard factory boxes.

If you're remodeling, specify your storage system to the cabinet manufacturer *before* they cut the boxes.

---

## Standards Reference

Per `standards.json`:
- Pull-out weight capacity: ≥ 100 lbs recommended
- Slide type: full-extension undermount preferred
- Soft-close: preferred
- Box material: plywood (3/4 in) preferred; avoid particleboard in wet zones
- Cabinet box joint: dovetail preferred over stapled

---

## Related Vault Category

Products captured for this category are saved in: `vault/cabinet_storage/`

Run a comparison with:
```bash
python compare/compare.py --folder vault/cabinet_storage
```
