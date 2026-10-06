# Security Policy

## Reporting a vulnerability

Please do not open a public issue for a security vulnerability. Use the
private vulnerability reporting feature on the GitHub repository. GitHub
requires the repository to be public before this feature can be enabled, so
maintainers must enable it as part of public launch. Until it is enabled, use
the Edgematrix Inc. security contact at [info@edgematrix.com](mailto:info@edgematrix.com).

Include the affected skill and resource path, a reproducible description, the
impact, and any suggested mitigation. Do not include station credentials,
tokens, personal data, or production logs in the report.

## Scope

This repository contains agent instructions and reference resources. Reports
about credential disclosure, unsafe command examples, prompt-injection
handling, secret handling, or misleading destructive operational guidance are
in scope.

Never publish real station passwords, API tokens, private hostnames, or
customer configuration in issues, pull requests, examples, or documentation.

## Public launch checklist

- Enable private vulnerability reporting after changing the repository to public.
- Enable secret scanning and push protection, then review any alerts privately.
- Verify that `info@edgematrix.com` is monitored for security reports until private
  vulnerability reporting is enabled.
