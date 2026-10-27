autoscale: true

# [fit] Practical<br>Algebraic Thinking

## [fit] Making the Type System Work for You

---

# [fit] Previously...

## We explored the mathematical foundations
## Today: **How to use these ideas in production code**

---

# [fit] Two Core Principles

1. **Make types more precise**
2. **Make impossible states impossible**

## Result: Fewer bugs, fewer tests, more confidence

---

# [fit] Part 1:<br>Precise Types

---

# [fit] Branded Types

## The Problem

```typescript
// ❌ Everything is just a string
function transferMoney(
  fromAccountId: string,
  toAccountId: string,
  amount: string
) {
  // Easy to mix up parameters
}

// Oops! Arguments in wrong order
transferMoney("100.00", "acc123", "acc456");
```

---

# [fit] The Solution

```typescript
// ✅ Branded types make misuse impossible
type AccountId = string & { readonly __brand: "AccountId" };
type Money = string & { readonly __brand: "Money" };

function AccountId(value: string): AccountId {
  if (!/^acc\d+$/.test(value)) {
    throw new Error(`Invalid account ID: ${value}`);
  }
  return value as AccountId;
}

function Money(value: string): Money {
  if (!/^\d+\.\d{2}$/.test(value)) {
    throw new Error(`Invalid money format: ${value}`);
  }
  return value as Money;
}
```

---

# [fit] Type Safety in Action

```typescript
function transferMoney(
  fromAccountId: AccountId,
  toAccountId: AccountId,
  amount: Money
) {
  // Implementation
}

// ✅ This works
transferMoney(
  AccountId("acc123"),
  AccountId("acc456"),
  Money("100.00")
);

// ❌ This won't compile!
transferMoney("100.00", "acc123", "acc456");
//            ^^^^^^^^  Type 'string' is not assignable to type 'Money'
```

---

# [fit] Tests We Don't<br>Need to Write

```typescript
// ❌ Without branded types, we need these tests:
describe('transferMoney', () => {
  it('should validate fromAccountId format', () => {
    expect(() => 
      transferMoney('invalid', 'acc456', '100.00')
    ).toThrow();
  });
  
  it('should validate toAccountId format', () => {
    expect(() => 
      transferMoney('acc123', 'invalid', '100.00')
    ).toThrow();
  });
  
  it('should validate amount format', () => {
    expect(() => 
      transferMoney('acc123', 'acc456', 'not-money')
    ).toThrow();
  });
  
  it('should not accept parameters in wrong order', () => {
    // How do you even test this?
  });
});
```

---

# [fit] With Branded Types

```typescript
// ✅ These tests are now impossible to write incorrectly!
describe('transferMoney', () => {
  it('should transfer money', () => {
    // The only test we need - the business logic
    const result = transferMoney(
      AccountId("acc123"),
      AccountId("acc456"),
      Money("100.00")
    );
    expect(result).toEqual({ success: true });
  });
});

// Validation is tested once, at the boundary
describe('AccountId', () => {
  it('should accept valid account IDs', () => {
    expect(() => AccountId("acc123")).not.toThrow();
  });
  
  it('should reject invalid account IDs', () => {
    expect(() => AccountId("invalid")).toThrow();
  });
});
```

---

# [fit] Real-World Example:<br>Email Validation

## Before: Validation Everywhere

```typescript
// ❌ Defensive programming nightmare
class UserService {
  async createUser(email: string, name: string) {
    if (!this.isValidEmail(email)) {
      throw new Error("Invalid email");
    }
    // ... create user
  }
  
  async sendWelcomeEmail(email: string) {
    if (!this.isValidEmail(email)) {
      throw new Error("Invalid email");
    }
    // ... send email
  }
  
  async updateEmail(userId: string, newEmail: string) {
    if (!this.isValidEmail(newEmail)) {
      throw new Error("Invalid email");
    }
    // ... update
  }
  
  private isValidEmail(email: string): boolean {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
  }
}
```

---

# [fit] After: Parse Don't Validate

```typescript
// ✅ Validation happens once at the boundary
type Email = string & { readonly __brand: "Email" };

function parseEmail(input: string): Email | null {
  if (/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(input)) {
    return input as Email;
  }
  return null;
}

class UserService {
  // No validation needed - type system guarantees validity
  async createUser(email: Email, name: string) {
    // Just use it!
  }
  
  async sendWelcomeEmail(email: Email) {
    // Just use it!
  }
  
  async updateEmail(userId: string, newEmail: Email) {
    // Just use it!
  }
}
```

---

# [fit] Refined Number Types

## The Problem

```typescript
// ❌ Runtime errors waiting to happen
function calculateDiscount(
  price: number,
  discountPercent: number
): number {
  if (price < 0) throw new Error("Price cannot be negative");
  if (discountPercent < 0 || discountPercent > 100) {
    throw new Error("Discount must be between 0 and 100");
  }
  return price * (1 - discountPercent / 100);
}

// These compile but fail at runtime
calculateDiscount(-50, 20);      // Negative price
calculateDiscount(100, 150);     // Invalid discount
calculateDiscount(100, -10);     // Negative discount
```

---

# [fit] The Solution

```typescript
// ✅ Make invalid states unrepresentable
type PositiveNumber = number & { readonly __brand: "PositiveNumber" };
type Percentage = number & { readonly __brand: "Percentage" };

function PositiveNumber(n: number): PositiveNumber {
  if (n < 0) throw new Error(`${n} is not positive`);
  return n as PositiveNumber;
}

function Percentage(n: number): Percentage {
  if (n < 0 || n > 100) throw new Error(`${n} is not a valid percentage`);
  return n as Percentage;
}

function calculateDiscount(
  price: PositiveNumber,
  discountPercent: Percentage
): PositiveNumber {
  const discounted = price * (1 - discountPercent / 100);
  return discounted as PositiveNumber; // Safe: math guarantees positive
}
```

---

# [fit] Part 2:<br>Parse, Don't Validate

---

# [fit] The Core Insight

## Validation = Checking but keeping imprecise types
## Parsing = Transforming into precise types

---

# [fit] Replace Option with<br>Precise Types

## The Problem

```typescript
// ❌ Using Option/null for business logic
interface BadUser {
  id: string;
  email: string;
  subscription?: {
    plan: string;
    expiresAt: Date;
  };
}

function canAccessPremiumFeature(user: BadUser): boolean {
  // Defensive checks everywhere
  if (!user.subscription) return false;
  if (user.subscription.expiresAt < new Date()) return false;
  return user.subscription.plan === "premium";
}

function getPlanName(user: BadUser): string {
  // More defensive programming
  return user.subscription?.plan ?? "free";
}
```

---

# [fit] The Solution

```typescript
// ✅ Parse into precise types at the boundary
type FreeUser = {
  type: "free";
  id: UserId;
  email: Email;
};

type PaidUser = {
  type: "paid";
  id: UserId;
  email: Email;
  plan: "basic" | "premium";
  expiresAt: FutureDate; // Parsed to ensure it's in the future
};

type User = FreeUser | PaidUser;

// No defensive checks needed!
function canAccessPremiumFeature(user: User): boolean {
  return user.type === "paid" && user.plan === "premium";
}

function getPlanName(user: User): string {
  return user.type === "paid" ? user.plan : "free";
}
```

---

# [fit] Replace Arrays with<br>Precise Types

## The Problem

```typescript
// ❌ Arrays that might be empty
interface BadTeam {
  name: string;
  members: string[];
}

function getTeamLead(team: BadTeam): string {
  if (team.members.length === 0) {
    throw new Error("Team has no members");
  }
  return team.members[0]; // Still might be undefined!
}

function assignTask(team: BadTeam, task: Task) {
  if (team.members.length === 0) {
    throw new Error("Cannot assign task to empty team");
  }
  // Defensive check repeated everywhere
}
```

---

# [fit] The Solution

```typescript
// ✅ Parse into NonEmptyArray at creation
type NonEmptyArray<T> = readonly [T, ...T[]];

type Team = {
  name: string;
  members: NonEmptyArray<TeamMember>;
};

// Parse at the boundary
function createTeam(
  name: string, 
  members: TeamMember[]
): Team | null {
  if (members.length === 0) return null;
  return {
    name,
    members: members as NonEmptyArray<TeamMember>
  };
}

// No defensive checks needed!
function getTeamLead(team: Team): TeamMember {
  return team.members[0]; // Always exists!
}

function assignTask(team: Team, task: Task) {
  // Just assign it - team always has members
}
```

---

# [fit] Replace Booleans with<br>Precise Types

## The Problem

```typescript
// ❌ Boolean flags lose information
interface BadApiResponse {
  success: boolean;
  data?: any;
  error?: string;
  statusCode?: number;
}

function handleResponse(response: BadApiResponse) {
  if (response.success) {
    if (!response.data) {
      // Success but no data?
      console.error("Invalid state");
    }
    processData(response.data);
  } else {
    if (!response.error) {
      // Failure but no error message?
      console.error("Unknown error");
    }
    logError(response.error);
  }
}
```

---

# [fit] The Solution

```typescript
// ✅ Parse into specific result types
type ApiResponse<T> =
  | { type: "success"; data: T; statusCode: 200 | 201 | 204 }
  | { type: "client_error"; error: string; statusCode: 400 | 401 | 403 | 404 }
  | { type: "server_error"; error: string; statusCode: 500 | 502 | 503; retryAfter?: number };

// Parse at the HTTP boundary
async function parseApiResponse<T>(
  response: Response,
  schema: z.ZodSchema<T>
): Promise<ApiResponse<T>> {
  if (response.ok) {
    const data = schema.parse(await response.json());
    return { 
      type: "success", 
      data, 
      statusCode: response.status as 200 | 201 | 204 
    };
  }
  
  const error = await response.text();
  if (response.status < 500) {
    return { 
      type: "client_error", 
      error, 
      statusCode: response.status as 400 | 401 | 403 | 404 
    };
  }
  
  return { 
    type: "server_error", 
    error, 
    statusCode: response.status as 500 | 502 | 503,
    retryAfter: response.headers.get("Retry-After") 
      ? parseInt(response.headers.get("Retry-After")!) 
      : undefined
  };
}

// Clean handling without defensive checks
function handleResponse<T>(response: ApiResponse<T>) {
  switch (response.type) {
    case "success":
      processData(response.data); // Data always exists
      break;
    case "client_error":
      showUserError(response.error); // Error always exists
      break;
    case "server_error":
      logError(response.error); // Error always exists
      if (response.retryAfter) {
        scheduleRetry(response.retryAfter);
      }
      break;
  }
}
```

---

# [fit] Validation Anti-Pattern:<br>Repeated Checks

```typescript
// ❌ Same validation logic everywhere
class OrderService {
  validateOrder(items: Item[], coupon?: string): boolean {
    if (items.length === 0) return false;
    if (items.some(item => item.quantity <= 0)) return false;
    if (items.some(item => item.price < 0)) return false;
    if (coupon && !this.isValidCoupon(coupon)) return false;
    return true;
  }
  
  calculateTotal(items: Item[], coupon?: string): number {
    // Repeat all the checks...
    if (items.length === 0) throw new Error("No items");
    if (items.some(item => item.quantity <= 0)) {
      throw new Error("Invalid quantity");
    }
    // ... calculate
  }
  
  submitOrder(items: Item[], coupon?: string) {
    // And again...
    if (!this.validateOrder(items, coupon)) {
      throw new Error("Invalid order");
    }
    // But we still don't know WHY it's invalid!
  }
}
```

---

# [fit] Parse Once, Use Everywhere

```typescript
// ✅ Parse into a valid order type
type ValidItem = {
  product: ProductId;
  quantity: PositiveInteger;
  price: PositiveMoney;
};

type ValidOrder = {
  items: NonEmptyArray<ValidItem>;
  coupon?: ValidCoupon;
};

// Parse at the boundary
function parseOrder(
  items: unknown[],
  coupon?: string
): ValidOrder | { error: string } {
  if (items.length === 0) {
    return { error: "Order must have at least one item" };
  }
  
  const validItems: ValidItem[] = [];
  for (const item of items) {
    const quantity = parsePositiveInteger(item.quantity);
    if (!quantity) return { error: `Invalid quantity: ${item.quantity}` };
    
    const price = parsePositiveMoney(item.price);
    if (!price) return { error: `Invalid price: ${item.price}` };
    
    validItems.push({ product: item.product, quantity, price });
  }
  
  if (coupon) {
    const validCoupon = parseCoupon(coupon);
    if (!validCoupon) return { error: `Invalid coupon: ${coupon}` };
    return { 
      items: validItems as NonEmptyArray<ValidItem>, 
      coupon: validCoupon 
    };
  }
  
  return { items: validItems as NonEmptyArray<ValidItem> };
}

// Now all functions just work with ValidOrder
class OrderService {
  calculateTotal(order: ValidOrder): PositiveMoney {
    // No validation needed - just calculate!
    const subtotal = order.items.reduce(
      (sum, item) => sum + (item.price * item.quantity), 
      0
    );
    return order.coupon 
      ? applyCoupon(subtotal, order.coupon)
      : subtotal as PositiveMoney;
  }
  
  submitOrder(order: ValidOrder): OrderId {
    // No validation needed - just submit!
    return db.createOrder(order);
  }
}
```

---

# [fit] Part 3:<br>Impossible States

# [fit] Form State Machine

## The Problem

```typescript
// ❌ Too many boolean flags = exponential complexity
interface BadFormState {
  isLoading: boolean;
  isSubmitting: boolean;
  hasError: boolean;
  errorMessage?: string;
  isSuccess: boolean;
  successMessage?: string;
  data?: FormData;
}

// Which combinations are valid?
// isLoading && isSubmitting?
// hasError && isSuccess?
// hasError but no errorMessage?
// isSuccess but no data?
```

---

# [fit] State Explosion

```typescript
// ❌ Defensive code everywhere
function FormComponent({ state }: { state: BadFormState }) {
  if (state.isLoading && state.isSubmitting) {
    // Is this possible? What do we show?
    return <div>Loading... Submitting...?</div>;
  }
  
  if (state.hasError && !state.errorMessage) {
    // Defensive programming
    return <div>Unknown error</div>;
  }
  
  if (state.isSuccess && !state.data) {
    // Another edge case
    return <div>Success but no data?</div>;
  }
  
  if (state.hasError && state.isSuccess) {
    // Which one wins?
    return <div>¯\_(ツ)_/¯</div>;
  }
  
  // ... more defensive checks
}
```

---

# [fit] The Solution:<br>Algebraic Data Types

```typescript
// ✅ Each state has exactly the data it needs
type FormState =
  | { type: "idle" }
  | { type: "loading" }
  | { type: "submitting"; data: FormData }
  | { type: "error"; message: string; canRetry: boolean }
  | { type: "success"; data: FormData; response: Response };

// Impossible states are now impossible!
// Can't be loading AND submitting
// Can't have error WITHOUT message
// Can't be success WITHOUT data
```

---

# [fit] Clean State Handling

```typescript
// ✅ Exhaustive, no defensive programming needed
function FormComponent({ state }: { state: FormState }) {
  switch (state.type) {
    case "idle":
      return <Form onSubmit={handleSubmit} />;
      
    case "loading":
      return <Spinner />;
      
    case "submitting":
      return <ProgressBar data={state.data} />;
      
    case "error":
      return (
        <ErrorMessage 
          message={state.message}
          onRetry={state.canRetry ? handleRetry : undefined}
        />
      );
      
    case "success":
      return <SuccessMessage response={state.response} />;
  }
}
```

---

# [fit] Tests We Eliminated

```typescript
// ❌ Without ADTs, we need to test invalid combinations
describe('FormComponent with boolean flags', () => {
  it('handles loading and submitting at same time', () => {});
  it('handles error state without message', () => {});
  it('handles success state without data', () => {});
  it('handles error and success at same time', () => {});
  it('handles all false flags', () => {});
  it('handles all true flags', () => {});
  // ... 2^6 = 64 possible combinations to test!
});

// ✅ With ADTs, only valid states exist
describe('FormComponent with ADT', () => {
  it('renders form in idle state', () => {});
  it('shows spinner when loading', () => {});
  it('shows progress when submitting', () => {});
  it('shows error with retry button', () => {});
  it('shows success with response', () => {});
  // Just 5 tests - one per valid state!
});
```

---

# [fit] Real-World Example:<br>API Request State

## Before: Boolean Soup

```typescript
// ❌ Classic loading/error/data pattern
interface BadApiState<T> {
  loading: boolean;
  error: Error | null;
  data: T | null;
  lastFetch?: Date;
  isStale?: boolean;
  isRefetching?: boolean;
}

function useApiData<T>(url: string): BadApiState<T> {
  const [state, setState] = useState<BadApiState<T>>({
    loading: true,
    error: null,
    data: null,
  });
  
  // Complex state updates
  useEffect(() => {
    setState(prev => ({ ...prev, loading: true, error: null }));
    
    fetch(url)
      .then(res => res.json())
      .then(data => {
        setState({
          loading: false,
          error: null,
          data,
          lastFetch: new Date(),
          isStale: false,
        });
      })
      .catch(error => {
        setState(prev => ({
          ...prev,
          loading: false,
          error,
          // Keep old data on error? 🤷
        }));
      });
  }, [url]);
  
  return state;
}
```

---

# [fit] After: Tagged Union

```typescript
// ✅ Every state is explicit and complete
type ApiState<T> =
  | { type: "idle" }
  | { type: "loading"; previousData?: T }
  | { type: "success"; data: T; fetchedAt: Date }
  | { type: "error"; error: Error; previousData?: T; canRetry: boolean };

function useApiData<T>(url: string): ApiState<T> {
  const [state, setState] = useState<ApiState<T>>({ type: "idle" });
  
  useEffect(() => {
    // Clear state transitions
    setState(prev => 
      prev.type === "success" 
        ? { type: "loading", previousData: prev.data }
        : { type: "loading" }
    );
    
    fetch(url)
      .then(res => res.json())
      .then(data => {
        setState({ 
          type: "success", 
          data, 
          fetchedAt: new Date() 
        });
      })
      .catch(error => {
        setState(prev => ({
          type: "error",
          error,
          previousData: prev.type === "loading" ? prev.previousData : undefined,
          canRetry: !error.message.includes("401"),
        }));
      });
  }, [url]);
  
  return state;
}
```

---

# [fit] Parse + State Machines

## Parsing Events Before Transitions

```typescript
// ❌ Validation approach - stringly typed events
type BadEvent = {
  type: string;
  payload?: any;
};

function handleEvent(state: State, event: BadEvent): State {
  if (event.type === "submit") {
    if (!event.payload?.items || event.payload.items.length === 0) {
      throw new Error("Invalid submit event");
    }
    // Still don't know if items are valid...
  }
  // More string checks...
}
```

---

# [fit] Parse Events into Types

```typescript
// ✅ Parse events into precise types
type CartEvent =
  | { type: "ADD_ITEM"; item: ValidItem }
  | { type: "REMOVE_ITEM"; itemId: ItemId }
  | { type: "APPLY_COUPON"; coupon: ValidCoupon }
  | { type: "SUBMIT"; shippingAddress: ValidAddress };

// Parse at the event boundary
function parseCartEvent(raw: unknown): CartEvent | { error: string } {
  const { type, ...payload } = raw as any;
  
  switch (type) {
    case "ADD_ITEM": {
      const item = parseValidItem(payload.item);
      if (!item) return { error: "Invalid item data" };
      return { type: "ADD_ITEM", item };
    }
    case "SUBMIT": {
      const address = parseAddress(payload.address);
      if (!address) return { error: "Invalid shipping address" };
      return { type: "SUBMIT", shippingAddress: address };
    }
    // ... other cases
  }
}

// State machine with parsed events
function cartReducer(state: CartState, event: CartEvent): CartState {
  switch (state.type) {
    case "shopping":
      switch (event.type) {
        case "ADD_ITEM":
          // event.item is guaranteed to be valid!
          return {
            ...state,
            items: [...state.items, event.item]
          };
        case "SUBMIT":
          // Can only submit non-empty cart with valid address
          if (state.items.length === 0) return state;
          return {
            type: "checking_out",
            items: state.items as NonEmptyArray<ValidItem>,
            shippingAddress: event.shippingAddress
          };
      }
  }
}
```

---

# [fit] Part 4:<br>LLM Agent Types

# [fit] Agent Tool Calls

## The Problem

```typescript
// ❌ Stringly-typed tool calls
interface BadToolCall {
  tool: string;
  parameters: Record<string, any>;
}

async function executeToolCall(call: BadToolCall) {
  switch (call.tool) {
    case "search":
      // Hope parameters.query exists and is a string!
      return await search(call.parameters.query);
      
    case "calculate":
      // Hope these exist and are numbers!
      return calculate(
        call.parameters.operation,
        call.parameters.a,
        call.parameters.b
      );
      
    case "send_email":
      // So many ways this can fail
      return await sendEmail(
        call.parameters.to,
        call.parameters.subject,
        call.parameters.body
      );
  }
}
```

---

# [fit] Type-Safe Tool Calls

```typescript
// ✅ Each tool has its own parameter type
type ToolCall =
  | { tool: "search"; parameters: { query: string; limit?: number } }
  | { tool: "calculate"; parameters: { 
      operation: "add" | "subtract" | "multiply" | "divide";
      a: number;
      b: number;
    }}
  | { tool: "send_email"; parameters: {
      to: Email;  // Using our branded type!
      subject: string;
      body: string;
      cc?: Email[];
    }};

async function executeToolCall(call: ToolCall) {
  switch (call.tool) {
    case "search":
      // TypeScript knows parameters.query exists
      return await search(call.parameters.query, call.parameters.limit);
      
    case "calculate":
      // All parameters are guaranteed to exist with correct types
      return calculate(
        call.parameters.operation,
        call.parameters.a,
        call.parameters.b
      );
      
    case "send_email":
      // Email type ensures valid email addresses
      return await sendEmail(call.parameters);
  }
}
```

---

# [fit] Agent State Machine

## The Problem

```typescript
// ❌ Agent with unclear state transitions
interface BadAgent {
  isThinking: boolean;
  isExecutingTool: boolean;
  currentTool?: string;
  hasResponse: boolean;
  response?: string;
  error?: Error;
  toolResults?: any[];
  needsMoreInfo: boolean;
}

// What's the flow? Can it be thinking AND executing?
// When do toolResults get cleared?
// What if there's an error during tool execution?
```

---

# [fit] Agent State Machine

```typescript
// ✅ Clear state transitions
type AgentState =
  | { type: "idle" }
  | { type: "thinking"; prompt: string }
  | { type: "requesting_tool"; tool: ToolCall; reason: string }
  | { type: "executing_tool"; tool: ToolCall }
  | { type: "processing_result"; tool: ToolCall; result: unknown }
  | { type: "needs_clarification"; questions: string[] }
  | { type: "complete"; response: string; toolsUsed: ToolCall[] }
  | { type: "failed"; error: Error; partialResponse?: string };

// State transitions are explicit
type AgentEvent =
  | { type: "START"; prompt: string }
  | { type: "REQUEST_TOOL"; tool: ToolCall; reason: string }
  | { type: "TOOL_COMPLETE"; result: unknown }
  | { type: "NEED_CLARIFICATION"; questions: string[] }
  | { type: "COMPLETE"; response: string }
  | { type: "ERROR"; error: Error };
```

---

# [fit] Type-Safe State Transitions

```typescript
// ✅ State machine ensures valid transitions
function agentReducer(
  state: AgentState,
  event: AgentEvent
): AgentState {
  switch (state.type) {
    case "idle":
      if (event.type === "START") {
        return { type: "thinking", prompt: event.prompt };
      }
      break;
      
    case "thinking":
      switch (event.type) {
        case "REQUEST_TOOL":
          return { 
            type: "requesting_tool", 
            tool: event.tool, 
            reason: event.reason 
          };
        case "NEED_CLARIFICATION":
          return { 
            type: "needs_clarification", 
            questions: event.questions 
          };
        case "COMPLETE":
          return { 
            type: "complete", 
            response: event.response, 
            toolsUsed: [] 
          };
      }
      break;
      
    case "executing_tool":
      if (event.type === "TOOL_COMPLETE") {
        return { 
          type: "processing_result", 
          tool: state.tool, 
          result: event.result 
        };
      }
      break;
  }
  
  // Invalid transition
  if (event.type === "ERROR") {
    return { 
      type: "failed", 
      error: event.error,
      partialResponse: state.type === "thinking" ? state.prompt : undefined
    };
  }
  
  return state; // No transition
}
```

---

# [fit] Parse LLM Responses

## The Problem

```typescript
// ❌ Trusting LLM to return correct format
async function callLLM(prompt: string): Promise<any> {
  const response = await llm.complete(prompt);
  try {
    return JSON.parse(response); // Hope it's valid JSON
  } catch {
    return { error: "Failed to parse" };
  }
}

async function getToolCall(): Promise<ToolCall> {
  const response = await callLLM("What tool to use?");
  // Hope it has the right shape...
  return response as ToolCall;
}
```

---

# [fit] Parse LLM Output

```typescript
// ✅ Parse LLM responses into precise types
const ToolCallSchema = z.discriminatedUnion("tool", [
  z.object({
    tool: z.literal("search"),
    parameters: z.object({
      query: z.string().min(1).max(200),
      limit: z.number().int().positive().max(10).default(5)
    })
  }),
  z.object({
    tool: z.literal("calculate"),
    parameters: z.object({
      operation: z.enum(["add", "subtract", "multiply", "divide"]),
      a: z.number(),
      b: z.number()
    })
  }),
  z.object({
    tool: z.literal("send_email"),
    parameters: z.object({
      to: z.string().email().transform(e => e as Email),
      subject: z.string().min(1).max(200),
      body: z.string().min(1).max(5000),
      cc: z.array(z.string().email().transform(e => e as Email)).optional()
    })
  })
]);

type ToolCall = z.infer<typeof ToolCallSchema>;

async function getToolCall(context: string): Promise<ToolCall | null> {
  const prompt = `Given context: ${context}
  
  Respond with a JSON tool call in this exact format:
  { "tool": "search", "parameters": { "query": "...", "limit": 5 } }`;
  
  const response = await llm.complete(prompt);
  
  // Parse and validate in one step
  const parsed = ToolCallSchema.safeParse(JSON.parse(response));
  if (!parsed.success) {
    console.error("Invalid tool call:", parsed.error);
    return null;
  }
  
  return parsed.data; // Guaranteed valid with correct types!
}
```

---

# [fit] Complex Agent Example

```typescript
// ✅ Multi-step agent with type safety throughout
type SearchResult = { title: string; url: string; snippet: string };
type WebContent = { url: string; text: string; links: string[] };

type AgentTool =
  | { tool: "web_search"; parameters: { query: string } }
  | { tool: "read_webpage"; parameters: { url: string } }
  | { tool: "summarize"; parameters: { text: string; maxWords: number } };

type AgentMemory = {
  searches: Array<{ query: string; results: SearchResult[] }>;
  pagesRead: Array<{ url: string; content: WebContent }>;
  summaries: Array<{ original: string; summary: string }>;
};

type ResearchAgentState =
  | { type: "planning"; goal: string; steps: string[] }
  | { type: "searching"; query: string; previousSearches: string[] }
  | { type: "evaluating_results"; results: SearchResult[]; goal: string }
  | { type: "reading_page"; url: string; reason: string }
  | { type: "synthesizing"; memory: AgentMemory; goal: string }
  | { type: "complete"; report: string; sources: string[] };
```

---

# [fit] Tests Eliminated

```typescript
// ❌ Without proper types
describe('Agent without types', () => {
  it('handles thinking while executing', () => {});
  it('handles response without completion', () => {});
  it('handles tool results in wrong state', () => {});
  it('validates tool parameters exist', () => {});
  it('checks tool parameter types', () => {});
  it('ensures email format in send_email', () => {});
  it('handles missing required parameters', () => {});
  it('handles unknown tool names', () => {});
  // ... dozens more defensive tests
});

// ✅ With algebraic types
describe('Agent with ADTs', () => {
  it('transitions from thinking to tool request', () => {});
  it('processes tool results', () => {});
  it('handles clarification needs', () => {});
  it('completes with response', () => {});
  it('handles errors gracefully', () => {});
  // Just test the business logic!
});
```

---

# [fit] Part 4:<br>API Validation

---

# [fit] Runtime Validation

## The Problem

```typescript
// ❌ Hope the API returns what we expect
interface User {
  id: string;
  email: string;
  age: number;
  role: "admin" | "user";
}

async function fetchUser(id: string): Promise<User> {
  const response = await fetch(`/api/users/${id}`);
  const data = await response.json();
  return data; // 🤞 Hope it matches User interface!
}

// Runtime error when API returns { id: 123, email: null, role: "superuser" }
```

---

# [fit] Parse at the Boundary

```typescript
// ✅ Validate at runtime, type-safe everywhere else
import { z } from "zod";

// Define schema (runtime + compile time)
const UserSchema = z.object({
  id: z.string(),
  email: z.string().email(),
  age: z.number().int().positive(),
  role: z.enum(["admin", "user"]),
});

// Extract the TypeScript type
type User = z.infer<typeof UserSchema>;

async function fetchUser(id: string): Promise<User> {
  const response = await fetch(`/api/users/${id}`);
  const data = await response.json();
  
  // Parse and validate in one step
  const user = UserSchema.parse(data);
  return user; // Guaranteed to be valid User!
}

// Or handle errors gracefully
async function fetchUserSafe(id: string): Promise<User | null> {
  const response = await fetch(`/api/users/${id}`);
  const data = await response.json();
  
  const result = UserSchema.safeParse(data);
  if (result.success) {
    return result.data;
  } else {
    console.error("Invalid user data:", result.error);
    return null;
  }
}
```

---

# [fit] Complex API Types

```typescript
// ✅ Nested validation with branded types
const EmailSchema = z.string().email().transform(email => email as Email);
const UserIdSchema = z.string().uuid().transform(id => id as UserId);

const CommentSchema = z.object({
  id: z.string(),
  authorId: UserIdSchema,
  content: z.string().min(1).max(500),
  createdAt: z.string().datetime(),
  edited: z.boolean(),
  editedAt: z.string().datetime().optional(),
});

const PostSchema = z.object({
  id: z.string(),
  authorId: UserIdSchema,
  title: z.string().min(1).max(200),
  content: z.string().min(1),
  tags: z.array(z.string()),
  status: z.enum(["draft", "published", "archived"]),
  comments: z.array(CommentSchema),
  metadata: z.object({
    views: z.number().int().nonnegative(),
    likes: z.number().int().nonnegative(),
    shareCount: z.number().int().nonnegative(),
  }),
});

type Post = z.infer<typeof PostSchema>;
// All nested types are validated and branded!
```

---

# [fit] Local Reasoning

---

# [fit] What is Local Reasoning?

## Understanding code behavior by looking **only** at:
1. The function signature
2. The types involved
3. The immediate context

## **Not** by:
- Tracing through the entire codebase
- Reading implementation details
- Checking all callers

---

# [fit] Example: Payment Processing

```typescript
// ❌ Without precise types - need to read everything
async function processPayment(
  customerId: string,
  cardNumber: string,
  amount: number,
  currency: string
): Promise<{ success: boolean; transactionId?: string }> {
  // Need to read implementation to know:
  // - Is customerId validated?
  // - Is cardNumber format checked?
  // - Can amount be negative?
  // - What currencies are valid?
  // - When is transactionId present?
}

// Must trace through callers to understand usage
const result = await processPayment(
  getUserId(),      // Is this the right ID format?
  getCardNumber(),  // Is this validated?
  calculateTotal(), // Can this be negative?
  "EUR"            // Is this supported?
);
```

---

# [fit] With Precise Types

```typescript
// ✅ Everything clear from the signature
type CustomerId = string & { readonly __brand: "CustomerId" };
type CardNumber = string & { readonly __brand: "CardNumber" };
type PositiveAmount = number & { readonly __brand: "PositiveAmount" };
type Currency = "USD" | "EUR" | "GBP";

type PaymentResult =
  | { type: "success"; transactionId: TransactionId; amount: PositiveAmount }
  | { type: "declined"; reason: string }
  | { type: "error"; code: string; retryable: boolean };

async function processPayment(
  customerId: CustomerId,
  cardNumber: CardNumber,
  amount: PositiveAmount,
  currency: Currency
): Promise<PaymentResult> {
  // Implementation doesn't matter for understanding!
}

// Usage is self-documenting
const result = await processPayment(
  CustomerId("cus_123"),        // ✅ Must be valid
  CardNumber("4242424242424242"), // ✅ Must be valid
  PositiveAmount(99.99),        // ✅ Must be positive
  "EUR"                         // ✅ IDE shows valid options
);

switch (result.type) {
  case "success":
    // TypeScript knows transactionId exists here
    console.log(`Transaction ${result.transactionId} completed`);
    break;
  case "declined":
    // TypeScript knows reason exists here
    showError(`Payment declined: ${result.reason}`);
    break;
  case "error":
    // TypeScript knows code and retryable exist here
    if (result.retryable) {
      retry();
    }
    break;
}
```

---

# [fit] Function Signatures<br>Tell the Whole Story

```typescript
// ✅ These signatures tell you everything

// Pure transformation - no side effects
function toUpperCase(s: string): string

// Might fail - check the result
function parseDate(s: string): Date | null

// Async operation that might fail
function fetchUser(id: UserId): Promise<User | null>

// Side effect with no return
function logError(error: Error): void

// Infallible parser with proof
function parsePositive(n: number): PositiveNumber | never

// State machine transition
function nextState(current: State, event: Event): State

// Builder pattern - returns new instance
function withTimeout(request: Request, ms: number): Request
```

---

# [fit] Key Takeaways

---

# [fit] 1. Parse at the Boundaries

```typescript
// ✅ Validate once, use everywhere
const email = parseEmail(userInput);
if (!email) {
  return { error: "Invalid email" };
}

// No more validation needed!
sendWelcomeEmail(email);
updateUserEmail(userId, email);
addToMailingList(email);
```

---

# [fit] 2. Make Illegal States<br>Unrepresentable

```typescript
// ✅ If it compiles, it works
type LoadingState =
  | { status: "idle" }
  | { status: "loading"; startedAt: Date }
  | { status: "success"; data: Data; loadedAt: Date }
  | { status: "error"; error: Error; canRetry: boolean };

// No defensive programming needed!
```

---

# [fit] 3. Use the Type System<br>as Documentation

```typescript
// ✅ Types explain the business rules
type OrderState =
  | { status: "draft"; items: Item[] }
  | { status: "submitted"; items: NonEmptyArray<Item>; submittedAt: Date }
  | { status: "paid"; items: NonEmptyArray<Item>; paidAt: Date; paymentId: PaymentId }
  | { status: "shipped"; items: NonEmptyArray<Item>; trackingNumber: TrackingNumber }
  | { status: "delivered"; items: NonEmptyArray<Item>; deliveredAt: Date };

// The types show: drafts can be empty, but submitted orders cannot
```

---

# [fit] The Testing Impact

---

# [fit] Tests Eliminated:<br>Validation

```typescript
// ❌ Before: Testing defensive programming
describe('OrderService - validation approach', () => {
  it('rejects empty order in calculateTotal', () => {});
  it('rejects negative quantities in calculateTotal', () => {});
  it('rejects negative prices in calculateTotal', () => {});
  it('rejects invalid coupon in calculateTotal', () => {});
  
  it('rejects empty order in submitOrder', () => {});
  it('rejects negative quantities in submitOrder', () => {});
  it('rejects negative prices in submitOrder', () => {});
  it('rejects invalid coupon in submitOrder', () => {});
  
  it('rejects empty order in validateOrder', () => {});
  // ... 20+ validation tests
});

// ✅ After: Testing business logic only
describe('OrderService - parse approach', () => {
  it('calculates total with items', () => {});
  it('applies coupon discount', () => {});
  it('submits order successfully', () => {});
  // Just 3-4 business logic tests!
});
```

---

# [fit] Tests Eliminated:<br>State Machines

```typescript
// ❌ Before: Testing impossible states
describe('FormComponent - boolean flags', () => {
  // Testing all 2^6 = 64 combinations
  it('handles isLoading=true, isSubmitting=true', () => {});
  it('handles isLoading=true, hasError=true', () => {});
  it('handles isSuccess=true, hasError=true', () => {});
  it('handles hasError=true, errorMessage=undefined', () => {});
  it('handles isSuccess=true, data=undefined', () => {});
  // ... 59 more impossible state tests
});

// ✅ After: Testing valid states only
describe('FormComponent - ADT', () => {
  it('shows form when idle', () => {});
  it('shows spinner when loading', () => {});
  it('shows error with message', () => {});
  it('shows success with data', () => {});
  it('transitions between states correctly', () => {});
  // Just 5 tests for 5 valid states!
});
```

---

# [fit] Tests Eliminated:<br>Type Safety

```typescript
// ❌ Before: Testing type mismatches
describe('Agent - without types', () => {
  it('validates tool exists', () => {});
  it('validates search has query parameter', () => {});
  it('validates calculate has operation parameter', () => {});
  it('validates calculate has numeric a and b', () => {});
  it('validates email has valid to address', () => {});
  it('validates email has subject', () => {});
  it('validates email has body', () => {});
  it('handles missing parameters gracefully', () => {});
  it('handles wrong parameter types', () => {});
  // ... dozens of parameter validation tests
});

// ✅ After: Compiler ensures correctness
describe('Agent - with types', () => {
  it('executes search tool', () => {});
  it('executes calculate tool', () => {});
  it('executes email tool', () => {});
  it('handles tool errors', () => {});
  // Just test the actual functionality!
});
```

---

# [fit] Total Impact

## Parse, Don't Validate
- **Before**: 20+ validation tests per service method
- **After**: 1 parser test + business logic tests
- **Reduction**: 85%

## State Machines
- **Before**: 2^n tests for n boolean flags
- **After**: n tests for n valid states
- **Reduction**: Exponential → Linear

## Type-Safe APIs
- **Before**: Defensive tests for every parameter
- **After**: Schema validation at boundary only
- **Reduction**: 90%

---

# [fit] Tests You Don't<br>Need to Write

## Before: ~200 defensive tests
## After: ~30 business logic tests

## 85% reduction in test code
## 100% increase in confidence

---

# [fit] Thank You!

## Questions?

### Resources:
- [Parse, Don't Validate](https://lexi-lambda.github.io/blog/2019/11/05/parse-don-t-validate/)
- [Making Impossible States Impossible](https://www.youtube.com/watch?v=IcgmSRJHu_8)
- [Type-Driven Development](https://blog.ploeh.dk/2015/08/10/type-driven-development/)
- [Algebra-Driven Design](https://leanpub.com/algebra-driven-design)