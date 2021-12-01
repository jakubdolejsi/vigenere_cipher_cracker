
# Vigenere Cipher cracking tool

## Theory
The main idea behind cracking Vigenere cipher came from process called <b>Kasiski examination</b>.
This method was discovered by Friedrich Kasiski in 1863 and  is used to attack 
ciphers with polyalphabetic substitutions.
The entire method can be divided into five steps, which are listed below.

<ol>

<li><b>Find repeating sequences</b> - The first step is to find repeating sequences of at least three characters. 
After finding all these repeating sequences, the length between each sequence is calculated. 
This length is called <i>spacing</i>.
</li>

<li><b>Finding factors of spacings</b> - The next step is to find all the factors of 
all the distances found in the previous step. The most common factor (number) is 
likely to be the length of the key. 
</li>

<li> <b>Finding nth letter</b> - This step is the key step of the whole algorithm. 
If the key is N letters long, then every Nth letter must be encrypted with the same letter. 
After grouping every Nth letter together, we have N groups of messages.
</li>

<li> <b>Frequecny analysis</b> - Having created these groups, we can now use frequency analysis
to find out. The most frequent letters in the language for each group.
</li>

<li> <b>Brute-force</b> - After obtaining the most frequent letters for each group
(where each group represents one letter in the key), we can start a brute force attack.
If the brute force attack fails, we return to step 3) and try the whole process for the
second most frequent factors. If it fails again, try for the third common factor, and so on.
</li>
</ol>

## Project description
The project consists of two scripts. One script is used to encrypt the message using Vigenere Cipher and
save it to the file. The second script is used to decrypt the text inside that file using Kasiski's
examination.

At first it is needed to cipher text with Vigenere Cihper. This can be done using online tool (e.g. https://cryptii.com/pipes/vigenere-cipher). 
The ciphered message is need to be saved into file called <i>encrypted.txt</i>.

After the ciphered message has been created, the <i>vc_cracker.py</i> script can be used to crack the cipher. This
script reads the content from <i>encrypted.txt</i> file, tries to decrypt it and the decrypted message saves to the 
<i>decrypted.txt</i> file and print it to the standard output.

## How to run
The script is written only in Python 3.8. There is no need to install other dependencies except Python. 

The following code example shows the script usage.

```
usage: python vc_cracker.py [-h] [-k KEY] [-l LETTERS] [-f FILE] [-s]

Python tool for cracking Vigenere Cipher

optional arguments:
  -h, --help            show this help message and exit
  -k KEY, --key KEY     maximum key length
  -l LETTERS, --letters LETTERS
                        number of tested letters per key
  -f FILE, --file FILE  the name of the file from which the content is read
  -s, --suppress        run in silent mode, suppress stdout
```

