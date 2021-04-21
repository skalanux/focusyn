# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## 0.12.0

### Fixed

- Ratio rounding in Timer payload

### Added

- Shortcuts to change session to pomodoro (Ctrl+1), short break (Ctrl+2) and long break (Ctrl+3)
- Shortcut to open settings
- EndSessionPayload have the same fields of a SessionPayload plus the previous field that is the last SessionPayload

### Changed

- Session actions (start, stop, reset) keys in shortcuts section in the config
- Join python-focusyn and focusyn-gtk projects
- Timer, Session and App have their own state values instead of a shared Enum
- Redesign the event API
- Redesign the plugin API

### Removed

- Remove Session, Timer, Config, and View blinker.Signal objects
- Remove State and Session enums

## 0.11.0

### Added

- Session keyboard shortcuts

## 0.10.0

### Changed

- The timer, session and settings now emit a payload object instead of a dictionary

## 0.9.2

### Fixed

- Timer countdown blinking

## 0.9.1

### Changed

- Arch linux installation instructions

## 0.9.0

### Changed

- Change UI to use a headerbar widget instead of a toolbar
- The Task enum was renamed to Sessions

### Removed

- Show notifications in then main widget (**show\_message view interface**)

## 0.8.0

## Added

- Show notifications in the main widget (**show\_message** view interface)

### Fixed

- Reopen from command line

### Changed

- Arch installation instructions

## 0.7.0

### Added

- Using wiring.scanning
- Add plugin settings window
  
### Changed

- Python 3 only

## 0.6.0

### Added

- Add menu widget

## 0.5.0

### Fixed

- Fix Gtk warnings

## 0.4.0

### Added

- Using the new event system
  
### Removed

- Remove appindicator3 dependency
