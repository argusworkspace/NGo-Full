# NGO — Next.js Frontend

Modular monolith frontend for the NGO Platform built with **Next.js 15**, **shadcn/ui**, **Tailwind CSS**, and **TypeScript**.

---

## Tech Stack

| Layer | Library |
|---|---|
| Framework | Next.js 15 (App Router) |
| UI Components | shadcn/ui (Radix UI primitives) |
| Styling | Tailwind CSS v3 |
| Forms | React Hook Form + Zod |
| HTTP Client | Axios |
| Notifications | Sonner |
| Theme | next-themes |

---

## Folder Structure

```
src/
├── app/                        # Next.js App Router pages
│   ├── (auth)/
│   │   ├── login/page.tsx
│   │   └── register/page.tsx
│   ├── (dashboard)/
│   │   └── dashboard/page.tsx
│   ├── layout.tsx
│   ├── page.tsx
│   └── globals.css
│
├── modules/                    # Modular monolith — each module is self-contained
│   ├── auth/
│   │   ├── api/               # API calls scoped to this module
│   │   ├── components/        # UI components scoped to this module
│   │   ├── hooks/             # React hooks scoped to this module
│   │   ├── types/             # TypeScript types
│   │   └── index.ts           # Barrel export
│   ├── donors/
│   │   ├── api/
│   │   ├── components/
│   │   ├── hooks/
│   │   ├── types/
│   │   └── index.ts
│   ├── programs/
│   │   ├── api/
│   │   ├── components/
│   │   ├── hooks/
│   │   ├── types/
│   │   └── index.ts
│   └── volunteers/
│       ├── api/
│       ├── components/
│       ├── hooks/
│       ├── types/
│       └── index.ts
│
├── shared/                    # Cross-module shared code
│   ├── components/
│   │   ├── ui/               # shadcn/ui components (button, card, input…)
│   │   └── theme-provider.tsx
│   ├── hooks/                 # Global hooks
│   ├── lib/
│   │   ├── api-client.ts     # Axios instance (base URL, auth interceptor)
│   │   └── utils.ts          # cn() and other helpers
│   └── types/
│       └── api.ts            # ApiResponse, PaginatedResponse generics
│
└── config/
    └── env.ts                 # Typed env vars
```

### Modular Monolith Rules

- **A module never imports from another module directly.** Cross-module data flows through the API or shared layer.
- **`shared/`** is the only cross-module dependency.
- **Add a new module** by creating `src/modules/<name>/{api,components,hooks,types,index.ts}`.

---

## Getting Started

```bash
# 1. Install dependencies
npm install

# 2. Copy env and configure
cp .env.local.example .env.local
# Set NEXT_PUBLIC_API_URL=http://localhost:8000

# 3. Run dev server
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

---

## shadcn/ui

Components live in `src/shared/components/ui/`. Add new ones with:

```bash
npx shadcn-ui@latest add <component>
```

The `components.json` config maps all aliases correctly.

---

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `NEXT_PUBLIC_API_URL` | `http://localhost:8000` | FastAPI backend URL |
| `NEXT_PUBLIC_APP_URL` | `http://localhost:3000` | Frontend URL |

---

## Branch Strategy

- `main` — production-ready releases
- `dev` — integration branch; all features merge here first
- Feature branches cut from `dev`: `feat/<name>`, `fix/<name>`, `chore/<name>`
