---
name: queryable-encryption-workshop
description: Generate MongoDB Queryable Encryption demos customized for industry verticals (healthcare, finance, government) with compliance mapping and production patterns
license: MIT
metadata:
  version: 1.0.0
  author: Michael Lynn [mlynn.org](https://mlynn.org)
  category: security
  domain: queryable-encryption
  updated: 2026-03-01
  python-tools: vertical_analyzer.py, demo_generator.py, compliance_mapper.py
  tech-stack: mongodb, queryable-encryption, python, compliance
---

# queryable-encryption-workshop

## Trigger

Use this skill when demonstrating Queryable Encryption, mapping compliance requirements, or building industry-specific security demos.

**Trigger phrases:**
- "Build QE demo for [healthcare/finance/government]"
- "Map QE to HIPAA/PCI-DSS/GDPR"
- "Generate encryption demo"
- "Show QE compliance patterns"

## Overview

Queryable Encryption (QE) is MongoDB's client-side field-level encryption that allows encrypted search. Different industries have different compliance needs, data sensitivity levels, and use cases.

This skill generates **industry-customized demos** that map QE features to specific compliance requirements.

**Not for:** General encryption education. This is about **vertical-specific demos** with compliance context.

## How to Use

### Quick Start

1. **Analyze vertical requirements:**
   ```bash
   python scripts/vertical_analyzer.py --vertical healthcare --output analysis.json
   ```

2. **Generate demo code:**
   ```bash
   python scripts/demo_generator.py analysis.json --output demo/
   ```

3. **Map compliance requirements:**
   ```bash
   python scripts/compliance_mapper.py --vertical healthcare --framework HIPAA --output compliance.md
   ```

### Python Tools
- `scripts/vertical_analyzer.py` — Analyze industry data sensitivity patterns
- `scripts/demo_generator.py` — Generate vertical-specific QE demo code
- `scripts/compliance_mapper.py` — Map QE to compliance frameworks

### Reference Docs
- `references/qe-compliance-guide.md` — QE mapped to HIPAA, PCI-DSS, GDPR
- `references/industry-patterns.md` — Common patterns by vertical

### Templates & Assets
- `assets/healthcare-schema.json` — Patient data with PHI fields
- `assets/finance-schema.json` — Financial data with PII/PCI fields
- `assets/government-schema.json` — Citizen data with SSN/TIN fields

## Industry Verticals

### Healthcare (HIPAA)

**Sensitive data:**
- PHI (Protected Health Information)
- SSN, date of birth, medical record numbers
- Diagnoses, prescriptions, lab results

**QE approach:**
- **Equality queries:** SSN, medical record number (exact lookups)
- **Range queries:** Date of birth (age-based queries)
- **Unencrypted:** Non-PHI (names for display, city for analytics)

**Example schema:**
```javascript
{
  patientId: "P12345",  // Deterministic (equality search)
  ssn: "***-**-6789",   // Deterministic (encrypted, searchable)
  dob: "1980-05-15",    // Range (encrypted, age queries)
  diagnosis: "...",     // Random (encrypted, not searchable)
  fullName: "John Doe", // Plaintext (not PHI for display)
  city: "Boston"        // Plaintext (analytics)
}
```

**Compliance mapping:**
- HIPAA §164.312(a)(2)(iv): Encryption at rest ✅
- HIPAA §164.312(e)(2)(ii): Encryption in transit ✅
- HIPAA §164.308(a)(4): Access controls ✅ (key management)

### Finance (PCI-DSS)

**Sensitive data:**
- Credit card numbers (PAN)
- CVV, expiration dates
- Account numbers, routing numbers
- SSN, transaction details

**QE approach:**
- **Deterministic:** Last 4 digits of card (customer lookup)
- **Random:** Full card number (store but never query)
- **Unencrypted:** Transaction amounts (reporting), merchant names

**Example schema:**
```javascript
{
  customerId: "C12345",      // Deterministic
  cardLast4: "4242",         // Deterministic (searchable)
  cardNumberFull: "****",    // Random (encrypted, not searchable)
  expirationDate: "12/25",   // Random
  transactionAmount: 99.99,  // Plaintext (analytics)
  merchantName: "Store Inc"  // Plaintext
}
```

**Compliance mapping:**
- PCI-DSS Req 3.4: Encryption of PAN ✅
- PCI-DSS Req 3.5.1: Key management ✅
- PCI-DSS Req 3.6.4: Cryptographic key changes ✅

### Government (FedRAMP, FISMA)

**Sensitive data:**
- SSN, TIN (Tax ID)
- Clearance levels
- Citizen records
- Classified information

**QE approach:**
- **Deterministic:** SSN (citizen lookup)
- **Range:** Security clearance level (range queries)
- **Random:** Classified notes
- **Unencrypted:** Public records, statistics

**Example schema:**
```javascript
{
  citizenId: "CIT12345",    // Deterministic
  ssn: "***-**-6789",       // Deterministic (searchable)
  clearanceLevel: 3,        // Range (encrypted, level queries)
  classifiedNotes: "...",   // Random (encrypted, not searchable)
  state: "MA",              // Plaintext (analytics)
  registrationDate: "2020"  // Plaintext
}
```

**Compliance mapping:**
- FISMA: Encryption requirements ✅
- FedRAMP: Key management ✅
- NIST 800-53: Access controls ✅

## QE Encryption Types

### 1. Deterministic (Equality Queries)

**Use for:** Exact match searches (SSN, email, account number)

**Properties:**
- Same plaintext → same ciphertext (searchable)
- Supports: `$eq`, `$in`, `$ne`
- **Not secure for low-cardinality fields** (gender, state)

**Example:**
```javascript
{
  ssn: {
    encrypt: {
      keyId: "key1",
      algorithm: "AEAD_AES_256_CBC_HMAC_SHA_512-Deterministic",
      bsonType: "string"
    }
  }
}
```

### 2. Range (Range Queries)

**Use for:** Numeric ranges, date ranges (age, salary, dates)

**Properties:**
- Supports: `$gt`, `$gte`, `$lt`, `$lte`, `$range`
- More secure than deterministic
- Requires min/max bounds

**Example:**
```javascript
{
  dateOfBirth: {
    encrypt: {
      keyId: "key2",
      algorithm: "Range",
      bsonType: "date",
      min: ISODate("1900-01-01"),
      max: ISODate("2024-12-31"),
      sparsity: 2
    }
  }
}
```

### 3. Random (No Queries)

**Use for:** Sensitive data never queried (full card numbers, notes)

**Properties:**
- Same plaintext → different ciphertext (most secure)
- Not searchable
- Best for high-sensitivity fields

**Example:**
```javascript
{
  creditCardNumber: {
    encrypt: {
      keyId: "key3",
      algorithm: "AEAD_AES_256_CBC_HMAC_SHA_512-Random",
      bsonType: "string"
    }
  }
}
```

## Key Management Patterns

### Pattern 1: AWS KMS (Production)

**Best for:** Production deployments, compliance audits

**Setup:**
```javascript
const clientEncryption = new ClientEncryption(client, {
  keyVaultNamespace: "encryption.__keyVault",
  kmsProviders: {
    aws: {
      accessKeyId: process.env.AWS_ACCESS_KEY_ID,
      secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY
    }
  }
});
```

**Compliance:** FIPS 140-2 validated, audit trails, key rotation

### Pattern 2: Local Key (Demos)

**Best for:** Workshops, POCs, local development

**Setup:**
```javascript
const localKey = crypto.randomBytes(96);
const clientEncryption = new ClientEncryption(client, {
  keyVaultNamespace: "encryption.__keyVault",
  kmsProviders: {
    local: {
      key: localKey
    }
  }
});
```

**Warning:** Not for production (key stored in code)

### Pattern 3: Azure Key Vault

**Best for:** Azure deployments, Microsoft shops

**Setup:**
```javascript
const clientEncryption = new ClientEncryption(client, {
  keyVaultNamespace: "encryption.__keyVault",
  kmsProviders: {
    azure: {
      tenantId: process.env.AZURE_TENANT_ID,
      clientId: process.env.AZURE_CLIENT_ID,
      clientSecret: process.env.AZURE_CLIENT_SECRET
    }
  }
});
```

## Demo Structure

### Phase 1: Unencrypted Baseline (5 min)

Show data in plaintext, query patterns:
```javascript
// Insert plaintext
db.patients.insertOne({
  ssn: "123-45-6789",
  dob: new Date("1980-05-15"),
  diagnosis: "Hypertension"
});

// Query plaintext
db.patients.findOne({ ssn: "123-45-6789" });
```

**Demonstrate:** Data visible in MongoDB Compass, logs, backups

### Phase 2: Enable QE (10 min)

1. Create data encryption keys
2. Define encrypted fields schema
3. Create encrypted client
4. Insert encrypted data

```javascript
// Create DEK
const keyId = await clientEncryption.createDataKey("local");

// Define schema
const schema = {
  "patients": {
    encryptedFields: {
      fields: [
        { path: "ssn", keyId, bsonType: "string", queries: { queryType: "equality" } },
        { path: "dob", keyId, bsonType: "date", queries: { queryType: "range", min: ..., max: ... } },
        { path: "diagnosis", keyId, bsonType: "string" }  // Random
      ]
    }
  }
};

// Insert encrypted
const encryptedClient = new MongoClient(uri, { autoEncryption: { keyVaultNamespace, kmsProviders, encryptedFieldsMap: schema } });
await encryptedClient.db("hospital").collection("patients").insertOne({
  ssn: "123-45-6789",  // Encrypted deterministic
  dob: new Date("1980-05-15"),  // Encrypted range
  diagnosis: "Hypertension"  // Encrypted random
});
```

### Phase 3: Query Encrypted Data (10 min)

Show what queries work:
```javascript
// ✅ Works: Equality on deterministic field
await patients.findOne({ ssn: "123-45-6789" });

// ✅ Works: Range on range field
await patients.find({ dob: { $gte: new Date("1980-01-01") } });

// ❌ Fails: Query on random field
await patients.findOne({ diagnosis: "Hypertension" });  // No results (encrypted)
```

**Show in Compass:** Ciphertext blobs, metadata collection

### Phase 4: Compliance Mapping (5 min)

Connect to compliance requirements:
- "This meets HIPAA §164.312(a)(2)(iv) encryption requirement"
- "Key vault in AWS KMS provides FIPS 140-2 compliance"
- "Access controls via MongoDB RBAC satisfy HIPAA §164.308(a)(4)"

## Python Tool Details

### 1. Vertical Analyzer

**Input:** Vertical name

**Output:** Sensitivity analysis
```json
{
  "vertical": "healthcare",
  "sensitive_fields": [
    { "name": "ssn", "type": "deterministic", "regulation": "HIPAA", "reason": "PHI identifier" },
    { "name": "dob", "type": "range", "regulation": "HIPAA", "reason": "PHI demographic" },
    { "name": "diagnosis", "type": "random", "regulation": "HIPAA", "reason": "PHI medical" }
  ],
  "plaintext_fields": ["fullName", "city"],
  "compliance_frameworks": ["HIPAA", "HITECH"]
}
```

### 2. Demo Generator

**Input:** Vertical analysis

**Output:** Complete demo code (Node.js + Python)
- `setup.js` — Create keys, schema
- `insert.js` — Insert encrypted data
- `query.js` — Query examples
- `README.md` — Workshop guide

### 3. Compliance Mapper

**Input:** Vertical + framework

**Output:** Compliance mapping document
```markdown
# HIPAA Compliance Mapping

## §164.312(a)(2)(iv): Encryption and Decryption
✅ MongoDB Queryable Encryption provides encryption at rest
✅ TLS 1.2+ provides encryption in transit

## §164.308(a)(4): Access Controls
✅ MongoDB RBAC restricts key vault access
✅ AWS KMS provides key access audit trails
...
```

## Common Patterns

### Pattern 1: Healthcare Patient Lookup

**Scenario:** Find patient by SSN, show non-PHI

```javascript
// Encrypted: ssn, dob, diagnosis
// Plaintext: fullName, city (for UX)

const patient = await patients.findOne({ ssn: "123-45-6789" });
// Returns: { fullName: "John Doe", city: "Boston", ssn: <encrypted>, ... }
```

### Pattern 2: Finance Transaction Search

**Scenario:** Lookup by last 4 digits, hide full card

```javascript
// Encrypted: cardLast4 (deterministic), cardNumberFull (random)
// Plaintext: merchantName, amount

const transactions = await txns.find({ cardLast4: "4242" });
// Returns masked card, plaintext merchant/amount
```

### Pattern 3: Government Clearance Query

**Scenario:** Find citizens with clearance level >= 3

```javascript
// Encrypted: ssn (deterministic), clearanceLevel (range)
// Plaintext: state, registrationDate

const citizens = await citizens.find({ clearanceLevel: { $gte: 3 } });
```

## Workshop Agenda (60 min)

**0-10 min:** Introduction
- Why encryption? (breaches, compliance)
- Encryption at rest vs in use vs QE
- Demo preview

**10-25 min:** QE Deep Dive
- Three encryption types (deterministic, range, random)
- Key management (AWS KMS, local)
- Schema definition

**25-45 min:** Live Demo
- Phase 1: Plaintext baseline
- Phase 2: Enable QE
- Phase 3: Query encrypted data
- Show in Compass (ciphertext)

**45-55 min:** Compliance Mapping
- Map to HIPAA/PCI-DSS/FISMA
- Production considerations
- Key rotation, access controls

**55-60 min:** Q&A + Resources

## Compliance Cheat Sheet

| Framework | Requirements | QE Mapping |
|-----------|--------------|------------|
| **HIPAA** | Encryption at rest (§164.312) | ✅ QE encrypts fields |
| | Access controls (§164.308) | ✅ RBAC + KMS |
| | Audit trails (§164.312) | ✅ KMS logs |
| **PCI-DSS** | Encrypt PAN (Req 3.4) | ✅ QE on card fields |
| | Key management (Req 3.5) | ✅ AWS KMS |
| | Key rotation (Req 3.6.4) | ✅ Manual rotation |
| **GDPR** | Data protection (Art 32) | ✅ QE encryption |
| | Right to erasure (Art 17) | ⚠️ Manual delete |
| **FISMA** | FIPS 140-2 (NIST 800-53) | ✅ AWS KMS FIPS |

## Production Considerations

### 1. Performance

**Impact:**
- Encrypted writes: ~10-20% slower (encryption overhead)
- Encrypted reads: ~5-10% slower (decryption)
- Range queries: Higher overhead than equality

**Mitigation:**
- Index plaintext fields for filtering
- Use deterministic sparingly (lower security)
- Cache decrypted results when safe

### 2. Key Rotation

**Manual process:**
1. Create new data encryption key
2. Re-encrypt data with new key
3. Update schema to reference new key

**Automation:** Use scripts, schedule quarterly

### 3. Backup & Disaster Recovery

**Key vault backup:**
- AWS KMS: Automatic replication
- Local keys: Backup to secure storage

**Encrypted data backup:**
- Backup encrypted documents (safe)
- Restore requires key vault access

## Quality Checklist

Before workshop:
- [ ] Vertical analysis complete
- [ ] Demo code tested locally
- [ ] Compliance mapping reviewed
- [ ] AWS KMS credentials configured (or local key ready)
- [ ] MongoDB Compass installed (show ciphertext)
- [ ] Timing rehearsed (60 min)

During demo:
- [ ] Show plaintext first (contrast)
- [ ] Explain each encryption type clearly
- [ ] Demo all three query patterns
- [ ] Show Compass (visual proof)
- [ ] Map to compliance requirements
- [ ] Leave time for Q&A

## When to Use vs. Other Tools

| Use `queryable-encryption-workshop` | Use other tools |
|-------------------------------------|-----------------|
| Industry-specific QE demos | General encryption education |
| Compliance mapping | Security architecture design |
| Workshop prep | Production implementation |
| Vertical analysis | Performance tuning |

## References

- QE Compliance Guide: `references/qe-compliance-guide.md`
- Industry Patterns: `references/industry-patterns.md`
- Official docs: https://www.mongodb.com/docs/manual/core/queryable-encryption/
- Compliance: https://www.mongodb.com/compliance

## Credits

**Michael Lynn** — [mlynn.org](https://mlynn.org) · [@mlynn](https://twitter.com/mlynn) · [LinkedIn](https://linkedIn.com/in/mlynn) · [GitHub](https://github.com/mrlynn)

---

**Next steps after workshop:**
1. Customer-specific schema design
2. Production KMS setup
3. Performance testing
4. Compliance audit preparation
