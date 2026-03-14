# Language-Specific Analysis Patterns

## Python Projects

### Common Structures

**Flask/Django**
```
app/ or project_name/
├── __init__.py
├── models.py          # Database models
├── views.py           # Route handlers
├── templates/         # HTML templates
└── static/            # CSS/JS assets
```

**FastAPI**
```
app/
├── main.py            # FastAPI app instance
├── routers/           # API route modules
├── models/            # Pydantic models
├── services/          # Business logic
└── dependencies/      # Dependency injection
```

**Package**
```
package_name/
├── __init__.py
├── core/              # Core functionality
├── utils/             # Utilities
└── tests/             # Test suite
```

### Key Files

- `requirements.txt` / `pyproject.toml` - Dependencies
- `setup.py` - Package configuration
- `tox.ini` - Test environments
- `pytest.ini` / `setup.cfg` - Test configuration
- `.flake8` / `pyproject.toml` - Linting config

### Common Commands

```bash
# Run application
python main.py
python -m module_name

# Run tests
pytest
python -m pytest

# Install dependencies
pip install -r requirements.txt
pip install -e .
```

## JavaScript/TypeScript Projects

### Common Structures

**React App**
```
src/
├── components/        # React components
├── hooks/             # Custom hooks
├── contexts/          # React contexts
├── services/          # API calls
├── utils/             # Utilities
├── types/             # TypeScript types
└── assets/            # Static assets
```

**Next.js**
```
src/ or root/
├── app/               # App router (Next 13+)
├── pages/             # Pages router
├── components/        # Shared components
├── lib/               # Utilities
├── public/            # Static files
└── styles/            # CSS files
```

**Node.js API**
```
src/
├── routes/            # API routes
├── controllers/       # Route controllers
├── middleware/        # Express middleware
├── models/            # Data models
├── services/          # Business logic
└── config/            # Configuration
```

### Key Files

- `package.json` - Dependencies and scripts
- `tsconfig.json` - TypeScript configuration
- `.eslintrc.js` - Linting rules
- `vite.config.ts` / `next.config.js` - Build config

### Common Commands

```bash
# Development
npm run dev
npm start

# Build
npm run build

# Test
npm test
npm run test:watch

# Lint
npm run lint
npm run format
```

## Go Projects

### Common Structures

```
cmd/
├── app1/              # Main applications
│   └── main.go
└── app2/
    └── main.go
pkg/                   # Library code
├── package1/
└── package2/
internal/              # Private code
web/                   # Web assets
docs/                  # Documentation
```

### Key Files

- `go.mod` - Module definition
- `go.sum` - Dependency checksums
- `Makefile` - Build automation

### Common Commands

```bash
# Run
go run main.go
go run ./cmd/app

# Build
go build
go build -o app ./cmd/app

# Test
go test ./...
go test -v -race ./...

# Dependencies
go mod tidy
go mod download
```

## Rust Projects

### Common Structures

```
src/
├── main.rs            # Binary entry point
├── lib.rs             # Library entry point
├── bin/               # Additional binaries
├── modules/           # Module files
└── tests/             # Integration tests
```

### Key Files

- `Cargo.toml` - Package manifest
- `Cargo.lock` - Dependency lock
- `rustfmt.toml` - Formatting config

### Common Commands

```bash
# Build
cargo build
cargo build --release

# Run
cargo run
cargo run --bin binary_name

# Test
cargo test
cargo test --lib

# Check
cargo check
cargo clippy
```
