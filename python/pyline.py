#inputs:
# -c command
# -m imports
# -r recursive
# args globs, files, or directories

#if -r, then it looks for args recursively under the current dir
#if a directory is passed, then 

import getopt
import glob
import re
import sys

def applyCodeObj(codeobj, stream, file = None):
    #for now, all output goes to stdout
    write = sys.stdout.write
    for numz, line in enumerate(stream):
        line = line[:-1]
        num = numz + 1
        words = [w for w in line.strip().split(' ') if len(w)]
        result = eval(codeobj,globals(),locals())
        if result is None or result is False:
            continue
        elif isinstance(result,list) or isinstance(result,tuple):
            result = ' '.join(map(str,result))
        else:
            result = str(result)

        write(result)
        if not result.endswith('\n'):
            write('\n')

def pyline(codeobj, globs, recurse = None, imports = None):
    files = []
    if imports is None:
        imports = []
    for imp in imports:
        locals()[imp] = __import__(imp.strip())
    if recurse is not None:
        from os import walk
        from os.path import join
        import fnmatch
        for root,dirnames,filenames in walk(recurse):
            for glob in globs:
                for filename in fnmatch.filter(filenames,glob):
                    files.append(join(root,filename))
    else:
        for glob in globs:
            files.extend(glob.glob(arg))
    for file in files:
        fd = open(file)
        data = fd.readlines()
        fd.close()
        applyCodeObj(codeobj,data,file)
    if len(files) == 0:
        #this is stdin
        applyCodeObj(codeobj,sys.stdin)

def commandLine(argv):
    opts, args = getopt.getopt(sys.argv[1:], 'm:f:g:r:')
    opts = dict(opts)

    #default the command to print a line
    imports = []
    recurse = None
    command = ' '.join(args)
    if not command.strip():
        command = 'line'

    #import modules requested
    if '-m' in opts:
        imports = [imp for imp in opts['-m'].split(',')]

    if '-r' in opts:
        recurse = opts['-r']

    if '-g' in opts:
        globs = [glob for glob in opts['-g'].split(',')]


    codeobj = compile(command, 'command', 'eval')
    pyline(codeobj, globs, recurse, imports)

if __name__ == '__main__':
    commandLine(sys.argv)
