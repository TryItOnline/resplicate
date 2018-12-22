#ResPlicate Interpreter by Quintopia, based on code by nooodl

from collections import deque
import sys
class PatternRepeated(LookupError):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return "Pattern repeated with period "+str(self.value)

def popsafe(q): # return 0 if empty                                                             #1
    try: return q.popleft()                                                                     #2
    except IndexError: return 0                                                                 #3

def remember(q,count,prev = {},cyclenums = {}):
    row = prev.setdefault(len(q),[])
    copy = hash(tuple(q))
    if copy in row: raise PatternRepeated(count-cyclenums[copy])
    row.append(copy)
    cyclenums[copy]=count

def run(q,haltonrepeat=True,quiet=True,prlen=False,maxlength=0,io=False,summary=False):
    def log(string):
        if io:
            print >> sys.stderr, string
        else:
            print string

    q = deque(q)
    count = 0; maxl = len(q); repeat = 0
    prev={}; cyclenums={}
    nocheck = (io and min(q)<0) or not haltonrepeat
    quiet = quiet or summary
    try:
        while len(q)>0 and (maxlength==0 or len(q)<=maxlength):                                 #4
            if len(q)>maxl: maxl=len(q)
            if not quiet: log(' '.join(map(str, q)).join('()'))
            if prlen: log(len(q))
            if not nocheck: remember(q,count,prev,cyclenums)
            if summary: log(' '.join(map(str, list(q)[0:q[0]+2])).join('()'))
            x = popsafe(q); y = popsafe(q)                                                      #5,6
            if io and x==0:
                if y>=0:
                    try: sys.stdout.write(chr(y))
                    except ValueError: pass
                else: q.append(ord(sys.stdin.read(1))+y+1)
            else: q.extend([popsafe(q) for _ in xrange(x)] * y)                                 #7
            count+=1
        if maxlength>0 and len(q)>maxlength:
            if len(q)>maxl: maxl=len(q)
            if not quiet: log(' '.join(map(str, q)).join('()'))
            if prlen: log(len(q))
    except PatternRepeated as e: repeat = e.value
    except KeyboardInterrupt: raise KeyboardInterrupt(list(q),count,maxl,repeat)
    return (list(q),count,maxl,repeat)

if __name__=="__main__":
    import optparse
    parser = optparse.OptionParser(description="ResPlicate Interpreter by Quintopia.", usage="%prog [options] [arguments]")
    parser.add_option('-n', help="Set the simulation to halt when the queue exceeds this length.", metavar="<value>", action="store", dest="maxlength", type=int, default=0)
    parser.add_option('-q', '--quiet', help="Turn off verbose output.", dest="quiet", action="store_true", default=False)
    parser.add_option('-l', help="Print the length of the queue at each step.", dest="prlen", action="store_true", default=False)
    parser.add_option('-i', '--io', help="Run with I/O extension.", dest="io", action="store_true", default=False)
    parser.add_option('-c', '--continue', help="Do not check for and halt on repeated/periodic sequences.", dest="haltonrepeat", action="store_false", default=True)
    parser.add_option('-f', '--file', help="Load a ResPlicate program from a file.", metavar="<filename>", action="store", dest="filename", type=str, default=None)
    parser.add_option('-o', '--command', help="Display only the numbers that were popped each cycle.", dest="summary", action="store_true", default=False)
    (options, args) = parser.parse_args()
  
    if options.filename is not None:
        try: openfile = open(options.filename,"r")
        except IOError: print >> sys.stderr, "File '"+options.filename+"' not found."
        else: args = openfile.read().split(); openfile.close()
    if len(args)>0:
        if len(args)==1: args=args[0].split()
        try: (final,count,maxl,repeat) = run(map(int, args),options.haltonrepeat,options.quiet,options.prlen,options.maxlength,options.io,options.summary)
        except KeyboardInterrupt as e: print >> sys.stderr, "Simulation interrupted by user."; (final, count, maxl, repeat) = e.args
        except ValueError: parser.error("All arguments must be integers unless the -f flag is used to specify a file.")
        if options.quiet:
            if len(final)<100: print >> sys.stderr, "Final sequence: "+' '.join(map(str, final)).join('()')
            else: print >> sys.stderr, "Final sequence: "+(' '.join(map(str,final[0:100]))+"...").join('()')
        if repeat>0: print >> sys.stderr, "Pattern repeated with period "+str(repeat)+"."
        print >> sys.stderr, "Simulation proceeded for "+str(count)+" steps, with queue reaching a maximum length of "+str(maxl)+" and a final length of "+str(len(final))+"."
    else:
        parser.error("No program to execute.")
