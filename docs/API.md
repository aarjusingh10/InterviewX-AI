# API Routes

Base URL: `/api/v1`

## Auth

- `POST /auth/signup`
- `POST /auth/login`
- `POST /auth/google`
- `POST /auth/forgot-password`
- `POST /auth/reset-password`
- `GET /auth/me`

## Resumes

- `POST /resumes/upload`
- `GET /resumes`
- `GET /resumes/{resume_id}`

## Interviews

- `POST /interviews/generate`
- `GET /interviews`
- `GET /interviews/{interview_id}`
- `POST /interviews/{interview_id}/answer`
- `POST /interviews/{interview_id}/complete`
- `POST /interviews/{interview_id}/transcribe`

## Analytics

- `GET /analytics/overview`
- `GET /analytics/interviews/{interview_id}`

## Reports

- `POST /reports/{interview_id}`
- `GET /reports/{report_id}/download`

