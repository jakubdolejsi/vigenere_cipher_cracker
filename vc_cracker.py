import argparse
import itertools
import re
from vigenere_cipher import VigenereCipher, FrequencyAnalysis, Dictionary


class KasiskiExamination:

    def __init__(self,
                 encrypted_message: str,
                 max_key_length: int,
                 letter_per_subkey: int,
                 alphabet: str,
                 suppress: bool
                 ):
        self.message = encrypted_message
        self.decrypted_message = None
        self._non_letter = re.compile('[^A-Z]')
        self._max_key_length = max_key_length
        self._letter_per_subkey = letter_per_subkey
        self._alphabet = alphabet
        self._suppress = suppress

        print('************************************************')
        print('Initializing Kasiski Examination')
        print(f'Max key length: {self._max_key_length}')
        print(f'Letter per subkey: {self._letter_per_subkey}')
        print('************************************************\n\n')

    def _flex_print(self, string: str) -> None:
        if not self._suppress:
            print(string)

    def _get_repeated_sequences(self, message: str) -> dict:
        # Goes through the message and finds any 3 to 5 letter sequences
        # that are repeated. Returns a dict with the keys of the sequence and
        # values of a list of spacings (num of letters between the repeats).

        # Use a regular expression to remove non-letters from the message:
        message = self._non_letter.sub('', message.upper())

        # Compile a list of seqLen-letter sequences found in the message:
        spacings = {}  # Keys are sequences, values are lists of int spacings.
        for sequence_len in range(3, 6):
            for sequence_start in range(len(message) - sequence_len):
                # Determine what the sequence is, and store it in seq:
                seq = message[sequence_start:sequence_start + sequence_len]

                # Look for this sequence in the rest of the message:
                for i in range(sequence_start + sequence_len, len(message) - sequence_len):
                    if message[i:i + sequence_len] == seq:
                        # Found a repeated sequence.
                        if seq not in spacings:
                            spacings[seq] = []  # Initialize a blank list.

                        # Append the spacing distance between the repeated
                        # sequence and the original sequence:
                        spacings[seq].append(i - sequence_start)
        return spacings

    def _get_factors(self, number: int) -> list:
        """
        Return factors of number that are in range <1; max_key_length +1>
        """
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
        # First, get a count of how many times a factor occurs in seqFactors:
        factors_count = {}  # Key is a factor, value is how often it occurs.

        # seqFactors keys are sequences, values are lists of factors of the
        # spacings. seqFactors has a value like: {'GFD': [2, 3, 4, 6, 9, 12,
        # 18, 23, 36, 46, 69, 92, 138, 207], 'ALW': [2, 3, 4, 6, ...], ...}
        for seq in sequence_factors:
            factors = sequence_factors[seq]
            for factor in factors:
                if factor not in factors_count:
                    factors_count[factor] = 0
                factors_count[factor] += 1

        # Second, put the factor and its count into a tuple, and make a list
        # of these tuples so we can sort them:
        factors_by_count = []
        for factor in factors_count:
            # Exclude factors larger than MAX_KEY_LENGTH:
            if factor <= self._max_key_length:
                # factorsByCount is a list of tuples: (factor, factorCount)
                # factorsByCount has a value like: [(3, 497), (2, 487), ...]
                factors_by_count.append((factor, factors_count[factor]))

        # Sort the list by the factor count:
        factors_by_count.sort(key=self._get_item_at_first_index, reverse=True)

        return factors_by_count

    def _kasiski_examination(self) -> list:
        # Find out the sequences of 3 to 5 letters that occur multiple times
        # in the ciphertext. repeatedSeqSpacings has a value like:
        # {'EXG': [192], 'NAF': [339, 972, 633], ... }
        repeated_spacings = self._get_repeated_sequences(self.message)

        # (See getMostCommonFactors() for a description of seqFactors.)
        sequence_factors = {}
        for seq in repeated_spacings:
            sequence_factors[seq] = []
            for spacing in repeated_spacings[seq]:
                sequence_factors[seq].extend(self._get_factors(spacing))

        # (See getMostCommonFactors() for a description of factorsByCount.)
        factors_by_count = self._get_most_common_factors(sequence_factors)

        # Now we extract the factor counts from factorsByCount and
        # put them in allLikelyKeyLengths so that they are easier to
        # use later:
        probable_keys = []
        for factor in factors_by_count:
            probable_keys.append(factor[0])

        return probable_keys

    def _get_nth_subkey_letter(self, nth: int, key_len: int, message: str) -> str:
        # Returns every nth letter for each keyLength set of letters in text.
        # E.g. getNthSubkeysLetters(1, 3, 'ABCABCABC') returns 'AAA'
        #      getNthSubkeysLetters(2, 3, 'ABCABCABC') returns 'BBB'
        #      getNthSubkeysLetters(3, 3, 'ABCABCABC') returns 'CCC'
        #      getNthSubkeysLetters(1, 5, 'ABCDEFGHI') returns 'AF'

        # Use a regular expression to remove non-letters from the message:
        message = self._non_letter.sub('', message)

        i = nth - 1
        letters = []
        while i < len(message):
            letters.append(message[i])
            i += key_len
        return ''.join(letters)

    def _try_hack_by_key(self, most_likely_keys: int) -> str or None:
        vigenere_cipher = VigenereCipher(self._alphabet)
        freqAnalysis = FrequencyAnalysis(self._alphabet)
        dictionary = Dictionary(self._alphabet)

        # Determine the most likely letters for each letter in the key:
        upper_case_message = self.message.upper()
        # allFreqScores is a list of mostLikelyKeyLength number of lists.
        # These inner lists are the freqScores lists.
        overall_scores = []
        for nth in range(1, most_likely_keys + 1):
            nthLetters = self._get_nth_subkey_letter(nth, most_likely_keys, upper_case_message)

            # freqScores is a list of tuples like:
            # [(<letter>, <Eng. Freq. match score>), ... ]
            # List is sorted by match score. Higher score means better match.
            # See the englishFreqMatchScore() comments in freqAnalysis.py.
            inner_scores = []
            for possible_key in self._alphabet:
                decrypted_message = vigenere_cipher.decrypt_message(nthLetters, possible_key)
                current_score = (possible_key, freqAnalysis.get_score(decrypted_message))
                inner_scores.append(current_score)
            # Sort by match score:
            inner_scores.sort(key=self._get_item_at_first_index, reverse=True)

            overall_scores.append(inner_scores[:self._letter_per_subkey])

        if not self._suppress:
            for index, score in enumerate(overall_scores):
                # for i in range(len(overall_scores)):
                # Use i + 1 so the first letter is not called the "0th" letter:
                print(f'Possible letters for letter {(index + 1)} of the key: ', end='')
                for freqScore in score:
                    print(f'{freqScore[0]}', end='')
                print()  # Print a newline.

        # Try every combination of the most likely letters for each position
        # in the key:
        for indexes in itertools.product(range(self._letter_per_subkey), repeat=most_likely_keys):
            # Create a possible key from the letters in allFreqScores:
            possible_keys = []
            for i in range(most_likely_keys):
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

                self._flex_print(f'Possible encryption hack with key {possible_key}:')
                return decrypted_message

        return None

    def run(self):

        likely_keys = self._kasiski_examination()
        if not self._suppress:
            self._flex_print(f"Kasiski Examination results say the most likely key "
                             f"lengths are: {' '.join(list(map(str, likely_keys)))}")
        decrypted_message = None
        for keyLength in likely_keys:
            self._flex_print(f'Attempting hack with key length %s (%s possible keys)... '
                             f'{keyLength, self._letter_per_subkey ** keyLength}')
            decrypted_message = self._try_hack_by_key(keyLength)
            if decrypted_message is not None:
                break

        if decrypted_message is None:
            self._flex_print('Unable to hack message with likely key length(s). Brute forcing key length...')
        self.decrypted_message = decrypted_message

    def print_results(self):
        print('\n\n************************************************')
        print('         DECRYPTED MESSAGE BELOW')
        print('************************************************')
        print(self.decrypted_message)
        print('************************************************')
        return self

    def save_to_file(self, output_file='decrypted.txt'):
        try:
            with open(output_file, 'w+') as file:
                file.write(self.decrypted_message)
        except Exception as e:
            print(f'Cannot write decrypted message to file: {output_file}')
            print(f'Following exception has occured: {e}')


def parse_args():
    parser = argparse.ArgumentParser(description="Python tool for cracking Vigenere Cipher")
    parser.add_argument("-k", "--key", action="store", dest="key", default=16,
                        help="maximum key length", )
    parser.add_argument("-l", "--letters", action="store", dest="letters", default=4,
                        help="number of tested letters per key")
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
            alphabet=alphabet,
            suppress=args.suppress,
        )
        kasiski_examination.run()
        kasiski_examination.print_results()
        kasiski_examination.save_to_file()


if __name__ == '__main__':
    main()
