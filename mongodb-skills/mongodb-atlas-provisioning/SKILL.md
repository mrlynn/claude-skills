---
name: mongodb-atlas-provisioning
description: Self-service Atlas cluster provisioning with HTTP Digest auth, Admin API v2 client, 9-step orchestration with rollback, status polling, and DevRel attribution tracking
license: MIT
metadata:
  version: 1.0.0
  author: Michael Lynn [mlynn.org](https://mlynn.org)
  category: mongodb-devrel
  domain: cloud-infrastructure
  updated: 2026-03-01
  python-tools: atlas_cost_estimator.py
  tech-stack: atlas-admin-api, digest-auth, mongoose
---

# mongodb-atlas-provisioning

## Trigger

Use this skill when building self-service Atlas cluster management, programmatic Atlas Admin API integration, or any feature that provisions MongoDB resources for users/teams. This is MongoDB DevRel's most unique and strategically valuable pattern.

> *This is the one that makes people's eyes light up in demos. Self-service cluster provisioning is MongoDB's secret weapon for hackathon platforms.* — ML

## Overview

This skill provides a complete Atlas Admin API v2 client with HTTP Digest authentication, a 9-step provisioning orchestration with automatic rollback on failure, status polling, cluster cleanup, and DevRel attribution tracking. It enables self-service M0 cluster provisioning for hackathons, workshops, training sessions, and any event where participants need their own MongoDB instance.

## How to Use

### Quick Start
Invoke with `/mongodb-atlas-provisioning` or let Claude auto-activate when building Atlas cluster management features.

### Python Tools
- `scripts/atlas_cost_estimator.py` — Estimate monthly Atlas cost for a cluster configuration

### Reference Docs
- `references/provisioning-lifecycle.md` — 9-step provisioning flow with rollback rules
- `references/atlas-api-reference.md` — Key Atlas Admin API v2 endpoints used

### Templates & Samples
- `assets/sample_provisioning_config.json` — Example atlasProvisioning subdocument
- `assets/sample_cluster_document.json` — Example AtlasCluster model document

## Architecture Decisions

- **HTTP Digest Auth**: Atlas Admin API v2 uses HTTP Digest Authentication, not Bearer tokens or API keys. The `digest-fetch` library handles the challenge-response protocol.
- **Versioned Accept header**: Atlas API requires `application/vnd.atlas.YYYY-MM-DD+json` Accept headers. This ensures API compatibility and enables new features.
- **Idempotent provisioning**: Before creating resources, always check if they already exist. This prevents duplicate clusters from retries or race conditions.
- **Rollback on failure**: If any step in the provisioning flow fails, the Atlas project is deleted to prevent orphaned resources.
- **One-time credential display**: Database passwords are generated, used to create the Atlas user, then returned to the caller exactly once. They are never stored in the platform database.
- **DevRel attribution via appName**: Connection strings include `appName=devrel-platform-hackathon-atlas` for MongoDB internal tracking of DevRel-generated usage.

## File Structure

```
src/lib/atlas/
├── atlas-client.ts           # HTTP Digest auth + typed CRUD operations
├── provisioning-service.ts   # 9-step orchestration with rollback
├── status-service.ts         # Poll Atlas API for cluster status
├── utils.ts                  # Password gen, name sanitization, attribution
└── auth-guard.ts             # Team leader/member verification
```

## Code Patterns

### Pattern 1: Atlas Admin API v2 Client

```typescript
// src/lib/atlas/atlas-client.ts
import DigestFetch from 'digest-fetch';

const ATLAS_BASE_URL = process.env.ATLAS_BASE_URL || 'https://cloud.mongodb.com/api/atlas/v2';
const ATLAS_PUBLIC_KEY = process.env.ATLAS_PUBLIC_KEY!;
const ATLAS_PRIVATE_KEY = process.env.ATLAS_PRIVATE_KEY!;
const ATLAS_ORG_ID = process.env.ATLAS_ORG_ID!;
const ATLAS_API_VERSION = '2025-03-12';

let digestClient: DigestFetch | null = null;

function getDigestClient(): DigestFetch {
  if (!digestClient) {
    digestClient = new DigestFetch(ATLAS_PUBLIC_KEY, ATLAS_PRIVATE_KEY);
  }
  return digestClient;
}

export class AtlasApiError extends Error {
  constructor(
    public statusCode: number,
    public atlasError: { errorCode?: string; detail?: string; reason?: string }
  ) {
    super(`Atlas API error ${statusCode}: ${atlasError.detail || atlasError.reason || 'Unknown'}`);
    this.name = 'AtlasApiError';
  }
}

async function atlasRequest<T>(
  path: string,
  options: { method: 'GET' | 'POST' | 'PATCH' | 'DELETE'; body?: unknown }
): Promise<T> {
  const url = `${ATLAS_BASE_URL}${path}`;
  const client = getDigestClient();

  const headers: Record<string, string> = {
    Accept: `application/vnd.atlas.${ATLAS_API_VERSION}+json`,
    'Content-Type': 'application/json',
  };

  try {
    const response = await client.fetch(url, {
      method: options.method,
      headers,
      body: options.body ? JSON.stringify(options.body) : undefined,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new AtlasApiError(response.status, error);
    }
    if (response.status === 204) return undefined as T;
    return response.json() as Promise<T>;
  } catch (error) {
    if (error instanceof AtlasApiError) throw error;
    throw new Error(`Atlas API request failed: ${(error as Error).message}`);
  }
}

// --- Type Definitions ---
export interface AtlasProject { id: string; name: string; orgId: string; }
export interface AtlasClusterResponse {
  id?: string; name: string; stateName: string; mongoDBVersion?: string;
  connectionStrings?: { standard?: string; standardSrv?: string };
}
export interface AtlasDbUser {
  username: string; databaseName: string;
  roles: { roleName: string; databaseName: string }[];
}
export interface IpAccessEntry { cidrBlock: string; comment?: string; }

// --- Project Operations ---
export async function createAtlasProject(name: string): Promise<AtlasProject> {
  return atlasRequest('/groups', { method: 'POST', body: { name, orgId: ATLAS_ORG_ID } });
}
export async function getAtlasProjectByName(name: string): Promise<AtlasProject> {
  return atlasRequest(`/groups/byName/${encodeURIComponent(name)}`, { method: 'GET' });
}
export async function deleteAtlasProject(groupId: string): Promise<void> {
  return atlasRequest(`/groups/${groupId}`, { method: 'DELETE' });
}

// --- Cluster Operations (M0 free tier) ---
export async function createM0Cluster(
  groupId: string,
  config: { name: string; backingProvider: 'AWS' | 'GCP' | 'AZURE'; region: string }
): Promise<AtlasClusterResponse> {
  return atlasRequest(`/groups/${groupId}/clusters`, {
    method: 'POST',
    body: {
      name: config.name,
      clusterType: 'REPLICASET',
      replicationSpecs: [{
        regionConfigs: [{
          providerName: 'TENANT',
          backingProviderName: config.backingProvider,
          regionName: config.region,
          priority: 7,
          electableSpecs: { instanceSize: 'M0' },
        }],
      }],
    },
  });
}
export async function getAtlasCluster(groupId: string, name: string): Promise<AtlasClusterResponse> {
  return atlasRequest(`/groups/${groupId}/clusters/${name}`, { method: 'GET' });
}
export async function deleteAtlasCluster(groupId: string, name: string): Promise<void> {
  return atlasRequest(`/groups/${groupId}/clusters/${name}`, { method: 'DELETE' });
}

// --- Database User Operations ---
export async function createAtlasDatabaseUser(
  groupId: string,
  config: { username: string; password: string; clusterName: string; roles?: { roleName: string; databaseName: string }[] }
): Promise<AtlasDbUser> {
  return atlasRequest(`/groups/${groupId}/databaseUsers`, {
    method: 'POST',
    body: {
      databaseName: 'admin',
      username: config.username,
      password: config.password,
      roles: config.roles || [{ roleName: 'readWriteAnyDatabase', databaseName: 'admin' }],
      scopes: [{ name: config.clusterName, type: 'CLUSTER' }],
    },
  });
}
export async function listAtlasDatabaseUsers(groupId: string): Promise<AtlasDbUser[]> {
  const response = await atlasRequest<{ results: AtlasDbUser[] }>(`/groups/${groupId}/databaseUsers`, { method: 'GET' });
  return response.results || [];
}

// --- IP Access List ---
export async function addIpAccessListEntries(
  groupId: string,
  entries: { cidrBlock?: string; ipAddress?: string; comment?: string }[]
): Promise<void> {
  return atlasRequest(`/groups/${groupId}/accessList`, { method: 'POST', body: entries });
}
```

### Pattern 2: Provisioning Service with Rollback

```typescript
// src/lib/atlas/provisioning-service.ts
import { connectToDatabase } from '@/lib/db/connection';
import { AtlasClusterModel } from '@/lib/db/models/AtlasCluster';
import { EventModel } from '@/lib/db/models/Event';
import * as atlas from './atlas-client';
import { generateSecurePassword, generateAtlasProjectName, addAppNameToConnectionString } from './utils';

export class ConflictError extends Error {
  constructor(message: string) { super(message); this.name = 'ConflictError'; }
}

export interface ProvisionClusterParams {
  eventId: string; teamId: string; projectId: string; userId: string;
  provider?: 'AWS' | 'GCP' | 'AZURE'; region?: string;
}

export async function provisionCluster(params: ProvisionClusterParams) {
  await connectToDatabase();

  // 1. Validate event has provisioning enabled
  const event = await EventModel.findById(params.eventId);
  if (!event?.atlasProvisioning?.enabled) throw new Error('Provisioning not enabled');

  // 2. Check for existing cluster (idempotency)
  const existing = await AtlasClusterModel.findOne({
    eventId: params.eventId, teamId: params.teamId, status: { $nin: ['deleted', 'error'] },
  });
  if (existing) throw new ConflictError('Cluster already exists for this team');

  // 2b. Clean up old records to avoid unique index collision
  await AtlasClusterModel.deleteMany({
    eventId: params.eventId, teamId: params.teamId, status: { $in: ['deleted', 'error'] },
  });

  // 3. Resolve provider/region from event defaults
  const provider = params.provider || event.atlasProvisioning.defaultProvider || 'AWS';
  const region = params.region || event.atlasProvisioning.defaultRegion || 'US_EAST_1';

  // 4. Generate names
  const projectName = generateAtlasProjectName(params.eventId, params.teamId);
  const clusterName = 'hackathon-cluster';

  let atlasProject: atlas.AtlasProject | null = null;

  try {
    // 5. Resolve or create Atlas project
    try {
      atlasProject = await atlas.getAtlasProjectByName(projectName);
    } catch {
      atlasProject = await atlas.createAtlasProject(projectName);
    }

    // 6. Create M0 cluster
    const clusterResponse = await atlas.createM0Cluster(atlasProject.id, {
      name: clusterName, backingProvider: provider, region,
    });

    // 7. Create database user
    const dbUsername = `team-${params.teamId.slice(-6)}`;
    const dbPassword = generateSecurePassword();
    await atlas.createAtlasDatabaseUser(atlasProject.id, {
      username: dbUsername, password: dbPassword, clusterName,
    });

    // 8. Configure IP access
    if (event.atlasProvisioning.openNetworkAccess) {
      await atlas.addIpAccessListEntries(atlasProject.id, [
        { cidrBlock: '0.0.0.0/0', comment: 'Hackathon open access' },
      ]);
    }

    // 9. Save to platform database
    const clusterDoc = await AtlasClusterModel.create({
      eventId: params.eventId, teamId: params.teamId,
      projectId: params.projectId, provisionedBy: params.userId,
      atlasProjectId: atlasProject.id, atlasProjectName: projectName,
      atlasClusterName: clusterName, atlasClusterId: clusterResponse.id || '',
      connectionString: addAppNameToConnectionString(clusterResponse.connectionStrings?.standardSrv || ''),
      standardConnectionString: addAppNameToConnectionString(clusterResponse.connectionStrings?.standard || ''),
      databaseUsers: [{ username: dbUsername, createdAt: new Date(), createdBy: params.userId }],
      status: 'creating', providerName: provider, regionName: region,
    });

    // Return with one-time credentials (password is NEVER stored)
    return { ...clusterDoc.toObject(), _initialCredentials: { username: dbUsername, password: dbPassword } };
  } catch (error) {
    // ROLLBACK: delete Atlas project if provisioning failed
    if (atlasProject?.id) {
      try { await atlas.deleteAtlasProject(atlasProject.id); } catch { /* log only */ }
    }
    throw error;
  }
}
```

### Pattern 3: Utility Functions

```typescript
// src/lib/atlas/utils.ts
import crypto from 'crypto';

export function generateSecurePassword(length: number = 24): string {
  const upper = 'ABCDEFGHJKLMNPQRSTUVWXYZ';
  const lower = 'abcdefghjkmnpqrstuvwxyz';
  const nums = '23456789';
  const special = '!@#$%^&*-_=+';

  let pw = '';
  pw += upper[crypto.randomInt(upper.length)];
  pw += lower[crypto.randomInt(lower.length)];
  pw += nums[crypto.randomInt(nums.length)];
  pw += special[crypto.randomInt(special.length)];

  const all = upper + lower + nums + special;
  for (let i = 4; i < length; i++) pw += all[crypto.randomInt(all.length)];

  return pw.split('').sort(() => crypto.randomInt(3) - 1).join('');
}

export function sanitizeClusterName(name: string): string {
  return name.toLowerCase().replace(/[^a-z0-9-]/g, '-').replace(/^-+|-+$/g, '').replace(/-+/g, '-').substring(0, 64);
}

export function mapAtlasStateToPlatformStatus(state: string) {
  const map: Record<string, string> = {
    CREATING: 'creating', IDLE: 'active', UPDATING: 'active',
    DELETING: 'deleting', DELETED: 'deleted', REPAIRING: 'active',
  };
  return map[state] || 'active';
}

export function generateAtlasProjectName(eventId: string, teamId: string): string {
  return `mh-${eventId.slice(-6)}-${teamId.slice(-6)}`;
}

export const DEVREL_APP_NAME = 'devrel-platform-hackathon-atlas';

export function addAppNameToConnectionString(cs: string): string {
  if (!cs || cs.includes(`appName=${DEVREL_APP_NAME}`)) return cs;
  const sep = cs.includes('?') ? '&' : '?';
  return `${cs}${sep}appName=${DEVREL_APP_NAME}`;
}
```

### Pattern 4: Status Polling Service

```typescript
// src/lib/atlas/status-service.ts
import { connectToDatabase } from '@/lib/db/connection';
import { AtlasClusterModel } from '@/lib/db/models/AtlasCluster';
import * as atlas from './atlas-client';
import { mapAtlasStateToPlatformStatus, addAppNameToConnectionString } from './utils';

export async function refreshClusterStatus(clusterId: string) {
  await connectToDatabase();
  const cluster = await AtlasClusterModel.findById(clusterId);
  if (!cluster) throw new Error('Cluster not found');
  if (cluster.status === 'deleted') return { atlasState: 'DELETED', platformStatus: 'deleted', connectionString: '', mongoDBVersion: '' };

  try {
    const atlasCluster = await atlas.getAtlasCluster(cluster.atlasProjectId, cluster.atlasClusterName);
    const platformStatus = mapAtlasStateToPlatformStatus(atlasCluster.stateName);
    cluster.status = platformStatus;
    cluster.connectionString = addAppNameToConnectionString(atlasCluster.connectionStrings?.standardSrv || cluster.connectionString);
    cluster.mongoDBVersion = atlasCluster.mongoDBVersion || '';
    cluster.lastStatusCheck = new Date();
    await cluster.save();
    return { atlasState: atlasCluster.stateName, platformStatus, connectionString: cluster.connectionString, mongoDBVersion: cluster.mongoDBVersion };
  } catch (error) {
    cluster.status = 'error';
    cluster.errorMessage = `Status check failed: ${(error as Error).message}`;
    cluster.lastStatusCheck = new Date();
    await cluster.save();
    throw error;
  }
}
```

### Pattern 5: AtlasCluster Model

```typescript
// src/lib/db/models/AtlasCluster.ts
import { Schema, model, models, Document, Types } from 'mongoose';

export interface IAtlasCluster extends Document {
  eventId: Types.ObjectId; teamId: Types.ObjectId; projectId: Types.ObjectId; provisionedBy: Types.ObjectId;
  atlasProjectId: string; atlasProjectName: string; atlasClusterName: string; atlasClusterId: string;
  connectionString: string; standardConnectionString: string;
  databaseUsers: { username: string; createdAt: Date; createdBy: Types.ObjectId }[];
  ipAccessList: { cidrBlock: string; comment: string; addedAt: Date; addedBy: Types.ObjectId }[];
  status: 'creating' | 'idle' | 'active' | 'deleting' | 'deleted' | 'error';
  providerName: 'AWS' | 'GCP' | 'AZURE'; regionName: string; mongoDBVersion: string;
  errorMessage?: string; lastStatusCheck: Date; deletedAt?: Date;
}

const AtlasClusterSchema = new Schema<IAtlasCluster>({
  eventId: { type: Schema.Types.ObjectId, ref: 'Event', required: true },
  teamId: { type: Schema.Types.ObjectId, ref: 'Team', required: true },
  projectId: { type: Schema.Types.ObjectId, ref: 'Project', required: true },
  provisionedBy: { type: Schema.Types.ObjectId, ref: 'User', required: true },
  atlasProjectId: { type: String, required: true, unique: true },
  atlasProjectName: { type: String, required: true },
  atlasClusterName: { type: String, required: true },
  atlasClusterId: { type: String, default: '' },
  connectionString: { type: String, default: '' },
  standardConnectionString: { type: String, default: '' },
  databaseUsers: [{ username: { type: String, required: true }, createdAt: { type: Date, default: Date.now }, createdBy: { type: Schema.Types.ObjectId, ref: 'User', required: true } }],
  ipAccessList: [{ cidrBlock: { type: String, required: true }, comment: { type: String, default: '' }, addedAt: { type: Date, default: Date.now }, addedBy: { type: Schema.Types.ObjectId, ref: 'User', required: true } }],
  status: { type: String, enum: ['creating', 'idle', 'active', 'deleting', 'deleted', 'error'], default: 'creating' },
  providerName: { type: String, enum: ['AWS', 'GCP', 'AZURE'], default: 'AWS' },
  regionName: { type: String, default: 'US_EAST_1' },
  mongoDBVersion: { type: String, default: '' },
  errorMessage: { type: String },
  lastStatusCheck: { type: Date, default: Date.now },
  deletedAt: { type: Date },
}, { timestamps: true });

AtlasClusterSchema.index({ eventId: 1, teamId: 1 }, { unique: true });
AtlasClusterSchema.index({ atlasProjectId: 1 });
AtlasClusterSchema.index({ eventId: 1, status: 1 });

export const AtlasClusterModel = models.AtlasCluster || model<IAtlasCluster>('AtlasCluster', AtlasClusterSchema);
```

### Pattern 6: Event Model Atlas Config

Add this subdocument to your Event model to control provisioning per-event:

```typescript
atlasProvisioning: {
  enabled: { type: Boolean, default: false },
  defaultProvider: { type: String, enum: ['AWS', 'GCP', 'AZURE'], default: 'AWS' },
  defaultRegion: { type: String, default: 'US_EAST_1' },
  openNetworkAccess: { type: Boolean, default: true },   // 0.0.0.0/0
  maxDbUsersPerCluster: { type: Number, default: 5 },
  autoCleanupOnEventEnd: { type: Boolean, default: true },
  allowedProviders: [{ type: String, enum: ['AWS', 'GCP', 'AZURE'] }],
  allowedRegions: [{ type: String }],
}
```

## Environment Variables

```bash
ATLAS_PUBLIC_KEY=your-atlas-public-key
ATLAS_PRIVATE_KEY=your-atlas-private-key
ATLAS_ORG_ID=your-atlas-org-id
ATLAS_BASE_URL=https://cloud.mongodb.com/api/atlas/v2  # Optional override
```

## Dependencies

```bash
npm install digest-fetch
```

## Common Pitfalls

- **Never store database passwords.** The password is generated, sent to Atlas, returned to the user once, and discarded. It's never saved in the platform DB.
- **Always check for existing resources before creating.** Atlas operations are not idempotent — creating a duplicate project/cluster will fail.
- **Handle 404/409 gracefully during cleanup.** When deleting clusters, the cluster may already be gone (404) or still terminating (409). Ignore these errors.
- **Use `0.0.0.0/0` for hackathon IP access.** Participants don't have static IPs. For production workshops, require specific CIDRs.
- **Poll for status, don't assume instant creation.** M0 clusters take 1-3 minutes to provision. Poll `refreshClusterStatus()` until the status changes from `creating` to `active`.
- **Include appName in connection strings.** This is required for DevRel attribution tracking within MongoDB.
