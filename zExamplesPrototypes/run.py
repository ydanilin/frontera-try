import trace
from recurse import recurse

def main():
    print('This is the main program.')
    tracer = trace.Trace(count=0, trace=0, countcallers=1, outfile="trace.bin")
    # recurse(2)
    tracer.runfunc(recurse, 2)
    r = tracer.results()
    r.write_results(show_missing=True, coverdir=".")
    return

if __name__ == '__main__':
    main()
