# Java and Kotlin Examples

## Kotlin

### Coproduct

```kotlin
sealed interface DocState {
    data object Draft : DocState
    data class Approved(val approvedBy: String) : DocState
    data class Published(val approvedBy: String, val publishedAt: String) : DocState
}
```

### Refined type

```kotlin
@JvmInline
value class Email private constructor(val value: String) {
    companion object {
        fun parse(raw: String): Email {
            val normalized = raw.trim().lowercase()
            require(normalized.isNotEmpty()) { "empty email" }
            return Email(normalized)
        }
    }
}
```

### Pullback witness

```kotlin
data class Customer(val accountId: String, val name: String)
data class Subscription(val accountId: String, val plan: String)

data class CustomerSubscription private constructor(
    val customer: Customer,
    val subscription: Subscription,
) {
    companion object {
        fun create(customer: Customer, subscription: Subscription): CustomerSubscription {
            require(customer.accountId == subscription.accountId) { "account mismatch" }
            return CustomerSubscription(customer, subscription)
        }
    }
}
```

### Exponential

```kotlin
typealias Formatter = (String) -> String

fun withPrefix(prefix: String): Formatter = { body -> prefix + body }
```

## Java

### Product

```java
public record Money(int amount, String currency) {}
```

### Coproduct

```java
public sealed interface DocState permits Draft, Approved, Published {}

public record Draft() implements DocState {}
public record Approved(String approvedBy) implements DocState {}
public record Published(String approvedBy, String publishedAt) implements DocState {}
```

### Refined type

```java
public final class Email {
    private final String value;

    private Email(String value) {
        this.value = value;
    }

    public static Email parse(String raw) {
        String normalized = raw.trim().toLowerCase();
        if (normalized.isEmpty()) {
            throw new IllegalArgumentException("empty email");
        }
        return new Email(normalized);
    }

    public String value() {
        return value;
    }
}
```

### Exponential

```java
import java.util.function.Function;

Function<String, String> withPrefix(String prefix) {
    return body -> prefix + body;
}
```
