
# Vigenere Cipher cracking tool

## Theory
The main idea behind cracking Vigenere cipher came from process called <b>Kasiski examination</b>.
This method was discovered by Friedrich Kasiski in 1863 and  is used to attack 
ciphers with polyalphabetic substitutions. The entire method can be divided into five steps, which are listed below.

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
to find out the most frequent letters in the language for each group.
</li>

<li> <b>Brute-force</b> - After obtaining the most frequent letters for each group
(where each group represents one letter in the key), we can start a brute force attack.
If the brute force attack fails, we return to step 3) and try the whole process for the
second most frequent factors. If it fails again, try for the third common factor, and so on.
</li>
</ol>

The algorithm is based on the book [Cracking Code With Python] [1].

## Script description

At first it is needed to cipher the text with Vigenere Cihper. This can be done using online tool (e.g. https://cryptii.com/pipes/vigenere-cipher). 
The ciphered message is need to be saved into file called <i>encrypted.txt</i>.

After the ciphered message has been created, the <i>vc_cracker.py</i> script can be used to crack the cipher. This
script reads the content from <i>encrypted.txt</i> file and tries to decrypt it. If the decryption is successful, the
decrypted message is printed to the standard output and the message is saved into file <i>decrypted.txt</i>.

## How to run
The script is written only in Python 3.8. There is no need to install other dependencies except Python3 interpreter. 

```
usage: python3 vc_cracker.py [-h] [-k KEY] [-l LETTERS] [-r SEQUENCES] [-f FILE] [-s]

Python tool for cracking Vigenere Cipher

optional arguments:
  -h, --help            show this help message and exit
  -k KEY, --key KEY     maximum key length
  -l LETTERS, --letters LETTERS
                        number of tested letters per key
  -r SEQUENCES, --sequences SEQUENCES
                        the length of repeated sequences
  -f FILE, --file FILE  the name of the file from which the content is read
  -s, --suppress        run in silent mode, suppress stdout
```


### Example run

The following code show example of running this script. The parameter <i>key</i> is set to 20, so it will assume that
the key is no longer than 20 characters. The parameter <i>letters</i> is set to 5, so at each character position 
in the key, the algorithm will attempt to test only the five most common letters. The <i>sequences</i> parameter is set to 3, so it will 
try to find repeating sequences with length of 3 (AAA, AAB, etc.). The last parameter <i>file</i> is not set, so it will
be used the default file, which is <i>encrypted.txt</i>.

```
python vc_cracker.py --key 20 --letters 5 --sequences 3
```

### Example output

After running the command above, the output should be something like this.


```
************************************************
Initializing Kasiski Examination
Max key length: 20
Letter per subkey: 5
************************************************


The most likely key lengths are: 5 2 10 3 15 4 13 9 6 12 11 7 8 16

--------------------- Attempt number 1 ---------------------

Currently trying key length: 5 ( 1024 total key combinations)
Possible letters for letter 1 of the key: AEGL
Possible letters for letter 2 of the key: REXC
Possible letters for letter 3 of the key: ETDI
Possible letters for letter 4 of the key: AEGO
Possible letters for letter 5 of the key: ALOE
Attempting with key: AREAA
Possible encryption with key AREAA:


************************************************
         DECRYPTED MESSAGE BELOW
************************************************
Here will be decrypted message
```



## References

[1]: https://ihatefeds.com/No.Starch.Cracking.Codes.With.Python.2018.pdf "Cracking Codes With Python"