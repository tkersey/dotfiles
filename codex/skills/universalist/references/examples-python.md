# Python Examples

## Product and terminal object

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Money:
    amount: int
    currency: str
```

## Coproduct and initial object

```python
from dataclasses import dataclass
from typing import Union

@dataclass(frozen=True)
class Draft:
    tag: str = "draft"

@dataclass(frozen=True)
class Approved:
    approved_by: str
    tag: str = "approved"

@dataclass(frozen=True)
class Published:
    approved_by: str
    published_at: str
    tag: str = "published"

DocState = Union[Draft, Approved, Published]
```

## Refined type

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Email:
    value: str

    @classmethod
    def parse(cls, raw: str) -> "Email":
        value = raw.strip().lower()
        if not value:
            raise ValueError("empty email")
        return cls(value)
```

## Pullback witness

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Customer:
    account_id: str
    name: str

@dataclass(frozen=True)
class Subscription:
    account_id: str
    plan: str

@dataclass(frozen=True)
class CustomerSubscription:
    customer: Customer
    subscription: Subscription

    @classmethod
    def create(cls, customer: Customer, subscription: Subscription) -> "CustomerSubscription":
        if customer.account_id != subscription.account_id:
            raise ValueError("account mismatch")
        return cls(customer=customer, subscription=subscription)
```

## Exponential

```python
from typing import Callable

Formatter = Callable[[str], str]

def with_prefix(prefix: str) -> Formatter:
    return lambda body: f"{prefix}{body}"
```

## Free construction

```python
from dataclasses import dataclass
from typing import Union

@dataclass(frozen=True)
class Lit:
    value: int

@dataclass(frozen=True)
class Add:
    left: "Expr"
    right: "Expr"

Expr = Union[Lit, Add]

def eval_expr(expr: Expr) -> int:
    if isinstance(expr, Lit):
        return expr.value
    if isinstance(expr, Add):
        return eval_expr(expr.left) + eval_expr(expr.right)
    raise TypeError(f"unknown expression: {expr!r}")

def pretty(expr: Expr) -> str:
    if isinstance(expr, Lit):
        return str(expr.value)
    if isinstance(expr, Add):
        return f"({pretty(expr.left)} + {pretty(expr.right)})"
    raise TypeError(f"unknown expression: {expr!r}")
```

## ADD sub-lens

```python
from dataclasses import dataclass, field

@dataclass(frozen=True)
class Log:
    lines: tuple[str, ...] = field(default_factory=tuple)

def combine_log(a: Log, b: Log) -> Log:
    return Log(lines=a.lines + b.lines)
```
