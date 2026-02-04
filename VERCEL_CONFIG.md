# Vercel Deployment Configuration

This document outlines the Vercel deployment configuration for the somm.dev project.

## Project Structure

```
somm.dev/
├── frontend/          # Next.js 16 application (deployed to Vercel)
├── backend/           # Python FastAPI (separate deployment)
└── ...
```

## Vercel Dashboard Settings

### 1. Root Directory Configuration

**IMPORTANT:** Since the Next.js app is in the `frontend/` subdirectory, you must configure the Root Directory in Vercel Dashboard:

1. Go to [Vercel Dashboard](https://vercel.com/2weeks-team/somm-dev/settings)
2. Navigate to **Build & Deployment** → **Root Directory**
3. Set Root Directory to: `frontend`
4. Click **Save**

### 2. Framework Preset

- **Framework Preset:** Next.js (automatically detected)
- **Build Command:** `next build` (default)
- **Output Directory:** `.next` (default)
- **Install Command:** `npm install` (default)
- **Development Command:** `next dev --port $PORT`

### 3. Node.js Version

Set in Vercel Dashboard → **General** → **Node.js Version**:
- **Version:** 22.x (or higher, matching Next.js 16 requirements)

### 4. Environment Variables

Configure in Vercel Dashboard → **Environment Variables**:

```
NEXT_PUBLIC_API_URL=https://your-backend-url.com
```

## Configuration Files

### vercel.json

Located at `frontend/vercel.json`:

- Framework preset: Next.js
- Regions: Tokyo (`hnd1`)
- Security headers configured
- Image optimization settings
- Function timeout: 10s

### next.config.ts

Located at `frontend/next.config.ts`:

- React Strict Mode enabled
- Typed routes (experimental)
- Image optimization (WebP, AVIF)
- Compression enabled
- Custom headers for security

## Deployment Commands

### Local Development

```bash
cd frontend
npm run dev
```

### Deploy to Vercel

```bash
# From repository root (requires root directory configured in dashboard)
vercel

# Or specify frontend directory
vercel frontend

# Production deployment
vercel --prod
```

## Build Settings

| Setting | Value | Location |
|---------|-------|----------|
| Framework | Next.js | vercel.json |
| Build Command | `next build` | vercel.json |
| Install Command | `npm install` | vercel.json |
| Dev Command | `next dev --port $PORT` | vercel.json |
| Output Directory | `.next` | Default |
| Root Directory | `frontend` | Dashboard |
| Node.js Version | 22.x | Dashboard |

## Regions

- **Primary Region:** Tokyo (`hnd1`) - Best for Korean/Japanese users

## Security Headers

Configured in `vercel.json`:

- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`
- `Referrer-Policy: strict-origin-when-cross-origin`
- Static assets cached for 1 year
- API routes use `must-revalidate`

## Learn More

- [Vercel Next.js Documentation](https://vercel.com/docs/frameworks/nextjs)
- [Vercel Project Configuration](https://vercel.com/docs/project-configuration)
- [Next.js on Vercel](https://nextjs.org/docs/deployment)
