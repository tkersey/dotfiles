# Agentic-Flow SDK Examples

## Topologies
```typescript
await swarm.init({
  topology: 'mesh',
  agents: ['coder', 'tester', 'reviewer'],
  communication: 'broadcast'
});
```

```typescript
await swarm.init({
  topology: 'hierarchical',
  queen: 'architect',
  workers: ['backend-dev', 'frontend-dev', 'db-designer']
});
```

```typescript
await swarm.init({
  topology: 'adaptive',
  optimization: 'task-complexity'
});
```

## Orchestration Modes
```typescript
const results = await swarm.execute({
  tasks: [
    { agent: 'coder', task: 'Implement API endpoints' },
    { agent: 'frontend', task: 'Build UI components' },
    { agent: 'tester', task: 'Write test suite' }
  ],
  mode: 'parallel',
  timeout: 300000
});
```

```typescript
await swarm.pipeline([
  { stage: 'design', agent: 'architect' },
  { stage: 'implement', agent: 'coder', after: 'design' },
  { stage: 'test', agent: 'tester', after: 'implement' },
  { stage: 'review', agent: 'reviewer', after: 'test' }
]);
```

```typescript
await swarm.autoOrchestrate({
  goal: 'Build production-ready API',
  constraints: {
    maxTime: 3600,
    maxAgents: 8,
    quality: 'high'
  }
});
```

## Shared Memory
```typescript
await swarm.memory.store('api-schema', {
  endpoints: ['GET /items', 'POST /items'],
  models: ['Item', 'Error']
});

const schema = await swarm.memory.retrieve('api-schema');
```

## Load Balancing and Resiliency
```typescript
await swarm.enableLoadBalancing({
  strategy: 'dynamic',
  metrics: ['cpu', 'memory', 'task-queue']
});

await swarm.setResiliency({
  retry: { maxAttempts: 3, backoff: 'exponential' },
  fallback: 'reassign-task'
});
```

## Metrics
```typescript
const metrics = await swarm.getMetrics();
// { throughput, latency, success_rate, agent_utilization }
```
