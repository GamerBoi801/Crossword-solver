import sys
from dictionary import FastDictionary
from models import Crossword, Variable
import copy
class Solver():
    
    def __init__(self, crossword: Crossword , fast_dictionary : FastDictionary):
       '''
       Initialise the CSP solver with a crossword structure and the 
       dictionary engine

       creates the domain for every possible word for every slot on the on the board
       if lets say a Var is  len 3 then __init__ asks FastDictionary to return all the possible 
       3 letter words and adds them to the domain of that variable  
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

        checks for a single overlap between 2 words (X n Y), and checks to see is there any word in slot X that makes slot Y impossible
        if X and Y share a letter X, only keeps those words that have a potential partner in Y

        for exp 
        - Slot X (Across) and Slot Y(Down) and overlap at the first letter
        - X's domain is {'dog', 'cat'} and slot Y's domain has only words that start with 'C like 'cup' 
        
        - revise looks at 'dog, it see's Y has no words starting with 'D' so it removes that words from variable Y's domain

        
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
        Updates self.domain in such that each var is arc consistent

        if u del a word from one slot it might affect the other neighbors and this keeps the whole board consistent 

        for exp:
        - if u prune X's domain because Y's domain
        - so since X's domain is changed it checks to see if Var Z's domain (which overlaps var x on the crossword)

        '''
        if arcs is None:
            queue = []
            
            #we need to add every pair of variables that overlap
            for v1 in self.crossword.variables:
                for v2 in self.crossword.neighbors(v1):
                    queue.append((v1, v2))


        else:
            queue = list(arcs)


        while queue:
            # taking the first arc (X, y) from the queue
            x, y = queue.pop(0)

            if self.revise(x, y): #calling fast dictionary under the hood
                # if x has no words left then return false
                 if len(self.domains[x]) == 0:
                     return False
                 
                 #since x's domain has changed, any neighbor z might be inconsistent with the 
                #  new similar domain of X
                 for z in self.crossword.neighbors(x):
                    if z != y:
                        queue.append((z, x))
        return True
    
    def solve(self):
        '''Initializes the solving process'''
        self.ac3() #ini consistency check
        return self.backtrack(dict())
        
    def assignment_complete(self, assignment):
        '''checks if all the variables have been assigned to a word'''
        return len(assignment) == len(self.crossword.variables)
    
    def select_unassigned_variable(self, assignment):
        '''decides which empty slot to try to fill next. Uses MRV(Min remaining values) heuristic
        and it does this to remove identify and remove conflicts much more easily
        '''
        unassigned = [v for v in self.crossword.variables if v not in assignment]
        # sort by domain size (MRV) min remaining value
        return min(unassigned, key=lambda var: len(self.domains[var]))
    
    
    def consistent(self, word, var, assignment):
        '''checks if assigning 'word' to var conflicts with the current assignment
        
        - prevents u from using the same word twice in the puzzle and double checks their overlaps
        
        - for exp if u try to put 'dog' in slot 1, but slot 2 alr has 'cat' and they overlap at 'C' consistent will say False 
        because 'D' does not equal to 'C'
        ''' 
        #checking the uniqueness of the word:
        if word in assignment.values():
            return False
        
        #checking intersections with alr assigned neighbors 
        for neighbor in self.crossword.neighbors(var):
            if neighbor in assignment:
                x_index, y_index = self.crossword.overlaps[var, neighbor]
                if word[x_index] != assignment[neighbor][y_index]:
                    return False 
        return True
    
    def backtrack(self, assignment):
        '''main recursive search function, tries to fit in words and corrects them by backtracking the solution if it gets stuck
        
        for exp: 
        1. for slot 1 let's try 'CAT'
        2 Run ac3 -> it says if 'CAT' used then Slot 2 is possible
        3 Move to slot 2 -> 'Try' Cup
        4. of slot 3 becomes impossible -> go back to slot2 abd try a different word than 'CUP'
        '''
        #base case
        if self.assignment_complete(assignment):
            return assignment
        
        # selecting the next variable using MRV (min remaining value)
        var = self.select_unassigned_variable(assignment)

        #trying each word in the domain
        for value in list(self.domains[var]):
            if self.consistent(value, var, assignment):

                domain_record = copy.deepcopy(self.domains)

                #assign the word
                assignment[var] = value
                self.domains[var] = {value} # this var must be this word

                # maintaining arc consistency
                #seeing if this choice makes future slots impossible
                if self.ac3([(n, var) for n in self.crossword.neighbors(var)]):
                    result = self.backtrack(assignment)
                    if result is not None:
                        return result
                    
                
                #backtrack
                del assignment[var] #erases that option that makes it stuck
                self.domains = domain_record # backtracks

        return None


''' BIGGER PICTURE
 1. __init__ gives everyone a list
 2. ac3 runs once to remove words that r immediately impossible based on grid shape
 3. backtrack  starts the trial and error phase
 4. ac3 and revise tells me the solver if the guess is going to ruin the puzzle later on
 '''

