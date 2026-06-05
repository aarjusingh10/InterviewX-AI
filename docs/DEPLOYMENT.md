# Deployment

## Production Checklist

- Set a strong `JWT_SECRET_KEY`.
- Configure managed PostgreSQL with TLS.
- Configure persistent Chroma or a managed vector database.
- Set `GEMINI_API_KEY`.
- Put backend behind HTTPS reverse proxy.
- Restrict CORS to production frontend domain.
- Store uploaded resumes and reports in S3 or GCS.
- Enable observability for API latency, AI cost, error rates, and database health.
- Move report generation and large audio/video processing to async workers for heavy traffic.

## Docker

```bash
docker compose up --build -d
```

## Suggested Cloud Layout

- Frontend: Vercel, Netlify, or Cloudflare Pages
- Backend: Fly.io, Render, ECS, Cloud Run, or Kubernetes
- Database: Neon, Supabase, RDS, or Cloud SQL
- Vector DB: Chroma server, Pinecone, Weaviate, or pgvector
- Object Storage: S3-compatible bucket

