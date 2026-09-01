# Backend Architecture

A modular, scalable, clean-architecture backend scaffolding.

## 📁 Directory Structure

```text
├── .env.example                     # Sample environment variable template
├── .gitignore                       # Git ignore configurations
├── Dockerfile                       # Container definition
├── docker-compose.yml               # Multi-container orchestration
├── package.json                     # Project manifest and dependencies
├── tsconfig.json                    # TypeScript compiler configuration
├── README.md                        # Project documentation
│
├── src/
│   ├── config/                      # App configuration (database, redis, logger, env)
│   ├── constants/                   # Static constants, error codes, HTTP status codes
│   ├── controllers/                 # Request handlers / Controller layer
│   ├── database/
│   │   ├── migrations/              # Database migration scripts
│   │   └── seeders/                 # Database seed scripts
│   ├── dtos/                        # Data Transfer Objects
│   ├── integrations/                # Third-party integrations (carriers, payment, external APIs)
│   ├── interfaces/                  # TypeScript interfaces and type definitions
│   ├── jobs/
│   │   ├── queues/                  # Message / task queue definitions
│   │   └── workers/                 # Background workers and consumers
│   ├── middlewares/                 # Express / HTTP middlewares (auth, errors, rate limiter, etc.)
│   ├── models/                      # Database models / entities
│   ├── repositories/                # Data access layer (database abstraction)
│   ├── routes/                      # Route definitions and versioning (e.g. /v1)
│   ├── services/                    # Core business logic layer
│   ├── utils/                       # Shared utility functions, logger, response wrappers
│   ├── validations/                 # Request validation schemas (e.g. Zod / Joi)
│   ├── app.ts                       # Application configuration & middleware mounting
│   └── server.ts                    # Server initialization & entrypoint
│
└── tests/
    ├── unit/                        # Unit tests
    ├── integration/                 # Integration tests
    ├── e2e/                         # End-to-end tests
    └── fixtures/                    # Test data and mock fixtures
```
