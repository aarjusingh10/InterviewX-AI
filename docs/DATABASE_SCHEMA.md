# Database Schema

## users

- `id`: primary key
- `email`: unique login identity
- `full_name`
- `password_hash`: nullable for Google accounts
- `avatar_url`
- `provider`: `email` or `google`
- `created_at`

## password_reset_tokens

- `id`
- `user_id`
- `token_hash`
- `expires_at`
- `used_at`

## resumes

- `id`
- `user_id`
- `filename`
- `text`
- `parsed`: name, skills, projects, experience, education, certifications
- `scores`: ATS, resume strength, internship readiness, industry readiness, detections
- `suggestions`
- `created_at`

## interviews

- `id`
- `user_id`
- `resume_id`
- `role`
- `difficulty`
- `personality`
- `status`
- `questions`
- `transcript`
- `scores`
- `weaknesses`
- `roadmap`
- `premium`: hiring probability, salary prediction, skill ranking, confidence, eye contact, body language
- `created_at`
- `completed_at`

## reports

- `id`
- `interview_id`
- `user_id`
- `file_path`
- `created_at`

