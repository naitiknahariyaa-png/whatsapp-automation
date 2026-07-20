# AGENTS.md - NEXUS Platform Development Guide

## Project Overview

NEXUS is a unified AI automation platform built with TypeScript/Node.js that integrates WhatsApp, Telegram, GitHub, and Web capabilities.

## Tech Stack

- **Runtime**: Node.js 20+
- **Language**: TypeScript 5.6+
- **AI**: OpenAI GPT-4 / LangGraph
- **WhatsApp**: Baileys
- **Telegram**: Telegraf
- **GitHub**: Octokit
- **Web**: Playwright
- **Database**: PostgreSQL 15
- **Cache**: Redis 7
- **Deploy**: Docker

## Commands

```bash
# Development
npm run dev          # Start development server with hot reload
npm run build        # Build TypeScript to dist/
npm start            # Run production build

# Docker
npm run docker:build # Build Docker image
npm run docker:run   # Start with Docker Compose

# Quality
npm test             # Run tests with Vitest
npm run lint          # Run ESLint
```

## Code Style

- Use ES Modules (`type: "module"` in package.json)
- Use TypeScript strict mode
- Use `console.log` for logging (will integrate Winston later)
- All file paths use `.js` extension (required for ESM)
- Use async/await for all asynchronous operations
- Export classes for connectors and functions for utilities

## Adding New Connectors

1. Create connector in `src/connectors/`
2. Export from `src/connectors/index.ts`
3. Initialize in `src/index.ts`
4. Add API endpoints
5. Add tests

## Adding New AI Capabilities

1. Extend `NEXUSAgent` class in `src/agents/core.ts`
2. Add intent handlers
3. Update system prompt
4. Document in README

## Environment Variables

See `.env.example` for all required variables.
