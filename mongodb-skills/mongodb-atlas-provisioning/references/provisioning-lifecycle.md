# Provisioning Lifecycle Reference

The Atlas cluster provisioning flow is a 9-step orchestration that creates an Atlas project, M0 cluster, database user, and IP access list for a hackathon team. If any step fails after project creation, the entire Atlas project is rolled back (deleted) to prevent orphaned resources.

## State Transition Diagram

```
[Request Received]
        |
        v
  1. Validate Event -----> [Error: Provisioning not enabled]
        |
        v
  2. Check Existing -----> [ConflictError: Cluster already exists]
        |
        v
  3. Resolve Config
        |
        v
  4. Generate Names
        |
        v
  5. Create/Resolve Project
        |                     +---------------------------+
        v                     |                           |
  6. Create M0 Cluster -----> |  ROLLBACK: Delete Project |
        |                     |                           |
        v                     |                           |
  7. Create DB User --------> |  (on any failure from     |
        |                     |   step 6, 7, 8, or 9)     |
        v                     |                           |
  8. Configure IP Access ---> |                           |
        |                     +---------------------------+
        v
  9. Save to Platform DB
        |
        v
  [Return with one-time credentials]
        |
        v
  Status: "creating" (poll until "active")
```

## Step Details

### Step 1: Validate Event

**What happens:** The system loads the event by ID and checks that `event.atlasProvisioning.enabled === true`.

**What can fail:**
- Event not found (invalid eventId) -- throws generic Error
- Provisioning not enabled for this event -- throws Error with message "Provisioning not enabled"
- Database connection failure -- throws connection error

**Rollback:** None needed. No external resources have been created.

### Step 2: Check Existing Cluster

**What happens:** Queries the `AtlasCluster` collection for an existing record matching `{ eventId, teamId, status: { $nin: ['deleted', 'error'] } }`. If a non-terminal cluster exists, provisioning is blocked. Old records in `deleted` or `error` status are cleaned up via `deleteMany` to avoid unique index collisions on `{ eventId, teamId }`.

**What can fail:**
- Active cluster already exists -- throws `ConflictError` with message "Cluster already exists for this team"
- Database query failure

**Rollback:** None needed. No external resources have been created.

### Step 3: Resolve Provider and Region

**What happens:** Determines the cloud provider and region for the new cluster. Priority order:
1. Explicit params passed by the caller (`params.provider`, `params.region`)
2. Event-level defaults (`event.atlasProvisioning.defaultProvider`, `.defaultRegion`)
3. Hardcoded fallbacks (`'AWS'`, `'US_EAST_1'`)

**What can fail:** Nothing -- this step always resolves to valid defaults.

**Rollback:** None needed.

### Step 4: Generate Names

**What happens:** Creates deterministic names for the Atlas project and cluster:
- Project name: `mh-{last6CharsOfEventId}-{last6CharsOfTeamId}` (e.g., `mh-a1b2c3-d4e5f6`)
- Cluster name: `hackathon-cluster` (fixed name, one cluster per project)

**What can fail:** Nothing -- this is pure string manipulation.

**Rollback:** None needed.

### Step 5: Create or Resolve Atlas Project

**What happens:** First tries to find an existing project by name using `getAtlasProjectByName()`. If no project exists (404), creates a new one with `createAtlasProject()` using the organization ID from `ATLAS_ORG_ID`.

**What can fail:**
- Atlas API authentication failure (invalid keys) -- throws AtlasApiError
- Organization quota exceeded -- throws AtlasApiError with 403
- Network connectivity to Atlas API -- throws generic Error
- Duplicate project name in a different context -- throws AtlasApiError with 409

**Rollback:** If this step fails, no Atlas project was created, so no cleanup is needed. If the project was created but a later step fails, the project is deleted in the catch block.

### Step 6: Create M0 Cluster

**What happens:** Creates a free-tier (M0) cluster in the Atlas project. The API call specifies:
- `clusterType: 'REPLICASET'`
- `providerName: 'TENANT'` (required for M0)
- `backingProviderName`: AWS, GCP, or AZURE
- `regionName`: the resolved region
- `electableSpecs.instanceSize: 'M0'`

The Atlas API returns immediately with `stateName: 'CREATING'`. The cluster takes 1-3 minutes to become IDLE.

**What can fail:**
- M0 cluster limit reached for the organization -- throws AtlasApiError with 400/403
- Invalid region for the chosen provider -- throws AtlasApiError with 400
- Cluster name already exists in the project -- throws AtlasApiError with 409
- Atlas API rate limiting -- throws AtlasApiError with 429

**Rollback:** The catch block deletes the Atlas project created in Step 5. This cascades to delete the cluster as well.

### Step 7: Create Database User

**What happens:** Generates a secure password (24 chars, mixed case + numbers + special) and creates a database user scoped to the cluster:
- Username: `team-{last6CharsOfTeamId}`
- Database: `admin` (authentication database)
- Roles: `readWriteAnyDatabase` on `admin`
- Scopes: restricted to the cluster created in Step 6

The password is generated using `crypto.randomInt()` for cryptographic security. It is NEVER stored in the platform database.

**What can fail:**
- Atlas API error creating user -- throws AtlasApiError
- Username collision (unlikely with team-based naming) -- throws AtlasApiError with 409

**Rollback:** The catch block deletes the entire Atlas project, which cascades to delete both the cluster and the database user.

### Step 8: Configure IP Access

**What happens:** If `event.atlasProvisioning.openNetworkAccess === true`, adds a `0.0.0.0/0` CIDR entry to the project's IP access list with the comment "Hackathon open access". This allows connections from any IP address.

For production workshops, specific CIDRs can be configured instead.

**What can fail:**
- Atlas API error adding IP entries -- throws AtlasApiError
- IP access list limit reached -- throws AtlasApiError

**Rollback:** Same as Steps 6/7 -- delete the Atlas project.

### Step 9: Save to Platform Database

**What happens:** Creates an `AtlasCluster` document in the platform's MongoDB database with:
- References: eventId, teamId, projectId, provisionedBy
- Atlas identifiers: atlasProjectId, atlasProjectName, atlasClusterName, atlasClusterId
- Connection strings (with `appName=devrel-platform-hackathon-atlas` appended)
- Database users array (username only, no password)
- Status: `'creating'`
- Provider and region information

**What can fail:**
- Platform database connection failure -- throws connection error
- Unique index violation on `{ eventId, teamId }` -- throws MongoError E11000 (should be prevented by Step 2's cleanup, but race conditions are possible)

**Rollback:** The catch block deletes the Atlas project. The platform database record may or may not have been created. If it was partially created, the next provisioning attempt will clean it up in Step 2.

## Post-Provisioning

After the 9 steps complete successfully, the function returns the cluster document with `_initialCredentials` attached:

```typescript
{
  ...clusterDocument,
  _initialCredentials: {
    username: "team-d4e5f6",
    password: "generated-24-char-password"
  }
}
```

The password is displayed to the user exactly once. It is not stored anywhere in the platform.

## Status Polling

After provisioning, the cluster status must be polled until it transitions from `creating` to `active`:

```
creating  -->  active    (normal flow, 1-3 minutes)
creating  -->  error     (Atlas provisioning failed)
active    -->  deleting  (admin triggered cleanup)
deleting  -->  deleted   (cleanup complete)
```

The `refreshClusterStatus()` function:
1. Loads the platform cluster record
2. Calls `getAtlasCluster()` to get the current Atlas state
3. Maps the Atlas state to the platform status using `mapAtlasStateToPlatformStatus()`
4. Updates the connection string (populated once cluster is IDLE)
5. Saves the updated record

### Atlas State to Platform Status Mapping

| Atlas stateName | Platform status |
|----------------|-----------------|
| CREATING       | creating        |
| IDLE           | active          |
| UPDATING       | active          |
| REPAIRING      | active          |
| DELETING       | deleting        |
| DELETED        | deleted         |

## Cleanup

When an event concludes and `autoCleanupOnEventEnd === true`:
1. Find all AtlasCluster records for the event with status not `deleted`
2. For each cluster, call `deleteAtlasCluster()` then `deleteAtlasProject()`
3. Update the platform record status to `deleted` with `deletedAt` timestamp
4. Handle 404 errors gracefully (cluster may already be gone)

## DevRel Attribution

All connection strings include `appName=devrel-platform-hackathon-atlas` as a query parameter. This allows MongoDB internal analytics to track usage originating from DevRel platform provisioning. The `addAppNameToConnectionString()` utility handles idempotent appending of this parameter.
