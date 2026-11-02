# SingularJobs

A job recommendation web app for students that works from a plain-English
description of your skills and interests, instead of keyword search.

## The idea

Job search breaks down when titles are bloated, skill names are written a
dozen different ways, and descriptions are vague — keyword matching returns
noise. SingularJobs normalizes what a user actually means and recommends
roles from that, rather than matching strings literally.

## How it works

The core is a skill entity-matching pipeline (`user/entity_matching.py`):

- **Abbreviation expansion** — maps short forms to canonical skill names.
- **Fuzzy matching** — a normalized edit-distance ratio matches free-text
  skills against a curated skill taxonomy, so variants like "react", "react.js"
  and "reactjs" resolve to the same skill.
- **Grouping** — matched skills roll up to parent skills/groups.
- **Concurrency** — skills are resolved in parallel via a thread pool.

The resolved profile is then used to surface relevant job listings.

## Architecture

- **This repo** — the Django web app (registration, login, profile, job feed, FAQ).
- **singularjobsapi** — a separate API backend for user accounts/auth.
- **singularjobs_skills_file_csv** — the skill taxonomy (CSV skill bases,
  abbreviations, and group-parent mappings) consumed by the matcher.

## Tech

Python · Django 3.2 · MongoDB (via djongo / pymongo) · gunicorn · WhiteNoise ·
deployed on Heroku

## Status

College project (2021–2022). Part of a series of natural-language
recommendation engines — see also Singular-News.

## Demo

Intro video: https://www.youtube.com/watch?v=1rS7ZXl-saY