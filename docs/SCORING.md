# Scoring Logic

InterviewX AI uses deterministic scoring formulas when an external AI provider is unavailable.

## Interview Score Inputs

- Role keyword coverage
- Measurable evidence such as percentages, counts, revenue, users, or time saved
- Answer depth by word count
- STAR-style structure signals: situation, task, action, result, problem, solution, outcome
- Reasoning signals: because, tradeoff, constraint, risk, alternative, measured
- Leadership signals: led, owned, managed, collaborated, stakeholder, negotiated
- Confidence signal from voice/interview metadata
- Filler-word penalty for vague phrasing
- Difficulty multiplier

## Interview Dimensions

- Technical Knowledge
- Communication
- Confidence
- Clarity
- Problem Solving
- Leadership

The overall score is the weighted average of these dimensions after applying the difficulty multiplier.

## Resume Score Inputs

- Section coverage
- Keyword density
- Quantified impact
- Contact/link signals
- Bullet count
- Project depth
- Action verbs
- Weak-language penalty
- File quality signal in hosted demo mode

## Why Scores Change

Two candidates with different answers should receive different scores because the formula reacts to:

- Specific role vocabulary
- Use of numbers and proof
- Stronger examples
- Clearer decision reasoning
- Less vague language
- Better structure

