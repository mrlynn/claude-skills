# Industry Patterns

## Healthcare Pattern

**Schema:**
```javascript
{
  patientId: "P12345",        // Deterministic
  ssn: "encrypted",           // Deterministic
  dob: "encrypted",           // Range
  diagnosis: "encrypted",     // Random
  fullName: "John Doe"        // Plaintext
}
```

**Queries:**
- Lookup by SSN: `findOne({ ssn: "123-45-6789" })`
- Age-based: `find({ dob: { $gte: cutoffDate } })`
- Display name: Plaintext

## Finance Pattern

**Schema:**
```javascript
{
  customerId: "C12345",       // Deterministic
  cardLast4: "encrypted",     // Deterministic
  cardFull: "encrypted",      // Random
  amount: 99.99,              // Plaintext
  merchant: "Store"           // Plaintext
}
```

**Queries:**
- Lookup by last 4: `findOne({ cardLast4: "4242" })`
- Transaction analytics: Plaintext amount/merchant

## Government Pattern

**Schema:**
```javascript
{
  citizenId: "CIT123",        // Deterministic
  ssn: "encrypted",           // Deterministic
  clearance: "encrypted",     // Range
  notes: "encrypted",         // Random
  state: "MA"                 // Plaintext
}
```

**Queries:**
- Lookup by SSN: `findOne({ ssn: "..." })`
- Clearance level: `find({ clearance: { $gte: 3 } })`

## Common Principles

1. **Deterministic** for exact lookups
2. **Range** for numeric/date queries
3. **Random** for high-sensitivity, no queries
4. **Plaintext** for analytics and UX
