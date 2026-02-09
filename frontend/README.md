# Frontend

React + TypeScript (Vite) frontend for the t2ai MVP.

## Requirements
- Node.js LTS

## Run (dev)
```bash
npm install
npm run dev
```

## Routes
- `/` : Home
- `/phase1` : Phase1 (Goal setting scaffold)
- `/phase3` : Phase3 (Daily review scaffold)

## Backend health check
The Home page calls `GET http://localhost:8000/health` and shows the status.

If the backend is unavailable, an error banner is displayed instead of only logging to console.

## Acceptance checks
1. Install dependencies and start the dev server.
2. Open `http://localhost:5173` and verify `Frontend OK` is displayed.
3. Navigate to `/phase1` and `/phase3` using the AppBar links.
4. Confirm the Home page shows `Backend health: ok` when the backend is running.
5. Stop the backend to see the error banner on the Home page.
