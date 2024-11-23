# py-bondi
A library for creating event driven systems using domain driven design.

### Installation

```bash
pip install pybondi
```

### Introduction

This library provides a framework for modeling complex domains using an event driven architecture and the pub/sub pattern. It provides:

- An in memory message bus for handling events and commands.
- A simple in memory publisher for publishing messages to external systems.
- A base aggregate root that can collect domain events and a base aggregate class.
- A base repository class for storing and retrieving aggregates.
- A session class for managing transactions and unit of work. 
- Default events for handling aggregate's state when it is added to a session, saved, or rolled back.

Soon I will be updating this README with a more detailed explanation of how to use the library.