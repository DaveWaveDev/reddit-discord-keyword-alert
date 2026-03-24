# Reddit Discord Keyword Alert

Personal, non-commercial, read-only Reddit alert bot.

## Purpose

This project monitors a small list of public subreddits for new posts that match a small set of keywords, then sends a minimal notification to a private Discord channel that I control.

The goal is to help me discover relevant discussions and return to Reddit to read or participate manually on the platform.

## Intended Use

This bot is intended for personal use only.

Initial subreddit scope:

- r/Anthropic
- r/vibecoding
- r/OpenAI

Initial keyword examples:

- Claude Code
- Claude
- Anthropic
- OpenAI
- vibe coding

## How It Works

1. Authenticate to Reddit using the official OAuth API.
2. Check a small configured list of public subreddits for new submissions.
3. Compare post titles against a configured keyword list.
4. If a match is found, send a message to a private Discord channel.
5. The Discord message contains only minimal metadata and a Reddit permalink.

## Example Alert

```text
Keyword match found
Subreddit: r/Anthropic
Keyword: Claude Code
Post: https://reddit.com/...
