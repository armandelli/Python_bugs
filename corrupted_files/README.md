Hey everyone!

I am a humble infrasctructure/infosec analyst who tries to work smart and is curious about the python world! I am currently running a python script to read an old database of postfix email files, parse some fields and insert them into an MSSQL database for indexing and fast search.

However, after running a final version of the script I came accross a bunch of files that seemed to have been "corrupted" during the process, in a way that some files seem to have their content overwritten with chunks of other mail files.

This is basically what the script does:

It sets a few variables, like the folder path, date, time and database credencials. Then I define a function for parsing the data from the emails and another to convert email files from LATIN-1/ISO-8859 to UTF-8.

The main part of the code is a loop that lists all files in the given folder and for each files listed checks if it is an email file or a regular file.

If it is an email file, it checks the encoding.
If it is UTF-8, it runs the parsing function and inserts the tada into the database. If it is an LATIN-1 file, it converts to UTF-8 and then runs the parsing function.
If it is not an email file, it moves to the next file.
I log some info, including the errors encountered. Through the log I was able to see errors only regarding the parsing function and when I opened the mail file, found it to be corrupt.

I have made available in this folder some sample mail files, a log of the running script and the script coding (there might be some typos as I translated from portugueses to english for better understanding, but keep in mind that the script is rugnning without any synthax or identation errors)

Any ideas?

Thanks much!
