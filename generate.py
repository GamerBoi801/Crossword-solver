import sys

from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        _, _, w, h = draw.textbbox((0, 0), letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        for key, value in self.domains.items():

            #every value in a var's domain has same no. of letters as var's length
            for word in list(value):
                if key.length != len(word):
                    self.domains[key].remove(word)
        

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        revised = False
        list_of_overlaps = self.crossword.overlaps[x, y]

        if list_of_overlaps is  None:
            return False # no overlap so no revision
        
        x_cord, y_cord  = list_of_overlaps
        to_remove = set()
       
        #looping over x.domains
        for x_val in self.domains[x]:
            #for each xval check fi there exists any yval in y's domain that's consistent
            if not any(x_val[x_cord] == y_val[y_cord] for y_val in self.domains[y]):
                to_remove.add(x_val)

        if to_remove:
            self.domains[x] -= to_remove
            revised = True

        return revised
            


    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        if arcs is None:
            #begin with ini list of all the arcs in the problem
            queue = []
            for domain in self.domains:
                for neighbor in self.crossword.neighbors(domain):
                    if self.crossword.overlaps[domain, neighbor]: #checks and filters constraints
                        queue.append((domain, neighbor))
        else:
         queue = arcs

        while queue:
           X, Y = queue.pop(0)
           if self.revise(X, Y):
               
               if len(self.domains[X]) == 0:
                   return False
               
               for neighbor in self.crossword.neighbors(X):
                   if neighbor != Y:   
                    queue.append((neighbor, X))
        return True  



    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        # keys r vars object, values r strings representing words those vars will take on
        for domain in self.domains:
            if domain not in assignment:
                return False
        return True
        

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        # each word assigned to a var should be same len as var
        for var, word in assignment.items():
            if len(word) != var.length:
                return False       
       
            
        # check all the words r unique or not
        if len(set(assignment.values())) < len(assignment):
            return False
                  

        # same char at both vars intersection
        for var in assignment:
            for neighbor in self.crossword.neighbors(var):
                if neighbor in assignment:
                    x, y = self.crossword.overlaps[var, neighbor]

                    if assignment[var][x] != assignment[neighbor][y]:
                        return False
                    
        
        return True


    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        #approach
        """check at  intersecting points whether the char is the same for the other values' domain;
          and then expand search to the next var and do this until  no more words fit out criteria"""
        
        conflicts = dict() #key: var, value: no. of conflicts
        
        #conflicts only occur when 2 vars intersect
        neighbors = self.crossword.neighbors(var)

        for x_val in self.domains[var]:
            conflicts[x_val] = 0 #ini counts to 0

            for neighbor in neighbors:
                if neighbor in assignment:
                    #skip assigned neighbors
                    continue

                intersection = self.crossword.overlaps[var, neighbor]
                if intersection is None:
                    continue  # no conflicts
                
                X, Y = intersection

                for y_val in self.domains[neighbor]:
                    #check if intersecting neighbors overlap as the same char at the pt

                    if x_val[X] != y_val[Y]:
                        conflicts[x_val] += 1

            
        sorted_values = list(sorted(conflicts.items(), key=lambda item: item[1]))
        return [val for val, count in sorted_values]
            




    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """Pre-made by Google
        empty_spots = dict()
        
        #iterating over the Var domains
        for var, domain in self.domains.items():
            if var not in assignment:
                empty_spots[var] = len(domain)

        #MRV and Degree heuristic
        minima = min([value for var, value in empty_spots.items()])
        small_domains = [var for var, size in empty_spots.items() if size == minima]
        
        max_degree = -1
        selected = None

        #picking the one wit the highest degree
        for var in small_domains:
            degree = len(self.crossword.neighbors(var))
            if degree > max_degree:
                max_degree = degree
                selected = var

        
        return selected


        

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        #Checks if assignment is complete or not
        
        #base-case
        if self.assignment_complete(assignment):
            return assignment
        
        var = self.select_unassigned_variable(assignment)

        for value in self.order_domain_values(var, assignment):
            temp_assignment = assignment.copy()
            temp_assignment[var] = value
            if self.consistent((temp_assignment)):
                result = self.backtrack(temp_assignment)
                if result is not None:
                    return result
        
        return None



def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
