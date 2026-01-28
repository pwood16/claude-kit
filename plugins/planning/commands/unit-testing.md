---
description: Guide for writing unit tests using TDD, test patterns, and mocking strategies
allowed-tools: Read, Glob, Grep, AskUserQuestion
argument-hint: [language-or-framework]
---

# Unit Testing Best Practices

Provide guidance on writing effective unit tests using TDD methodology, proven test patterns, and proper mocking strategies.

## Your Role

You are a testing expert who helps developers write effective, maintainable unit tests. You advocate for TDD, understand common test patterns, and know when and how to use mocks appropriately.

## Your Task

### 1. Understand Context

**Identify the testing environment:**
- Check `$ARGUMENTS` for language/framework hints
- Use `Glob` to find existing test files and infer patterns
- Look for test configuration files (jest.config.js, pytest.ini, etc.)
- Read a few existing tests to understand current conventions

**Ask clarifying questions if needed:**
- What are you trying to test?
- Is this new code (TDD opportunity) or existing code?
- Are there specific testing challenges you're facing?

### 2. Provide Relevant Guidance

Based on context, provide guidance from the knowledge base below. Tailor examples to the user's language/framework.

---

## Test-Driven Development (TDD)

### The TDD Cycle

```
    ┌─────────────────┐
    │   RED: Write    │
    │   failing test  │
    └────────┬────────┘
             │
             ▼
    ┌─────────────────┐
    │  GREEN: Write   │
    │  minimal code   │
    │  to pass test   │
    └────────┬────────┘
             │
             ▼
    ┌─────────────────┐
    │ REFACTOR: Clean │
    │ up while green  │
    └────────┬────────┘
             │
             └──────────► (repeat)
```

### TDD Rules

1. **Write a failing test first** - No production code without a failing test
2. **Write only enough test** - Test one behavior at a time
3. **Write only enough code** - Make the test pass, nothing more
4. **Refactor mercilessly** - Clean up while tests are green

### TDD Benefits

- **Design feedback**: Hard-to-test code indicates design problems
- **Documentation**: Tests show how code should be used
- **Confidence**: Refactor without fear
- **Focus**: One thing at a time

### TDD Example Flow

```python
# Step 1: RED - Write failing test
def test_calculator_adds_two_numbers():
    calc = Calculator()
    result = calc.add(2, 3)
    assert result == 5

# Run: FAILS - Calculator doesn't exist

# Step 2: GREEN - Minimal implementation
class Calculator:
    def add(self, a, b):
        return 5  # Simplest thing that works!

# Run: PASSES

# Step 3: RED - Add another test to force real implementation
def test_calculator_adds_different_numbers():
    calc = Calculator()
    result = calc.add(10, 20)
    assert result == 30

# Run: FAILS - Returns 5, not 30

# Step 4: GREEN - Real implementation
class Calculator:
    def add(self, a, b):
        return a + b

# Run: PASSES

# Step 5: REFACTOR - Clean up if needed (nothing to clean here)
```

### When TDD Works Best

- New features with clear requirements
- Bug fixes (write test that reproduces bug first)
- Refactoring existing code
- API design (tests clarify interface)

### When to Adapt TDD

- Exploratory/spike work (write tests after learning)
- UI code (test behavior, not layout)
- Integration points (may need integration tests instead)

---

## Test Structure Patterns

### Arrange-Act-Assert (AAA)

The fundamental pattern for all unit tests:

```python
def test_user_can_change_email():
    # Arrange - Set up test data and dependencies
    user = User(email="old@example.com")
    new_email = "new@example.com"

    # Act - Execute the behavior being tested
    user.change_email(new_email)

    # Assert - Verify the expected outcome
    assert user.email == new_email
```

### Given-When-Then (BDD Style)

Same structure, different vocabulary:

```python
def test_user_can_change_email():
    # Given a user with an existing email
    user = User(email="old@example.com")

    # When they change their email
    user.change_email("new@example.com")

    # Then their email is updated
    assert user.email == "new@example.com"
```

### One Assert Per Test (Conceptually)

Test one behavior, not one assertion:

```python
# GOOD - Multiple asserts for one behavior
def test_order_calculates_total_with_tax():
    order = Order(items=[Item(price=100)])
    order.apply_tax(rate=0.1)

    assert order.subtotal == 100
    assert order.tax == 10
    assert order.total == 110  # These all verify "total calculation"

# BAD - Multiple behaviors in one test
def test_order():
    order = Order()
    order.add_item(Item(price=100))
    assert len(order.items) == 1  # Testing add_item

    order.apply_tax(0.1)
    assert order.total == 110  # Testing apply_tax

    order.apply_discount(10)
    assert order.total == 100  # Testing apply_discount
```

### Test Data Builders

Create readable, flexible test data:

```python
# Builder pattern
class UserBuilder:
    def __init__(self):
        self.name = "Default Name"
        self.email = "default@example.com"
        self.role = "user"

    def with_name(self, name):
        self.name = name
        return self

    def with_role(self, role):
        self.role = role
        return self

    def build(self):
        return User(name=self.name, email=self.email, role=self.role)

# Usage
def test_admin_can_delete_users():
    admin = UserBuilder().with_role("admin").build()
    target = UserBuilder().with_name("Target User").build()

    admin.delete_user(target)

    assert target.is_deleted
```

### Parameterized Tests

Test multiple cases without duplication:

```python
# Python/pytest
@pytest.mark.parametrize("input,expected", [
    ("hello", "HELLO"),
    ("World", "WORLD"),
    ("", ""),
    ("123", "123"),
])
def test_uppercase(input, expected):
    assert uppercase(input) == expected

# JavaScript/Jest
test.each([
    ["hello", "HELLO"],
    ["World", "WORLD"],
    ["", ""],
])("uppercase(%s) returns %s", (input, expected) => {
    expect(uppercase(input)).toBe(expected);
});
```

---

## Mocking Strategies

### When to Mock

**DO mock:**
- External services (APIs, databases, file systems)
- Non-deterministic behavior (time, random, UUIDs)
- Slow operations
- Operations with side effects (sending emails, payments)

**DON'T mock:**
- The system under test
- Simple value objects
- Pure functions
- Things that are fast and deterministic

### Types of Test Doubles

```
┌─────────────┬────────────────────────────────────────────────┐
│ Double Type │ Purpose                                        │
├─────────────┼────────────────────────────────────────────────┤
│ Dummy       │ Passed but never used (satisfies signature)    │
│ Stub        │ Returns predetermined values                   │
│ Spy         │ Records calls for later verification           │
│ Mock        │ Stub + Spy with expectations                   │
│ Fake        │ Working implementation (e.g., in-memory DB)    │
└─────────────┴────────────────────────────────────────────────┘
```

### Stub Example

Replace dependency with predetermined responses:

```python
# Production code
class OrderService:
    def __init__(self, inventory_client):
        self.inventory = inventory_client

    def place_order(self, product_id, quantity):
        available = self.inventory.check_stock(product_id)
        if available >= quantity:
            return Order(product_id, quantity)
        raise InsufficientStockError()

# Test with stub
def test_place_order_when_in_stock():
    # Stub always returns 100 units available
    inventory_stub = Mock()
    inventory_stub.check_stock.return_value = 100

    service = OrderService(inventory_stub)
    order = service.place_order("PROD-1", 5)

    assert order.quantity == 5
```

### Spy Example

Verify interactions occurred:

```python
def test_order_checks_inventory():
    inventory_spy = Mock()
    inventory_spy.check_stock.return_value = 100

    service = OrderService(inventory_spy)
    service.place_order("PROD-1", 5)

    # Verify the interaction
    inventory_spy.check_stock.assert_called_once_with("PROD-1")
```

### Fake Example

Working but simplified implementation:

```python
# Fake in-memory repository
class FakeUserRepository:
    def __init__(self):
        self.users = {}

    def save(self, user):
        self.users[user.id] = user

    def find_by_id(self, user_id):
        return self.users.get(user_id)

    def find_by_email(self, email):
        return next(
            (u for u in self.users.values() if u.email == email),
            None
        )

# Test with fake
def test_user_registration():
    repo = FakeUserRepository()
    service = UserService(repo)

    service.register("test@example.com", "password")

    user = repo.find_by_email("test@example.com")
    assert user is not None
```

### Mock Patterns

**Partial mocking** - Mock one method, keep the rest:

```python
def test_with_partial_mock():
    service = UserService()
    service.send_email = Mock()  # Mock just this method

    service.register("test@example.com")

    service.send_email.assert_called_once()
```

**Context-specific returns:**

```python
def test_retry_on_failure():
    client = Mock()
    # Fail twice, then succeed
    client.fetch.side_effect = [
        ConnectionError(),
        ConnectionError(),
        {"data": "success"}
    ]

    result = resilient_fetch(client)

    assert result == {"data": "success"}
    assert client.fetch.call_count == 3
```

### Mocking Anti-Patterns

**Over-mocking** - Testing mocks, not behavior:

```python
# BAD - This tests nothing useful
def test_save_user():
    repo = Mock()
    service = UserService(repo)

    service.save(User("test"))

    repo.save.assert_called_once()  # Just verifying you called a method
```

**Mocking what you own** - Mock boundaries, not internals:

```python
# BAD - Mocking internal helper
def test_calculate_total():
    order = Order()
    order._apply_discount = Mock(return_value=90)  # Don't mock internals

    total = order.calculate_total()

# GOOD - Test the actual behavior
def test_calculate_total_with_discount():
    order = Order(items=[Item(100)], discount_percent=10)

    total = order.calculate_total()

    assert total == 90
```

---

## Test Naming Conventions

### Descriptive Names

Tests should read like specifications:

```python
# Pattern: test_[unit]_[scenario]_[expected_result]

def test_user_with_expired_subscription_cannot_access_premium_content():
    ...

def test_empty_cart_returns_zero_total():
    ...

def test_duplicate_email_raises_validation_error():
    ...
```

### Nested Describes (JavaScript/RSpec style)

```javascript
describe('ShoppingCart', () => {
    describe('when empty', () => {
        it('returns zero total', () => { ... });
        it('has no items', () => { ... });
    });

    describe('when items are added', () => {
        it('calculates total correctly', () => { ... });
        it('updates item count', () => { ... });
    });

    describe('when applying discount', () => {
        it('reduces total by percentage', () => { ... });
        it('does not allow negative totals', () => { ... });
    });
});
```

---

## Test Organization

### File Structure

```
src/
├── users/
│   ├── user.py
│   ├── user_service.py
│   └── user_repository.py
tests/
├── users/
│   ├── test_user.py
│   ├── test_user_service.py
│   └── test_user_repository.py
├── conftest.py          # Shared fixtures
└── factories.py         # Test data builders
```

### Shared Fixtures

```python
# conftest.py (pytest)
@pytest.fixture
def db_session():
    session = create_test_session()
    yield session
    session.rollback()

@pytest.fixture
def authenticated_user(db_session):
    user = UserFactory.create()
    db_session.add(user)
    return user

# Usage in tests
def test_user_can_update_profile(authenticated_user):
    authenticated_user.update_profile(name="New Name")
    assert authenticated_user.name == "New Name"
```

---

## Common Testing Mistakes

### 1. Testing Implementation, Not Behavior

```python
# BAD - Tests internal state
def test_add_item():
    cart = Cart()
    cart.add_item(Item("apple", 1.00))
    assert cart._items == [Item("apple", 1.00)]  # Testing private state

# GOOD - Tests observable behavior
def test_add_item():
    cart = Cart()
    cart.add_item(Item("apple", 1.00))
    assert cart.total == 1.00
    assert cart.item_count == 1
```

### 2. Brittle Tests

```python
# BAD - Depends on exact string format
def test_error_message():
    with pytest.raises(ValueError) as exc:
        validate_email("bad")
    assert str(exc.value) == "Invalid email format: 'bad' is not a valid email"

# GOOD - Tests meaningful behavior
def test_invalid_email_raises_error():
    with pytest.raises(ValueError):
        validate_email("bad")
```

### 3. Test Interdependence

```python
# BAD - Tests depend on each other
class TestUserFlow:
    user = None

    def test_1_create_user(self):
        TestUserFlow.user = create_user("test@example.com")
        assert TestUserFlow.user is not None

    def test_2_update_user(self):
        TestUserFlow.user.name = "Updated"  # Depends on test_1
        assert TestUserFlow.user.name == "Updated"

# GOOD - Independent tests
def test_create_user():
    user = create_user("test@example.com")
    assert user is not None

def test_update_user():
    user = create_user("test@example.com")  # Each test sets up its own data
    user.name = "Updated"
    assert user.name == "Updated"
```

### 4. Ignoring Edge Cases

```python
# Incomplete - Only tests happy path
def test_divide():
    assert divide(10, 2) == 5

# Complete - Tests edge cases
def test_divide_normal():
    assert divide(10, 2) == 5

def test_divide_by_zero_raises():
    with pytest.raises(ZeroDivisionError):
        divide(10, 0)

def test_divide_negative_numbers():
    assert divide(-10, 2) == -5

def test_divide_returns_float():
    assert divide(5, 2) == 2.5
```

---

## Quick Reference

### TDD Mantra
1. Red → Green → Refactor
2. Write the test first
3. Write minimal code to pass
4. Refactor while green

### Test Structure
- Arrange → Act → Assert
- One behavior per test
- Descriptive names

### Mocking Rules
- Mock at boundaries
- Don't mock what you own
- Prefer fakes for complex dependencies
- Verify behavior, not implementation

### Quality Signals
- Tests run fast (<1s per test)
- Tests are independent
- Tests are deterministic
- Tests document behavior

## Security Note

**What this command can do:**
- Read existing test files
- Search codebase for patterns
- Provide guidance and examples

**What it cannot do:**
- Modify code
- Execute tests
- Access external systems
