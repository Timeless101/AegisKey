# AegisKey Architecture

## Purpose

This document describes the current CLI v1.x architecture.

The design intentionally keeps user-interface code, application flow, feature logic, storage access, validation, and cryptographic operations separate enough that the CLI can later be complemented by a REST API and web interface.

## High-level flow

```text
User
 ↓
Interface
 ↓
Core / Services
 ↓
Storage Logic
 ↓
Database Logic
 ↓
SQLite
```

Cryptography and validation are used by the core/service layers where required.

## Entry point

### `src/main.py`

Starts the application through:

```text
main()
 → core.main_logic.program_flow()
```

The entry point intentionally contains very little application logic.

## Core layer

### `src/core/main_logic.py`

Owns the top-level application/session loop.

Responsibilities include:

- moving between authentication and vault flows
- holding the active `email`, `userid`, and `encryption_key`
- clearing session references when the vault is locked/exited

### `src/core/login_logic.py`

Coordinates registration and login.

Responsibilities include:

- database initialization
- account lookup
- email/password validation
- master-password verification
- encryption-key derivation
- creating new users

### `src/core/vault_logic.py`

Coordinates the main vault screen and dispatches the user into feature flows such as Add, View, and Search.

It does not perform low-level database work directly.

## Services layer

The services layer contains feature-specific application behavior.

### `src/services/add_items.py`

- collects confirmed credential data from the interface
- encrypts the credential password
- passes the resulting values to storage

### `src/services/view_items.py`

- lists and opens credentials
- maps screen numbers to credential IDs
- reveals/decrypts passwords on explicit request
- copies revealed passwords to the clipboard
- coordinates Edit and Delete actions

Credential reads are scoped to both credential ID and logged-in user ID.

### `src/services/edit.py`

- loads the current field
- handles edit confirmation
- encrypts replacement passwords before persistence
- updates only credentials owned by the active user
- handles password-decryption failure safely

### `src/services/search.py`

- manages the Search flow
- searches Service, Username, and Comment
- tracks search pagination/state
- scopes results to the active user

### `src/services/pagination.py`

Owns pagination state such as:

- current page
- page size
- offset
- total pages
- visible range

This is intentionally stateful because those values belong to one pagination session.

## Interface layer

### `src/interface/`

Contains terminal input/output.

Examples:

- Rich tables and panels
- prompts and choices
- success/error messages
- masked password presentation
- empty-state and no-results screens

Interface modules should not contain SQL or database-access logic.

## Storage layer

### `src/storage/storage_logic.py`

Acts as the application-facing storage boundary.

Responsibilities include:

- supplying the application database/table context
- adapting low-level database calls into functions used by core/services
- centralizing common storage operations

### `src/storage/database_logic.py`

Contains low-level SQLite operations.

Responsibilities include:

- table/database creation
- inserts
- credential reads
- search queries
- updates
- deletes

User-controlled SQL values are passed using SQLite parameters.

Credential-specific reads, updates, and deletes include `UserID` ownership filtering in the active application paths.

## Cryptography

### `src/crypto.py`

Owns cryptographic primitives:

- Argon2id master-password hashing
- Argon2id encryption-key derivation
- Fernet password encryption
- Fernet password decryption
- translation of invalid/corrupt ciphertext into an application-level decryption error

Cryptographic functions do not own CLI presentation.

## Validation

### `src/validator.py`

Contains input-validation behavior such as email/password checks and menu-related validation.

## Shared code

### `src/common/errors.py`

Defines application-specific exceptions so lower layers can report failures without deciding how the CLI should present them.

### `src/common/helper_functions.py`

Contains small shared CLI/helper functions.

## Credential data flow

### Add

```text
Interface input
 → services.add_items
 → encrypt password
 → storage_logic
 → database_logic
 → SQLite
```

### View / Reveal

```text
User selects credential
 → services.view_items
 → ownership-scoped storage read
 → encrypted password loaded only when needed
 → crypto.password_decryption
 → interface displays plaintext after confirmation
```

### Edit

```text
User chooses field
 → services.edit
 → ownership-scoped read
 → optional password decryption
 → user confirmation
 → password re-encrypted when applicable
 → ownership-scoped update
```

### Search

```text
Search input
 → services.search
 → database search scoped by UserID
 → paginated results
 → existing View/Open flow
```

## Future API direction

The intended future shape is:

```text
CLI Interface ─┐
               ├→ Core / Services → Storage / Crypto
FastAPI API ───┘
```

The API should become another interface into the same application concepts rather than duplicating business logic.

This is a design direction, not a guarantee that the existing CLI modules will remain unchanged.
