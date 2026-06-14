# EDITH Security Protocols 🔒

EDITH implements robust, multi-tier protection layers to secure Boss's data.

## 1. Owner Verification
- **Biometric Profiles**: Simulated face encoding comparisons and vocal speaker print checking.
- **PIN fallbacks**: High-stakes operations (transactions, file deletions, email drafts) require secondary PIN verification.

## 2. Intrusions and Decoys
- **Honeypot mode**: Spawns realistic mock financial sheets to occupy unauthorized users while silently notifying Boss.
- **Jailbreak Detection**: Scans prompt headers to block overrides and system instructions hijacking.
- **Rate limiting**: Restricts unverified input frequencies to 10 queries per minute to prevent system abuse.

## 3. Panic Protocols
- **Wipe Sequence**: Triggered silently when the panic word is parsed. Instantly clears session context, flushes the cached responses directory, and secure database rows.
