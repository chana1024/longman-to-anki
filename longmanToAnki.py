import requests
from bs4 import BeautifulSoup
import genanki
import random
import os
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import argparse

class LongmanScraper:
    def __init__(self):
        self.base_url = "https://www.ldoceonline.com/dictionary/"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.session = requests.Session()
        retry_strategy = Retry(
            total=5,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)

    #deprecated
    def _extract_ipa(self, pron_codes_span):
       if not pron_codes_span:
           return ''
       
       # Extract British pronunciation
       brit_pron = pron_codes_span.find('span', class_='PRON')
       brit_ipa = brit_pron.text if brit_pron else ''
       
       # Extract American pronunciation variation
       am_var = pron_codes_span.find('span', class_='AMEVARPRON')
       if am_var:
           # Find the actual different part
           am_diff = am_var.find(class_=False)  # Find span without class, which contains the different part
           am_diff_text = am_diff.text if am_diff else am_var.text
           # Remove the '$ ' prefix if it exists
           am_diff_text = am_diff_text.replace('$ ', '')
           
           # If American pronunciation is just a suffix difference
           if am_diff_text.startswith('-'):
               am_ipa = brit_ipa[:-1] + am_diff_text[1:]
           else:
               am_ipa = am_diff_text
       else:
           am_ipa = brit_ipa
       
       # Format the final IPA string
       return f"UK: /{brit_ipa}/ US: /{am_ipa}/"

    def get_word_info(self, word):
        try:
            url = f"{self.base_url}{word}"
            response = self.session.get(url, headers=self.headers, timeout=10)
            if response.status_code != 200:
                print(f"Failed to get data for word: {word}. Status code: {response.status_code}")
                return None
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            definition_section = soup.find('span', {'class': 'DEF'})
            if not definition_section:
                print(f"No definition found for word: {word}")
                return None

            parent_section = definition_section.find_parent('span', {'class': 'Sense'})
            
          # Extract IPA using the new method
            pron_codes_span = soup.find('span', class_='PronCodes')
            ipa = pron_codes_span.text
            example = parent_section.find('span', class_='EXAMPLE')
            
            audio_element = parent_section.find('span', class_='speaker')
            word_audio_element=soup.select('span.ldoceEntry > span.Head > span.speaker')
            worduk_audio_url = word_audio_element[0].get('data-src-mp3') if word_audio_element[0] else None
            wordus_audio_url = word_audio_element[1].get('data-src-mp3') if word_audio_element[1] else None
            example_audio_element=soup.select_one('.Sense .speaker')
            example_audio_url = example_audio_element.get('data-src-mp3') if example_audio_element else None
            
            # Format the link as per the requirement
            formatted_link = f'<a href="{url}">check in dictionary</a>'
            
            word_info = {
                'word': word,
                'ipa': ipa if ipa else '',
                'meaning': definition_section.text.strip(),
                'example': example.text.strip() if example else '',
                'link': formatted_link,
                'worduk_audio_filename': None,
                'wordus_audio_filename': None,
                'meaning_audio_filename': None,
                'example_audio_filename': None
            }
            
            if worduk_audio_url:
                self._download_audio(worduk_audio_url, word_info,'worduk')
            if wordus_audio_url:
                self._download_audio(wordus_audio_url, word_info,'wordus')
            if example_audio_url:
                self._download_audio(example_audio_url, word_info,'example')

            return word_info

        except Exception as e:
            print(f"Error processing word {word}: {str(e)}")
            return None

    def _download_audio(self, audio_url, word_info, type):
        try:
            word = word_info['word']
            filename = f"{word}_{type}_audio.mp3"
            
            # Create 'dist' folder if it doesn't exist
            os.makedirs('dist', exist_ok=True)
            
            # Set the full path for the audio file
            filepath = os.path.join('dist', filename)
            
            if not os.path.exists(filepath):
                response = self.session.get(audio_url, headers=self.headers)
                if response.status_code == 200:
                    with open(filepath, 'wb') as f:
                        f.write(response.content)
            word_info[f"{type}_audio_filename"] = filename
        except Exception as e:
            print(f"Failed to download audio for {word}: {str(e)}")
        return None

class AnkiCardGenerator:
    def __init__(self, deck_name='my words from reading'):
        self.model = genanki.Model(
            random.randrange(1 << 30, 1 << 31),
            deck_name,
            fields=[
                {'name': 'Word'},
                {'name': 'IPA'},
                {'name': 'Meaning'},
                {'name': 'Example'},
                {'name': 'Link'},
                {'name': 'Sound'},
                {'name': 'Sound_us'},
                {'name': 'Sound_Meaning'},
                {'name': 'Sound_Example'},
                {'name': 'Image'}
            ],
            templates=[
                {
                    'name': 'Card 1',
                    'qfmt': '''
                        <div id="rubric">4000 Essential English Words</div>
                        <div style='font-family: Arial; font-size: 70px;color:#FF80DD;'>{{Word}}</div>
                        {{Sound}}
                        {{Sound_us}}
                        <div style='font-family: Arial; font-size: 70px;color:#FF80DD;'>{{IPA}}</div>
                    ''',
                    'afmt': '''
                        <div style='font-family: Arial; color:#FF80DD;'>{{Word}}</div>
                        <hr>
                        {{Image}}
                        <hr>
                        <div style='font-family: Arial; color:#00aaaa; text-align:left;'>
                        Meaning: {{Meaning}}</div>
                        <hr>
                        <div style='font-family: Arial; color:#9CFFFA; text-align:left;'>
                        &nbsp;→&nbsp;Example: {{Example}}</div>
                        <hr>
                        <div style='font-family: Arial; color:#9CFFFA; text-align:left;'>
                        &nbsp;→&nbsp;{{Link}}</div>
                        {{Sound}}
                        {{Sound_Example}}
                    ''',
                },
            ])
        self.deck = genanki.Deck(
            random.randrange(1 << 30, 1 << 31),
            deck_name
        )

    def create_note(self, word_info):
        if not word_info:
            return
        
        note = genanki.Note(
            model=self.model,
            fields=[
                word_info['word'],
                word_info['ipa'],
                word_info['meaning'],
                word_info['example'],
                word_info['link'],
                f'[sound:{word_info["worduk_audio_filename"]}]' if word_info['worduk_audio_filename'] else '',
                f'[sound:{word_info["wordus_audio_filename"]}]' if word_info['wordus_audio_filename'] else '',
                f'[sound:{word_info["meaning_audio_filename"]}]' if word_info['meaning_audio_filename'] else '',
                f'[sound:{word_info["example_audio_filename"]}]' if word_info['example_audio_filename'] else '',
                ''  # Empty Image field
            ]
        )
        self.deck.add_note(note)

    def save_deck(self, filename='english_words.apkg'):
        # Create 'dist' folder if it doesn't exist (though it should already exist)
        os.makedirs('dist', exist_ok=True)

        # Get all MP3 files from the 'dist' folder
        media_files = [f for f in os.listdir('dist') if f.endswith('.mp3')]

        package = genanki.Package(self.deck)
        package.media_files = [os.path.join('dist', f) for f in media_files]

        # Save the file in the 'dist' folder
        output_path = os.path.join('dist', filename)
        package.write_to_file(output_path)
        print(f"Deck saved to: {output_path}")
        print(f"Media files location: {os.path.abspath('dist')}")

def read_words_from_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return [line.strip() for line in file if line.strip()]

def main():
    parser = argparse.ArgumentParser(
        description='Generate Anki cards from Longman dictionary definitions.',
        epilog='Example usage:\n'
               'python longmanToAnki.py -f words.txt\n'
               'python longmanToAnki.py -w apple banana cherry'
    )
    
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-f', '--file', type=str, metavar='FILE',
                       help='Path to a text file containing words (one per line)')
    group.add_argument('-w', '--words', nargs='+', metavar='WORD',
                       help='List of words to process (space-separated)')

    parser.add_argument('-o', '--output', type=str, default='english_words.apkg',
                        help='Name of the output Anki deck file (default: english_words.apkg)')
    parser.add_argument('-d', '--deck-name', type=str, default='my words from reading',
                        help='Name of the Anki deck (default: "my words from reading")')

    args = parser.parse_args()

    if args.file:
        words = read_words_from_file(args.file)
    else:
        words = args.words

    scraper = LongmanScraper()
    generator = AnkiCardGenerator(deck_name=args.deck_name)

    for word in words:
        word_info = scraper.get_word_info(word)
        if word_info:
            generator.create_note(word_info)

    generator.save_deck(args.output)

if __name__ == "__main__":
    main()
