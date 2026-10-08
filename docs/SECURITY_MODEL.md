# AegisKey Security Model

## Scope

AegisKey is a local CLI password-vault project.

Its current security model is designed around:

- verifying a local user's master password
- deriving an encryption key after successful authentication
- encrypting stored credential passwords
- preventing credentials belonging to one application user from being accessed through another user's normal application session
- avoiding accidental disclosure of plaintext passwords during normal browsing

It is not an audited password manager and does not claim protection against every local or host-level threat.

## Authentication

During registration, the master password is processed with Argon2id.

The application stores:

- a derived password-verification value
- a salt for password verification
- a separate salt for encryption-key derivation

During login, the supplied master password is verified against the stored password-verification value.

After successful authentication, the master password and encryption salt are used to derive the Fernet-compatible encryption key used by the active session.

## Credential encryption

The credential Password field is encrypted with Fernet before it is written to SQLite.

The encryption key itself is not stored directly in the vault database by the application.

Credential passwords are normally shown as masked values and are decrypted only when required by an explicit operation such as Reveal or Password Edit.

If a stored Fernet token is corrupted or cannot be decrypted using the active key, the application converts that failure into a controlled application error instead of exposing the underlying key/ciphertext through a normal traceback.

## User ownership

Credential-specific application paths use the active `UserID` as part of database filtering.

This applies to current credential:

- detail/password reads
- edits/updates
- deletes
- search/list results

The purpose is to prevent a logged-in user from accessing another application's user's credential merely by supplying or reaching another credential ID.

## SQL handling

User-controlled values are passed to SQLite through parameterized queries.

Some table/column identifiers are built dynamically in generic storage helpers, but in the current CLI those identifiers are supplied by trusted application code rather than direct user text input.

This distinction is important: SQL values and SQL identifiers are handled differently by SQLite parameter binding.

## Session handling

The active session carries:

- email
- user ID
- derived encryption key

When the user locks/exits the vault session, the application's references to these values are cleared.

Python does not provide a reliable secure-memory wiping guarantee. Assigning a variable to `None` releases the application reference but does not guarantee that the previous bytes are immediately overwritten in process memory.

## Clipboard behavior

When the user explicitly chooses Copy, AegisKey places the plaintext password in the operating-system clipboard.

In CLI v1.0, AegisKey does **not** automatically clear the clipboard.

This is an intentional design choice. The copied password remains available until the clipboard is overwritten by the user or another application.

Users should understand that other local applications with clipboard access may be able to read clipboard contents.

## Database contents

The SQLite database is not a fully encrypted database.

The credential Password field is encrypted, but other information may remain visible to someone who can directly inspect the database, including data such as:

- account email addresses
- password-verification hashes/derived values
- salts
- service names
- usernames
- comments
- timestamps

Therefore AegisKey should not be described as providing full-database encryption.

## Local machine compromise

AegisKey does not protect secrets from a fully compromised or hostile host.

An attacker with sufficient control of the operating system or running process may be able to:

- capture keyboard input
- inspect process memory
- read clipboard contents
- alter the application
- access plaintext passwords while they are revealed
- replace dependencies or application files

AegisKey assumes the local operating system and Python environment are reasonably trusted.

## Database tampering

Direct modification of the SQLite database is outside the normal application flow.

Ownership checks limit cross-user access through normal application operations, but they are not a substitute for filesystem permissions or protection against a hostile administrator modifying the database/application itself.

Corrupt encrypted password values are handled as decryption failures rather than being silently accepted as plaintext.

## Error handling and sensitive output

Normal user-facing errors should not include:

- master passwords
- encryption keys
- decrypted passwords
- raw encrypted credential values

Debug output containing credential rows should not be left enabled in release code.

## Cryptographic limitations

The project uses established primitives from the Python `cryptography` package rather than implementing custom encryption algorithms.

However, correct primitive selection alone does not make the complete application independently secure.

Security depends on:

- application logic
- dependency integrity
- host security
- password strength
- safe handling of secrets
- correct configuration and future maintenance

The project has not undergone an external cryptographic or application-security audit.

## Intended use

AegisKey is intended as:

- a software-engineering and security-learning project
- a local CLI demonstration of password-vault concepts
- a foundation for future API/web development

Users should use an independently audited password manager for important production credentials.

## Responsible disclosure

For vulnerability reporting instructions, see the repository-level [SECURITY.md](../SECURITY.md).
