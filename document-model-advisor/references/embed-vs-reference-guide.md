# Embed vs Reference: The Definitive Guide

## The Question

"Should I embed or reference?" - The most common MongoDB question.

## Quick Answer

**Embed** when data is accessed together and bounded.
**Reference** when data is accessed separately or unbounded.

## The Decision Tree

```
Always accessed together?
├─ Yes → Embed (unless unbounded)
└─ No → Reference
```

## Examples

### ✅ Embed: User Addresses
```json
{
  "_id": "user123",
  "addresses": [
    {"type": "home", "street": "123 Main"},
    {"type": "work", "street": "456 Park"}
  ]
}
```
**Why:** Few addresses, always shown with user profile.

### ✅ Reference: Blog Comments
```json
// Post
{"_id": "post123", "title": "..."}

// Comments (separate)
{"_id": "c1", "postId": "post123", "text": "..."}
```
**Why:** Unbounded comments, paginated separately.

## Trade-Offs

| Embed | Reference |
|-------|-----------|
| ✅ Faster reads (1 query) | ✅ Smaller docs |
| ✅ Atomic updates | ✅ No duplication |
| ❌ Doc size limits | ❌ Multiple queries |
| ❌ Duplication if shared | ❌ No atomic updates |

## Rules of Thumb

1. **Favor embedding for:**
   - One-to-few relationships
   - Data rarely accessed separately
   - Data with same lifecycle

2. **Favor referencing for:**
   - One-to-many (unbounded)
   - Many-to-many
   - Data used across entities

3. **Consider denormalization for:**
   - Display fields (name, avatar)
   - Read-heavy workloads
   - Acceptable eventual consistency

## References

- MongoDB docs: https://docs.mongodb.com/manual/core/data-model-design/
