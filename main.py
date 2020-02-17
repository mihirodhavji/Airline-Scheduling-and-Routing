from solution import ASARProblem
import search
import sys
import time
start_time = time.time()

f1 = open(sys.argv[1], "r")
f2 = open('saida.txt',"w")
problem = ASARProblem()
problem.load(f1)
node = search.astar_search(problem,problem.heuristic)

if(node == None):
    problem.save(f2,None)
else:
    problem.save(f2,node.state)
f1.close()
f2.close()
finish_time = time.time()
print("--- %s seconds ---" % (finish_time - start_time))