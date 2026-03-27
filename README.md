# Study Planner Website

## Overview

This project is a personal productivity website designed to help me organize:

- GATE DA preparation
- DSA in Python
- College study
- Daily tasks and long-term goals
- Future categories that I may add later

The main purpose of this website is to convert big goals into daily actionable work, track progress over time, and maintain focus with clear deadlines and priorities.

## Problem Statement

I want a website that helps me decide:

- what I should study today
- which goals are most important
- how many days are left for each target
- whether I am making consistent progress

Instead of keeping everything in scattered notes, I want one place where I can manage preparation, study planning, and execution.

## Goals

- Create daily study plans
- Track short-term and long-term goals
- Organize tasks by category
- Monitor progress with deadlines
- Build a system that is simple now and expandable later

## Target Users

Primary user:

- Me

Future possibility:

- Students preparing for competitive exams while also managing college work

## Core Features

### 1. Dashboard

A central dashboard showing:

- today's tasks
- upcoming deadlines
- active goals
- progress summary
- completed tasks

### 2. Goal Management

The user should be able to:

- create goals
- assign a category
- set start date and target date
- break goals into smaller tasks
- mark progress

Example goals:

- Complete GATE DA probability revision
- Practice 100 DSA questions in Python
- Finish college assignment before deadline

### 3. Daily Task Planner

The website should allow:

- adding tasks for each day
- setting task priority
- linking tasks to a larger goal
- marking tasks as completed, pending, or postponed

Example daily tasks:

- Solve 3 array problems
- Revise linear algebra notes
- Complete college lab record

### 4. Category-Based Planning

Initial categories:

- GATE DA
- DSA in Python
- College Study

Future categories can be added later, such as:

- Aptitude
- Projects
- Placement Preparation
- Revision

### 5. Progress Tracking

The website should show:

- daily completion rate
- weekly consistency
- percentage progress per goal
- overdue tasks
- streaks or study consistency

### 6. Calendar and Deadline View

Useful for:

- viewing tasks by date
- checking upcoming exams or submissions
- planning workload in advance

### 7. Notes Section

Optional feature:

- quick notes for study topics
- reminders
- important formulas
- revision points

## Suggested Pages

- Home / Dashboard
- Goals Page
- Daily Tasks Page
- Calendar Page
- Progress Page
- Notes Page
- Settings Page

## Suggested Tech Stack

### Frontend

- HTML
- CSS
- JavaScript

or

- React for a more scalable frontend

### Backend

- Python
- Flask or Django

### Database

- SQLite for starting simple

Later upgrade options:

- PostgreSQL
- Firebase

## Suggested Data Model

### Goal

- `id`
- `title`
- `category`
- `description`
- `start_date`
- `target_date`
- `status`
- `progress`

### Task

- `id`
- `goal_id`
- `title`
- `category`
- `due_date`
- `priority`
- `status`
- `estimated_time`

### Category

- `id`
- `name`

### Note

- `id`
- `title`
- `content`
- `created_at`

## Minimum Viable Product

For the first version, the website should support:

- adding goals
- adding daily tasks
- selecting category
- setting target dates
- marking tasks complete
- viewing progress in a simple dashboard

This will keep the project focused and easier to build.

## Future Enhancements

- login and user authentication
- reminders and notifications
- dark mode
- analytics charts
- drag-and-drop task planning
- AI-based study suggestions
- mobile responsive dashboard
- export tasks and reports

## Sample Use Case

If I have a goal:

`Complete GATE DA preparation for Linear Algebra in 10 days`

The website should help me:

- divide the goal into daily tasks
- assign tasks across 10 days
- track daily completion
- show remaining work
- alert me if I fall behind schedule

## Project Vision

This website is not only a task manager. It is a personal study management system that helps me stay disciplined, structured, and consistent across exam preparation and college responsibilities.

## Development Approach

Recommended phases:

1. Design the pages and layout
2. Build task and goal input forms
3. Add local storage or database
4. Show tasks on dashboard
5. Add progress tracking
6. Improve UI and add future features

## Folder Structure Suggestion

```text
study-planner-website/
├── README.md
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── script.js
├── backend/
│   ├── app.py
│   ├── models.py
│   └── database.db
└── assets/
```

## Success Criteria

This project will be successful if it helps me:

- clearly see what to do every day
- connect daily tasks with larger goals
- stay consistent in GATE DA preparation
- improve DSA practice in Python
- balance exam preparation with college studies

## Status

Planning stage. README prepared as the foundation for development.

## Quick Start

```bash
cd Projects/study-planner-website
pip install -r requirements.txt
python app.py
```

Then open:

```text
http://127.0.0.1:5000
```

## Current Implementation

The starter version already includes:

- a Flask backend
- a dashboard page
- goal creation
- daily task creation
- a progress page
- database-backed storage with cloud deployment support
- a responsive UI

## Cloud Access

To open this on any phone and keep your progress synced, deploy the project to a public host.

This project is now prepared for deployment with:

- `gunicorn` for production serving
- `MONGODB_URI` support for MongoDB Atlas
- `Procfile` for simple hosting setups
- `render.yaml` for Render deployment

### Deploy on Render with MongoDB Atlas

1. Create a free MongoDB Atlas cluster
2. Get your connection string
3. Push this project to GitHub
4. Create a Render web service from the repo
5. Set:

```text
MONGODB_URI=your atlas connection string
MONGODB_DB_NAME=study_planner
```

6. Render will give you a public URL like:

```text
https://your-project-name.onrender.com
```

### MongoDB Atlas Free

MongoDB Atlas offers a free tier for cloud databases.

Typical connection string format:

```text
mongodb+srv://USERNAME:PASSWORD@cluster-name.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0
```

Use that value as `MONGODB_URI`.

### Old Render Blueprint Note

The previous PostgreSQL blueprint setup has been replaced. The app now targets MongoDB instead of SQL storage.

### Custom Domain

If you buy your own domain, you can connect it after deployment.

Examples:

- `studywithjay.com`
- `planner.yourdomain.com`

Then you can open the same progress from any phone using that domain.
