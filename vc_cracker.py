import argparse
import itertools
import re
from collections import Counter
from vigenere_cipher import VigenereCipher, FrequencyAnalysis, Dictionary


class KasiskiExamination:

    def __init__(self,
                 encrypted_message: str,
                 max_key_length: str,
                 letter_per_subkey: str,
                 length_of_sequences: str,
                 alphabet: str,
                 suppress: bool
                 ):
        self.message = encrypted_message
        self.decrypted_message = None
        self._non_letter = re.compile('[^A-Z]')
        self._max_key_length = int(max_key_length)
        self._letter_per_subkey = int(letter_per_subkey)
        self.length_of_sequences = int(length_of_sequences)
        self._alphabet = alphabet
        self._suppress = suppress

        print('************************************************')
        print('Initializing Kasiski Examination')
        print(f'Max key length: {self._max_key_length}')
        print(f'Letter per subkey: {self._letter_per_subkey}')
        print(f'Length of repeating sequences: {self.length_of_sequences}')
        print('************************************************\n\n')


    def _flex_print(self, string: str) -> None:
        if not self._suppress:
            print(string)

    def _get_repeated_sequences(self, message: str) -> dict:
        message = self._non_letter.sub('', message.upper())

        spacings = {}
        for sequence_len in range(3, self.length_of_sequences + 3):
            for sequence_start in range(len(message) - sequence_len):
                seq = message[sequence_start:sequence_start + sequence_len]

                for i in range(sequence_start + sequence_len, len(message) - sequence_len):
                    if message[i:i + sequence_len] == seq:
                        if seq not in spacings:
                            spacings[seq] = []
                        spacings[seq].append(i - sequence_start)
        return spacings

    def _get_factors(self, number: int) -> list:
        if number < 2:
            return []

        factors = []

        for i in range(2, self._max_key_length + 1):
            if number % i == 0:
                factors.append(i)
                other_factors = int(number / i)
                if other_factors < self._max_key_length + 1 and other_factors != 1:
                    factors.append(other_factors)
        return list(set(factors))

    def _get_item_at_first_index(self, items: int or None) -> tuple:
        return items[1]

    def _get_most_common_factors(self, sequence_factors: dict) -> list:
        factors_by_each_sequence = list(sequence_factors.values())
        all_factors = list(itertools.chain(*factors_by_each_sequence))

        counter = Counter(all_factors)
        return [factor[0] for factor in counter.most_common(self._max_key_length)]

    def _kasiski_examination(self) -> list:
        repeated_spacings = self._get_repeated_sequences(self.message)

        sequence_factors = {}
        for seq in repeated_spacings:
            sequence_factors[seq] = []
            for spacing in repeated_spacings[seq]:
                sequence_factors[seq].extend(self._get_factors(spacing))

        return self._get_most_common_factors(sequence_factors)

    def _get_nth_subkey_letter(self, nth: int, key_len: int, message: str) -> str:
        message = self._non_letter.sub('', message)

        i = nth - 1
        letters = []
        while i < len(message):
            letters.append(message[i])
            i += key_len
        return ''.join(letters)

    def _try_hack_by_key(self, most_likely_key: int) -> str or None:
        vigenere_cipher = VigenereCipher(self._alphabet)
        frequency_analysis = FrequencyAnalysis(self._alphabet)
        dictionary = Dictionary(self._alphabet)

        upper_case_message = self.message.upper()
        overall_scores = []
        for nth in range(1, most_likely_key + 1):
            nth_letters = self._get_nth_subkey_letter(nth, most_likely_key, upper_case_message)

            inner_scores = []
            for possible_key in self._alphabet:
                decrypted_message = vigenere_cipher.decrypt_message(nth_letters, possible_key)
                current_score = (possible_key, frequency_analysis.get_score(decrypted_message))
                inner_scores.append(current_score)
            inner_scores.sort(key=self._get_item_at_first_index, reverse=True)

            overall_scores.append(inner_scores[:self._letter_per_subkey])

        if not self._suppress:
            for index, score in enumerate(overall_scores):
                print(f'Possible letters for letter {(index + 1)} of the key: ', end='')
                for freq_score in score:
                    print(f'{freq_score[0]}', end='')
                print("")

        for indexes in itertools.product(range(self._letter_per_subkey), repeat=most_likely_key):
            possible_keys = []
            for i in range(most_likely_key):
                possible_keys.append(overall_scores[i][indexes[i]][0])
            possible_key = ''.join(possible_keys)

            self._flex_print(f"Attempting with key: {''.join(possible_key)}")

            decrypted_message = vigenere_cipher.decrypt_message(upper_case_message, ''.join(possible_key))

            if dictionary.is_valid_language(decrypted_message):
                decrypted_letters = []
                for cipher, decrypt in zip(self.message, decrypted_message):
                    if cipher.isupper():
                        decrypted_letters.append(decrypt.upper())
                    else:
                        decrypted_letters.append(decrypt.lower())

                decrypted_message = ''.join(decrypted_letters)

                self._flex_print(f'Possible encryption with key: {possible_key}')
                return decrypted_message

        return None

    def run(self):

        likely_keys = self._kasiski_examination()
        self._flex_print(f"\nThe most likely key lengths are: {' '.join(list(map(str, likely_keys)))}")

        decrypted_message = None
        for attempt, most_likely_key in enumerate(likely_keys):

            self._flex_print(f'\n--------------------- Attempt number {attempt + 1} ---------------------')
            self._flex_print(f'\nCurrently trying key length: {most_likely_key} '
                             f'({self._letter_per_subkey ** most_likely_key} '
                             f'possible key combinations)')
            decrypted_message = self._try_hack_by_key(most_likely_key)
            if decrypted_message is not None:
                break

        if decrypted_message is None:
            self._flex_print('Unable to hack message with likely key length.')
        self.decrypted_message = decrypted_message

    def print_results(self):
        print('\n\n************************************************')
        print('         DECRYPTED MESSAGE BELOW')
        print('************************************************')
        if self.decrypted_message:
            print(self.decrypted_message)
        else:
            print('Message cannot be decrypted')
            print('Halting...')
        return self

    def save_to_file(self, output_file='decrypted.txt'):
        if not self.decrypted_message:
            return
        try:
            with open(output_file, 'w+') as file:
                file.write(self.decrypted_message)
        except Exception as e:
            print(f'Cannot write decrypted message to file: {output_file}')
            print(f'Following exception has occurred: {e}')


def parse_args():
    parser = argparse.ArgumentParser(description="Python tool for cracking Vigenere Cipher")
    parser.add_argument("-k", "--key", action="store", dest="key", default=16,
                        help="maximum key length", )
    parser.add_argument("-l", "--letters", action="store", dest="letters", default=4,
                        help="number of tested letters per key")
    parser.add_argument("-r", "--sequences", action="store", dest="sequences", default=3,
                        help="The length of repeated sequences")
    parser.add_argument("-f", "--file", action="store", dest="file", default="encrypted.txt",
                        help="the name of the file from which the content is read")
    parser.add_argument("-s", "--suppress", dest="suppress", action="store_true", default=False,
                        help="run in silent mode, suppress stdout", )
    return parser.parse_args()


def main():
    args = parse_args()
    alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    language = 'english'

    with open(args.file, 'r+') as file:
        kasiski_examination = KasiskiExamination(
            encrypted_message=file.read(),
            max_key_length=args.key,
            letter_per_subkey=args.letters,
            length_of_sequences=args.sequences,
            alphabet=alphabet,
            suppress=args.suppress,
        )
        kasiski_examination.run()
        kasiski_examination.print_results()
        kasiski_examination.save_to_file()


if __name__ == '__main__':
    main()
