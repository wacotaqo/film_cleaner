# filename_mod.py
#
# Modifies the filename of a file.close
# To clean filenames and remove trash
#

import sys

QUIET = False
VERY_QUIET = False
DEBUG = False

def log(msg):
    if DEBUG:
        from time import strftime, localtime, time
        fh = open('filename_mod.debug.txt', 'a')
        fh.write('%s\t%s\n'%(strftime('%Y-%m-%d %H:%M:%S', localtime(time())), msg))
        fh.close()

def isFile(filetype):
    return filetype == 'F'

    
def get_files_recursive(rootdir, file_filter='', dir_filter='', ignore_case=0):
    import os
    import os.path
    import re

    filenames = []
    for (basedir, dirs, files) in os.walk(rootdir):

        for name in files:
            wholename = os.path.join(basedir, name)
            if not file_filter and not dir_filter:
                filenames.append(('F', basedir, name))
            elif file_filter and len(file_filter) > 1:
                match = re.match(file_filter, name, flags=ignore_case)
                if match:
                    filenames.append(('F', basedir, name))

        for name in dirs:
            wholename = os.path.join(basedir, name)
            if not file_filter and not dir_filter:
                filenames.append(('D', basedir, name))
            elif dir_filter and len(dir_filter) > 1:
                match = re.match(dir_filter, name, flags=ignore_case)
                if match:
                    filenames.append(('D', basedir, name))
                
    return filenames

def get_files(rootdir, file_filter='', dir_filter='', ignore_case=0):
    import os
    import os.path
    import re
    
    contents = os.listdir(rootdir)
    files = []
    dir = rootdir
    for name in contents:
        wholename = rootdir + '/' + name
        if os.path.isfile(wholename):
            filetype = 'F'
        elif os.path.isdir(wholename):
            filetype = 'D'
        else:
            filetype = '?'
        if not file_filter and not dir_filter:
            files.append((filetype, dir, name))
        elif isFile(filetype) and file_filter:
            if len(file_filter) > 1:
                match = re.match(file_filter, name, flags=ignore_case)
                if match:
                    files.append((filetype, dir, name))
        elif filetype == 'D' and dir_filter:
            if len(dir_filter) > 1:
                match = re.match(dir_filter, name, flags=ignore_case)
                if match:
                    files.append((filetype, dir, name))
            
    return files

def rename_file(olddir, oldname, newdir, newname):
    import os
    old_filename = '%s/%s'%(olddir, oldname)
    new_filename = '%s/%s'%(newdir, newname)
    os.rename(old_filename, new_filename)

        
def print_instructions():
    print("filename_mod.py")
    print()
    print("filename_mod [-h] [-a] -[-q] [-Q] [-e] [-s] [-g] [-i][-x replace-ext] [-f File-filter] [-d Dir-filter] [-r remove-pattern] [-c Cut-after-pattern] [-p rePlace-pattern -w replace-with-text] [-x replace-extension] <root_directory> ")
    print()
    print(" -h | --help: Print These Instructions")
    print(" -a | --apply: Apply Intructions")
    print(" -q | --quiet: Reduced output")
    print(" -Q | --veryquiet: Almost no output")
    print(" -e | --equalfilter: Same File and Directory Filter")
    print(" -s | --sub: Traverse Subdirectories")
    print(" -g | --debug: Debug mode - some extra output")
    print(" -f | --file <filter>: File RegExp Filter")
    print(" -d | --dir <filter>: Directory RegExp Filter")
    print(" -i | --ignorecase: Ignore case in regexp and txt searches")
    print(" -r | --remove <pattern>: Text to remove")
    print(" -c | --cut <pattern>: Text to crop after")
    print(" -p | --replace <filter>: RegExp text to look for to replace")
    print(" -w | --replacewith <text>: Text to replace with")
    print(" -x | --replaceXtension with <text>: Text to replace extension with")
    print()

def print_general(msg):
    if not QUIET and not VERY_QUIET:
        print(msg)
    if DEBUG:
        log(msg)

def print_action(msg):
    if not VERY_QUIET:
        print(msg)
    if DEBUG:
        log(msg)

def main(*input_args):
    global QUIET
    global VERY_QUIET
    global DEBUG
    import getopt
    import re
    import os.path
    try:
        opts, args = getopt.getopt(input_args[1:], 'qQehasgif:d:r:c:p:w:x:', ['quiet', 'veryquiet', '33', 'apply', 'help', 'sub', 'debug', 'ignorecase', 'file=', 'dir=', 'remove=', 'cut=', 'replace=', 'replacewith=', 'replaceext='])
    except getopt.GetoptError:
        # print help information and exit:
        print_instructions()
        return 2
    try:
        if len(args) < 1:
            print_instructions()
            return 2

        rootdir = args[0]
        file_filter = ''
        dir_filter = ''
        cut_after = ''
        remove_text = []
        replace_filter = ''
        replace_with_text = ''
        replace_ext = ''
        apply = False
        search_subdirectories = False
        equal_filter = False # Same dir and file filter
        can_apply = False
        ignore_case = 0
        for o, a in opts:
            if o == '-f' or o == '--file':
                file_filter = a
            if o == '-d' or o == '--dir':
                dir_filter = a
            if o == '-r' or o == '--remove':
                remove_text.append(a)
                can_apply = True
            if o == '-c' or o == '--cut':
                cut_after = a
                can_apply = True
            if o == '-i' or o == '--ignorecase':
                ignore_case = re.IGNORECASE
            if o == '-p' or o == '--replace':
                replace_filter = a
                can_apply = True
            if o == '-x' or o == '--replaceext':
                replace_ext = a
            if o == '-w' or o == '--replacewith':
                replace_with_text = a
            if o == '-a' or o == '--apply':
                apply = True
            if o == '-g' or o == '--debug':
                DEBUG = True
            if o == '-h' or o == '--help':
                print_instructions()
                return 0
            if o == '-e' or o == '--equalfilter':
                equal_filter = True
            if o == '-s' or o == '--sub':
                search_subdirectories = True
            if o == '-q' or o == '--quiet':
                QUIET = True
            if o == '-Q' or o == '--veryquiet':
                QUIET = VERY_QUIET = True

        if equal_filter:
            if file_filter:
                dir_filter = file_filter
            elif dir_filter:
                file_filter = dir_filter

        if rootdir:

            print_general("Looking in dir: %s"%rootdir)
            if file_filter:
                print_general("File Filter: %s"%file_filter)
                if equal_filter:
                    print_general("File and Directory filter are identical.")
            if dir_filter:
                print_general("Directory Filter: %s"%dir_filter)
            if remove_text:
                print_general("Removing parts of name: %s"%remove_text)
            if cut_after:
                print_general("Cutting name after: %s"%cut_after)
            if replace_filter:
                print_general("Replacing: '%s' with '%s'"%(replace_filter, replace_with_text))
            if replace_ext:
                print_general("Replacing extension with : '%s'"%(replace_ext))
            if ignore_case:
                print_general("Ignoring Case")
            if QUIET:
                if VERY_QUIET:
                    print_general("Quiet: VERY")
                else:
                    print_general("Quiet: True")
            if search_subdirectories:
                print_general("Search Subdirectories: True")
            if can_apply:
                print_general("Apply changes: %s"%apply)

            if search_subdirectories:
                files = get_files_recursive(rootdir, file_filter, dir_filter, ignore_case)
            else:
                files = get_files(rootdir, file_filter, dir_filter, ignore_case)                

            for (ftype, dir, f) in files:
                nf = f
                log("Handling file: %s :: %s :: %s"%(ftype, dir, f))
                if remove_text:
                    for dt in remove_text:
                        log(" Search::Remove text::%s"%dt)
                        if dt in f:
                            log("  Found::Remove::text::%s"%dt)
                            nf = nf.replace(dt, '')

                if cut_after:
                    if isFile(ftype):
                        (name, ext) = os.path.splitext(nf)
                    else:
                        name = nf
                    parts = re.split('(%s)'%cut_after, name)
                    if len(parts) > 2:
                        name = '%s%s'%(parts[0], parts[1])
                    if isFile(ftype) and ext:
                        name = name + ext
                    nf = name

                if replace_filter :
                    if isFile(ftype ):
                        (name, ext) = os.path.splitext(nf)
                    else:
                        name = nf
                    log(" Searching replacement::%s::%s::%s"%(replace_filter, replace_with_text, name))
                    oldname = name
                    name = re.sub(replace_filter, replace_with_text, name, flags=ignore_case)
                    #print("Changed %s to %s with ('%s'->'%s')"%(oldname, name, replace_filter, replace_with_text)
                    if isFile(ftype) and ext:
                        name = name + ext
                    nf = name

                if replace_ext:
                    if isFile(ftype ):
                        (name, ext) = os.path.splitext(nf)
                        if replace_ext[0] != '.':
                            replace_ext = '.' + replace_ext
                        nf = name = name + replace_ext
            
                if nf != f:
                    print_action("%10s: %s: %s : %s --> %s"%("Rename", ftype, dir, f, nf))
                    if apply:
                        rename_file(dir, f, dir, nf)
                else:
                    print_general("%10s: %s: %s"%("No change", ftype, f))
                

                        
    except:
        raise
    else:
        return 0

if __name__ == '__main__':
    sys.exit(main(*sys.argv))