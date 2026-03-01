# Atlas Admin API v2 Quick Reference

Quick reference for the MongoDB Atlas Admin API v2 endpoints used by the provisioning system. All requests require HTTP Digest Authentication and the versioned Accept header.

## Authentication

All requests use HTTP Digest Authentication with Atlas programmatic API keys:
- **Public Key**: Used as the username
- **Private Key**: Used as the password
- **Library**: `digest-fetch` handles the challenge-response protocol

```typescript
import DigestFetch from 'digest-fetch';
const client = new DigestFetch(ATLAS_PUBLIC_KEY, ATLAS_PRIVATE_KEY);
```

## Common Headers

Every request must include:

```
Accept: application/vnd.atlas.2025-03-12+json
Content-Type: application/json
```

The date in the Accept header (`2025-03-12`) is the API version. This ensures backward compatibility.

## Base URL

```
https://cloud.mongodb.com/api/atlas/v2
```

Override with `ATLAS_BASE_URL` environment variable for testing.

---

## Project Operations

### Create Project

Creates a new Atlas project within an organization.

```
POST /groups
```

**Request Body:**
```json
{
  "name": "mh-a1b2c3-d4e5f6",
  "orgId": "60a1b2c3d4e5f6a7b8c9d0e1"
}
```

**Response (201):**
```json
{
  "id": "60f1a2b3c4d5e6f7a8b9c0d1",
  "name": "mh-a1b2c3-d4e5f6",
  "orgId": "60a1b2c3d4e5f6a7b8c9d0e1",
  "created": "2025-01-15T10:30:00Z"
}
```

**Common Errors:**
- `409`: Project name already exists in the organization
- `403`: Organization project limit reached or insufficient permissions

---

### Get Project by Name

Retrieves a project by its exact name. Used for idempotent provisioning (check before create).

```
GET /groups/byName/{projectName}
```

**Path Parameters:**
- `projectName`: URL-encoded project name

**Response (200):**
```json
{
  "id": "60f1a2b3c4d5e6f7a8b9c0d1",
  "name": "mh-a1b2c3-d4e5f6",
  "orgId": "60a1b2c3d4e5f6a7b8c9d0e1"
}
```

**Common Errors:**
- `404`: Project not found (expected during first provisioning)

---

### Delete Project

Deletes a project and all its resources (clusters, users, access lists). Used for rollback on provisioning failure and event cleanup.

```
DELETE /groups/{groupId}
```

**Path Parameters:**
- `groupId`: Atlas project ID

**Response:** `204 No Content`

**Common Errors:**
- `404`: Project already deleted
- `409`: Project has active clusters that are still being deleted

---

## Cluster Operations

### Create M0 Cluster

Creates a free-tier (M0) cluster. M0 clusters use the `TENANT` provider with a backing provider.

```
POST /groups/{groupId}/clusters
```

**Path Parameters:**
- `groupId`: Atlas project ID

**Request Body:**
```json
{
  "name": "hackathon-cluster",
  "clusterType": "REPLICASET",
  "replicationSpecs": [
    {
      "regionConfigs": [
        {
          "providerName": "TENANT",
          "backingProviderName": "AWS",
          "regionName": "US_EAST_1",
          "priority": 7,
          "electableSpecs": {
            "instanceSize": "M0"
          }
        }
      ]
    }
  ]
}
```

**Key fields:**
- `providerName`: Must be `"TENANT"` for M0/M2/M5 clusters
- `backingProviderName`: `"AWS"`, `"GCP"`, or `"AZURE"`
- `regionName`: Provider-specific region code (e.g., `US_EAST_1` for AWS)
- `instanceSize`: `"M0"` for free tier

**Response (201):**
```json
{
  "id": "cluster-id-string",
  "name": "hackathon-cluster",
  "stateName": "CREATING",
  "clusterType": "REPLICASET",
  "mongoDBVersion": "8.0.4",
  "connectionStrings": {
    "standard": "",
    "standardSrv": ""
  }
}
```

Note: `connectionStrings` are empty while `stateName` is `CREATING`. They populate once the cluster reaches `IDLE`.

**Common Errors:**
- `400`: Invalid region for the specified provider
- `400`: M0 cluster limit reached (1 free cluster per project)
- `409`: Cluster name already exists in the project

---

### Get Cluster

Retrieves cluster details including current state and connection strings. Used for status polling.

```
GET /groups/{groupId}/clusters/{clusterName}
```

**Path Parameters:**
- `groupId`: Atlas project ID
- `clusterName`: Cluster name (e.g., `hackathon-cluster`)

**Response (200):**
```json
{
  "id": "cluster-id-string",
  "name": "hackathon-cluster",
  "stateName": "IDLE",
  "mongoDBVersion": "8.0.4",
  "connectionStrings": {
    "standard": "mongodb://hackathon-cluster-shard-00-00.xxxxx.mongodb.net:27017,...",
    "standardSrv": "mongodb+srv://hackathon-cluster.xxxxx.mongodb.net"
  }
}
```

**Cluster States:**
| stateName | Meaning                           |
|-----------|-----------------------------------|
| CREATING  | Cluster is being provisioned      |
| IDLE      | Cluster is ready for connections  |
| UPDATING  | Configuration change in progress  |
| REPAIRING | Automatic repair in progress      |
| DELETING  | Cluster is being terminated       |
| DELETED   | Cluster has been removed          |

---

### Delete Cluster

Terminates a cluster. Used during event cleanup.

```
DELETE /groups/{groupId}/clusters/{clusterName}
```

**Response:** `202 Accepted`

The cluster transitions to `DELETING` state. Full deletion takes a few minutes.

**Common Errors:**
- `404`: Cluster not found or already deleted
- `409`: Cluster is already being deleted

---

## Database User Operations

### Create Database User

Creates a database user scoped to a specific cluster.

```
POST /groups/{groupId}/databaseUsers
```

**Request Body:**
```json
{
  "databaseName": "admin",
  "username": "team-d4e5f6",
  "password": "SecureP@ssw0rd!GeneratedHere",
  "roles": [
    {
      "roleName": "readWriteAnyDatabase",
      "databaseName": "admin"
    }
  ],
  "scopes": [
    {
      "name": "hackathon-cluster",
      "type": "CLUSTER"
    }
  ]
}
```

**Key fields:**
- `databaseName`: Authentication database, always `"admin"`
- `roles`: Array of role grants. `readWriteAnyDatabase` is standard for hackathons
- `scopes`: Restricts the user to specific clusters. Omit for project-wide access

**Response (201):**
```json
{
  "username": "team-d4e5f6",
  "databaseName": "admin",
  "roles": [
    { "roleName": "readWriteAnyDatabase", "databaseName": "admin" }
  ],
  "scopes": [
    { "name": "hackathon-cluster", "type": "CLUSTER" }
  ]
}
```

**Common Errors:**
- `409`: Username already exists in this project

---

### List Database Users

Lists all database users in a project. Used for auditing.

```
GET /groups/{groupId}/databaseUsers
```

**Response (200):**
```json
{
  "results": [
    {
      "username": "team-d4e5f6",
      "databaseName": "admin",
      "roles": [{ "roleName": "readWriteAnyDatabase", "databaseName": "admin" }]
    }
  ],
  "totalCount": 1
}
```

---

## IP Access List Operations

### Add IP Access Entries

Adds one or more IP addresses or CIDR blocks to the project's access list.

```
POST /groups/{groupId}/accessList
```

**Request Body (array):**
```json
[
  {
    "cidrBlock": "0.0.0.0/0",
    "comment": "Hackathon open access"
  }
]
```

Alternative format for single IPs:
```json
[
  {
    "ipAddress": "203.0.113.50",
    "comment": "Workshop participant"
  }
]
```

**Response:** `201 Created`

**Common Errors:**
- `400`: Invalid CIDR notation
- `409`: Entry already exists (safe to ignore)

**Notes:**
- `0.0.0.0/0` allows all IPv4 addresses -- standard for hackathons where participants have dynamic IPs
- For production workshops, use specific CIDRs
- Entries can take up to 60 seconds to propagate

---

## Error Response Format

All Atlas API errors follow this structure:

```json
{
  "errorCode": "DUPLICATE_CLUSTER_NAME",
  "detail": "A cluster with name hackathon-cluster already exists in this project.",
  "reason": "Conflict",
  "parameters": []
}
```

The provisioning system wraps these in `AtlasApiError` with `statusCode` and `atlasError` properties for structured error handling.

## Rate Limits

Atlas Admin API has rate limits that vary by endpoint:
- Most endpoints: 100 requests per minute per project
- Cluster creation: Lower limits apply
- The provisioning system does not implement explicit rate limiting because it provisions one cluster at a time per team

If rate-limited, the API returns `429 Too Many Requests` with a `Retry-After` header.
