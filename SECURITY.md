# Security Policy

## Supported version

The actively supported version is the current CLI v1.x release line.

Security fixes for unreleased development work are made on the active development branch before the next release.

## Reporting a vulnerability

Please do **not** publish security vulnerabilities, proof-of-concept exploits, real credentials, database files, encryption keys, master passwords, decrypted passwords, or other sensitive information in a public GitHub issue.

If you believe you have found a security issue:

1. Contact the repository owner privately through an available private contact method on the GitHub profile/repository.
2. Include a clear description of the issue and the affected version.
3. Include reproduction steps that do not contain real secrets.
4. If possible, explain the security impact and any conditions required to reproduce it.

Public issues may be used after the sensitive details have been removed or after a fix is available.

## Security scope

AegisKey is a local CLI password-vault learning project.

The project aims to protect stored credential passwords against casual disclosure from the SQLite database and to prevent one authenticated application user from reading, editing, or deleting another user's credentials through normal application flows.

The project has **not** undergone an independent security audit and should not be treated as an audited production password manager.

See [docs/SECURITY_MODEL.md](docs/SECURITY_MODEL.md) for the detailed threat model, guarantees, assumptions, and known limitations.
