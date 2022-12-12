# Allows to bulk clean dir and filenames in given or current directory
#
#
import os
import sys

DEFAULT_DIRNAME = r'D:\Films'
FILM_EXTENSIONS = ['avi', 'mp3', 'wmv', 'mov', 'mp4']

VAR_STARTDIR = None # Starting folder
VAR_HANDLETYPE = 'b' # (f)ile, (d)irectory, (b)oth
VAR_HANDLEFILE = False
VAR_HANDLEDIR = False
VAR_APPLY_SUGGESTIONS = False
VAR_LOG_VERBOSE = False

RESULT_CHANGED = 1
RESULT_FAILED = 2
RESULT_SKIPPED = 3
RESULT_NO_CHANGES_FOUND = 4
RESULT_CHANGES_FOUND = 5

PART_UNKNOWN = 0
PART_TEXT = 1
PART_YEAR = 2
PART_FILMTERM = 3
PART_COUNTER = 4
PART_EXTENSION = 99

SEP_KEEP = 21
SEP_SKIP = 22
SEP_DEFAULT = ' '
SEP_SKIPLIST = '[]()'

def log(msg):
    if VAR_LOG_VERBOSE:
        print(msg)

def is_seperator(part_info):
    return part_info in (SEP_KEEP, SEP_SKIP)

def find_cd_counter(filename_parts, filename_parts_info):
    for index in range(0, len(filename_parts)):
        part = filename_parts[index].lower()
        part_info = filename_parts_info[index]
        if is_seperator(part_info):
            continue
        if len(part) > 2 and \
           part[:2] == 'cd':
            part_len = len(part)
            can_be_number = part[2:]
            num_formatter = '%%0%dd'%(part_len-2)
            print('FindCounter: Part %s in %s -> %s in %s'%(part, filename_parts, can_be_number, part))
            try:
                can_be_number_recalc = num_formatter%(int(can_be_number))
                if can_be_number_recalc == can_be_number:
                    filename_parts_info[index] = PART_COUNTER
            except:
                pass
    return filename_parts_info
    

def find_year(filename_parts, filename_parts_info):
    first_year_index = -1
    last_year_index = -1
    for index in range(0, len(filename_parts)):
        part = filename_parts[index]
        part_info = filename_parts_info[index]
        if is_seperator(part_info):
            continue
        if len(part) == 4 and part[:2] in ('19', '20'):
            try:
                if str(int(part)) == part:
                    filename_parts_info[index] = PART_YEAR
                    if first_year_index == -1:
                        first_year_index = index
                    last_year_index = index
            except:
                pass

    # Make all fields that come before a year be tagged as text to keep
    for index in range(0, last_year_index):
        part_info = filename_parts_info[index]
        if is_seperator(part_info):
            continue
        if filename_parts_info[index] == PART_UNKNOWN:
            filename_parts_info[index] = PART_TEXT
    for index in range(last_year_index, len(filename_parts)):
        part_info = filename_parts_info[index]
        if is_seperator(part_info):
            filename_parts_info[index] = SEP_SKIP

    return filename_parts_info

def find_film_terms(filename_parts, filename_parts_info):
    FILM_TERMS = ['divx', 'ac3', 'dvdrip', 'swesub', 'xvid']
    for index in range(0, len(filename_parts)):
        part = filename_parts[index].lower()
        for film_term in FILM_TERMS:
            if film_term in part:
                filename_parts_info[index] = PART_FILMTERM
    return filename_parts_info

def find_ok_text(filename_parts, filename_parts_info):
    first_year_index = -1
    last_year_index = -1
    for index in range(0, len(filename_parts)):
        if filename_parts_info[index] == PART_YEAR:
            if first_year_index == -1:
                first_year_index = index
            last_year_index = index

    if first_year_index == -1: # No year.. make all unknowns into text
        for index in range(0, len(filename_parts)):
            if filename_parts_info[index] == PART_UNKNOWN:
                filename_parts_info[index] = PART_TEXT
    return filename_parts_info

def filter_out_parts(filename_parts, filename_parts_info, bad_parts):
    joined_parts = zip(filename_parts, filename_parts_info)
    clean_parts = [(filepart, fileinfo) for (filepart, fileinfo) in joined_parts if not fileinfo in bad_parts]
    return clean_parts 

def find_seperators(filename, filename_parts):
    # First find the seperators
    from collections import defaultdict
    seperators = filename
    for part in filename_parts:
        pindex = seperators.find(part)
        plen = len(part)
        if pindex == 0:
            seperators = seperators[plen:]
        else:
            seperators = seperators[:pindex] + seperators[pindex+plen:]
    seperators = list(seperators)
    seperators = [sep if not sep in SEP_SKIPLIST else ' ' for sep in seperators ]
    print('FindSeperator - Found: %s'%str(seperators))

    # Then Find the common  seperator and ignore that
    # Approve the uncommon seperators
    seperator_counter_dict = defaultdict(int)
    seperator_dict = {}
    for sep in seperators:
        seperator_counter_dict[sep] += 1
    for (k, v) in seperator_counter_dict.iteritems():
        if v <= len(seperator_counter_dict)/2:
            seperator_dict[k] = SEP_KEEP
        else:
            seperator_dict[k] = SEP_SKIP

    seperators_info = [seperator_dict[i] for i in seperators]   

    return seperators, seperators_info

def analyse_filename(filename):

    import re

    print('Analyse filename: %s'%filename)

    splitter = re.compile(r"[a-zA-Z0-9\']+") # Old version = re.compile(r"\w+")
    filename_parts = splitter.findall(filename)
    filename_parts_info = [PART_UNKNOWN for i in filename_parts]
    filename_parts_info[-1] = PART_EXTENSION
    filename_seperators, seperators_info = find_seperators(filename, filename_parts)

    all_parts = []
    all_info = []
    for i in range(len(filename_parts)):
        all_parts.append(filename_parts[i])
        all_info.append(filename_parts_info[i])
        if i < len(filename_seperators):
            all_parts.append(filename_seperators[i])
            all_info.append(seperators_info[i])  

    finders = [find_year, find_cd_counter, find_film_terms, find_ok_text]
    for finder in finders:
        print("Analyse filename: Calling %s with %s - %s"%(finder, all_parts, all_info))
        filename_parts_info = finder(all_parts, all_info)
        print("Analyse filename: found %s"%(all_info))

    for index in range(0, len(all_parts)):
        if filename_parts_info[index] == PART_TEXT:
            # Capitalize if first letter small
            if all_parts[index][0].islower():
                all_parts[index] = all_parts[index].capitalize()

    print('Analyse filename: Before Cleaning: %s, %s'%(all_parts, all_info))

    clean_parts_and_info = filter_out_parts(all_parts, all_info, (SEP_SKIP, PART_UNKNOWN, PART_FILMTERM))
    new_filename = ''
    time_for_seperator = False

    # Look through the clean parts to combined to make the filename
    for (part, part_type) in clean_parts_and_info:
        #print("START:", new_filename, time_for_seperator, part, part_type
        if part_type == PART_EXTENSION:
            new_filename += '.' + part
            break #Stop after extension

        if time_for_seperator: # Expect a seperator every second time
            if is_seperator(part_type) and part_type == SEP_KEEP:
                new_filename += part
            else:
                new_filename += SEP_DEFAULT
                # Since it was not a seperator, we need to add the text
                new_filename += part
                time_for_seperator = True
                continue
        else:
            if not is_seperator(part_type):
                new_filename += part
            else:
                print("Strange, 2 seperators in a row. Check this:")
                print("   %s"%clean_parts_and_info)


        time_for_seperator = not time_for_seperator # Toggle switch between seperator and not seperator
        #print("END:", new_filename, time_for_seperator, part, part_type

    return new_filename

def handle_file(filenamefull):
    global VAR_STARTDIR
    global VAR_APPLY_SUGGESTIONS
    import os.path
    import shutil

    (filepath, filename) = os.path.split(filenamefull)
    (nada, fileext) = os.path.splitext(filename)
    if len(fileext) > 0 and fileext[0] == '.':
        fileext = fileext[1:]

    if not fileext in FILM_EXTENSIONS:
        #print("File is not a film. Skipping: %s"%filenamefull
        return RESULT_SKIPPED
    
    filename_analysed = analyse_filename(filename)
    if filename != filename_analysed and len(filename_analysed) > 6:
        
        if VAR_APPLY_SUGGESTIONS:
            print(" Changing from: %s"% filename)
            print(" ------------>  %s"% filename_analysed)

            from_file = os.path.join(VAR_STARTDIR, filename)
            to_file = os.path.join(VAR_STARTDIR, filename_analysed)

            #print("Move from %s to %s"%(from_file, to_file)
            shutil.move(from_file, to_file)
            return RESULT_CHANGED
        else:
            print(" Suggest from: %s"% filename)
            print(" ----------->  %s"% filename_analysed)
            return RESULT_CHANGES_FOUND

    return RESULT_NO_CHANGES_FOUND

def handle_dir(dirname):
    print("DIR: %s"%dirname)

def match_filter(filename, filenamefilter):
    filename = filename.lower()
    matches = 0
    for filter in filenamefilter:
        filter = filter.lower()
        if filter in filename:
            matches += 1
    return matches == len(filenamefilter)

def clean_filmnames_in_folder(args):
    global VAR_STARTDIR
    global VAR_HANDLETYPE
    global VAR_APPLY_SUGGESTIONS
    global VAR_LOG_VERBOSE
    import os.path
    import os
    from collections import defaultdict

    startdir_suggestion = args.startdir
    if os.path.isdir(startdir_suggestion):
        VAR_STARTDIR = startdir_suggestion
    else:
        print("This is not a valid directory name: %s"%startdir_suggestion)
        return False

    VAR_HANDLETYPE = args.handletype
    VAR_HANDLEFILE = VAR_HANDLETYPE in ('f', 'b')
    VAR_HANDLEDIR = VAR_HANDLETYPE in ('d', 'b')
    VAR_FILTER = args.filenamefilter
    VAR_APPLY_SUGGESTIONS = args.apply
    VAR_LOG_VERBOSE = args.verbose

    print(">>Scanning folder: %s"%VAR_STARTDIR)
    print(">>Handling filetypes: %s"%VAR_HANDLETYPE.upper())
    print(">>Using filters: %s"%str(VAR_FILTER))
    print(">>Will apply changes: %s"%VAR_APPLY_SUGGESTIONS)
    summary = defaultdict(int)
    files = os.listdir(VAR_STARTDIR)
    for file in files:
        filename = os.path.join(VAR_STARTDIR, file)

        if os.path.isfile(filename):
            if VAR_HANDLEFILE:
                if VAR_FILTER:
                    if not match_filter(filename, VAR_FILTER):
                        continue
                summary[handle_file(filename)] += 1
        elif os.path.isdir(filename):
            if VAR_HANDLEDIR:
                if VAR_FILTER:
                    if not match_filter(filename, VAR_FILTER):
                        continue
                summary[handle_dir(filename)] += 1
        else:
            print("Don't know how to handle: %s"%filename)

    print(">>Number of Items changed: %d"%summary[RESULT_CHANGED])
    print(">>Number of Items identified to change: %d"%summary[RESULT_CHANGES_FOUND])
    print(">>Number of Items not requiring changes: %d"%summary[RESULT_NO_CHANGES_FOUND])
    print(">>Number of Items skipped: %d"%summary[RESULT_SKIPPED])
    print(">>Number of Items failed: %d"%summary[RESULT_FAILED])

    return True
        



def start():
    import argparse # Python 2.7 onwards

    parser = argparse.ArgumentParser(\
        description='List films in a folder and suggest names if they look messy.'\
        )

    parser.add_argument('-d', dest='startdir', help='_D_irectory to work with', default=DEFAULT_DIRNAME)
    parser.add_argument('-t', dest='handletype', help='_T_ypes of files/dirs to handle. (F)ile, (D)irectory or (B)oth.', choices='fdb', default='f')
    parser.add_argument('-f', dest='filenamefilter', help='Filename text to_f_ilter.', action='append', default=[])
    parser.add_argument('-a', dest='apply', help='_A_pply identified filename changes.', action='store_true', default=False)
    parser.add_argument('-v', dest='verbose', help='Output in _V_erbose mode.', action='store_true', default=False)
    args  = parser.parse_args()

    print(args)

    clean_filmnames_in_folder(args)        

if __name__ == "__main__":
    start()

