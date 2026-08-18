# hello.py
"""
A comprehensive OOP example in Python.

This script demonstrates:
- Classes and objects
- Inheritance and method overriding
- Encapsulation with private attributes and property getters/setters
- Class methods and static methods
- Use of @dataclass for simple data containers
- A simple factory pattern
- A small demo in the `if __name__ == "__main__"` block
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import List, ClassVar

# ---------------------------------------------------------------------------
# Base class: Person
# ---------------------------------------------------------------------------
class Person:
    """Base class representing a generic person.

    Attributes
    ----------
    _first_name: str
        The person's first name (protected).
    _last_name: str
        The person's last name (protected).
    age: int
        Public attribute for the person's age.
    """

    # Class variable to keep track of how many Person instances exist
    _population: ClassVar[int] = 0

    def __init__(self, first_name: str, last_name: str, age: int) -> None:
        self._first_name = first_name
        self._last_name = last_name
        self.age = age
        Person._population += 1
        print(f"[Person] Created: {self.full_name()}, age {self.age}")

    # -------------------------------------------------------------------
    # Encapsulation: property for full name (read‑only)
    # -------------------------------------------------------------------
    @property
    def full_name(self) -> str:
        """Return the person's full name as a single string."""
        return f"{self._first_name} {self._last_name}"

    # -------------------------------------------------------------------
    # Class method to query the population
    # -------------------------------------------------------------------
    @classmethod
    def population(cls) -> int:
        """Return the total number of Person (or subclass) instances created."""
        return cls._population

    # -------------------------------------------------------------------
    # Static method – a utility that does not depend on class/instance state
    # -------------------------------------------------------------------
    @staticmethod
    def is_adult(age: int) -> bool:
        """Return ``True`` if *age* is considered adult (>= 18)."""
        return age >= 18

    # -------------------------------------------------------------------
    # Magic methods for nicer printing and comparison
    # -------------------------------------------------------------------
    def __repr__(self) -> str:
        return f"Person('{self._first_name}', '{self._last_name}', {self.age})"

    def __str__(self) -> str:
        return f"{self.full_name}, {self.age} years old"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Person):
            return NotImplemented
        return (
            self._first_name == other._first_name
            and self._last_name == other._last_name
            and self.age == other.age
        )

    # -------------------------------------------------------------------
    # Destructor – decrement population counter (for demo purposes)
    # -------------------------------------------------------------------
    def __del__(self):
        Person._population -= 1
        print(f"[Person] Deleted: {self.full_name}")

# ---------------------------------------------------------------------------
# Subclass: Employee
# ---------------------------------------------------------------------------
class Employee(Person):
    """Represents an employee, extending :class:`Person`.

    Additional attributes
    --------------------
    employee_id: str
        Unique identifier for the employee.
    _salary: float
        Private attribute storing the employee's salary.
    """

    _id_counter: ClassVar[int] = 1

    def __init__(self, first_name: str, last_name: str, age: int, salary: float) -> None:
        super().__init__(first_name, last_name, age)
        self.employee_id = f"EMP{Employee._id_counter:04d}"
        Employee._id_counter += 1
        self._salary = salary
        print(f"[Employee] Assigned ID {self.employee_id} with salary ${self._salary:,.2f}")

    # Property for salary with validation
    @property
    def salary(self) -> float:
        return self._salary

    @salary.setter
    def salary(self, value: float) -> None:
        if value < 0:
            raise ValueError("Salary cannot be negative")
        self._salary = value
        print(f"[Employee] Salary for {self.employee_id} updated to ${self._salary:,.2f}")

    def give_raise(self, percent: float) -> None:
        """Increase salary by *percent* (e.g., 5 for a 5% raise)."""
        if percent < 0:
            raise ValueError("Raise percent must be non‑negative")
        increment = self._salary * (percent / 100)
        self.salary = self._salary + increment
        print(f"[Employee] {self.employee_id} received a {percent}% raise.")

    def __repr__(self) -> str:
        return (
            f"Employee('{self._first_name}', '{self._last_name}', {self.age}, "
            f"salary={self._salary})"
        )

# ---------------------------------------------------------------------------
# Subclass: Manager (inherits from Employee)
# ---------------------------------------------------------------------------
class Manager(Employee):
    """A manager is an employee who supervises other employees."""

    def __init__(self, first_name: str, last_name: str, age: int, salary: float) -> None:
        super().__init__(first_name, last_name, age, salary)
        self._team: List[Employee] = []
        print(f"[Manager] {self.employee_id} now manages a team.")

    def add_to_team(self, employee: Employee) -> None:
        if employee is self:
            raise ValueError("A manager cannot manage themselves")
        self._team.append(employee)
        print(f"[Manager] Added {employee.employee_id} to {self.employee_id}'s team.")

    def remove_from_team(self, employee: Employee) -> None:
        self._team.remove(employee)
        print(f"[Manager] Removed {employee.employee_id} from {self.employee_id}'s team.")

    @property
    def team(self) -> List[Employee]:
        """Return a copy of the manager's team list (read‑only)."""
        return list(self._team)

    def __repr__(self) -> str:
        return (
            f"Manager('{self._first_name}', '{self._last_name}', {self.age}, "
            f"salary={self._salary}, team_size={len(self._team)})"
        )

# ---------------------------------------------------------------------------
# Simple data container using @dataclass
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class Address:
    street: str
    city: str
    zip_code: str
    country: str = "USA"

    def __str__(self) -> str:
        return f"{self.street}, {self.city}, {self.zip_code}, {self.country}"

# ---------------------------------------------------------------------------
# Factory pattern – creates Person/Employee/Manager based on role
# ---------------------------------------------------------------------------
class PersonFactory:
    @staticmethod
    def create(role: str, first_name: str, last_name: str, age: int, **kwargs) -> Person:
        role = role.lower()
        if role == "person":
            return Person(first_name, last_name, age)
        elif role == "employee":
            salary = kwargs.get("salary", 0.0)
            return Employee(first_name, last_name, age, salary)
        elif role == "manager":
            salary = kwargs.get("salary", 0.0)
            return Manager(first_name, last_name, age, salary)
        else:
            raise ValueError(f"Unknown role '{role}'. Use 'person', 'employee', or 'manager'.")

# ---------------------------------------------------------------------------
# Demo / entry point
# ---------------------------------------------------------------------------
def main() -> None:
    # Create a few objects using the factory
    alice = PersonFactory.create("person", "Alice", "Anderson", 30)
    bob = PersonFactory.create("employee", "Bob", "Brown", 28, salary=55000)
    carol = PersonFactory.create("manager", "Carol", "Clark", 40, salary=95000)

    # Manager builds a team
    carol.add_to_team(bob)

    # Give Bob a raise
    bob.give_raise(5)

    # Show some info
    print("\n--- Summary ---")
    print(f"Total population: {Person.population()}")
    print(f"Alice: {alice}")
    print(f"Bob: {bob}, Salary: ${bob.salary:,.2f}")
    print(f"Carol: {carol}, Team size: {len(carol.team)}")

    # Demonstrate the Address dataclass
    addr = Address("123 Main St", "Springfield", "12345")
    print(f"Address example: {addr}")

    # Clean‑up (explicitly delete to see destructor messages)
    del alice
    del bob
    del carol
    print(f"Population after deletions: {Person.population()}")

if __name__ == "__main__":
    main()
