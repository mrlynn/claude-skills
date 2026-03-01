# Registration Flow Reference

The registration system uses a 3-tier wizard that adapts to the event's configuration. Each tier adds more fields, giving organizers control over how much information they collect.

## Tier Overview

```
+---------------------+     +---------------------+     +---------------------+
|      TIER 1         |     |      TIER 2         |     |      TIER 3         |
|  Always Shown       | --> |  Configurable       | --> |  Fully Custom       |
|                     |     |  (optional)         |     |  (optional)         |
+---------------------+     +---------------------+     +---------------------+
| - Email             |     | - Skills            |     | - Custom questions  |
| - Password (new)    |     | - GitHub URL        |     |   defined by the    |
| - Name              |     | - Bio               |     |   event organizer   |
| - Terms acceptance  |     | - Custom questions  |     |                     |
| - Experience level* |     |                     |     |                     |
| - Custom questions* |     |                     |     |                     |
+---------------------+     +---------------------+     +---------------------+
  * = optional per config
```

## Tier 1: Core Information (Always Shown)

Tier 1 collects the minimum information needed to register a user. It is always displayed regardless of event configuration.

### Required Fields

| Field      | Type     | Validation                                |
|------------|----------|-------------------------------------------|
| `email`    | string   | Valid email, lowercased, unique per event  |
| `name`     | string   | Min 2 characters                          |
| `terms`    | boolean  | Must be `true`                            |

### Conditional Fields

| Field            | Type     | Shown When                                  |
|------------------|----------|---------------------------------------------|
| `password`       | string   | User does not have an existing account. Min 8 chars. |
| `experienceLevel`| enum     | `registrationFormConfig.tier1.showExperienceLevel === true` |

Experience level options: `"beginner"`, `"intermediate"`, `"advanced"`

### Optional Custom Questions (Max 2)

Tier 1 supports up to 2 custom questions defined in `registrationFormConfig.tier1.customQuestions`. These appear below the core fields.

## Tier 2: Profile Enrichment (Configurable)

Tier 2 collects profile data that helps with team matching and participant discovery. It is only shown when `registrationFormConfig.tier2.enabled === true`.

### Configuration

```typescript
tier2: {
  enabled: boolean;           // Whether to show this tier
  prompt: string;             // Header text (e.g., "Help us match you with a great team")
  showSkills: boolean;        // Show skills multi-select
  showGithub: boolean;        // Show GitHub URL field
  showBio: boolean;           // Show bio textarea
  customQuestions: ICustomQuestion[];  // Additional questions
}
```

### Fields

| Field    | Type       | Shown When             | Validation               |
|----------|------------|------------------------|--------------------------|
| `skills` | string[]   | `showSkills === true`  | Min 1, max 10 items      |
| `github` | string     | `showGithub === true`  | Optional, URL format     |
| `bio`    | string     | `showBio === true`     | Optional, max 1000 chars |

### Custom Questions

Each custom question has this structure:

```typescript
{
  id: string;           // Unique identifier (e.g., "q_dietary")
  label: string;        // Display label
  type: "text" | "select" | "multiselect" | "checkbox";
  options: string[];    // For select/multiselect types
  required: boolean;
  placeholder: string;
}
```

## Tier 3: Event-Specific Questions (Fully Custom)

Tier 3 is entirely defined by the event organizer. It is only shown when `registrationFormConfig.tier3.enabled === true`.

### Configuration

```typescript
tier3: {
  enabled: boolean;
  prompt: string;             // Header text (e.g., "A few more questions from the organizers")
  customQuestions: ICustomQuestion[];
}
```

All fields in Tier 3 are custom questions. There are no pre-built fields. This tier is typically used for:
- Dietary restrictions for in-person events
- T-shirt size
- Travel/visa needs
- Specific technology experience questions
- Company/affiliation information

## sessionStorage Persistence

Wizard progress is stored in the browser's `sessionStorage` to prevent data loss when users navigate away and return.

### Storage Key

```
registration_{eventId}
```

### Stored Data

```json
{
  "currentTier": 2,
  "tier1": { "email": "user@example.com", "name": "Alice", "experienceLevel": "intermediate" },
  "tier2": { "skills": ["javascript", "react"], "github": "https://github.com/alice" },
  "tier3": {},
  "savedAt": "2025-01-15T10:30:00Z"
}
```

### Behavior

- Data is saved to sessionStorage after each tier is completed
- On page load, existing data is restored from sessionStorage
- The wizard jumps to the last incomplete tier
- Data is cleared from sessionStorage after successful registration
- sessionStorage is tab-scoped -- opening a new tab starts fresh

## Backend Registration Flow

When the user clicks "Submit" on the final tier, the client sends all collected data to the registration API endpoint.

### API Endpoint

```
POST /api/events/[eventId]/register
```

### Request Validation Schema

```typescript
const registrationSchema = z.object({
  name: z.string().min(2),
  email: z.string().email(),
  password: z.string().min(8).optional(),     // Only for new users
  skills: z.array(z.string()).min(1).max(10),
  experienceLevel: z.enum(["beginner", "intermediate", "advanced"]).optional(),
  github: z.string().optional(),
  bio: z.string().max(1000).optional(),
  customAnswers: z.record(z.string(), z.unknown()).optional(),
});
```

### Processing Steps

#### 1. Validate Event State

```
Check: event exists
Check: event.status === "open"
Check: registrationDeadline not passed
Check: capacity not reached (atomic count)
```

If any check fails, return an appropriate error (404, 409, or 422).

#### 2. Resolve User (Atomic)

Two paths depending on whether the user already has an account:

**Existing user (has account, no password in request):**
```
Find user by email
Verify account is not banned or deleted
Check user is not already registered for this event
```

**New user (no account, password provided):**
```
Create user atomically:
  - email (lowercased)
  - name
  - passwordHash (bcrypt)
  - role: "participant"
  - createdAt, updatedAt
Handle E11000 duplicate key error (race condition with concurrent registration)
```

The user creation is wrapped in a try/catch that handles the duplicate key error gracefully. If two concurrent requests try to create the same user, one succeeds and the other falls through to the "existing user" path.

#### 3. Create Participant Record

Create or update the Participant document linking the user to the event:

```javascript
{
  userId: user._id,
  eventId: event._id,
  status: "registered",
  registeredAt: new Date(),
  experienceLevel: data.experienceLevel,
  skills: data.skills,
  customResponses: {
    [eventId]: data.customAnswers   // Keyed by eventId to support multi-event
  }
}
```

Custom answers are stored keyed by `eventId` so a user can register for multiple events without data conflicts.

#### 4. Fire-and-Forget Post-Processing

After the registration response is sent (202 Accepted), these operations run asynchronously without blocking:

```typescript
// All wrapped in .catch(() => {}) -- failures do not affect registration

// a) Generate skills embedding for vector-based team matching
embedSkills(user.skills).catch(() => {});

// b) Create in-app notification
createNotification({
  userId: user._id,
  type: "registration_confirmed",
  message: `You're registered for ${event.name}!`,
}).catch(() => {});

// c) Send registration confirmation email
const template = await renderEmailTemplate("registration_confirmation", {
  userName: user.name,
  eventName: event.name,
  eventDate: formatDateRange(event.startDate, event.endDate),
  eventLocation: event.isVirtual ? "Virtual" : event.location,
  dashboardUrl: `${NEXTAUTH_URL}/events/${event._id}`,
});
sendEmail({ to: user.email, subject: template.subject, html: template.html }).catch(() => {});

// d) Send email verification (if new user without verified email)
if (!user.emailVerified) {
  sendVerificationEmail(user).catch(() => {});
}
```

## Capacity Checks

Capacity is validated at the API level, not just the frontend. This prevents race conditions where multiple users register simultaneously.

```typescript
// Atomic capacity check
const currentCount = await ParticipantModel.countDocuments({
  eventId: event._id,
  status: { $ne: "cancelled" }
});

if (currentCount >= event.capacity) {
  return errorResponse("This event has reached its registration capacity", 409);
}
```

For extremely high-concurrency scenarios (thousands of simultaneous registrations), consider using a counter field on the Event document with `findOneAndUpdate` and `$inc` for true atomicity.

## Error Responses

| Status | Message                                      | Cause                              |
|--------|----------------------------------------------|-------------------------------------|
| 404    | "Event not found"                            | Invalid eventId                     |
| 409    | "Event is not accepting registrations"       | Status is not "open"                |
| 409    | "Registration deadline has passed"           | Past registrationDeadline           |
| 409    | "Event is at capacity"                       | participantCount >= capacity        |
| 409    | "Already registered for this event"          | Duplicate registration              |
| 422    | Zod validation error message                 | Invalid input data                  |
| 500    | "Internal server error"                      | Unexpected failure                  |

## RegistrationFormConfig Model

The registration form configuration is stored as a separate document and linked to events via the landing page config:

```typescript
// Event.landingPage.registrationFormConfig -> ObjectId ref to RegistrationFormConfig

interface IRegistrationFormConfig {
  name: string;           // e.g., "Hackathon 2025 Registration"
  slug: string;           // Unique URL identifier
  description: string;
  isBuiltIn: boolean;     // Built-in configs cannot be deleted

  tier1: {
    showExperienceLevel: boolean;
    customQuestions: ICustomQuestion[];  // Max 2
  };

  tier2: {
    enabled: boolean;
    prompt: string;
    showSkills: boolean;
    showGithub: boolean;
    showBio: boolean;
    customQuestions: ICustomQuestion[];
  };

  tier3: {
    enabled: boolean;
    prompt: string;
    customQuestions: ICustomQuestion[];
  };
}
```

Organizers can create multiple registration form configs and reuse them across events.
