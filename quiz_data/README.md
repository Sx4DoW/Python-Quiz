# Quiz Data

This folder contains quiz questions in JSON format. Each JSON file should contain an array of question objects.

## Question Format

Each question must have the following structure:

```json
{
    "prompt": "Question text here?",
    "option_a": "First option",
    "option_b": "Second option",
    "option_c": "Third option",
    "option_d": "Fourth option",
    "correct_option": "b"
}
```

- `prompt`: The question text
- `option_a`, `option_b`, `option_c`, `option_d`: The four answer options
- `correct_option`: Must be one of: "a", "b", "c", or "d"

## Loading Questions

To load questions into the database, run:

```bash
python seed_questions.py
```

The script will:
1. Read all `.json` files from this folder
2. Load questions into the database
3. Ask for confirmation if questions already exist

## Adding New Questions

To add new questions:
1. Create a new `.json` file in this folder (e.g., `python_advanced.json`)
2. Follow the question format above
3. Run `python seed_questions.py` to load them into the database
