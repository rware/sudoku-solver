#!/usr/bin python

from __future__ import print_function
import itertools
import sys
import subprocess

'''
Solves SAT problem given in infile
and outputs result to 'solver-output.zchaff'.

If solution to sudoku exists, will print 
solution to standard output. Otherwise, will print
that there is no solution.
'''

def call_zchaff(infile):
	cmd = 'zchaff ' + infile + ' > solver-output.zchaff'
	process = subprocess.Popen(cmd ,stdout=subprocess.PIPE, shell=True)
   	#stdout = iter(process.stdout.read().split())
	#print (process.stdout.read())
	process.wait()

	with open('solver-output.zchaff', 'r') as f:
		zchaffOutput = iter(f.read().split())
		

	# helper function for getting/printing sudoku solution
	def print_solution(zChaffOutput):
		# zchaffOuput iterator should now be at the beginning
		s = zChaffOutput.next()
		# get all true boolean variables
		true_vars = []
		while(s != 'Random'):
			if (int(s) > 0):	
				true_vars.append(s)
			s=zchaffOutput.next()
		
		assert(len(true_vars)==81)
		solution = iter(true_vars)

		print("SUDOKU SOLUTION:")
		bool_vars = bool_vars_reverse() 
		for row in range(0,9):
			for column in range(0,9):
				print(bool_vars[int(solution.next())][2], end=' ')	
			print()

	while(True):
		if (zchaffOutput.next() == 'Instance'):
			s = zchaffOutput.next()
			if (s == 'Satisfiable'):
				# SUDOKU HAS A SOLUTION - PRINT	
				print_solution(zchaffOutput)	
			elif (s == 'Unsatisfiable'):
				print("SUDOKU HAS NO SOLUTION")
			else:	# should never get here
				print("SOMETHING WENT WRONG WITH ZCHAFF. OOPS")
			break
	

'''
	Generates boolean variable dictionary:
	v = {
			(1,1,1) : 1,
			(1,1,2) : 2,
			(1,1,3) : 3,
			....
		}

	Can access individual variables using dictionary
	commands:

	>> v[(9,9,9)]  	# x_99 = 9
	729				# returns number 729
'''
def bool_vars(size=9):
	return {(row,col,d): (row - 1)*(size**2) + (col - 1)*size + d
				for row in range(1, size+1)
					for col in range(1, size+1)
						for d in range(1, size+1)}

# generates reverse dictionary where keys are the 
# boolean variable number and values are (row,col,d)
def bool_vars_reverse(size=9):
	return {(row - 1)*(size**2) + (col - 1)*size + d : (row,col,d)
				for row in range(1, size+1)
					for col in range(1, size+1)
						for d in range(1, size+1)}
	

# create cnf file
def create_cnf_file(outfile):
   	with open('clauses.txt', 'w') as f:
   		sudoku(f)
   		get_clues(9, f)	

	with open('clauses.txt', 'r') as f:
		print("c CNF file created by SudokuSolver.py", file=outfile)
		# add 0 to the end of the clauses
		clauses = [c+' 0' for c in f.read().splitlines()]
	
	numclauses = len(clauses)
	print("p cnf", 9**3, numclauses, file=outfile)
	print(*clauses, sep='\n', file=outfile)

# reads clues from input file
def get_clues(size, outfile):
	try:
		with open(sys.argv[1], 'r') as f:
			input = iter(f.read().split())
	except IndexError as e:
		print ("Expected command line argument (file with sudoku clues)")
	
	clues = [(row, col, int(input.next())) 
				for row in range(1, size+1)
					for col in range(1, size+1)]
	
	# note that the above ensures only one clue per square
	# change to a set for faster 'in' operation
	clues = set(clues)	
	
	# match up to dictionary of boolean variables
	v = bool_vars()
	for key in v:
		if key in clues:
			print(v[key], file=outfile)
	
	
# returns general clauses for all sudoku
def sudoku(outfile=None):
    # definedness clauses
    for i in range(0,9**2):
		print (*defined(9)[i], sep=' ', file=outfile)

    # uniqueness clauses
    bool_vars = get_vars(9, ispos=False)
    for i in range(0, len(bool_vars), 9):
        unique(bool_vars[i:i+9], outfile)

    # validity clauses for rows
    for row in range(1,10):       
        z = [(row,col) for col in range(1,10)]
        valid(z, outfile)                

    # validity clauses for columns
    for col in range(1,10):       
        z = [(row,col) for row in range(1,10)]
        valid(z, outfile)

    # validity clauses for squares
    for a in [1,4,7]: 
        for b in [1,4,7]:
            z=[(a,b), (a,b+1), (a, b+2), 
               (a+1, b), (a+1, b+1), (a+1, b+2),
               (a+2, b), (a+2, b+1), (a+2, b+2)]
            valid(z, outfile)    

# returns clauses for unique(z1,z2,z3,z4,...,zn)
def unique(z, outfile=sys.stdout):
    if not outfile :
        for i in itertools.combinations(z, 2):
			print (*i)
    else: # file is not none
        for i in itertools.combinations(z, 2):
			print (*i, file=outfile)

# returns the boolean variable for x_rowcol = d
# ispos determines if you return a positive or negative number
def get_var(row, col, d, size=9, ispos=True):
    # calculate the variable
    if ispos:    
        return  (row - 1)*(size**2) + (col - 1)*size + d
    # else
    return -((row - 1)*(size**2) + (col - 1)*size + d)

# generate all the boolean variables
# returns range
def get_vars(size, ispos=True):
    if ispos:
        return range(1, (size**3)+1)
    # else
    return range(-1, -(size**3)-1, -1)
    
# returns definedness clauses
def defined(size):
    bool_vars = get_vars(size)
    return [bool_vars[i:i+size] 
        for i in range(0, len(bool_vars)-1, size)]

# returns clauses for valid(z1,z2,z3,z4,...,zn)
def valid(z, outfile=sys.stdout):
    n = len(z)
    for d in range(0,n):
        for i in range(0, n-1):
            for j in range(i+1, n):
				x1 = z[i]
				x2 = z[j]
				print (get_var(x1[0], x1[1], d+1, ispos=False), get_var(x2[0], x2[1], d+1, ispos=False), file=outfile)


if __name__=='__main__':
	create_cnf_file(open('sudoku.cnf', 'w'))
	call_zchaff('sudoku.cnf')
