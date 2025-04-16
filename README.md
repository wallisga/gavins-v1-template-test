# gavins-v1-template

A standardized Python project structure with commit validation, changelog automation, and Hatch-based packaging. Built for trunk-based development and rapid releases.

---

## 📦 Installation

```bash
pip install gavins-v1-template
```

---

## 🚀 Project Features

- 🔒 Commit enforcement (feat(scope): ...) using a custom pre-push script

- 📝 Automatic changelog updates per commit

- 📦 Hatch-based build with dynamic versioning

- ✅ Versioned and structured for PyPI

---

## 🔄 Changelog

Changelog is maintained in CHANGELOG.md and auto-updated from validated commits.

---

## 🤝 Contributing

- Follow conventional commit format:

`feat(scope): description`

- Use `git safe-push` to validate and update changelog