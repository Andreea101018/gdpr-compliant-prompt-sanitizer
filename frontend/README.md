# GDPR-Compliant Prompt Sanitizer

A GDPR-aware privacy-preserving prompt sanitization pipeline with span-level PII/PHI detection, selective masking, retention logging, and reformulation support.

## Overview

Large Language Models (LLMs) increasingly process user-generated prompts that may contain Personally Identifiable Information (PII) or Protected Health Information (PHI). This project implements a GDPR-aligned sanitization pipeline that:

- Detects PII/PHI at span level
- Supports selective masking or removal
- Logs data retention metadata
- Enables prompt reformulation after sanitization
- Provides a dashboard for transparency and lifecycle management

The system is designed to support privacy-preserving AI applications in compliance-driven environments.

---

## Architecture

The system consists of three components:

### 1. Backend (Flask API)
- PII detection via BERT-based NER model
- Span-level masking
- Retention policy parsing
- SQLite audit logging
- REST endpoints for sanitization and reformulation

### 2. Detection Engine (`bert/`)
- Fine-tuned transformer-based NER model
- Regex-enhanced financial/entity detection
- Topic detection module
- Rule-based fallback masking

### 3. Frontend (Next.js)
- Interactive masking interface
- Selective removal UI
- Retention policy management
- Audit dashboard

---

## Features

- Span-level PII/PHI detection
- Selective masking (`[TYPE_REMOVED]`)
- GDPR-style retention control (e.g., `30d`, `365d`)
- Expiration tracking
- Audit logging
- Reformulation of sanitized prompts
- Position-aware masking (no offset corruption)

---

## Data Governance

This system supports:

- Data minimization
- Storage limitation
- Transparency
- Controlled retention
- Explicit masking decisions

Note: The database stores only what is explicitly selected by the user.

---

## Installation

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python api.py
