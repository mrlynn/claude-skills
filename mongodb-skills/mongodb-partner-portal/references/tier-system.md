# Partner Tier System Reference

The platform uses a 5-tier sponsorship system to categorize partner organizations by their level of engagement and contribution. Tiers control visibility, sort order, badge styling, and perks across the platform.

## Tier Hierarchy

```
1. platinum   (highest)
2. gold
3. silver
4. bronze
5. community  (lowest)
```

## Tier Details

### Platinum

The highest sponsorship tier for major strategic partners.

| Property        | Value                                        |
|-----------------|----------------------------------------------|
| **Sort Priority** | 1 (displayed first)                        |
| **Badge Color** | `#B0B0B0` (silver-gray metallic)             |
| **Default**     | No                                           |

**Typical Perks:**
- Logo placement in hero section of event landing pages
- Dedicated sponsor section with full description
- Priority listing in partner directory
- Access to participant data (aggregated, anonymized)
- Branded prize category
- Speaking slot at events
- Custom booth/virtual booth at in-person/virtual events

---

### Gold

Major sponsors with significant contribution and visibility.

| Property        | Value                                        |
|-----------------|----------------------------------------------|
| **Sort Priority** | 2                                          |
| **Badge Color** | `#FFD700` (gold)                             |
| **Default**     | No                                           |

**Typical Perks:**
- Logo in sponsors section of landing pages
- Listed in partner directory with description
- Co-branded prize category (optional)
- Mention in event communications
- Access to aggregated event analytics

---

### Silver

Mid-tier sponsors providing meaningful support.

| Property        | Value                                        |
|-----------------|----------------------------------------------|
| **Sort Priority** | 3                                          |
| **Badge Color** | `#C0C0C0` (silver)                           |
| **Default**     | No                                           |

**Typical Perks:**
- Logo in sponsors section (smaller placement than gold)
- Listed in partner directory
- Mention in event wrap-up communications
- Basic event analytics access

---

### Bronze

Entry-level sponsors or organizations beginning their partnership.

| Property        | Value                                        |
|-----------------|----------------------------------------------|
| **Sort Priority** | 4                                          |
| **Badge Color** | `#CD7F32` (bronze)                           |
| **Default**     | Yes (default tier for new partners)          |

**Typical Perks:**
- Logo in sponsors section (standard listing)
- Listed in partner directory
- Event participation acknowledgment

---

### Community

Non-monetary partners contributing through community engagement, mentorship, or in-kind support.

| Property        | Value                                        |
|-----------------|----------------------------------------------|
| **Sort Priority** | 5 (displayed last)                         |
| **Badge Color** | `#00ED64` (MongoDB Spring Green)             |
| **Default**     | No                                           |

**Typical Perks:**
- Listed in community partners section
- Community shout-out in event communications
- Mentor/volunteer access to events
- No monetary contribution expected

---

## Database Implementation

### Compound Index

The most common query pattern is "show all active partners sorted by tier." The compound index supports this:

```typescript
PartnerSchema.index({ tier: 1, status: 1 });
```

This index efficiently serves queries like:

```typescript
// All active partners, sorted by tier (platinum first)
const partners = await PartnerModel.find({ status: "active" })
  .sort({ tier: 1 })
  .lean();
```

Note: MongoDB sorts strings alphabetically, which does NOT match tier hierarchy. To sort correctly by tier priority, use an aggregation with `$addFields`:

```typescript
const TIER_SORT_ORDER = {
  platinum: 1, gold: 2, silver: 3, bronze: 4, community: 5
};

const partners = await PartnerModel.aggregate([
  { $match: { status: "active" } },
  { $addFields: {
    tierOrder: {
      $switch: {
        branches: [
          { case: { $eq: ["$tier", "platinum"] }, then: 1 },
          { case: { $eq: ["$tier", "gold"] }, then: 2 },
          { case: { $eq: ["$tier", "silver"] }, then: 3 },
          { case: { $eq: ["$tier", "bronze"] }, then: 4 },
          { case: { $eq: ["$tier", "community"] }, then: 5 },
        ],
        default: 6
      }
    }
  }},
  { $sort: { tierOrder: 1, name: 1 } }
]);
```

Alternatively, sort in application code:

```typescript
partners.sort((a, b) => TIER_SORT_ORDER[a.tier] - TIER_SORT_ORDER[b.tier]);
```

### Partner Status Values

| Status     | Meaning                                      |
|------------|----------------------------------------------|
| `active`   | Partner is active and visible on the platform |
| `inactive` | Partner has been deactivated (hidden)         |
| `pending`  | New partner awaiting admin approval           |

### Schema Enum

```typescript
tier: {
  type: String,
  enum: ["platinum", "gold", "silver", "bronze", "community"],
  default: "bronze"
}
```

## UI Rendering

### TIER_COLORS Mapping

Use this mapping for badge rendering, border accents, and tier indicators:

```typescript
const TIER_COLORS: Record<string, string> = {
  platinum: "#B0B0B0",    // Silver-gray metallic
  gold: "#FFD700",        // Classic gold
  silver: "#C0C0C0",      // Standard silver
  bronze: "#CD7F32",      // Warm bronze
  community: "#00ED64",   // MongoDB Spring Green
};
```

### Badge Component Pattern

```tsx
<Chip
  label={partner.tier.charAt(0).toUpperCase() + partner.tier.slice(1)}
  size="small"
  sx={{
    backgroundColor: `${TIER_COLORS[partner.tier]}20`,  // 12% opacity background
    color: TIER_COLORS[partner.tier],
    fontWeight: 600,
    borderRadius: 6,
  }}
/>
```

### Display Rules

| Context               | Platinum | Gold | Silver | Bronze | Community |
|-----------------------|:--------:|:----:|:------:|:------:|:---------:|
| Landing page hero     |    Y     |      |        |        |           |
| Sponsors section (large) |  Y    |   Y  |        |        |           |
| Sponsors section (small) |       |      |   Y    |   Y    |           |
| Community section     |          |      |        |        |     Y     |
| Partner directory     |    Y     |   Y  |   Y    |   Y    |     Y     |
| Event email footer    |    Y     |   Y  |   Y    |        |           |

### Landing Page Sponsor Rendering

On event landing pages, sponsors are grouped and displayed by tier:

```typescript
// Group partners by tier for landing page rendering
const sponsorsByTier = {
  platinum: partners.filter(p => p.tier === "platinum"),
  gold: partners.filter(p => p.tier === "gold"),
  silver: partners.filter(p => p.tier === "silver"),
  bronze: partners.filter(p => p.tier === "bronze"),
  community: partners.filter(p => p.tier === "community"),
};
```

- **Platinum**: Full-width cards with logo, name, description, and website link
- **Gold**: Medium cards with logo and name
- **Silver/Bronze**: Small logo grid
- **Community**: Text list with links

## Changing a Partner's Tier

Tier changes are made via the admin API:

```
PATCH /api/admin/partners/[partnerId]
Body: { "tier": "gold" }
```

Required role: super_admin or admin. Tier changes take effect immediately and update the partner's visibility across all linked events.

## Partner Access Workflow

When a new partner contact registers:

1. User fills out partner registration form at `/partner/register`
2. A Partner record is created with `status: "pending"` and `tier: "bronze"` (default)
3. Admin reviews the request in the admin panel
4. Admin approves (user gets `partner` role, `partner_access_approved` email) or denies (`partner_access_denied` email)
5. Admin can change the tier after approval based on the sponsorship agreement
