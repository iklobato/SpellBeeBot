# Spelling Bee Solver

An automated solver for the SpellBee.org unlimited game using Playwright for browser automation and Python.

## Description

This script automatically solves the Spelling Bee puzzle on SpellBee.org by:
1. Loading a dictionary of valid words
2. Accessing the game through an automated browser session
3. Identifying the puzzle letters
4. Finding valid words
5. Automatically entering them into the game

## Features

- Automated browser control using Playwright
- Mobile device emulation for better compatibility
- Progress monitoring with real-time updates
- Word filtering based on game rules
- Pangram detection
- Progress bar for word submission
- Console-based progress tracking

## Prerequisites

- Python 3.x
- Playwright
- tqdm (for progress bars)
- A word dictionary file (words2.txt)

## Installation

```bash
pip install playwright tqdm
playwright install chromium
```

## Dictionary Requirements

The script expects a dictionary file (default: 'words2.txt') with the following characteristics:
- One word per line
- Words should be in plain text format
- Words are filtered based on:
  - Minimum length of 4 characters
  - Minimum of 4 unique letters
  - Only alphabetical characters

## How It Works

1. **Dictionary Loading**
   - Loads words from the specified dictionary file
   - Filters words based on minimum length and unique letter requirements
   - Converts all words to lowercase

2. **Browser Setup**
   - Launches a headless Chromium browser
   - Configures mobile device emulation settings
   - Navigates to spellbee.org/unlimited

3. **Game Analysis**
   - Identifies the center letter and surrounding letters
   - Finds valid words that:
     - Contain the center letter
     - Only use available letters
     - Identifies pangrams (words using all available letters)

4. **Word Submission**
   - Sorts words by length (pangrams first)
   - Automatically types each word
   - Submits valid words
   - Displays real-time progress
   - Shows points needed for next level

## Progress Monitoring

The script includes a sophisticated progress monitoring system that:
- Observes DOM mutations for game progress updates
- Displays current title and points needed for next level
- Updates progress in real-time using custom events
- Shows a progress bar for word submission

## Usage

```bash
python spelling_bee_solver.py
```

The script will:
1. Print the center letter and available letters
2. Display the number of valid words and pangrams found
3. Show real-time progress of word submission
4. Wait for user input before closing

## Output Example

```
Center letter: A
All letters: B, C, D, E, F, G
Found 150 valid words (3 pangrams)
Current Level - 50 points to Next Level
[████████████████████] 100% | Words submitted: 150
```

## Error Handling

- Handles browser closure gracefully
- Provides logging for execution time and errors
- Restores cursor visibility after execution
- Includes timeout handling for page loading

## Limitations

- Requires a reliable internet connection
- Depends on the spellbee.org website structure
- Dictionary quality affects solver effectiveness
- Site changes may require script updates

## Notes

- The script uses a headless browser by default
- Includes a small delay between word submissions
- Progress is displayed using ANSI escape sequences
- Browser closes after user confirmation
