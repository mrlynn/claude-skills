# Event Lifecycle Reference

Events follow a 4-state lifecycle: `draft` -> `open` -> `in_progress` -> `concluded`. Each state controls what actions are allowed and what UI features are visible.

## State Machine

```
  +-------+       +------+       +-------------+       +-----------+
  | draft | ----> | open | ----> | in_progress | ----> | concluded |
  +-------+       +------+       +-------------+       +-----------+
      |               |                |
      |               |                +---> (back to open: rare, admin override)
      |               +---> (back to draft: admin can unpublish)
      +---> (delete: only drafts can be hard-deleted)
```

## State Details

### draft

The initial state for all new events. The event is being configured and is not visible to the public.

**What is allowed:**
- Full CRUD: edit all event fields including name, dates, capacity, rules, rubrics
- Configure Atlas provisioning settings
- Configure landing page content
- Link feedback forms
- Set up judging rubrics and criteria
- Add partners and organizers
- Delete the event entirely (hard delete)

**What is NOT allowed:**
- Public registration (event not visible to non-admins)
- Project submissions
- Judging and scoring
- Publishing results
- Sending feedback requests

**Who can transition to `open`:**
- super_admin, admin, organizer

**Side effects of transitioning to `open`:**
- Landing page becomes publicly accessible (if `landingPage.published === true`)
- Event appears in public event listing
- Registration becomes available (if `registrationDeadline` has not passed)

**Validation before transition:**
- Event must have `name`, `description`, `startDate`, `endDate`, `registrationDeadline`, `location`, and `capacity` set
- `startDate` must be in the future (warning, not blocking)
- `registrationDeadline` must be before or equal to `startDate`

---

### open

The event is published and accepting registrations. This is the primary public-facing state.

**What is allowed:**
- User registration (if `registrationDeadline` has not passed and capacity is not reached)
- Team formation and management
- Edit event details (with care -- changes are visible to registered users)
- Configure landing page
- Manage judge assignments
- Atlas cluster provisioning for teams

**What is NOT allowed:**
- Project submissions (event has not started yet)
- Judging and scoring
- Publishing results
- Sending feedback requests

**Who can transition to `in_progress`:**
- super_admin, admin, organizer

**Side effects of transitioning to `in_progress`:**
- Registration is closed (regardless of deadline)
- Notification sent to all registered participants that the event has started
- Project submission forms become available

**Who can transition back to `draft`:**
- super_admin, admin (admin override for unpublishing)

**Side effects of transitioning back to `draft`:**
- Event removed from public listing
- Landing page becomes inaccessible to non-admins
- Existing registrations are preserved

---

### in_progress

The event is actively running. Participants are building, mentors are guiding, and judges are preparing.

**What is allowed:**
- Project submissions (until `submissionDeadline` if set)
- Judging and scoring by assigned judges
- Team management (join/leave, but capacity limits apply)
- Atlas cluster usage
- Mentor access to team details
- Edit event details (limited -- dates should not change)

**What is NOT allowed:**
- New registrations
- Publishing results (event not concluded)
- Deleting the event

**Who can transition to `concluded`:**
- super_admin, admin, organizer

**Side effects of transitioning to `concluded`:**
- Project submissions are closed
- Judging is frozen (no new scores accepted)
- Notification sent to participants that the event has concluded
- Results can now be published
- Feedback request emails can be sent
- Atlas cluster auto-cleanup is triggered (if `autoCleanupOnEventEnd === true`)

**Who can transition back to `open`:**
- super_admin only (rare, emergency rollback)

---

### concluded

The event is over. Results can be published, feedback collected, and resources cleaned up.

**What is allowed:**
- Publishing results (`resultsPublished: true`, `resultsPublishedAt: Date`)
- Sending feedback request emails to participants and partners
- Viewing final scores and rankings
- Generating AI feedback summaries
- Atlas cluster cleanup
- Exporting event data

**What is NOT allowed:**
- New registrations
- New project submissions
- New judge scores (scoring is frozen)
- Deleting the event (preserve audit trail)

**Who can publish results:**
- super_admin, admin, organizer

**Side effects of publishing results:**
- `resultsPublished` set to `true`
- `resultsPublishedAt` set to current timestamp
- Rankings become visible to participants on the event page
- Notification sent to all participants

---

## Business Rules Summary

| Rule                                            | Enforced Where                       |
|-------------------------------------------------|--------------------------------------|
| Registration only when status is `open`         | Registration API route + middleware  |
| Registration blocked after `registrationDeadline` | Registration API route             |
| Registration blocked when capacity is reached   | Registration API route (atomic check)|
| Submissions only when status is `in_progress`   | Submission API route                 |
| Submissions blocked after `submissionDeadline`  | Submission API route                 |
| Judging only when status is `in_progress`       | Scoring API route                    |
| Results only published when status is `concluded`| Results API route                   |
| Feedback requests only when status is `concluded`| Send feedback API route             |
| Hard delete only for `draft` events             | Delete API route                     |
| Atlas cleanup on conclude (if enabled)          | Event status transition handler      |

## Capacity Management

Capacity is checked atomically during registration to prevent race conditions:

```typescript
// Pseudocode for atomic capacity check
const participantCount = await ParticipantModel.countDocuments({ eventId });
if (participantCount >= event.capacity) {
  return errorResponse("Event is at capacity", 409);
}
```

For high-concurrency scenarios, use MongoDB's `findOneAndUpdate` with a counter field to ensure atomicity.

## Date Relationships

```
registrationDeadline <= startDate <= submissionDeadline <= endDate
```

- `registrationDeadline`: Last date to register. Must be at or before `startDate`.
- `startDate`: When the event begins. Transition to `in_progress` typically happens here.
- `submissionDeadline`: When project submissions close. Optional. Defaults to `endDate` if not set.
- `endDate`: When the event ends. Transition to `concluded` typically happens here.

## Landing Page Visibility

| Event Status  | `landingPage.published` | Landing Page Visible To          |
|--------------|:-----------------------:|----------------------------------|
| draft         | true or false          | Admin panel roles only (preview) |
| open          | true                   | Everyone (public)                |
| open          | false                  | Admin panel roles only           |
| in_progress   | true                   | Everyone (public)                |
| concluded     | true                   | Everyone (read-only, results)    |

## Notification Triggers

| Transition              | Notification                                    | Recipients               |
|------------------------|-------------------------------------------------|--------------------------|
| draft -> open           | "Event is now accepting registrations"          | None (discovery-based)   |
| Registration            | Registration confirmation email                  | Registering user         |
| open -> in_progress     | "The event has started!"                        | All participants         |
| in_progress -> concluded| "The event has concluded"                       | All participants         |
| Results published       | "Results are in!"                               | All participants         |
| Feedback request sent   | Feedback request email                           | Selected participants    |
