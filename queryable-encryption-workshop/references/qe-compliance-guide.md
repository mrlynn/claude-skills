# QE Compliance Guide

## HIPAA (Healthcare)

**Key Requirements:**
- §164.312(a)(2)(iv): Encryption at rest
- §164.312(e)(2)(ii): Encryption in transit
- §164.308(a)(4): Access controls

**QE Mapping:**
- ✅ Field-level encryption (PHI fields)
- ✅ Key management via AWS KMS
- ✅ RBAC for key vault access
- ✅ Audit trails (KMS logs)

**PHI Fields to Encrypt:**
- SSN, medical record numbers
- Date of birth
- Diagnoses, prescriptions
- Lab results

## PCI-DSS (Finance)

**Key Requirements:**
- Req 3.4: Render PAN unreadable
- Req 3.5: Document key management
- Req 3.6.4: Cryptographic key changes
- Req 10: Track access to cardholder data

**QE Mapping:**
- ✅ Encrypt full card numbers (random)
- ✅ Encrypt last 4 (deterministic for lookup)
- ✅ KMS key management
- ⚠️ Manual key rotation process

**PAN Fields to Encrypt:**
- Full card number
- CVV
- Expiration date
- Account numbers

## FISMA/FedRAMP (Government)

**Key Requirements:**
- FIPS 140-2 cryptographic modules
- NIST 800-53 SC-28: Encryption at rest
- NIST 800-53 AC-2: Access controls

**QE Mapping:**
- ✅ AWS KMS is FIPS 140-2 validated
- ✅ Field-level encryption
- ✅ MongoDB RBAC
- ✅ Audit logging

**Sensitive Fields:**
- SSN, TIN
- Security clearance levels
- Classified notes

## GDPR (EU)

**Key Requirements:**
- Art 32: Data protection by design
- Art 17: Right to erasure

**QE Mapping:**
- ✅ Encryption at rest (Art 32)
- ⚠️ Manual deletion required (Art 17)

## Key Takeaways

- QE provides **encryption at rest** for all frameworks
- **AWS KMS** satisfies FIPS and key management requirements
- **MongoDB RBAC** handles access controls
- **Manual key rotation** needed for PCI-DSS compliance
