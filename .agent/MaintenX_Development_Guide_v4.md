# MaintenX -- Project Development Guide

## 1. Project Overview

**MaintenX** is a web-based **Maintenance Management System for
Organizations**.

It replaces unorganized maintenance communication such as verbal
complaints, phone calls, WhatsApp messages, paper registers, and direct
communication with maintenance staff with a centralized digital
workflow.

**Core workflow:**

`Problem → Digital Request → Review → Assignment → Work → Resolution → Closure → History`

### One-line project definition

> MaintenX is a web-based maintenance management system that allows
> users in an organization to report maintenance problems digitally and
> enables administrators and maintenance staff to assign, track, update,
> and resolve those problems efficiently.

### Target organizations

-   Companies and offices
-   Hospitals
-   Hotels
-   Factories
-   Schools and colleges
-   Apartment complexes
-   Government buildings
-   Shopping malls
-   Other facilities

------------------------------------------------------------------------

# 2. Problem Statement

Traditional maintenance requests are often handled through informal
communication. This causes:

-   Complaints being forgotten or lost
-   No centralized record
-   Difficult status tracking
-   Manual assignment
-   Poor accountability
-   No reliable maintenance history
-   Difficult reporting
-   Repeated follow-up by users

MaintenX creates a permanent digital record for every maintenance
request and tracks it through its complete lifecycle.

------------------------------------------------------------------------

# 3. Project Objectives

1.  Centralize maintenance requests.
2.  Allow users to report problems digitally.
3.  Record every request permanently.
4.  Allow administrators to review and assign requests.
5.  Allow maintenance staff to manage assigned work.
6.  Allow users to track request status.
7.  Support priority-based maintenance.
8.  Maintain a complete request history.
9.  Improve accountability.
10. Provide dashboards and statistics.
11. Reduce lost or forgotten complaints.
12. Make maintenance operations easier to monitor.

------------------------------------------------------------------------

# 4. User Roles

## 4.1 User / Employee

A normal organization member who reports and tracks maintenance problems.

### User Pages

The User module consists of the following main pages:

1. **Dashboard**
2. **My Requests**
3. **Add Request**
4. **Requests**
5. **Profile**

The user module is designed around two main purposes:

- Reporting maintenance problems.
- Viewing and tracking maintenance activity.

---

## 4.1.1 User Dashboard

**Route:** `/user/dashboard`

The Dashboard provides a quick overview of maintenance requests relevant to the user.

It should contain sections/cards for:

- **All Requests**
- **Requests on Hold**
- **Approved Requests**
- **Solved/Rectified Requests**

Example:

```text
MaintenX Dashboard

┌────────────────┐ ┌────────────────┐
│ ALL REQUESTS   │ │ ON HOLD        │
│      25        │ │       4        │
└────────────────┘ └────────────────┘

┌────────────────┐ ┌────────────────┐
│ APPROVED       │ │ SOLVED         │
│      12        │ │       9        │
└────────────────┘ └────────────────┘

Recent Request Activity
────────────────────────────────────
Request #104   Plumbing    Approved
Request #103   Electrical  On Work
Request #102   Furniture   Rectified
```

### Dashboard purpose

The Dashboard gives the user a quick status overview without requiring them to open every request.

The exact definition of the Dashboard sections can be adjusted during implementation depending on whether "All Requests" means all requests in the organization or all requests visible to the logged-in user. The current design should keep this distinction clear from **My Requests**.

---

## 4.1.2 My Requests

**Route:** `/user/my-requests`

This page contains the maintenance requests **submitted by the currently logged-in user**.

Each request should show its current stage clearly.

### Request confirmation/status flow

For the user interface, use the following terminology:

```text
REQUESTED
    ↓
APPROVED
    ↓
ON WORK
    ↓
RECTIFIED
```

The user should be able to immediately understand where their request currently stands.

Example:

```text
My Requests

┌──────────────────────────────────────────────┐
│ Request #104                                │
│ Water leakage near wash basin               │
│ Plumbing                                     │
│                                              │
│ ✓ REQUESTED                                  │
│ ✓ APPROVED                                   │
│ ● ON WORK                                    │
│ ○ RECTIFIED                                  │
└──────────────────────────────────────────────┘
```

Another completed request:

```text
Request #102
Broken chair

✓ REQUESTED
✓ APPROVED
✓ ON WORK
✓ RECTIFIED
```

### Purpose

This page answers:

> "What are the maintenance requests that I have submitted, and what is happening with each one?"

Users should only see requests that they have submitted on this page.

---

## 4.1.3 Add Request

**Route:** `/user/request/new`

This is the page where the user creates a new maintenance request.

### Form

```text
Add Maintenance Request

Title
[____________________________]

Category
[ Plumbing ▼ ]

Location
[____________________________]

Priority
[ Medium ▼ ]

Description
[____________________________
 ____________________________
 ____________________________]

[ Submit Request ]
```

Possible future field:

```text
[ Upload Image ]
```

### Submission workflow

```text
User fills form
       ↓
Clicks Submit
       ↓
Backend validates information
       ↓
Request stored in database
       ↓
Initial status = REQUESTED
       ↓
Request ID generated
       ↓
User redirected to request details
```

After submission, the user should receive confirmation such as:

```text
Request submitted successfully.

Request ID: #104
Status: REQUESTED
```

---

## 4.1.4 Requests

**Route:** `/user/requests`

This page allows the user to see the **maintenance requests in the organization/college**, along with their updates.

Unlike **My Requests**, this page is intended to provide visibility into maintenance activity across the organization.

### Example

```text
All Maintenance Requests

#104  Water leakage
      Plumbing
      2nd Floor – Restroom
      Status: ON WORK

      Updates:
      ✓ Requested
      ✓ Approved
      ● On Work
      ○ Rectified

────────────────────────────────────

#103  AC not working
      HVAC
      Meeting Room
      Status: APPROVED

      Updates:
      ✓ Requested
      ✓ Approved
      ○ On Work
      ○ Rectified
```

### Purpose

The Requests page provides broader visibility into maintenance activity.

It should show:

- Request ID
- Problem/title
- Category
- Location
- Current status
- Relevant updates
- Request timeline

### Privacy consideration

Only information appropriate for organization-wide visibility should be displayed.

Private information such as:

- Passwords
- Private user information
- Internal administrative notes
- Sensitive contact information

must never be exposed.

---

## 4.1.5 Review & Feedback

**Route:** `/user/feedback`

This page allows users to communicate with the administrator about the MaintenX application.

Users can submit three types of entries:

1. **Review** – General opinion about the application.
2. **Feedback** – Suggestions, complaints, or ideas for improvement.
3. **Bug Report** – A technical problem or error found while using the application.

### Example

```text
Review & Feedback

Type
[ Review ▼ ]

Subject
[____________________________]

Message
[____________________________
 ____________________________]

Rating
☆ ☆ ☆ ☆ ☆

[ Submit ]
```

For a bug report:

```text
Type
[ Bug Report ▼ ]

Subject
[____________________________]

Page / Feature
[____________________________]

Expected Behaviour
[____________________________]

Actual Behaviour
[____________________________]

Description
[____________________________
 ____________________________]

[ Submit Bug Report ]
```

### Submission workflow

```text
User opens Review & Feedback
          ↓
Selects Review / Feedback / Bug Report
          ↓
Enters details
          ↓
Backend validates input
          ↓
Submission stored in database
          ↓
Administrator can view it
          ↓
Admin reviews / responds / resolves if required
```

### Review

A review can contain:

- Rating from 1–5
- Review title
- Review message
- Submission date

### Feedback

A feedback entry can contain:

- Subject
- Description
- Suggested improvement
- Submission date

### Bug Report

A bug report should contain:

- Bug title
- Description
- Page/feature
- Expected behaviour
- Actual behaviour
- Optional screenshot/attachment
- Submission date

### Important rule

Users can submit reviews, feedback, and bug reports. Only administrators should manage, respond to, or change the status of these submissions.

---

## 4.1.6 Profile

**Route:** `/user/profile`

The Profile page contains the logged-in user's account information.

Example:

```text
My Profile

Name
Abhijith

Email
example@email.com

Phone
XXXXXXXXXX

Department
IT

Role
Employee

[ Update Profile ]
```

Possible actions:

- Update name
- Update phone
- Update department
- Change password
- View account information

---

## 4.1.6 User Navigation

The main user navigation should be:

```text
┌─────────────────────────────────────────────────────────────┐
│ MaintenX                                                    │
│                                                             │
│ Dashboard | My Requests | Add Request | Requests | Profile │
│                                                             │
│ Logout                                                       │
└─────────────────────────────────────────────────────────────┘
```

### User navigation structure

```text
USER
│
├── Dashboard
│   ├── All Requests
│   ├── On Hold
│   ├── Approved
│   └── Solved / Rectified
│
├── My Requests
│   └── Requests submitted by current user
│       └── Requested → Approved → On Work → Rectified
│
├── Add Request
│   └── Create new maintenance request
│
├── Requests
│   └── Organization/college maintenance requests
│       └── View updates and current status
│
└── Profile
    └── View / update personal information
```

---

## 4.1.7 User Request Status Terminology

The user-facing status terminology should be:

| Status | Meaning |
|---|---|
| **Requested** | User has submitted the maintenance request |
| **Approved** | Administrator/authorized person has approved the request |
| **On Work** | Maintenance staff is currently working on the problem |
| **Rectified** | The reported problem has been repaired/fixed |

### Internal status mapping

If the backend needs more detailed states, internal database statuses can be mapped to these user-facing labels.

For example:

```text
PENDING       → REQUESTED
ASSIGNED      → APPROVED
IN_PROGRESS   → ON WORK
RESOLVED      → RECTIFIED
```

If the project later requires a separate `CLOSED` state, it can remain an internal/admin state after `RECTIFIED`.

---

## 4.2 Maintenance Staff

A person responsible for handling maintenance work.

Examples:

- Electrician
- Plumber
- HVAC/AC technician
- Carpenter
- Network technician
- General maintenance worker

### Can

- Login/logout
- View assigned requests
- View request details
- Start assigned work
- Add work notes
- Update progress
- Mark work as rectified/resolved
- View relevant request history

### Cannot

- Assign requests
- Manage users
- Change roles
- Access unrestricted admin functions
- Modify requests assigned to other staff

---

## 4.3 Administrator / Maintenance Manager

Controls the maintenance workflow.

### Can

- Login/logout
- View all requests
- Review requests
- Approve requests
- Assign staff
- Change priority
- Manage users
- Manage staff
- Manage categories
- Monitor pending/on-hold requests
- View dashboards
- View statistics
- View history
- Generate reports
- View user reviews and feedback
- View and manage bug reports
- Respond to user feedback
- Track feedback/bug-report status
- Close/complete requests where required


# 5. Main Features

## Authentication

-   Registration
-   Login
-   Logout
-   Password hashing
-   Session management
-   Role-based authorization

## Maintenance Request Management

Each request contains:

-   Request ID
-   User
-   Category
-   Location
-   Title
-   Description
-   Priority
-   Status
-   Assigned staff
-   Created time
-   Updated time
-   Resolution time
-   Closure time

## Priority

-   Low
-   Medium
-   High
-   Critical

## Status

`REQUESTED → APPROVED → ON WORK → RECTIFIED → CLOSED`

## Request History

Records:

-   Who performed an action
-   What changed
-   Previous status
-   New status
-   Work note
-   Timestamp

## Dashboard

### User

-   Total requests
-   Pending
-   In progress
-   Resolved
-   Closed
-   Recent requests

### Staff

-   Assigned requests
-   In-progress requests
-   Resolved requests
-   High-priority work

### Admin

-   Total requests
-   Pending
-   Assigned
-   In progress
-   Resolved
-   Closed
-   Critical requests
-   Requests by category
-   Requests by priority
-   Staff workload
-   Recent requests

## Search and Filtering

Future/extended functionality:

-   Request ID
-   Title
-   Status
-   Priority
-   Category
-   Assigned staff
-   Date
-   Sorting

## Reports

Possible statistics:

-   Requests by category
-   Requests by priority
-   Requests by status
-   Staff workload
-   Monthly request count
-   Average resolution time

------------------------------------------------------------------------

# 6. Complete Request Workflow

``` text
User identifies problem
        ↓
User creates maintenance request
        ↓
System validates and stores request
        ↓
Status = PENDING
        ↓
Administrator reviews request
        ↓
Administrator assigns staff
        ↓
Status = ASSIGNED
        ↓
Staff starts work
        ↓
Status = IN_PROGRESS
        ↓
Staff repairs problem
        ↓
Staff adds resolution note
        ↓
Status = RESOLVED
        ↓
Administrator verifies
        ↓
Status = CLOSED
        ↓
Request remains in maintenance history
```

------------------------------------------------------------------------

# 7. Status Rules

  Current       Action                       Next
  ------------- ---------------------------- -------------
  New           Create request               PENDING
  PENDING       Admin assigns staff          ASSIGNED
  ASSIGNED      Assigned staff starts work   IN_PROGRESS
  IN_PROGRESS   Staff resolves issue         RESOLVED
  RESOLVED      Admin closes request         CLOSED

Every important status change should create a `request_updates` history
record.

------------------------------------------------------------------------

# 8. Real-World Example

An employee finds water leakage in a second-floor restroom.

### User submits

``` text
Title: Water leakage near wash basin
Category: Plumbing
Location: 2nd Floor – Restroom
Priority: High
Description: Continuous water leakage near the wash basin.
```

### System

Creates request #104:

``` text
Status = PENDING
```

### Administrator

Assigns it to a plumber:

``` text
PENDING → ASSIGNED
```

### Plumber

Starts work:

``` text
ASSIGNED → IN_PROGRESS
```

Adds:

``` text
Pipe connection is damaged. Replacement required.
```

### Plumber completes repair

``` text
IN_PROGRESS → RESOLVED
```

Resolution:

``` text
Damaged pipe connection replaced and leakage stopped.
```

### Administrator

Verifies and closes:

``` text
RESOLVED → CLOSED
```

The complete timeline remains stored.

------------------------------------------------------------------------

# 9. Existing vs Proposed System

  Existing System                MaintenX
  ------------------------------ ---------------------------------
  Verbal complaints              Digital complaints
  Phone/WhatsApp communication   Centralized platform
  Complaints can be forgotten    Every request recorded
  Difficult tracking             Status tracking
  Manual assignment              System-based assignment
  No proper history              Complete maintenance history
  Weak accountability            Assigned staff + action history
  Manual reporting               Dashboard/statistics

------------------------------------------------------------------------

# 10. Recommended Technology Stack

For the current MCA project, use a simple and beginner-friendly stack:

### Frontend

-   HTML
-   CSS
-   JavaScript
-   Bootstrap (optional)

### Backend

-   Python
-   Flask

### Database

-   MySQL

### Authentication

-   Flask sessions
-   Werkzeug password hashing

### Recommended architecture

``` text
HTML + CSS + JavaScript
          ↓
        Flask
          ↓
        MySQL
```

React/Node can be considered later, but they are not required for the
first version.

------------------------------------------------------------------------

# 11. Recommended Flask Structure

``` text
MaintenX/
│
├── app.py
├── config.py
├── requirements.txt
├── README.md
│
├── database/
│   ├── connection.py
│   └── schema.sql
│
├── blueprints/
│   ├── auth/
│   │   ├── __init__.py
│   │   └── routes.py
│   │
│   ├── user/
│   │   ├── __init__.py
│   │   └── routes.py
│   │
│   ├── staff/
│   │   ├── __init__.py
│   │   └── routes.py
│   │
│   └── admin/
│       ├── __init__.py
│       └── routes.py
│
├── templates/
│   ├── base.html
│   ├── auth/
│   │   ├── login.html
│   │   └── register.html
│   ├── user/
│   │   ├── dashboard.html
│   │   ├── create_request.html
│   │   ├── requests.html
│   │   └── request_details.html
│   ├── staff/
│   │   ├── dashboard.html
│   │   ├── assigned_requests.html
│   │   └── request_details.html
│   └── admin/
│       ├── dashboard.html
│       ├── requests.html
│       ├── request_details.html
│       ├── users.html
│       ├── staff.html
│       ├── categories.html
│       └── reports.html
│
└── static/
    ├── css/
    │   └── style.css
    ├── js/
    │   └── script.js
    └── images/
```

The exact structure can change, but authentication, user, staff, and
admin responsibilities should remain separated.

------------------------------------------------------------------------

# 12. Blueprint Responsibilities

## Auth Blueprint

Handles:

-   Registration
-   Login
-   Logout
-   Password verification
-   Session creation

Routes:

``` text
/auth/register
/auth/login
/auth/logout
```

## User Blueprint

Handles:

-   User dashboard
-   Request creation
-   Own requests
-   Request details
-   Profile

## Staff Blueprint

Handles:

-   Staff dashboard
-   Assigned requests
-   Starting work
-   Work notes
-   Resolving requests

## Admin Blueprint

Handles:

-   Admin dashboard
-   All requests
-   Assignment
-   Users
-   Staff
-   Categories
-   Reports

------------------------------------------------------------------------

# 13. Route Guide

## Public/Auth Routes

  Method      Route              Purpose
  ----------- ------------------ -------------------
  GET, POST   `/auth/register`   Register user
  GET, POST   `/auth/login`      Authenticate user
  GET         `/auth/logout`     End session

## User Routes

  Method      Route                  Purpose
  ----------- ---------------------- -------------------
  GET         `/user/dashboard`      User dashboard
  GET, POST   `/user/request/new`    Create request
  GET         `/user/requests`       List own requests
  GET         `/user/request/<id>`   Request details
  GET         `/user/profile`        User profile

## Staff Routes

  Method   Route                           Purpose
  -------- ------------------------------- -------------------
  GET      `/staff/dashboard`              Staff dashboard
  GET      `/staff/requests`               Assigned requests
  GET      `/staff/request/<id>`           Request details
  POST     `/staff/request/<id>/start`     Start work
  POST     `/staff/request/<id>/note`      Add work note
  POST     `/staff/request/<id>/resolve`   Resolve request

## Admin Routes

  Method   Route                            Purpose
  -------- -------------------------------- ------------------------
  GET      `/admin/dashboard`               Admin dashboard
  GET      `/admin/requests`                All requests
  GET      `/admin/request/<id>`            Request details
  POST     `/admin/request/<id>/assign`     Assign staff
  POST     `/admin/request/<id>/priority`   Change priority
  POST     `/admin/request/<id>/close`      Close resolved request
  GET      `/admin/users`                   Manage users
  GET      `/admin/staff`                   Manage staff
  GET      `/admin/categories`              Manage categories
  POST     `/admin/categories/create`       Create category
  GET      `/admin/reports`                 Reports/statistics

Routes can be renamed during development, but their responsibilities
should remain consistent.

------------------------------------------------------------------------

# 14. How a Flask Route Works

General flow:

``` text
Browser
   ↓
URL
   ↓
Flask Route
   ↓
Python Function
   ↓
Authentication/Authorization
   ↓
Validation
   ↓
Business Logic
   ↓
Database
   ↓
Template or Redirect
   ↓
Browser
```

Every important function should have comments explaining:

1.  What it does.
2.  Which route uses it.
3.  Who can access it.
4.  What data it receives.
5.  What database operation occurs.
6.  Where the user is redirected.

------------------------------------------------------------------------

# 15. Database Tables

Initial database:

``` text
users
categories
maintenance_requests
request_updates
feedback
```

Future tables:

``` text
locations
assets
notifications
attachments
preventive_maintenance
```

------------------------------------------------------------------------

# 16. users Table

  Column          Type                  Description
  --------------- --------------------- ------------------
  id              INT PK                User ID
  name            VARCHAR(100)          Name
  email           VARCHAR(150) UNIQUE   Login email
  password_hash   VARCHAR(255)          Hashed password
  role            VARCHAR/ENUM          user/staff/admin
  phone           VARCHAR(20)           Optional
  department      VARCHAR(100)          Department
  is_active       BOOLEAN               Account status
  created_at      DATETIME              Creation time
  updated_at      DATETIME              Last update

**Important:** Never store plain-text passwords.

Normal registration should create `user` accounts. Admin should control
staff/admin privileges.

------------------------------------------------------------------------

# 17. categories Table

  Column        Type           Description
  ------------- -------------- -----------------
  id            INT PK         Category ID
  name          VARCHAR(100)   Category name
  description   TEXT           Description
  is_active     BOOLEAN        Active/inactive
  created_at    DATETIME       Creation time

Initial categories:

``` text
Electrical
Plumbing
HVAC / AC
Furniture
Network / IT
Civil / Building
Cleaning
Equipment
Other
```

Store categories in the database rather than permanently hard-coding
them.

------------------------------------------------------------------------

# 18. maintenance_requests Table

This is the central table.

  Column            Type           Description
  ----------------- -------------- ----------------------------------------------
  id                INT PK         Request ID
  user_id           INT FK         Reporting user
  category_id       INT FK         Category
  assigned_to       INT FK         Staff user
  title             VARCHAR(200)   Short problem title
  description       TEXT           Full problem
  location          VARCHAR(255)   Problem location
  priority          VARCHAR/ENUM   low/medium/high/critical
  status            VARCHAR/ENUM   pending/assigned/in_progress/resolved/closed
  resolution_note   TEXT           Final repair information
  created_at        DATETIME       Created time
  updated_at        DATETIME       Last update
  resolved_at       DATETIME       Resolution time
  closed_at         DATETIME       Closure time

Relationships:

``` text
users.id → maintenance_requests.user_id
users.id → maintenance_requests.assigned_to
categories.id → maintenance_requests.category_id
```

`assigned_to` should reference a user whose role is `staff`.

------------------------------------------------------------------------

# 19. request_updates Table

Stores the request timeline.

  Column       Type       Description
  ------------ ---------- ----------------------
  id           INT PK     Update ID
  request_id   INT FK     Request
  user_id      INT FK     Person making update
  old_status   VARCHAR    Previous status
  new_status   VARCHAR    New status
  note         TEXT       Work/action note
  created_at   DATETIME   Update time

Example:

``` text
10:15  User created request
      PENDING

11:00  Admin assigned plumber
      ASSIGNED

11:30  Plumber started work
      IN_PROGRESS

12:45  Plumber completed repair
      RESOLVED

13:15  Admin closed request
      CLOSED
```

------------------------------------------------------------------------

# 20. Database Relationship Diagram

``` text
                    USERS
                      │
          ┌───────────┴───────────┐
          │                       │
          ▼                       ▼
MAINTENANCE_REQUESTS       REQUEST_UPDATES
          │
          ▼
      CATEGORIES
```

Detailed relationships:

``` text
users.id
   │
   ├──────────────→ maintenance_requests.user_id
   │
   ├──────────────→ maintenance_requests.assigned_to
   │
   └──────────────→ request_updates.user_id

categories.id
   └──────────────→ maintenance_requests.category_id

maintenance_requests.id
   └──────────────→ request_updates.request_id
```

------------------------------------------------------------------------

# 21. Request Creation Function

Route:

``` text
GET/POST /user/request/new
```

Workflow:

``` text
Display form
    ↓
User submits form
    ↓
Validate title
    ↓
Validate description
    ↓
Validate category
    ↓
Validate location
    ↓
Validate priority
    ↓
Insert request
    ↓
Set status = REQUESTED
    ↓
Create initial history record
    ↓
Redirect to request details
```

Server-side validation is mandatory.

Do not trust values supplied by the browser.

------------------------------------------------------------------------

# 22. Assignment Function

Route:

``` text
POST /admin/request/<id>/assign
```

Workflow:

``` text
Admin opens request
       ↓
Selects staff
       ↓
Backend checks admin role
       ↓
Checks request exists
       ↓
Checks selected user is staff
       ↓
Updates assigned_to
       ↓
Changes status to ASSIGNED
       ↓
Creates history record
       ↓
Redirects to request details
```

------------------------------------------------------------------------

# 23. Start Work Function

Route:

``` text
POST /staff/request/<id>/start
```

Workflow:

``` text
Staff opens assigned request
       ↓
Backend checks staff role
       ↓
Checks request exists
       ↓
Checks assigned_to = current staff
       ↓
ASSIGNED → IN_PROGRESS
       ↓
Creates history record
       ↓
Redirects to request details
```

A staff member must not be able to modify another staff member's
request.

------------------------------------------------------------------------

# 24. Resolve Function

Route:

``` text
POST /staff/request/<id>/resolve
```

Workflow:

``` text
Check login
      ↓
Check staff role
      ↓
Check request belongs to current staff
      ↓
Validate resolution note
      ↓
Set status = RESOLVED
      ↓
Save resolution note
      ↓
Set resolved_at
      ↓
Create history record
      ↓
Redirect
```

------------------------------------------------------------------------

# 25. Close Function

Route:

``` text
POST /admin/request/<id>/close
```

Recommended rule:

``` text
Only RESOLVED → CLOSED
```

Workflow:

``` text
Admin clicks Close
       ↓
Check admin role
       ↓
Find request
       ↓
Check status = RESOLVED
       ↓
Set CLOSED
       ↓
Set closed_at
       ↓
Create history record
       ↓
Redirect
```

------------------------------------------------------------------------

# 26. Authentication Workflow

## Registration

``` text
Registration Form
       ↓
Validate input
       ↓
Check duplicate email
       ↓
Hash password
       ↓
Insert user
       ↓
Redirect to login
```

## Login

``` text
Login Form
       ↓
Validate credentials
       ↓
Find user
       ↓
Verify password hash
       ↓
Create session
       ↓
Check role
       ↓
Redirect to correct dashboard
```

Session example:

``` text
session["user_id"]
session["role"]
```

Never store passwords in sessions.

------------------------------------------------------------------------

# 27. Role-Based Access Control

Every protected route must check authentication and authorization.

Concept:

``` python
if not logged_in:
    redirect_to_login()

if role_not_allowed:
    return 403
```

Examples:

``` text
/user/*  → user
/staff/* → staff
/admin/* → admin
```

Hiding a button in HTML is not security. The backend must reject
unauthorized requests even if a user manually enters the URL.

------------------------------------------------------------------------

# 28. Important Backend Functions

Recommended functions:

``` text
register_user()
login_user()
logout_user()
get_current_user()

create_request()
get_user_requests()
get_request_by_id()
get_all_requests()

assign_request()
update_request_status()
add_request_update()
get_request_history()

get_categories()
create_category()

get_dashboard_statistics()

submit_feedback()
get_feedback()
get_all_feedback()
update_feedback_status()
```

Keep routes, validation, business logic, and database operations
reasonably separated.

------------------------------------------------------------------------

# 29. Beginner-Friendly Code Standard

Important functions should include docstrings/comments.

Example:

``` python
def create_request():
    """
    Creates a new maintenance request.

    Route:
        /user/request/new

    Access:
        Logged-in users.

    Steps:
        1. Read submitted form data.
        2. Validate the data.
        3. Insert the request into MySQL.
        4. Create the first history record.
        5. Redirect to request details.
    """
```

Future code should favor:

-   Clear variable names
-   Simple functions
-   Helpful comments
-   Small logical steps
-   Minimal unnecessary abstraction

Avoid writing complicated code merely to make the project look advanced.

------------------------------------------------------------------------

# 30. Frontend Pages

## Public

``` text
Landing Page
Login
Register
```

## User

``` text
Dashboard
Create Request
My Requests
Request Details
Profile
```

## Staff

``` text
Dashboard
Assigned Requests
Request Details
```

## Admin

``` text
Dashboard
All Requests
Request Details
Users
Staff
Categories
Reports
```

------------------------------------------------------------------------

# 31. Request Details Page

Example:

``` text
Request #104

Water leakage near wash basin

Category: Plumbing
Location: 2nd Floor – Restroom
Priority: HIGH
Status: IN_PROGRESS

Reported By:
Employee Name

Assigned To:
Plumber Name

Description:
Continuous water leakage near the wash basin.

Created:
05 September 2026, 10:15 AM

Work History:
--------------------------------
10:15 AM  Request created
11:00 AM  Assigned to plumber
11:30 AM  Work started
--------------------------------
```

For resolved requests:

``` text
Resolution:
Damaged pipe connection replaced and leakage stopped.
```

------------------------------------------------------------------------

# 32. Security Requirements

## Password security

-   Use Werkzeug password hashing.
-   Never store plain-text passwords.
-   Never display passwords.

## Authorization

Always check:

-   User is logged in.
-   User has required role.
-   Staff member is assigned to request.
-   User owns the request they are viewing.

## SQL Injection

Use parameterized queries.

Never construct SQL using raw user input.

## Input validation

Validate every important field on the server.

## CSRF

For POST forms, add CSRF protection such as Flask-WTF when the project
is stabilized.

------------------------------------------------------------------------

# 33. Error Handling

Expected errors:

``` text
Invalid login
→ "Invalid email or password."

Unauthorized page
→ 403 Access Denied

Missing request
→ 404 Request Not Found

Database failure
→ Friendly error message/page
```

Do not expose raw Python exceptions to normal users.

------------------------------------------------------------------------

# 34. Business Rules

These are the core rules and should remain consistent.

1.  Normal users can create requests.
2.  Users can view only their own requests.
3.  Administrators can view all requests.
4.  Only administrators can assign requests.
5.  Only assigned staff can work on a request.
6.  New requests start as `REQUESTED`.
7.  Administrative approval changes the user-facing status to `APPROVED`.
8.  Starting work changes the user-facing status to `ON WORK`.
9.  Completing the repair changes the user-facing status to `RECTIFIED`.
10. Admin closure changes status to `CLOSED`.
11. Major status changes create history records.
12. Passwords are always hashed.
13. Backend authorization is mandatory.

------------------------------------------------------------------------

# 35. Recommended Development Order

## Phase 1 -- Setup

1.  Create Flask project.
2.  Create virtual environment.
3.  Install dependencies.
4.  Configure Flask.
5.  Configure MySQL.
6.  Create database.
7.  Test connection.

## Phase 2 -- Authentication

1.  users table
2.  Register
3.  Login
4.  Password hashing
5.  Sessions
6.  Logout
7.  Role checks

## Phase 3 -- User Module

1.  Dashboard
2.  Create request
3.  Save request
4.  My requests
5.  Request details

## Phase 4 -- Admin Module

1.  Admin dashboard
2.  All requests
3.  Request details
4.  Assign staff
5.  User management
6.  Category management

## Phase 5 -- Staff Module

1.  Staff dashboard
2.  Assigned requests
3.  Start work
4.  Work notes
5.  Resolve request

## Phase 6 -- Workflow

1.  Status transitions
2.  Request history
3.  Resolution notes
4.  Timestamps
5.  Close request

## Phase 7 -- Reports

1.  Statistics
2.  Category counts
3.  Priority counts
4.  Staff workload
5.  Search/filter

## Phase 8 -- UI

1.  Navigation
2.  Forms
3.  Responsive layout
4.  Status badges
5.  Priority indicators
6.  Tables
7.  Dashboard cards
8.  Confirmation dialogs

------------------------------------------------------------------------

# 36. MVP Scope

The first complete version should contain:

## Authentication

-   Register
-   Login
-   Logout
-   Roles

## User

-   Dashboard
-   Create request
-   My requests
-   Status tracking

## Admin

-   Dashboard
-   All requests
-   Assign staff
-   Manage users
-   Manage categories

## Staff

-   Dashboard
-   Assigned requests
-   Start work
-   Add notes
-   Resolve request

## Database

``` text
users
categories
maintenance_requests
request_updates
```

This is enough to demonstrate the complete system.

------------------------------------------------------------------------

# 37. Do Not Overcomplicate the MVP

Do not add these before the core workflow works:

-   AI chatbot
-   Machine learning
-   IoT integration
-   WebSockets
-   Microservices
-   Mobile application
-   Payment systems
-   Predictive analytics
-   Complex notification infrastructure

The core system must work first:

`Report → Assign → Work → Resolve → Close`

------------------------------------------------------------------------

# 38. Future Features

## Useful next features

1.  Search and filtering
2.  Image attachments
3.  Notifications
4.  Email notifications
5.  User feedback
6.  Estimated/actual repair time
7.  Comments
8.  Better reports

## Advanced features

### Asset Management

An `assets` table could store:

``` text
Asset ID: AC-104
Type: Air Conditioner
Location: Meeting Room 2
Manufacturer: Example
Installation Date: ...
```

Requests can then reference a specific asset.

This allows repeated failures to be identified.

### Preventive Maintenance

Current system:

``` text
Problem → Report → Repair
```

Future system:

``` text
Scheduled maintenance
       ↓
Technician notified
       ↓
Inspection
       ↓
Maintenance recorded
```

Examples:

-   Monthly AC inspection
-   Generator service
-   Electrical inspection
-   Equipment servicing

### SLA

A future version can define configurable response targets:

``` text
CRITICAL → immediate
HIGH     → short response target
MEDIUM   → normal response target
LOW      → lower urgency
```

Exact times should be configurable by the organization.

------------------------------------------------------------------------

# 39. Dashboard Design

## User

``` text
Welcome, [Name]

My Requests
------------------
Total
Pending
In Progress
Resolved
Closed

[Create New Request]

Recent Requests
```

## Staff

``` text
Welcome, [Staff Name]

Assigned
In Progress
Resolved
High Priority

Assigned Requests
```

## Admin

``` text
MaintenX Admin Dashboard

Total Requests
Pending
Assigned
In Progress
Resolved
Closed
Critical

Requests by Category
Requests by Priority
Recent Requests
Staff Workload
```

------------------------------------------------------------------------

# 40. Request Form

``` text
Title
[____________________________]

Category
[ Plumbing ▼ ]

Location
[____________________________]

Priority
[ Medium ▼ ]

Description
[____________________________
 ____________________________
 ____________________________]

[ Submit Request ]
```

Future:

``` text
[ Upload Image ]
```

------------------------------------------------------------------------

# 41. Maintenance History

For every important action record:

``` text
Who?
What?
When?
Previous status?
New status?
Note?
```

This provides accountability and makes it possible to answer:

-   How many AC problems occurred?
-   Which category has the most requests?
-   Which department reports the most issues?
-   How long does resolution normally take?
-   Which staff member has the most assigned work?
-   Which assets fail repeatedly?

------------------------------------------------------------------------

# 42. Testing Checklist

## Authentication

-   [ ] Registration works.
-   [ ] Duplicate email rejected.
-   [ ] Password hashed.
-   [ ] Correct login works.
-   [ ] Wrong password rejected.
-   [ ] Logout works.
-   [ ] Unauthorized pages blocked.

## User

-   [ ] User can create request.
-   [ ] Empty required fields rejected.
-   [ ] User sees own requests.
-   [ ] User cannot see another user's private request.
-   [ ] Status displayed correctly.

## Admin

-   [ ] Admin sees all requests.
-   [ ] Admin can assign staff.
-   [ ] Non-staff cannot be assigned.
-   [ ] Admin can manage categories.
-   [ ] Admin can view statistics.

## Staff

-   [ ] Staff sees assigned requests.
-   [ ] Staff cannot modify another staff member's request.
-   [ ] Staff can start work.
-   [ ] Staff can add notes.
-   [ ] Staff can resolve requests.

## Workflow

-   [ ] New request = PENDING.
-   [ ] Assignment = ASSIGNED.
-   [ ] Start = IN_PROGRESS.
-   [ ] Resolve = RESOLVED.
-   [ ] Close = CLOSED.
-   [ ] History recorded.

------------------------------------------------------------------------

# 43. Final System Architecture

``` text
┌─────────────────────────────────────┐
│             FRONTEND                │
│       HTML + CSS + JavaScript       │
└──────────────────┬──────────────────┘
                   │ HTTP
                   ▼
┌─────────────────────────────────────┐
│           FLASK BACKEND             │
│                                     │
│  Auth │ User │ Staff │ Admin       │
│                                     │
│ Authentication                      │
│ Authorization                       │
│ Validation                          │
│ Business Logic                      │
└──────────────────┬──────────────────┘
                   │ SQL
                   ▼
┌─────────────────────────────────────┐
│               MYSQL                 │
│                                     │
│ users                               │
│ categories                          │
│ maintenance_requests                │
│ request_updates                     │
└─────────────────────────────────────┘
```

------------------------------------------------------------------------

# 44. Final Project Workflow

``` text
                    USER
                     │
                     ▼
             Create Request
                     │
                     ▼
                  PENDING
                     │
                     ▼
                  ADMIN
                     │
               Review + Assign
                     │
                     ▼
                  ASSIGNED
                     │
                     ▼
            MAINTENANCE STAFF
                     │
                 Start Work
                     │
                     ▼
                IN_PROGRESS
                     │
                 Repair
                     │
                     ▼
                 RESOLVED
                     │
                     ▼
                  ADMIN
                     │
                   Close
                     │
                     ▼
                  CLOSED
                     │
                     ▼
             MAINTENANCE HISTORY
```

------------------------------------------------------------------------

# 45. Future Development Decision Rules

Before adding any feature, ask:

1.  Which role needs it?
2.  Which route handles it?
3.  Which database table stores it?
4.  What validation is needed?
5.  What authorization is needed?
6.  Does it change the request workflow?
7.  Does it require a history entry?
8.  Does it require a schema change?
9.  Does it affect existing pages?
10. Does it break an existing business rule?

Do not add functionality simply because it looks advanced. It must have
a clear purpose.

------------------------------------------------------------------------

# 46. Source of Truth

This document is the baseline specification for MaintenX.

The primary workflow is:

**REPORT → APPROVE → ASSIGN → WORK → RECTIFY → CLOSE**

The initial core database is:

``` text
users
categories
maintenance_requests
request_updates
```

The three core roles are:

``` text
USER
STAFF
ADMIN
```

The core technology is:

``` text
HTML + CSS + JavaScript
Flask
MySQL
```

All future development should preserve the core workflow and role
responsibilities unless the project specification is deliberately
updated.

------------------------------------------------------------------------

# 47. Viva Answers

### What is your project?

> MaintenX is a web-based maintenance management system that allows
> users in an organization to report maintenance problems digitally and
> enables administrators and maintenance staff to assign, track, and
> resolve those problems efficiently.

### What problem does it solve?

> It replaces unorganized maintenance communication with a centralized
> system that records every maintenance request and tracks it from
> reporting to resolution.

### What is the main idea?

> The main idea is to create a centralized digital workflow where every
> maintenance problem can be reported, assigned, tracked, resolved, and
> stored as a permanent record.

### Who uses it?

> The three main roles are users or employees, maintenance staff, and
> administrators.

### What happens after a request is submitted?

> It starts as Pending. The administrator reviews and assigns it to
> appropriate maintenance staff. The staff changes it to In Progress
> while working and Resolved after completing the repair. The
> administrator can then close it.

### What is the main advantage?

> The main advantage is accountability and traceability because the
> system records who reported the problem, who was assigned, what
> actions were performed, when statuses changed, and how the problem was
> resolved.

------------------------------------------------------------------------

# 48. Recommended Project Title

**MaintenX -- A Smart Maintenance Management System for Organizations**

This title is broader than a campus-specific system and allows the same
application to be demonstrated for companies, offices, hospitals,
hotels, factories, schools, colleges, apartments, and other
organizations.### Staff pages/details
1. **Dashboard** — `/staff/dashboard`
   - Cards: Available Jobs, Accepted Jobs, On Work, Rectified, High Priority.
   - Recent available/accepted jobs.
   - Functions: `get_staff_dashboard()`, `get_available_job_count()`, `get_accepted_job_count()`, `get_on_work_count()`, `get_rectified_count()`, `get_high_priority_jobs()`.

2. **Jobs** — `/staff/jobs`
   - Shows available jobs that the staff member can select.
   - Staff opens a job to inspect its details.
   - Functions: `get_available_jobs()`, `get_staff_job_by_id()`, `filter_staff_requests()`, `search_staff_requests()`.

3. **Job Details** — `/staff/job/<id>`
   - This page is for viewing the job and accepting it only.
   - Shows request ID, title, category, location, priority, reporter, description, current status, and timeline.
   - If the job is available, show only `[ACCEPT JOB]`.
   - Do **not** show Start Work, Update Progress, or Mark Rectified here.
   - After successful acceptance, redirect to `/staff/history`.

4. **Accept Job**
   - POST `/staff/job/<id>/accept`
   - Verify staff role and job availability/eligibility.
   - Atomically claim the job so two staff members cannot accept it at the same time.
   - Set `accepted_by=current_staff_id`, `accepted_at=current_time`, and status `ACCEPTED`.
   - Create a `request_updates` history entry.
   - Redirect to `/staff/history`.
   - Function: `accept_job()`.

5. **Work History / Work Workspace** — `/staff/history`
   - This is the main workspace after a job is accepted.
   - Group jobs into:
     - **Accepted Jobs** → `[START WORK]`
     - **On Work** → `[UPDATE PROGRESS]` and `[MARK AS RECTIFIED]`
     - **Completed / Rectified Jobs** → `[VIEW WORK DETAILS]`
   - Functions: `get_staff_history()`, `get_completed_jobs()`, `get_job_history()`.

6. **Start Work**
   - POST `/staff/job/<id>/start`
   - Verify the logged-in staff member accepted the job.
   - Set status to `ON WORK`, save `started_by` and `started_at`, and create a history entry.
   - Function: `start_work()`.

7. **Update Work Progress**
   - POST `/staff/job/<id>/update`
   - Available only after the job is `ON WORK`.
   - Add work notes/progress updates to `request_updates`.
   - Status remains `ON WORK` unless changed by another valid workflow action.
   - Function: `add_work_update()`.

8. **Mark Rectified**
   - POST `/staff/job/<id>/rectify`
   - Available only to the staff member who accepted the job.
   - Save the resolution note, set status to `RECTIFIED`, save `resolved_by` and `resolved_at`, and create a history entry.
   - Function: `rectify_job()`.

9. **Bug Report** — `/staff/bug-report`
   - Specifically for bugs in MaintenX itself, sent to admin.
   - Fields: bug title, page/feature, expected behavior, actual behavior, description, optional screenshot.
   - POST `/staff/bug-report/submit`.
   - Uses the `feedback` table with `type='bug'`.
   - Bug status: `NEW → IN_REVIEW → RESOLVED → CLOSED`.
   - Only admin manages/responds.
   - Function: `submit_bug_report()`.

10. **Profile** — `/staff/profile`
   - Staff can update name, phone, department, profile photo, and other allowed profile information.
   - Staff cannot change role, employee ID, admin privileges, or account privileges.
   - Functions: `get_staff_profile()`, `update_staff_profile()`.

11. **Change Password**
   - POST `/staff/profile/password`
   - Kept inside Profile.
   - Verify current password, validate the new password, hash it, and update the database.
   - Function: `change_password()`.

12. Logout — `/auth/logout`.



---

# Architecture & Database Setup

**Architecture:**
HTML + CSS + JavaScript
          ↓
        Flask
          ↓
       SQLite

**Database:** SQLite

**Database file:**
instance/maintenx.db

*Note: SQLite is a file-based database. It requires no separate database server, eliminating the need to install or configure MySQL.*
