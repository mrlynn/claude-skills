#!/usr/bin/env python3
"""
Analyze industry vertical data sensitivity requirements.
Usage: python vertical_analyzer.py --vertical healthcare --output analysis.json
"""

import json
import argparse

VERTICALS = {
    "healthcare": {
        "sensitive_fields": [
            {"name": "ssn", "type": "deterministic", "regulation": "HIPAA", "reason": "PHI identifier"},
            {"name": "medicalRecordNumber", "type": "deterministic", "regulation": "HIPAA", "reason": "PHI identifier"},
            {"name": "dateOfBirth", "type": "range", "regulation": "HIPAA", "reason": "PHI demographic"},
            {"name": "diagnosis", "type": "random", "regulation": "HIPAA", "reason": "PHI medical"},
            {"name": "prescription", "type": "random", "regulation": "HIPAA", "reason": "PHI medical"},
        ],
        "plaintext_fields": ["fullName", "city", "state"],
        "compliance_frameworks": ["HIPAA", "HITECH"]
    },
    "finance": {
        "sensitive_fields": [
            {"name": "cardLast4", "type": "deterministic", "regulation": "PCI-DSS", "reason": "PAN lookup"},
            {"name": "cardNumberFull", "type": "random", "regulation": "PCI-DSS", "reason": "Full PAN"},
            {"name": "cvv", "type": "random", "regulation": "PCI-DSS", "reason": "Card security code"},
            {"name": "accountNumber", "type": "deterministic", "regulation": "PCI-DSS", "reason": "Account identifier"},
            {"name": "ssn", "type": "deterministic", "regulation": "PCI-DSS", "reason": "Customer identifier"},
        ],
        "plaintext_fields": ["merchantName", "transactionAmount", "transactionDate"],
        "compliance_frameworks": ["PCI-DSS", "SOX"]
    },
    "government": {
        "sensitive_fields": [
            {"name": "ssn", "type": "deterministic", "regulation": "FISMA", "reason": "Citizen identifier"},
            {"name": "taxId", "type": "deterministic", "regulation": "FISMA", "reason": "Tax identifier"},
            {"name": "clearanceLevel", "type": "range", "regulation": "FISMA", "reason": "Security clearance"},
            {"name": "classifiedNotes", "type": "random", "regulation": "FISMA", "reason": "Classified information"},
        ],
        "plaintext_fields": ["state", "registrationDate", "publicRecordId"],
        "compliance_frameworks": ["FISMA", "FedRAMP", "NIST-800-53"]
    }
}

def analyze_vertical(vertical):
    """Analyze vertical and return sensitivity requirements."""
    if vertical not in VERTICALS:
        raise ValueError(f"Unknown vertical: {vertical}. Choose from: {list(VERTICALS.keys())}")
    
    return {
        "vertical": vertical,
        **VERTICALS[vertical]
    }

def main():
    parser = argparse.ArgumentParser(description='Analyze vertical data sensitivity')
    parser.add_argument('--vertical', required=True, choices=VERTICALS.keys(), help='Industry vertical')
    parser.add_argument('--output', default='analysis.json')
    
    args = parser.parse_args()
    
    analysis = analyze_vertical(args.vertical)
    
    with open(args.output, 'w') as f:
        json.dump(analysis, f, indent=2)
    
    print(f"✅ Analyzed {args.vertical} vertical")
    print(f"✅ {len(analysis['sensitive_fields'])} sensitive fields identified")
    print(f"✅ Compliance frameworks: {', '.join(analysis['compliance_frameworks'])}")
    print(f"✅ Saved to {args.output}")

if __name__ == '__main__':
    main()
