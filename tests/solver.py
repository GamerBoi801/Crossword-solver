import sys
from dictionary import FastDictionary
from models import Crossword, Variable
class Solver():
    
    def __init__(self, crossword: Crossword , fast_dictionary : FastDictionary):
       '''
       Initialise the CSP solver with a crossword structure and the 
       dictionary engine
       '''

    # ini the domains using the dict engine
    # we query the dict for each var length 
    # passing an empty dict {} as requirement returns every word in the set
       self.crossword = crossword
       self.fast_dict = fast_dictionary

        #this does the word enforce_node_consistency and keeps those words in set that have the same len as the target var
       self.domains = {
          var: self.fast_dict.get_matches(var.length, {}) # returns words for a specific length, returns the set of words
          for var in self.crossword.variables
       }

       # if any var's domain is empty at the start it means the dictionary doesn't have words for this length
       for var, domain in self.domains.items():
           if not domain:
               print(f'Warning: No words found for variable {var} with length {var.length}')



    def revise(self, x: Variable, y: Variable):
        '''
        Makes the variable 'x' arc consistent with variable 'y' . 
        we remove values form self.domains[x] for which there are no possible corresponding 
        value for Y in self.domains[y] 
        returns True if a revision is made to the domain of X, 
        returns False if no revision is made
        '''

        revised = False
         
         # find the overlaps
        overlaps = self.crossword.overlaps.get((x, y))
        
        #if there is no overlap no constrains exist between them
        if overlaps is None: return False

        x_index, y_index = overlaps

        #loop over  Variable X's domain

        for x_word in list(self.domains[x]):

            #identify the char x_word puts at the meeting point
            char_to_check = x_word[x_index]

            # looping through y's domain, ; we r checking whether we have char to check y_index``

            possible_matches_for_y = self.fast_dict.get_matches(
                y.length,
                {y_index: char_to_check}
            )

            #pruning
            # if the engine finds an empty set it means no words for Y can ever satisfy the constraint created by this specific x_word
            if not possible_matches_for_y:
                self.domains[x].remove(x_word)
                revised = True


        return revised

    def ac3(self, arcs=None):
        '''
        Docstring for ac3
        
        :param arcs: 
        '''
        if arcs is None:
            queue = []
            for var in list(self.crossword.variables):
                neighbor = self.crossword.neighbors(var)
                queue.append((var, neighbor))


        else:


    