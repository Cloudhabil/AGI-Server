# Orbital Orchestrator UI

React + Vite + TypeScript + Tailwind + Zustand + TanStack Query.

## Development

```bash
cd frontend
npm install
npm run dev
```

The dev server runs at <http://localhost:5173>.

## Build

```bash
npm run build
```

Environment variables (Vite) can be set via `.env.local`:

- VITE_API_URL: FastAPI base URL (default `http://localhost:8000`)
- VITE_API_TOKEN: Bearer token sent to API (should match backend `AGENT_SHARED_SECRET` or a dev session token)
- VITE_USER_ROLE: Optional default role (`admin`|`operator`|`viewer`)

Optional: Generate typed API definitions (when backend is running):

```bash
API_URL=http://localhost:8000 npm run generate:api-types
```
