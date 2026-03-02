# MongoDB Schema Design Patterns

## 1. Attribute Pattern

**Problem:** Sparse fields or many similar fields.

**Solution:** Store as array of key-value pairs.

```json
{
  "product": "Widget",
  "specs": [
    {"k": "color", "v": "red"},
    {"k": "size", "v": "large"}
  ]
}
```

**Index:** `{"specs.k": 1, "specs.v": 1}`

## 2. Bucket Pattern

**Problem:** Unbounded time-series data.

**Solution:** Group into time buckets.

```json
{
  "sensor": "temp_123",
  "hour": "2024-03-01T14:00:00Z",
  "readings": [
    {"time": "14:00", "value": 72},
    {"time": "14:01", "value": 73}
  ]
}
```

## 3. Subset Pattern

**Problem:** Large array, only need subset.

**Solution:** Embed subset, reference full data.

```json
{
  "product": "...",
  "recentReviews": [{...}],  // Last 10
  "totalReviews": 1547
}
```

## 4. Extended Reference

**Problem:** Need reference but want to avoid lookup.

**Solution:** Denormalize display fields.

```json
{
  "postId": "...",
  "authorId": "user123",  // Reference
  "authorName": "John",  // Denormalized
  "authorAvatar": "..."  // Denormalized
}
```

## 5. Polymorphic Pattern

**Problem:** Similar entities with different fields.

**Solution:** Single collection with type field.

```json
{
  "type": "video",
  "title": "...",
  "duration": 120  // Video-specific
}
{
  "type": "article",
  "title": "...",
  "wordCount": 1500  // Article-specific
}
```

## References

- Building with Patterns: https://www.mongodb.com/blog/post/building-with-patterns-a-summary
