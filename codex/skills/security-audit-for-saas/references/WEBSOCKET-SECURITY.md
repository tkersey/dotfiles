# WebSocket Security

WebSockets are long-lived bidirectional channels. Most REST security patterns
don't apply directly. Authentication, authorization, rate limiting, and CSRF
all need different approaches.

---

## The WebSocket-Specific Risks

1. **Authentication during upgrade** — only happens once
2. **Authorization per message** — must be checked repeatedly
3. **Cross-Site WebSocket Hijacking** — WebSockets don't enforce CORS
4. **Message injection** — no input validation if not explicit
5. **Channel/topic authorization** — who can subscribe? who can publish?
6. **Connection limits** — DoS via many connections
7. **Unbounded state** — per-connection memory/state grows

---

## Authentication on Upgrade

### Problem
HTTP auth works on request. WebSocket upgrade is a single request — after
that, it's a TCP connection with no HTTP semantics.

### Solutions

**Option A: Cookie-based (simplest)**
The upgrade request includes cookies. Server validates session cookie.

```typescript
import { WebSocketServer } from 'ws';

const wss = new WebSocketServer({
  verifyClient: async (info, done) => {
    const cookies = parseCookies(info.req.headers.cookie);
    const session = await validateSession(cookies.sessionId);
    if (!session) {
      done(false, 401, 'Unauthorized');
      return;
    }
    info.req.user = session.user; // Attach to request for later
    done(true);
  },
});
```

**Problem:** Subject to CSWSH (see below).

**Option B: Token in query parameter**
```typescript
// Client:
const ws = new WebSocket(`wss://api.example.com/ws?token=${accessToken}`);

// Server:
const url = new URL(req.url, 'http://localhost');
const token = url.searchParams.get('token');
const user = await verifyToken(token);
```

**Problem:** Token may appear in logs (server logs URLs).

**Option C: Token in initial message**
```typescript
// After connection, first message must be auth
ws.send(JSON.stringify({ type: 'auth', token: accessToken }));
```

```typescript
// Server
ws.on('message', async (raw) => {
  const msg = JSON.parse(raw);
  if (!ws.authenticated) {
    if (msg.type === 'auth') {
      const user = await verifyToken(msg.token);
      if (user) {
        ws.authenticated = true;
        ws.user = user;
      } else {
        ws.close(4001, 'Auth failed');
      }
    } else {
      ws.close(4002, 'Auth required');
    }
    return;
  }
  // Handle authenticated messages
});
```

**Best:** Option C. Keeps tokens out of URLs and cookies out of the auth
decision.

---

## Cross-Site WebSocket Hijacking (CSWSH)

### The attack
Browser's same-origin policy doesn't apply to WebSockets. Any origin can open
a WebSocket to any URL. If you use cookies for WebSocket auth, a malicious
site can establish a WebSocket to your server on behalf of the victim's
browser, with their cookies.

### The fix

**Option A: Check `Origin` header on upgrade**
```typescript
const wss = new WebSocketServer({
  verifyClient: (info, done) => {
    const origin = info.req.headers.origin;
    const ALLOWED = ['https://app.example.com', 'https://example.com'];
    if (!ALLOWED.includes(origin)) {
      done(false, 403, 'Forbidden');
      return;
    }
    // ... then auth check
  },
});
```

**Option B: Don't use cookies for WebSocket auth**
Use token-in-first-message (Option C above). Tokens aren't sent automatically
by the browser, so CSWSH doesn't work.

---

## Per-Message Authorization

### The problem
Once authenticated, a client can send any message. Authorization must be
checked per message.

```typescript
ws.on('message', async (raw) => {
  const msg = JSON.parse(raw);

  switch (msg.type) {
    case 'subscribe':
      if (!canSubscribe(ws.user, msg.channel)) {
        ws.send(JSON.stringify({ error: 'Forbidden' }));
        return;
      }
      subscribeClient(ws, msg.channel);
      break;

    case 'publish':
      if (!canPublish(ws.user, msg.channel)) {
        ws.send(JSON.stringify({ error: 'Forbidden' }));
        return;
      }
      publishMessage(msg.channel, msg.payload);
      break;

    case 'admin_command':
      if (!ws.user.isAdmin) {
        ws.send(JSON.stringify({ error: 'Forbidden' }));
        return;
      }
      // ...
      break;
  }
});
```

---

## Channel/Topic Authorization

### Pub/sub authorization patterns

**Channel-based:**
```typescript
type Channel =
  | { type: 'user'; userId: string }           // user:alice — only alice can read/write
  | { type: 'org'; orgId: string }             // org:acme — members can read/write
  | { type: 'public' }                          // public — all can read, admin can write
  | { type: 'agent'; agentId: string };        // agent:bot — agent + admin

function canSubscribe(user: User, channel: Channel): boolean {
  switch (channel.type) {
    case 'user':
      return user.id === channel.userId;
    case 'org':
      return isOrgMember(user, channel.orgId);
    case 'public':
      return true;
    case 'agent':
      return user.id === channel.agentId || user.isAdmin;
    default: {
      const _exhaustive: never = channel;
      return false; // Unknown channel type → deny
    }
  }
}

function canPublish(user: User, channel: Channel): boolean {
  // Different from subscribe: publish is usually more restrictive
  switch (channel.type) {
    case 'user':
      return user.id === channel.userId;
    case 'org':
      return isOrgMember(user, channel.orgId) && user.canSend;
    case 'public':
      return user.isAdmin;  // Only admins can publish public messages
    case 'agent':
      return user.id === channel.agentId;  // Only the agent itself
    default: {
      const _exhaustive: never = channel;
      return false;
    }
  }
}
```

**Critical:** exhaustive type check (`_exhaustive: never`) forces compile-time
coverage when new channel types are added.

---

## Message Validation

Every message from a client must be validated:

```typescript
import { z } from 'zod';

const MessageSchema = z.discriminatedUnion('type', [
  z.object({
    type: z.literal('subscribe'),
    channel: z.string().max(200),
  }),
  z.object({
    type: z.literal('publish'),
    channel: z.string().max(200),
    payload: z.unknown(), // Further validation based on channel
  }),
  z.object({
    type: z.literal('ping'),
  }),
]);

ws.on('message', async (raw) => {
  let msg;
  try {
    const parsed = JSON.parse(raw.toString());
    msg = MessageSchema.parse(parsed);
  } catch {
    ws.send(JSON.stringify({ error: 'Invalid message' }));
    return;
  }
  // ...
});
```

---

## Rate Limiting

### Per-connection rate limits
```typescript
const messageRateLimit = new Map<WebSocket, { count: number; resetAt: number }>();

function checkRateLimit(ws: WebSocket, max = 60): boolean {
  const now = Date.now();
  const state = messageRateLimit.get(ws) ?? { count: 0, resetAt: now + 60_000 };

  if (now > state.resetAt) {
    state.count = 0;
    state.resetAt = now + 60_000;
  }

  state.count++;
  messageRateLimit.set(ws, state);

  return state.count <= max;
}

ws.on('message', (raw) => {
  if (!checkRateLimit(ws)) {
    ws.close(4003, 'Rate limited');
    return;
  }
  // ...
});
```

### Per-user connection limits
```typescript
const userConnections = new Map<string, Set<WebSocket>>();

wss.on('connection', (ws, req) => {
  const userId = req.user.id;
  const connections = userConnections.get(userId) ?? new Set();
  if (connections.size >= 10) {
    ws.close(4004, 'Too many connections');
    return;
  }
  connections.add(ws);
  userConnections.set(userId, connections);

  ws.on('close', () => {
    connections.delete(ws);
  });
});
```

---

## Connection Limits (DoS Prevention)

### Global limits
```typescript
const MAX_TOTAL_CONNECTIONS = 10_000;

wss.on('connection', (ws) => {
  if (wss.clients.size > MAX_TOTAL_CONNECTIONS) {
    ws.close(1013, 'Server full');
    return;
  }
});
```

### Per-IP limits
```typescript
const ipConnections = new Map<string, number>();

wss.on('connection', (ws, req) => {
  const ip = getClientIp(req);
  const count = ipConnections.get(ip) ?? 0;
  if (count >= 5) {
    ws.close(1013, 'Too many connections from this IP');
    return;
  }
  ipConnections.set(ip, count + 1);

  ws.on('close', () => {
    const newCount = (ipConnections.get(ip) ?? 1) - 1;
    if (newCount <= 0) ipConnections.delete(ip);
    else ipConnections.set(ip, newCount);
  });
});
```

---

## Heartbeat / Connection Health

WebSockets can die silently. Use heartbeats to detect and clean up dead
connections.

```typescript
function heartbeat() {
  this.isAlive = true;
}

wss.on('connection', (ws) => {
  ws.isAlive = true;
  ws.on('pong', heartbeat);
});

const interval = setInterval(() => {
  wss.clients.forEach((ws) => {
    if (!ws.isAlive) {
      ws.terminate();
      return;
    }
    ws.isAlive = false;
    ws.ping();
  });
}, 30_000);
```

---

## Resource Leaks

### Per-connection state must be bounded
```typescript
// BAD: unbounded state per connection
ws.userEvents = []; // Could grow indefinitely

// GOOD: bounded with LRU eviction
ws.userEvents = new LRU({ max: 1000 });
```

### Clean up on disconnect
```typescript
ws.on('close', () => {
  // Remove from all subscribed channels
  channels.forEach(ch => ch.unsubscribe(ws));
  // Remove from user connection map
  userConnections.get(ws.user.id)?.delete(ws);
  // Clear rate limit state
  messageRateLimit.delete(ws);
  // Clear any timers
  clearTimeout(ws.heartbeatTimer);
});
```

---

## The WebSocket Audit Checklist

### Authentication
- [ ] Origin header validated on upgrade
- [ ] Auth via first message (not cookies)
- [ ] Token validation is constant-time
- [ ] Unauthenticated connections close quickly

### Authorization
- [ ] Per-message authorization check
- [ ] Separate `canSubscribe` and `canPublish` logic
- [ ] Exhaustive check on channel types (TypeScript `never`)
- [ ] Admin actions gated separately

### Validation
- [ ] Every message validated with Zod/similar
- [ ] Max message size enforced
- [ ] Max payload fields enforced

### Rate limiting
- [ ] Per-connection message rate limit
- [ ] Per-user connection count limit
- [ ] Per-IP connection count limit
- [ ] Global connection limit

### Resource management
- [ ] Heartbeat/ping to detect dead connections
- [ ] State per connection is bounded
- [ ] All state cleaned up on disconnect
- [ ] Timeouts on idle connections

### Monitoring
- [ ] Track connection count over time
- [ ] Alert on unusual spikes
- [ ] Log auth failures
- [ ] Log authorization denials

---

## See Also

- [AUTH.md](AUTH.md)
- [API-SECURITY.md](API-SECURITY.md)
- [RATE-LIMITING.md](RATE-LIMITING.md)
- [COOKBOOK.md](COOKBOOK.md) — WebSocket pub/sub ACL pattern
