"""
This program will get the md5 sum of all files in a directory and all sug-directories.
It creates two files in the scanned root
  example: rootDir is '/Users/blainekuhn/Git'
    md5_log is the file created after a scan to get the initial md5 values
    md5_log_error will contain any files that don't have the same md5 sum
  If md5_log_error exists it will be deleted before beginning
  if md5_log does not exist it will be created and populated

"""
import os, hashlib, sys, shutil
md5 = hashlib.md5()
d_dict = {}

def create_log_file(file_w_path, logFile):
  rootDir = (os.path.abspath(file_w_path))
  #find rootDir by parsing file_w_path and stripping the filename
  for dirName, subdirList, fileList in os.walk(rootDir):
    for fname in fileList:
      filename = os.path.join(dirName,fname)
      d_dict[filename] = checksum_md5(filename)
  if not os.path.exists(logFile):
    with open(logFile, "w") as b:
      b.close()
  with open(logFile, 'r+') as f:
      f.write(str(d_dict))
      f.write("\n")
  f.close()
  print("%s files processed" % len(d_dict))


def check_files(*args):
  error = False
  rebuild_file = False
  result = "All Good"
  rootDir = args[0]
  if len(args) < 2:
    sys.exit(get_help())
  else:
    logFile = os.path.join(args[0], args[1])
  md5_log_error = os.path.join(rootDir, logFile+"_error")
  if os.path.exists(md5_log_error):
    shutil.move(md5_log_error, os.path.join(rootDir, md5_log_error+".old"))
 #  os.remove(md5_log_error)
    print("\nMoved the old md5_log_error %s" % os.path.join(rootDir, md5_log_error+".old"))
    print("A new md5_log has been generated, and includes any new files.\n")
  if not os.path.exists(logFile):
    print("\nThis tool has not yet been executed against %s. \n\
Running Now...\nThis file '%s',\nis very important and a backup may be a good idea.\n" % (rootDir, logFile))
    create_log_file(rootDir, logFile)
    sys.exit("Run some tests, then run this again to validate the md5 remains constant.\n")
  md5_dict = {}
  with open(logFile, "r") as f:
    md5_log = open(logFile, 'r')
    md5_log = eval(md5_log.read())
    for dirName, subdirList, fileList in os.walk(rootDir):
      for fname in fileList:
        filename = os.path.join(dirName, fname)
        md5_dict[filename] = checksum_md5(filename)
        if not filename in md5_log:
          md5_dict[filename] = checksum_md5(filename)
          rebuild_file = True
    """Checking md5 sum on all files, IF the keys in each dictionary are NOT the same"""
    if len(set(md5_log.items()) ^ set(md5_dict.items())) > 2:
      for log_key in md5_log:
        if log_key in md5_dict:
          if not md5_log[log_key] == md5_dict[log_key]:
            if not log_key == logFile:
              with open(md5_log_error, "a") as b:
                b.write(str(os.path.join(md5_log[log_key],log_key + "\n" )))
                error = True
        else:
          if not log_key == md5_log_error:
            print("\nThis file, has been deleted, since md5_log was generated %s\n" % log_key)
          #later need to have this remove from the md5_log for later uses bug #5
      if error == True:
        result = print("\nThere was an error.  See %s" % md5_log_error)
    else:
      result = print("\nNo files have changed under %s.\n\
A new log was generated to capture any newly added or removed files." % rootDir)
  if rebuild_file == True:
    create_log_file(rootDir, logFile)
    sys.exit()
  #return print(result)

def checksum_md5(filename):
  import hashlib
  md5 = hashlib.md5()
  with open(filename,'rb') as f: 
    for chunk in iter(lambda: f.read(8192), b''): 
      md5.update(chunk)
    result = md5.hexdigest()
  return result


def get_help():
  sys.exit(print("""
    *********************************************************************************
    valid options in order of placement:
        -path     <entire path from root to directory to scan>
        -log       <entire path to log file if different from -path>
        
    To use this program:
    python3 check_md5.py <full path to scan root>
    
        examples:
        To scan your homedir...
          python3 check_md5.py -path "/Users/username"
          
        To scan your homedir using a custom md5_log file...
          python3 check_md5.py -path "/Users/username/" -log "my_log"

    NOTES:
    -  You must supply at least one of the valid options '-path' or '-log' and it's valid argument.
    *********************************************************************************
  """))


if __name__ == "__main__":
  sysarg = len(sys.argv)
  if sysarg == 1:
    get_help()
  elif sysarg == 2:
    get_help()
  elif sysarg >=2:
    if sys.argv[1] == "-path":
      rootDir = sys.argv[2]
      if not os.path.isdir(rootDir):
        sys.exit(print("\n\n  -- Error The parameter '-path' is NOT a full path from root."), get_help())
    elif sys.argv[1] == "-log":
      rootDir = os.getcwd()
      logFile = sys.argv[2]
    if len(sys.argv) >= 4:
      if sys.argv[3] == "-log":
        logFile = os.path.join(rootDir, sys.argv[4])
  else:
    print("Please run  'python3 check_md5.py -help'   for help executing this tool")
#print("This is the rootDir %s\n\
#This is the logFile %s" % (rootDir, logFile))
  check_files(rootDir, logFile)


"""
BUGS
1. doesn't accept command line input for directory - always uses os.getcwd()
  FIXED with this checkin 01c39bdfbe62bc0056558dae68c10a7749faa4cd
2. Doesn't detect files that have been added to the directory after initial run to build md5_log
    If a file has been added since initial run, add md5 to file
    FIXED with this checkin 5094ba0dc65b72110e00834c043c81c216ac4030
2.1 Previous fix created a new bug - if not all(md5_log[n] - part now crashing due to error_log file
    FIXED - changed line to ^ the two dictionaries  - a7798f3842312136c6a9cbca67ea88c2d0f1fd25
3. Files deleted since initial run, crashes with Key error on full_path_to_deleted_file
    only happens when running to a folder other than cwd
    FIXED while working 2.1 - a7798f3842312136c6a9cbca67ea88c2d0f1fd25
4. If not run previously it should not run - instead tell the user to run check_files
    FIXED - if md5_log not exist must run first
5. After a file has been deleted, it should report deleted file and update the md5_log by removing the
    entry for the file.
6. Arguments need work
    FIXED
7. if directory has not been scanned yet, you get an error when running from command line
    FIXED - now runs
8. Reports removed error_log file as being removed since last run if programmatically deleted
    FIXED - now makes a backup copy of the error log as to not overwrite it
9.Needs to be able to run from python shell as chec_files('path')
    FIXED now runs from python 3 shell as   check_files("/path_to_files").
10. This line may need to move as it could repeat many times if many files are bad
      "There was an error.  See /Users/blainekuhn/Documents/md5_log_error"
      FIXED - a flag is now set and checked later.  If found True, print's message.
11. Fails to write log file when custom file is set whether it's with -path or alone
      FIXED
       
       



Enhancements:
- would be nice to have an option to remove the md5_log and start over.
- should be an option like, '-check' which uses md5_log in the current directory
  declined - default log file name is known and can be typed in easily with given options.
  In addition with current manor, it's not locked down to the current directory
- Could perhaps fail silently if path is not actually a path - same with log
- 

Tests:
- need to verify logfile only command line
- need to verify custom file and log
validate Command line options in bash shell
- test with no options
- test -path option using valid input
- test -path and -log with valid inputs
- test -log with valid input
validate Command line options in python shell
- test with one parameter
- test with all required parameters

Known issues:
- Crashes if non file path is used

"""


