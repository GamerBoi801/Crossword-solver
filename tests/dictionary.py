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
                length = int(length)

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
                        self.pattern_index[length][key_tuple].add(word)
                    else:
                        self.pattern_index[length][key_tuple].add(word)

                '''Basic idea of pattern_index is thi
                Imagine looking for a 3 letter word with 'O' in the middle index
                1. you go to look self,pattern_index[3]
                2. at that self.crossword.variable's index look up the key (1, 'O')
                3. U get a set of words like ['DOG', "POT', 'LOT', 'GOD']
                ]'''

   
    def get_matches(self, length : int, requirements : dict):
      '''
      length: int (required len of the word)
      requirements: dict {0: 'A', 2: 'T} means index 0 must be  A, 
      index 2 must be a T
      '''
      #first we get the universal set of words for this length
      len_result_set : set = self.length_index.get(length)

      #if no words of this len exist empty set
      if len_result_set is None:
          return set()
      
      len_result_set = len_result_set.copy()

      #apply each char filter one by 1
      for index, char in requirements.items():
          
          length_patterns = self.pattern_index.get(length, {})  #gives 
          matching_bucket = length_patterns.get((index, char))

          if matching_bucket is None:
              # if no words fit the specific char constraints return empty set
                return set()
          
        # this intersection keeps only the words that exist in both the result_set and the 
          len_result_set.intersection_update(matching_bucket)

          if not len_result_set: # if running out of words then stop checking
            break
      
      return len_result_set