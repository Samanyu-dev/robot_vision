# Phase 0 Log

Date: 2026-04-18

## Objective

Create the project foundation and document the mental model for the robot vision system before writing numerical kinematics code.

## Completed

- Confirmed the workspace starts empty.
- Confirmed the workspace was not already a git repository.
- Defined the frame chain:

```text
{G} -> {B} -> {E} -> {C} -> {I}
```

- Documented the core point flow:

```text
P_G -> P_C -> P_I
```

- Documented the camera projection equations.
- Created the initial project structure:

```text
docs/
logs/
outputs/
src/
tests/
```

- Initialized the local git repository on branch `main`.
- Configured local-only git identity for this repository:

```text
user.name  = Samanyu-dev
user.email = allipuramsamanyu@gmail.com
```

## GitHub Blocker

GitHub CLI is not installed in the environment:

```text
zsh:1: command not found: gh
```

Remote repository creation and push are blocked until either:

1. `gh` is installed and authenticated, or
2. an empty GitHub repository named `robot_vision` is created manually and its remote URL is added locally.

## Next Phase

Phase 1 will implement:

- DH parameter definition
- homogeneous transform construction
- forward kinematics for the 3R arm
- a small numerical sanity check
