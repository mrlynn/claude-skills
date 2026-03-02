#!/usr/bin/env python3
"""
  author: Michael Lynn [mlynn.org](https://mlynn.org)
  updated: 2026-03-02
  Map QE features to compliance requirements.
  Usage: python compliance_mapper.py --vertical healthcare --framework HIPAA --output compliance.md
"""

import argparse

MAPPINGS = {
    "HIPAA": {
        "§164.312(a)(2)(iv)": "Encryption at rest - QE encrypts sensitive fields",
        "§164.312(e)(2)(ii)": "Encryption in transit - TLS 1.2+ required",
        "§164.308(a)(4)": "Access controls - MongoDB RBAC + KMS key access",
        "§164.312(b)": "Audit trails - KMS provides key access logs",
    },
    "PCI-DSS": {
        "Req 3.4": "Encrypt PAN - QE encrypts card numbers",
        "Req 3.5": "Key management - AWS KMS or Azure Key Vault",
        "Req 3.6.4": "Key rotation - Manual re-encryption with new DEK",
        "Req 10": "Audit trails - MongoDB logs + KMS logs",
    },
    "FISMA": {
        "FIPS 140-2": "Cryptographic modules - AWS KMS is FIPS validated",
        "NIST 800-53 SC-28": "Encryption at rest - QE field-level encryption",
        "NIST 800-53 AC-2": "Access controls - MongoDB RBAC",
    }
}

def generate_compliance_doc(framework):
    """Generate compliance mapping document."""
    if framework not in MAPPINGS:
        raise ValueError(f"Unknown framework: {framework}")
    
    doc = f"# {framework} Compliance Mapping\n\n"
    doc += f"MongoDB Queryable Encryption alignment with {framework} requirements.\n\n"
    
    for requirement, description in MAPPINGS[framework].items():
        doc += f"## {requirement}\n"
        doc += f"✅ {description}\n\n"
    
    return doc

def main():
    parser = argparse.ArgumentParser(description='Map QE to compliance')
    parser.add_argument('--vertical', help='Industry vertical (for context)')
    parser.add_argument('--framework', required=True, choices=MAPPINGS.keys(), help='Compliance framework')
    parser.add_argument('--output', default='compliance.md')
    
    args = parser.parse_args()
    
    doc = generate_compliance_doc(args.framework)
    
    with open(args.output, 'w') as f:
        f.write(doc)
    
    print(f"✅ Generated {args.framework} compliance mapping")
    print(f"✅ Saved to {args.output}")

if __name__ == '__main__':
    main()
