# GraphQL Security

GraphQL is flexible but opens a large attack surface. Security-in-depth
problems that REST APIs handle trivially become complex in GraphQL.

---

## The GraphQL-Specific Risks

### 1. Query Depth Attacks (DoS)
### 2. Query Complexity Attacks (DoS)
### 3. Introspection Information Disclosure
### 4. Field-Level Authorization Bypass
### 5. Batching Attacks
### 6. Aliasing Attacks
### 7. IDOR via Flexible Queries
### 8. Mass Assignment via Mutations

---

## Query Depth Attacks

### The attack
```graphql
query {
  user(id: "1") {
    friends {
      friends {
        friends {
          friends {
            friends {
              friends {
                # nested 100 levels deep
                id name
              }
            }
          }
        }
      }
    }
  }
}
```

Each level multiplies the query. 100 levels × 10 friends = 10^100 database
queries.

### The fix
Limit query depth:
```typescript
import depthLimit from 'graphql-depth-limit';

const server = new ApolloServer({
  validationRules: [depthLimit(10)], // max 10 levels
});
```

---

## Query Complexity Attacks

### The attack
```graphql
query {
  users(first: 1000) {
    posts(first: 1000) {
      comments(first: 1000) {
        replies(first: 1000) {
          id
        }
      }
    }
  }
}
```

Without limits, that's 10^12 rows.

### The fix
Assign cost to each field and limit total:
```typescript
import costAnalysis from 'graphql-cost-analysis';

const server = new ApolloServer({
  validationRules: [
    costAnalysis({
      maximumCost: 1000,
      defaultCost: 1,
      variables: {},
      createError: (max, actual) => new Error(`Query exceeds cost ${max}: ${actual}`),
    }),
  ],
});
```

In schema:
```graphql
type Query {
  users(first: Int!): [User] @cost(complexity: 10, multipliers: ["first"])
}
```

---

## Introspection

### The risk
GraphQL introspection lets anyone query the schema, revealing all types and
fields. Attackers use this to map your API.

### The fix
Disable introspection in production:
```typescript
const server = new ApolloServer({
  introspection: process.env.NODE_ENV !== 'production',
});
```

**Tradeoff:** Some tools (Apollo Studio, Sentry) rely on introspection. Use
persisted queries or schema registries instead.

---

## Field-Level Authorization

### The problem
REST APIs have per-endpoint auth. GraphQL needs per-field auth.

```graphql
type User {
  id: ID
  email: String          # Should be private to owner
  publicName: String     # Public
  stripeCustomerId: String  # Should be admin only
}
```

### The fix
Use directives or middleware:

```typescript
const typeDefs = `
  directive @auth(requires: Role = USER) on FIELD_DEFINITION

  enum Role { USER ADMIN OWNER }

  type User {
    id: ID!
    publicName: String!
    email: String! @auth(requires: USER)
    stripeCustomerId: String @auth(requires: ADMIN)
  }
`;

// Resolver
const resolvers = {
  User: {
    email(user, _, context) {
      if (context.user.id !== user.id && !context.user.isAdmin) {
        throw new Error('Forbidden');
      }
      return user.email;
    },
  },
};
```

---

## Batching Attacks

### The attack
GraphQL servers often allow multiple queries in a single HTTP request. This
can bypass rate limiting.

```json
[
  {"query": "query { login(email: \"a@x.com\", password: \"pass1\") }"},
  {"query": "query { login(email: \"a@x.com\", password: \"pass2\") }"},
  {"query": "query { login(email: \"a@x.com\", password: \"pass3\") }"},
  // 1000 attempts in a single HTTP request
]
```

### The fix
Disable query batching OR rate-limit per operation, not per request:

```typescript
const server = new ApolloServer({
  allowBatchedHttpRequests: false,  // Disable batching
});
```

---

## Aliasing Attacks

### The attack
Aliases let you query the same field multiple times:
```graphql
query {
  a: login(email: "a@x.com", password: "pass1") { token }
  b: login(email: "a@x.com", password: "pass2") { token }
  c: login(email: "a@x.com", password: "pass3") { token }
  # 1000 aliases = 1000 login attempts in one query
}
```

### The fix
Rate-limit the resolver itself, not the HTTP request.

```typescript
const resolvers = {
  Mutation: {
    async login(_, { email, password }, context) {
      // Rate limit per email (not per request)
      if (!await checkRateLimit(`login:${email}`)) {
        throw new Error('Rate limited');
      }
      return await loginUser(email, password);
    },
  },
};
```

---

## IDOR via Flexible Queries

### The attack
GraphQL's flexibility means clients can ask for arbitrary records:
```graphql
query {
  user(id: "victim_id") {  # Not my user
    email
    subscriptions {
      stripeCustomerId
    }
  }
}
```

### The fix
Every resolver must check authorization:

```typescript
const resolvers = {
  Query: {
    user(_, { id }, context) {
      if (context.user.id !== id && !context.user.isAdmin) {
        throw new Error('Forbidden');
      }
      return db.user.findUnique({ where: { id } });
    },
  },
};
```

**Better:** Use an authorization library like `graphql-shield` or
`graphql-ruby` with explicit rules per field.

---

## Persisted Queries

### The pattern
Clients register allowed queries in advance. Server only executes pre-approved
queries.

**Benefits:**
- Prevents arbitrary query attacks
- Prevents introspection-based enumeration
- Faster (server can cache/precompile)
- Reduces payload size (just query hash)

### Implementation
```typescript
import { ApolloServer } from '@apollo/server';

const persistedQueries = new Map<string, string>();
persistedQueries.set('get-user-v1', 'query getUser($id: ID!) { user(id: $id) { ... } }');

const server = new ApolloServer({
  persistedQueries: {
    cache: persistedQueries,
    ttl: null, // Never expire (approved queries only)
  },
});
```

---

## Input Validation

### GraphQL does type validation, not semantic validation
```graphql
mutation { createUser(email: "not-an-email", age: -5) }
```
Type-valid (both strings/ints), but semantically wrong.

### Fix
Use input validation in resolvers:
```typescript
const resolvers = {
  Mutation: {
    createUser(_, { input }) {
      if (!isValidEmail(input.email)) throw new Error('Invalid email');
      if (input.age < 0 || input.age > 150) throw new Error('Invalid age');
      // ...
    },
  },
};
```

Or use scalar types:
```graphql
scalar Email
scalar PositiveInt

type Mutation {
  createUser(email: Email!, age: PositiveInt!): User
}
```

---

## Error Information Leakage

### The problem
GraphQL errors include stack traces by default in development, which may leak
into production.

### The fix
Customize error formatting:
```typescript
const server = new ApolloServer({
  formatError: (formattedError, error) => {
    // Log full error internally
    logger.error({ error }, 'GraphQL error');

    // Return sanitized to client in production
    if (process.env.NODE_ENV === 'production') {
      return {
        message: formattedError.message,
        extensions: {
          code: formattedError.extensions?.code || 'INTERNAL_ERROR',
        },
      };
    }
    return formattedError;
  },
});
```

---

## The GraphQL Security Audit Checklist

### Schema
- [ ] Introspection disabled in production
- [ ] Persisted queries for client-server communication
- [ ] Field-level auth directives or per-resolver checks
- [ ] Scalar types for semantic validation

### Queries
- [ ] Query depth limit configured
- [ ] Query complexity limit configured
- [ ] Batching disabled OR per-operation rate limiting
- [ ] Aliasing does NOT bypass rate limits

### Mutations
- [ ] All mutations require auth
- [ ] Mass assignment prevented (explicit input types)
- [ ] Rate limiting on sensitive mutations (login, password reset)
- [ ] Audit log for mutations

### Errors
- [ ] Error messages sanitized in production
- [ ] Stack traces never returned to client
- [ ] Enumeration-resistant error messages

### Monitoring
- [ ] Track query cost distribution
- [ ] Alert on expensive queries
- [ ] Alert on repeated failed queries (abuse)

---

## Libraries

- **Apollo Server** — most popular GraphQL server
- **graphql-shield** — authorization layer
- **graphql-cost-analysis** — complexity analysis
- **graphql-depth-limit** — depth limiting
- **graphql-rate-limit** — per-field rate limiting

---

## See Also

- [API-SECURITY.md](API-SECURITY.md)
- [AUTH.md](AUTH.md)
- [RATE-LIMITING.md](RATE-LIMITING.md)
