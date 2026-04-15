# Rust and Swift Examples

## Rust

### Product

```rust
struct Money {
    amount: i64,
    currency: String,
}
```

### Coproduct

```rust
enum DocState {
    Draft,
    Approved { approved_by: String },
    Published { approved_by: String, published_at: String },
}
```

### Refined type

```rust
#[derive(Clone, Debug, PartialEq, Eq)]
struct Email(String);

impl Email {
    fn parse(raw: &str) -> Result<Self, String> {
        let normalized = raw.trim().to_lowercase();
        if normalized.is_empty() {
            return Err("empty email".into());
        }
        Ok(Self(normalized))
    }
}
```

### Pullback witness

```rust
struct Customer {
    account_id: String,
    name: String,
}

struct Subscription {
    account_id: String,
    plan: String,
}

struct CustomerSubscription {
    customer: Customer,
    subscription: Subscription,
}

impl CustomerSubscription {
    fn create(customer: Customer, subscription: Subscription) -> Result<Self, String> {
        if customer.account_id != subscription.account_id {
            return Err("account mismatch".into());
        }
        Ok(Self { customer, subscription })
    }
}
```

## Swift

### Coproduct

```swift
enum DocState {
    case draft
    case approved(approvedBy: String)
    case published(approvedBy: String, publishedAt: String)
}
```

### Refined type

```swift
struct Email: Equatable {
    let value: String

    static func parse(_ raw: String) throws -> Email {
        let normalized = raw.trimmingCharacters(in: .whitespacesAndNewlines).lowercased()
        guard !normalized.isEmpty else { throw EmailError.empty }
        return Email(value: normalized)
    }
}

enum EmailError: Error {
    case empty
}
```

### Exponential

```swift
typealias Formatter = (String) -> String

func withPrefix(_ prefix: String) -> Formatter {
    { body in prefix + body }
}
```
