import argparse
import os


class Dictionary:
    def __init__(self, alphabet, lang='english'):
        self.letters_and_space = alphabet + alphabet.lower() + ' \t\n'
        if lang == 'english':
            self.lang = lang
            dictionary = open('dictionary.txt')
            words = {}
            for word in dictionary.read().split('\n'):
                words[word] = None
            dictionary.close()
            self.words = words

    def get_count(self, message):
        message = message.upper()
        message = self.remove_non_letters(message)
        possible_words = message.split()

        if not possible_words:
            return 0.0

        matches = 0
        for word in possible_words:
            if word in self.words:
                matches += 1
        return float(matches) / len(possible_words)

    def remove_non_letters(self, message):
        letters = []
        for symbol in message:
            if symbol in self.letters_and_space:
                letters.append(symbol)
        return ''.join(letters)

    def is_valid_language(self, message, word_percentage=20, letter_percentage=85):
        words = self.get_count(message) * 100 >= word_percentage
        number_of_letters = len(self.remove_non_letters(message))
        messag_percentage = float(number_of_letters) / len(message) * 100
        letters_match = messag_percentage >= letter_percentage
        return words and letters_match


class FrequencyAnalysis:

    def __init__(self, alphabet):
        self.frequency_alphabet = {
            'english': 'ETAOINSHRDLCUMWFGYPBVKJXQZ',
            'czech': 'XX'
        }
        self.alphabet = alphabet

    def count_letters(self, message):
        letter_count = dict.fromkeys([char for char in self.alphabet], 0)

        for letter in message.upper():
            if letter in self.alphabet:
                letter_count[letter] += 1

        return letter_count

    def get_frequency_order(self, message, frequency_alphabet):
        letter_frequency = self.count_letters(message)

        frequency_letter = {}
        for letter in self.alphabet:
            if letter_frequency[letter] not in frequency_letter:
                frequency_letter[letter_frequency[letter]] = [letter]
            else:
                frequency_letter[letter_frequency[letter]].append(letter)

        for freq in frequency_letter:
            frequency_letter[freq].sort(key=frequency_alphabet.find, reverse=True)
            frequency_letter[freq] = ''.join(frequency_letter[freq])

        frequency_pairs = list(frequency_letter.items())
        frequency_pairs.sort(key=lambda x: x[0], reverse=True)

        frequency_order = []
        for frequency_pair in frequency_pairs:
            frequency_order.append(frequency_pair[1])

        return ''.join(frequency_order)

    def get_score(self, message, alphabet='english'):
        frequency_alphabet = self.frequency_alphabet.get(alphabet)
        frequency_order = self.get_frequency_order(message, frequency_alphabet)

        score = 0
        for letter in frequency_alphabet[:6]:
            if letter in frequency_order[:6]:
                score += 1

        for letter in frequency_alphabet[-6:]:
            if letter in frequency_order[-6:]:
                score += 1

        return score


class VigenereCipher:

    def __init__(self, alphabet):
        self._alphabet = alphabet

    def __process_(self):
        pass

    def encrypt_message(self, message, key):
        print('Encrypting has started...')
        print(f'Message: {message}')
        print(f'Used key: {key}')
        translated = []

        index = 0
        key = key.upper()

        for letter in message:
            num = self._alphabet.find(letter.upper())
            if num != -1:
                num += self._alphabet.find(key[index])
                num %= len(self._alphabet)

                if letter.isupper():
                    translated.append(self._alphabet[num])
                elif letter.islower():
                    translated.append(self._alphabet[num].lower())

                index += 1
                if index == len(key):
                    index = 0
            else:
                translated.append(letter)

        return ''.join(translated)

    def decrypt_message(self, message, key):
        translated = []
        keyIndex = 0
        key = key.upper()

        for symbol in message:
            num = self._alphabet.find(symbol.upper())
            if num != -1:
                num -= self._alphabet.find(key[keyIndex])
                num %= len(self._alphabet)

                if symbol.isupper():
                    translated.append(self._alphabet[num])
                elif symbol.islower():
                    translated.append(self._alphabet[num].lower())

                keyIndex += 1
                if keyIndex == len(key):
                    keyIndex = 0
            else:
                translated.append(symbol)

        return ''.join(translated)


def parse_arguments():
    parser = argparse.ArgumentParser(description="Python tool for Vigenere Cipher encryptions")
    parser.add_argument("-k", "--key", action="store", dest="key", default="KAS",
                        help="key used during encryption")
    parser.add_argument("-m", "--message", action="store", dest="message", default="Default message",
                        help="message to be encrypted")
    parser.add_argument("-c", "--clear", dest="clear", action="store_true", default=False,
                        help="remove created files", )

    return parser.parse_args()


def main():
    file_name = "encrypted.txt"
    alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    args = parse_arguments()

    if args.clear:
        if os.path.exists(file_name):
            os.remove(file_name)
            print(f'File {file_name} has been successfully deleted')
        else:
            print(f'Nothing to be removed')
        return

    key, message = args.key, args.message

    vigenere_cipher = VigenereCipher(alphabet)
    encrypted_message = vigenere_cipher.encrypt_message(key=key, message=message)

    print(f'decrypted message: {vigenere_cipher.decrypt_message(encrypted_message, key)}')
    with open(file_name, 'w') as file:
        file.write(encrypted_message)
        print("Encrypted message has been successfully written into file 'encrypted.txt' ")


if __name__ == '__main__':
    main()
