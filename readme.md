## Overview

This program uses the NLTK word corpus to find step-words (a word + letter anagrammed into another word).

### Requirements

```
pip install nltk
```

### Commands

#### 1. Step

Find all possible step words that can be created by combining a word and letter.

```
python step-word.py step --word WORD --letter LETTER
```

**Options:**

* `-w, --word`: The starting word
* `-l, --letter`: The letter to add

#### 2. Unstep

Find the best combinations of words and letters that can be stepped.

```
python step-word.py unstep [options]
```

**Options:**

* `-w, --word`: Specific word to analyze
* `-c, --count`: Number of results to show (default: 5)
* `--reverse`: Sort in ascending order (shows the worst combinations)

### Notes

* Results are cached in 'processed_words.json' for performance in subsequent runs.
* Only alphabetic words are considered.
