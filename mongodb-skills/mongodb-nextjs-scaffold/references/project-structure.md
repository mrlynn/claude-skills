# Project Structure Reference

Full directory tree for a scaffolded Next.js + MongoDB DevRel project. Every file and directory is listed with its purpose.

## Root Directory

```
project-root/
├── .env.local                  # Environment variables (never committed)
├── .eslintrc.json              # ESLint configuration
├── .gitignore                  # Git ignore rules
├── next.config.ts              # Next.js configuration (webpack, env, redirects)
├── package.json                # Dependencies and scripts
├── tsconfig.json               # TypeScript compiler options (paths: @/ -> src/)
├── public/                     # Static assets served at /
│   ├── favicon.ico
│   ├── logo.svg                # MongoDB-branded logo
│   └── images/                 # Static images (backgrounds, placeholders)
└── src/                        # All application source code
```

## src/ Directory

### App Router (`src/app/`)

```
src/app/
├── layout.tsx                  # Root layout: <html>, <body>, font imports
├── globals.css                 # Global CSS resets (minimal, most styling via MUI)
├── (app)/                      # Route group for authenticated app shell
│   ├── layout.tsx              # App layout: ThemeRegistry + SessionProvider wrapper
│   ├── page.tsx                # Home / landing page
│   ├── dashboard/
│   │   └── page.tsx            # User dashboard (role-aware content)
│   ├── events/
│   │   ├── page.tsx            # Public event listing
│   │   └── [eventId]/
│   │       └── page.tsx        # Event detail page
│   ├── projects/
│   │   └── page.tsx            # Project gallery
│   ├── profile/
│   │   └── page.tsx            # User profile editor
│   ├── settings/
│   │   └── page.tsx            # Account settings (password, 2FA, notifications)
│   ├── admin/
│   │   ├── layout.tsx          # Admin layout: requireAdminPanel() guard + sidebar
│   │   ├── page.tsx            # Admin dashboard with stats
│   │   ├── events/
│   │   │   ├── page.tsx        # Event management list
│   │   │   └── [eventId]/
│   │   │       └── page.tsx    # Event detail admin view
│   │   ├── users/
│   │   │   └── page.tsx        # User management
│   │   ├── partners/
│   │   │   └── page.tsx        # Partner management
│   │   ├── templates/
│   │   │   └── page.tsx        # Judging rubric templates
│   │   ├── email-templates/
│   │   │   └── page.tsx        # Email template editor
│   │   ├── feedback/
│   │   │   └── page.tsx        # Feedback form builder
│   │   ├── rag/
│   │   │   └── page.tsx        # RAG ingestion dashboard
│   │   └── settings/
│   │       └── page.tsx        # Site-wide settings
│   ├── judging/
│   │   └── [eventId]/
│   │       └── page.tsx        # Judge scoring interface
│   └── partner/
│       ├── page.tsx            # Partner portal dashboard
│       └── register/
│           └── page.tsx        # Partner access request (public)
├── api/                        # API route handlers
│   ├── auth/
│   │   └── [...nextauth]/
│   │       └── route.ts        # NextAuth catch-all handler (GET + POST)
│   ├── admin/
│   │   ├── events/
│   │   │   ├── route.ts        # GET (list), POST (create)
│   │   │   └── [eventId]/
│   │   │       ├── route.ts    # GET, PATCH, DELETE
│   │   │       ├── assignments/route.ts       # Judge assignments
│   │   │       ├── atlas-provisioning/route.ts # Cluster config
│   │   │       ├── feedback-forms/route.ts    # Link forms to event
│   │   │       ├── feedback-responses/route.ts # Get submissions
│   │   │       ├── results/route.ts           # Final rankings
│   │   │       └── send-feedback/route.ts     # Trigger feedback emails
│   │   ├── users/
│   │   │   ├── route.ts        # GET (list), POST (create)
│   │   │   └── [userId]/
│   │   │       ├── route.ts    # GET, PATCH, DELETE
│   │   │       ├── ban/route.ts    # POST (ban/unban)
│   │   │       └── role/route.ts   # PATCH (change role)
│   │   ├── email-templates/
│   │   │   ├── route.ts        # GET (list), POST (create)
│   │   │   └── [id]/
│   │   │       ├── route.ts    # GET, PATCH, DELETE
│   │   │       ├── preview/route.ts   # POST (render preview)
│   │   │       └── test-send/route.ts # POST (send test email)
│   │   ├── templates/
│   │   │   ├── route.ts        # Judging rubric templates CRUD
│   │   │   └── [id]/
│   │   │       ├── route.ts
│   │   │       └── clone/route.ts
│   │   ├── feedback-forms/
│   │   │   ├── route.ts
│   │   │   └── [id]/
│   │   │       ├── route.ts
│   │   │       └── clone/route.ts
│   │   ├── teams/route.ts      # Team management
│   │   ├── projects/
│   │   │   └── [projectId]/
│   │   │       └── featured/route.ts  # Toggle featured
│   │   ├── site-settings/route.ts     # Global config
│   │   └── rag/
│   │       ├── status/route.ts        # Ingestion status
│   │       ├── ingest/route.ts        # Trigger ingestion
│   │       ├── cancel/route.ts        # Cancel running ingestion
│   │       ├── documents/route.ts     # Browse indexed docs
│   │       ├── files/route.ts         # List source files
│   │       └── runs/
│   │           ├── route.ts           # List ingestion runs
│   │           └── [runId]/route.ts   # Run details
│   ├── events/
│   │   └── [eventId]/
│   │       └── register/route.ts      # Public registration endpoint
│   ├── gallery/route.ts               # Public project gallery
│   ├── judging/
│   │   └── [eventId]/
│   │       ├── projects/route.ts      # Projects assigned to judge
│   │       └── score/route.ts         # Submit scores
│   ├── settings/
│   │   ├── password/route.ts          # Change password
│   │   ├── 2fa/route.ts              # Enable/disable 2FA
│   │   └── notifications/route.ts     # Notification preferences
│   └── health/
│       └── route.ts                   # Health check endpoint
└── login/
    └── page.tsx                # Login page (credentials + magic link)
```

### Components (`src/components/`)

```
src/components/
└── shared-ui/
    └── ThemeRegistry.tsx       # Emotion SSR cache + MUI ThemeProvider + CssBaseline
```

Additional components are added per feature. The `shared-ui/` directory holds cross-cutting UI components that don't belong to a specific feature.

### Library (`src/lib/`)

```
src/lib/
├── auth.ts                     # NextAuth v5 config (providers, callbacks, pages)
├── admin-guard.ts              # Role groups + server-side guard functions
├── utils.ts                    # errorResponse(), successResponse(), formatDate()
├── logger.ts                   # Structured logging utility
├── db/
│   ├── connection.ts           # Singleton Mongoose connection with global cache
│   ├── schemas.ts              # All Zod validation schemas (create/update pairs)
│   └── models/
│       ├── User.ts             # IUser interface + UserModel (8-role enum)
│       ├── Event.ts            # IEvent interface + EventModel (lifecycle states)
│       ├── Partner.ts          # IPartner interface + PartnerModel (5 tiers)
│       ├── Team.ts             # ITeam interface + TeamModel
│       ├── Project.ts          # IProject interface + ProjectModel
│       ├── Participant.ts      # IParticipant interface (event-user junction)
│       ├── Score.ts            # IScore interface (judge scores)
│       ├── Notification.ts     # INotification interface
│       ├── EmailTemplate.ts    # IEmailTemplate interface (DB-backed templates)
│       ├── FeedbackFormConfig.ts    # Dynamic feedback form schemas
│       ├── FeedbackResponse.ts      # Submitted feedback data
│       ├── RegistrationFormConfig.ts # 3-tier registration config
│       ├── AtlasCluster.ts     # IAtlasCluster (provisioned clusters)
│       ├── AiUsageLog.ts       # AI usage tracking
│       ├── RagDocument.ts      # RAG document chunks + embeddings
│       ├── RagIngestionRun.ts  # Ingestion run tracking
│       ├── RagConversation.ts  # Chat session history
│       └── SiteSettings.ts     # Global site configuration
├── email/
│   ├── email-service.ts        # SMTP singleton + sendEmail()
│   ├── template-renderer.ts    # DB lookup + interpolation + fallback
│   ├── templates.ts            # Hardcoded fallback email templates
│   └── seed-email-templates.ts # Upsert built-in templates to DB
├── atlas/
│   ├── atlas-client.ts         # HTTP Digest auth + Atlas Admin API v2 CRUD
│   ├── provisioning-service.ts # 9-step orchestration with rollback
│   ├── status-service.ts       # Poll cluster status
│   ├── utils.ts                # Password gen, name sanitization, attribution
│   └── auth-guard.ts           # Team leader/member verification
├── ai/
│   ├── usage-logger.ts         # Fire-and-forget AI cost tracking
│   ├── summary-service.ts      # OpenAI summarization
│   ├── feedback-service.ts     # Multi-source feedback synthesis
│   ├── project-suggestion.ts   # Structured idea generation
│   └── embedding-service.ts    # OpenAI embeddings (non-RAG uses)
└── rag/
    ├── types.ts                # IRagDocument, ChatMessage interfaces
    ├── embeddings.ts           # Voyage AI embeddings (document + query)
    ├── ingestion.ts            # Markdown -> chunks -> embeddings pipeline
    ├── chunker.ts              # Document parsing and chunking
    ├── retrieval.ts            # $vectorSearch + category boosting
    ├── chat.ts                 # Streaming chat with context injection
    └── rate-limit.ts           # Request throttling
```

### Other Source Directories

```
src/styles/
└── theme.ts                    # MongoDB brand theme (mongoBrand tokens + hackathonTheme)

src/types/
└── next-auth.d.ts              # NextAuth module augmentation (role, partnerId, impersonation)

src/contexts/                   # React context providers (added as needed)
```

## Configuration Files

### .env.local

```bash
# Database
MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/dbname

# Auth
AUTH_SECRET=random-string-min-32-characters
NEXTAUTH_URL=http://localhost:3000

# Email (optional)
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASS=your-api-key
EMAIL_FROM="App Name <noreply@yourdomain.com>"

# Atlas Provisioning (optional)
ATLAS_PUBLIC_KEY=your-public-key
ATLAS_PRIVATE_KEY=your-private-key
ATLAS_ORG_ID=your-org-id

# AI (optional)
OPENAI_API_KEY=sk-...
VOYAGE_API_KEY=pa-...
```

### next.config.ts

Key settings: `serverExternalPackages: ['mongoose']` to prevent Mongoose from being bundled into edge functions.

### tsconfig.json

Key settings: `paths: { "@/*": ["./src/*"] }` for clean imports.

### package.json

Core dependencies: `next`, `react`, `react-dom`, `mongoose`, `next-auth@beta`, `zod`, `@mui/material`, `@emotion/react`, `@emotion/cache`, `@emotion/styled`, `nodemailer`, `bcryptjs`, `openai`, `digest-fetch`.
