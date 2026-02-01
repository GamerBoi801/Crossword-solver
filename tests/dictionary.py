class FastDictionary():
    def __init__(self, filename = "data/words.csv"):
        self.all_words = set() #set for every word in the dictionary
        self.length_index = dict() #keys r ints  vals r set of words
        self.pattern_index = dict() #nested dictionary , l1 key is word length, l2 key  tuple(index, char)
        #value is the set of words that fit the specific len and letter at that specific point

        with open(filename , "r") as file:
            for line in file:
                word, length = line.strip().split(",")
                word = word.upper()

                self.all_words.add(word)
                
                if length not in self.length_index:
                    self.length_index[length] = set()
                    self.length_index[length].add(word)

                if length not in self.pattern_index:
                    self.pattern_index[length] = dict()

                for i, char in enumerate(word):
                    key_tuple = (i, char)

                    if (i, char) not in self.pattern_index[length]:
                        self.pattern_index[length][key_tuple] = set()
                        self.pattern_index[length][key_tuple] = word

                '''Basic idea of pattern_index is thi
                Imagine looking for a 3 letter word with 'O' in the middle index
                1. you go to look self,pattern_index[3]
                2. at that index look up the key (1, 'O')
                3. U get a set of words like ['DOG', "POT', 'LOT', 'GOD']
                ]'''

   