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

Initial check showed GitHub CLI was not installed in the environment:

```text
zsh:1: command not found: gh
```

After GitHub CLI was installed externally, a pure-git push was attempted using:

```text
origin = https://github.com/Samanyu-dev/robot_vision.git
git push -u origin main
```

GitHub responded:

```text
remote: Repository not found.
fatal: repository 'https://github.com/Samanyu-dev/robot_vision.git/' not found
```

Conclusion: plain `git` can push to an existing repository, but it cannot create a new GitHub repository by itself. Remote repository creation is still blocked until either:

1. an empty GitHub repository named `robot_vision` is created manually, or
2. repository creation is performed with `gh repo create` or the GitHub web UI/API.

## Next Phase

Phase 1 will implement:

- DH parameter definition
- homogeneous transform construction
- forward kinematics for the 3R arm
- a small numerical sanity check
