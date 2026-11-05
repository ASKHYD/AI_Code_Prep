# Product

<!-- impeccable:product-schema 1 -->

## Platform
web

## Stack
Streamlit 1.66.1 (Python 3.12)

## Users
Software engineers and computer science students preparing for technical coding interviews.

## Product Purpose
A local, zero-cost coding interview coach. The judge is code (sandboxed execution against hidden tests), not AI. Provides spaced repetition, real-time mock interviews with countdown timers, offline lint/hints, and performance analytics.

## Positioning
Code is the judge, not AI. Runs 100% locally with zero paid API keys, zero cloud dependencies, and instant sandboxed test execution.

## Operating Context
Local desktop web interface run via Streamlit on localhost. Supports both offline study and local Ollama-augmented hint generation when available.

## Capabilities and Constraints
- 12 built-in curated coding problems across Strings, Arrays, Trees, Dynamic Programming, Graphs.
- Sandboxed execution (3-second timeout, memory & network isolation).
- Spaced repetition scheduling based on review intervals.
- Mock interview countdown timer (45 minutes) with real-time UI fragment updates.
- Zero paid APIs, no LeetCode scraping, clean production database isolation.

## Brand Commitments
- Name: AI Coding Prep Coach
- Voice: Technical, focused, calm, distraction-free developer workbench.
- Aesthetics: Dark Mode (OLED), quiet panels, aligned figures, color spent only on data and state.

## Evidence on Hand
- Test suite: 26 passed tests in pytest.
- Clean database store (`coach.db`) with verified streak and repetition metrics.

## Product Principles
1. Code is the judge, never an LLM.
2. Quiet panels, aligned figures, color spent on data and pass/fail state.
3. Zero cost, zero latency, 100% privacy and local control.
