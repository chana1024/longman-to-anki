Longman Dictionary to Anki Flashcards Generator

This Python script scrapes word definitions from the Longman Dictionary and generates Anki flashcards. It includes features like:

- Scraping word definitions, IPA pronunciations, and example sentences
- Downloading audio for both UK and US pronunciations
- Creating Anki cards with formatted content
- Generating an Anki deck (.apkg file) with associated media

Ideal for language learners and educators looking to create custom vocabulary decks.

Usage:
1. From a file:
   python longmanToAnki.py -f words.txt

2. From command line:
   python longmanToAnki.py -w apple banana cherry

3. Custom output and deck name:
   python longmanToAnki.py -f words.txt -o my_deck.apkg -d "My Custom Deck"

The generated Anki deck and media files will be saved in the 'dist' folder.
