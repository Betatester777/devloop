# User Request

## Raw Request

name: Delicious Memory
summary: A Python-based colorful interactive desktop memory matching game themed around delicious dishes, dining, and drinks.
requirements:
- colorful card-based gameplay
  - board loads with hidden face-down square cards arranged in a grid
  - cards flip with visible animation and show food artwork
  - matched pairs stay revealed, mismatched pairs flip back after delay
  - rapid input during flip animation is ignored to prevent race conditions
- food-themed content categories
  - category names are equal to subfolder names in assets/images
  - load random images from selected category into cards
  - categories are visually distinct and recognizable at card size
  - all shipped assets are listed in an asset manifest with source URL and license
- multiple difficulty levels
  - easy, normal, and hard modes change board size and challenge settings
  - difficulty level changes number of cards (more or less cards)
  - difficulty selection is available from the main menu before starting a game
  - card placement is randomized each round
- score and timer systems
  - move counter increments correctly for each match and mismatch attempt
  - score formula matches documented product rules
  - timed mode shows a visible countdown that decreases accurately
  - timer expiry triggers a fail/retry screen without crash
  - victory screen shows correct summary of score, moves, and time
- optional save and resume
  - player can save mid-round and resume after restarting the application
  - restored state includes score, moves, timer, and matched card positions
  - continue option is disabled or hidden when no save file exists
  - corrupted save file is handled gracefully with an error message
- sound and theme settings
  - settings menu shows all configurable options
  - play sound on flip, match, not match, win, lose
  - sounds are located in assets/sounds folder
  - theme/color mode change applies immediately without breaking readability
  - sound and music can be muted/unmuted and the setting persists across sessions
  - reduced animation mode keeps interactions understandable with less motion
  - use color theme colors:
    - brand green G900: #005623
    - brand green G800: #006c2c
    - brand green G700: #008134
    - brand green G600: #00973d
    - brand green G500: #00ac46
    - brand green G400: #2bbd65
    - brand green G300: #57cd84
    - brand green G200: #82dba3
    - brand green G100: #ade9c3
    - brand green G20: #cceeda
    - brand green G15: #d9f3e3
    - neutrals N100: #fbfbfb
    - neutrals N100Bold: #ededed
    - neutrals N100Bolder: #d6d6d6
    - neutrals N200: #f3f5f3
    - neutrals N200Bold: #e2e4e2
    - neutrals N200Bolder: #cccecc
    - neutrals N300: #edefee
    - neutrals N400: #dcdfdc
    - neutrals N500: #b2b4b5
    - neutrals N600: #919394
    - neutrals N700: #707375
- responsive desktop UI
  - application launches and shows main menu without crash
  - window resize scales UI correctly with all controls visible
  - alt-tab and focus switching causes no rendering corruption or input lock
  - application closes cleanly from the quit button with no hang
- performance: startup time and frame rate
  - application starts within acceptable time on target machine
  - no visible frame stutter during normal gameplay
  - input response feels immediate with no perceptible lag
- reliability: crash-free and stable game loop
  - no crash during repeated play sessions of 30-60 minutes
  - no save corruption during normal use
  - no blocked progression in any game loop path
  - rapid restart loops reset state correctly every time
- usability: intuitive for new players
  - new player can start a round without needing external explanation
  - color themes maintain text readability across all backgrounds
  - result screens clearly explain success or failure
- accessibility: keyboard support and contrast
  - full game is playable with keyboard only, no mouse required
  - keyboard focus indicator is always visible during navigation
  - color contrast remains acceptable in all themes
  - audio is optional and not required for core gameplay
architecture:
  - python
  - pygame
  - pytest
  - linux
  - windows

## Additional Requests (2026-03-17)

- Add category selection in the settings/options screen so the player can choose which food category to play with
- The default color theme should be light (not green/dark)

## Date Received

2026-03-16

## Notes

Structured bulk input. Top-level requirements map to feature bundles. Sub-items map to acceptance criteria. Architecture section specifies tech stack and target platforms.
