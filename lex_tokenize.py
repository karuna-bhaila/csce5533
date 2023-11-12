from ply import lex
import re

class HTMLLexer(object):

    tokens = (
        'TAG',
        'TEXT_TAG',
        'FLOAT',
        'TIME',
        'COMMA_NUMBER',
        'HYPENATED',
        'ABBREVIATED',
        'WORD',
        'WHITESPACE',
        'PUNCTUATION',
    )

    #rule for html tags
    def t_TAG(self, t):
        r'\s*<[^>]*>\s*'
        pass

    #When a HTML tag is in the middle of a word, such as a <b> tag
    def t_TEXT_TAG(self, t):
        r'(\w+<[^>]*>\w+)+'
        t.value = re.sub("<[^>]*>", "", t.value)
        t.value = str(t.value).lower()
        return t

    #for hypenated words
    def t_HYPENATED(self, t):
        r"(\w+-\w+)(-\w+)*"
        t.value = re.sub("-*", "", t.value)
        t.value = str(t.value).lower()
        return t

    #rule for floats, we ignore everything in the decimal place
    def t_FLOAT(self, t):
        r"[-+]?\d*\.\d+"
        t.value = str(abs(int(float(t.value))))
        return t

    #numbers which have commas in them, we just remove the comma
    def t_COMMA_NUMBER(self, t):
        r"(\d*,\d+)+"
        t.value = re.sub(",", "", t.value)
        return t

    #numbers that have a colon in them
    def t_TIME(self, t):
        r"\w+:\w+"
        t.value = re.sub(":", "", t.value)
        return t

    #This rule catches abbreviations as well as websites urls
    def t_ABBREVIATED(self, t):
        r"(\w+\.\w+)(\.\w+)*"
        t.value = re.sub("\.", "", t.value)
        t.value = str(t.value).lower()
        return t

    #Every string of alphanumeric characters that does not have a rule yet
    def t_WORD(self, t):
        r'\w+'
        t.value = str(t.value).lower()
        return t

    def t_PUNCTUATION(self, t):
        r'[!"#$%&\'\(\)\*\+,-./:;<=>?@\[\]^_`{|}~\\/]'
        pass

    def t_WHITESPACE(self, t):
        r'\s+'
        pass

    # Error handling rule
    def t_error(self,t):
        # print("Illegal character '%s'" % t.value[0])
        t.lexer.skip(1)

    # Build the lexer
    def build(self,**kwargs):
        self.lexer = lex.lex(module=self, **kwargs)
        self.frequency = {}

    #after one file counts the frequency of words in the file, it calls this function to update the running total of token frequencies
    def updateFrequency(self, freq):
        for key in freq:
            if key in self.frequency:
                self.frequency[key] = self.frequency[key] + freq[key]
            else:
                self.frequency[key] = freq[key]

    #opens inputFile, tokenizes it and returns tokens
    # if getToknes is set to False, writes the tokens to outputFile
    def tokenizeFile(self, inputFile, outputFile=None, getTokens=True):

        tokens = []

        #read the file and tokenize
        with open(inputFile,'rb') as f:
            for line in f:
                line = line.decode(errors='ignore')
                self.lexer.input(line)
                while True:
                    tok = self.lexer.token()
                    if not tok:
                        break
                    tokens.append(tok.value)

        # return tokens here
        if getTokens:
            return tokens
        
        assert outputFile is not None
        
        #write the tokens
        with open(outputFile, 'w') as f:
            for x in tokens:
                f.write("%s " % x)
        
        #Count the frequency of tokens for this file
        freq = {}
        for x in tokens:
            if (x in freq):
                freq[x] += 1
            else:
                freq[x] = 1

        # update the global count of token frequencies
        self.updateFrequency(freq)
    
    #create the files with tokens sorted by frequency and also alphabetically
    def finish(self):

        with open("sorted.txt", "w") as f:
            for w in sorted(self.frequency):
                f.write("%s %d\n" % (w, self.frequency[w]))

        with open("frequency.txt", "w") as f:
            for w in sorted(self.frequency, key=self.frequency.get, reverse=True):
                f.write("%s %d\n" % (w, self.frequency[w]))

    #Test function that is from the ply examples
    def test(self,data):
        self.lexer.input(data)
        while True:
            tok = self.lexer.token()
            if not tok:
                break
            print(tok)
