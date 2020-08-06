# Import the email modules we'll need
from email.parser import BytesParser, Parser
from email.policy import default
from time import gmtime, strftime, strptime, localtime
import sys,traceback,textwrap,pyodbc,hashlib,subprocess,os,os.path,datetime,re,io

username=""
password=""
database=""
port=""
server=""

initial_date = strftime("%Y-%m-%d %H:%M:%S", localtime()) #INITIAL TIME
hora = strftime("%H:%M:%S", localtime()) #HOUR ONLY
folder_path = "/mnt/mail/domain/audit/.209005/cur" #FULL PATH TO FOLDER WHERE FILES ARE - USED IN LOOP
index_folder = re.match('^.*(\.[0-9]+.*)', str(folder_path)).group(1)  #SECTION OF PATH REGARDING THE SPECIFIC FOLDER BY YEAR - USED TO GENERATE THE SPECIFIC LOG FILE AND LOG MESSAGES
log_file_name = "index"+str(index_folder.split('/')[0])+str(index_folder.split('/')[1])+".log"#NAME OF THE LOG FILE
log_file = open(log_file_name, "a")#FILE LOG CREATION AND OPEN

counter = 0
counterb = 0
counterc = 0
counterd = 0
countertotal = 0

connprod = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password)
cursorprod = connprod.cursor()

print ("[START]","[",initial_date,"]: ", "------START of script------", file=open(log_file_name, "a"))
print ("[LOG]","[",initial_date,"]: ","Mail folder to be indexed: ", index_folder, file=open(log_file_name, "a"))


############################################################################################
###Function that parses data from mail files of SMTP and ASCII format and  UTF-8 encoding ##
############################################################################################

def ProcessEmail(file_path):
    h1 = subprocess.Popen(["md5sum", file_path], stdout=subprocess.PIPE)
    h2 = subprocess.Popen(["awk", '{print $1}'], stdin=h1.stdout, stdout=subprocess.PIPE)
    h1.stdout.close()
    hash_key = h2.communicate()[0].decode('utf-8')

    with open(file_path, 'rb') as fp:

        headers = BytesParser(policy=default).parse(fp)
        content = fp.read()
        new_format = "%Y-%m-%d %H:%M:%S"
        original_format = "%d %b %Y %H:%M:%S %z"
        subject_truncated = format(headers['subject'])[:200]

        try:
            original_date = str(format(headers['Date']))[5:31]
            converted_date = datetime.datetime.strptime(original_date, original_format).strftime(new_format)

        except:
            alternate_date = re.findall('\d\d\s(?:[A-Z][a-z][a-z])\s\d{4}\s[0-9]+:[0-9]+:[0-9]+\s\-[0-9]+', open(file_path).read())[0]
            converted_date = datetime.datetime.strptime(alternate_date, original_format).strftime(new_format)

        cursorprod.execute("insert into MAIL_AUDIT.dbo.mail_index (mail_hash,mail_to,mail_from,mail_subject,mail_date,mail_path) values (?,?,?,?,?,?)", hash_key, format(headers['to'])[0:500], format(headers['from'])[0:500], subject_truncated, converted_date, file_path)
        connprod.commit()

############################################################        

#############################################################
###Converts the email file from  ISO-8891/LATIN-1 to UTF-8###
#############################################################

def ConverteEmailIso(file_path):

    with io.open(file_path, 'r', encoding='latin-1') as f:
        text = f.read()
    
    with io.open(file_path, 'w', encoding='utf8') as f:
        f.write(text)

#####################################
#########Start of main loop#########
#####################################

for file in os.listdir(folder_path):
    
    countertotal += 1
    date_time = strftime("%Y-%m-%d %H:%M:%S", localtime())
    
  
###Detects file type###

    file_path = str(folder_path)+"/"+file
    p1 = subprocess.Popen(["file", file_path], stdout=subprocess.PIPE)
    p2 = subprocess.Popen(["awk", '{print $2}'], stdin=p1.stdout, stdout=subprocess.PIPE)
    p1.stdout.close()
    file_type = p2.communicate()[0].rstrip()


###Detects file format/encoding####
    
    file_path = str(folder_path)+"/"+file
    p1 = subprocess.Popen(["file", file_path], stdout=subprocess.PIPE)
    p2 = subprocess.Popen(["awk", '{print $4}'], stdin=p1.stdout, stdout=subprocess.PIPE)
    p1.stdout.close()
    file_format = p2.communicate()[0].rstrip()
    


    if (file_type.decode('utf-8') == "SMTP") or (file_type.decode('utf-8') != "SMTP" and re.match('([0-9]+)\.(.*)\.(.*)', str(file))):
        if (file_format.decode('utf-8') == 'ASCII' or file_format.decode('utf-8') == 'UTF-8'):
            try:
                ProcessEmail(file_path)
                counter += 1
  
            except:
                counterb +=1
                ex = sys.exc_info()[0]
                tb = textwrap.fill(traceback.format_exc(), 1000)
                print ("[ERRO]","[",date_time,"]: ","File: ", file, file=open(log_file_name, "a"))
                print ("[ERRO]","[",date_time,"]: ","Formato file: ", file_format, file=open(log_file_name, "a"))
                print ("[ERRO]","[",date_time,"]: ","Tipo do erro: ",ex, file=open(log_file_name, "a"))
                print ("[ERRO]","[",date_time,"]: ","Traceback: ", tb, file=open(log_file_name, "a"))
                pass

        elif (file_format.decode('utf-8') == 'ISO-8859'):
            try:
               
                ConverteEmailIso(file_path) 
                ProcessEmail(file_path)
                print ("[INFO]","[",date_time,"]: ", file,"-", file_format.decode('utf-8'), "convertido para UTF-8",file=open(log_file_name, "a"))        
                counter += 1
                counterd += 1
                
            except:
                counterb +=1
                ex = sys.exc_info()[0]
                tb = textwrap.fill(traceback.format_exc(), 1000)
                print ("[ERRO]","[",date_time,"]: ","File: ", file, file=open(log_file_name, "a"))
                print ("[ERRO]","[",date_time,"]: ","Formato file: ", file_format, file=open(log_file_name, "a"))
                print ("[ERRO]","[",date_time,"]: ","Tipo do erro: ",ex, file=open(log_file_name, "a"))
                print ("[ERRO]","[",date_time,"]: ","Traceback: ", tb, file=open(log_file_name, "a"))
                pass
            
    else:
         print ("[INFO]","[",date_time,"]: ", file, "não é do tipo SMTP", file=open(log_file_name, "a"))
         counterc += 1

####################################      
###End of main loop###
####################################

###################################
###Logs data###
###################################

final_date = strftime("%Y-%m-%d %H:%M:%S", localtime())
time_running = datetime.datetime.strptime(final_date, '%Y-%m-%d %H:%M:%S')- datetime.datetime.strptime(initial_date, '%Y-%m-%d %H:%M:%S')
print ("[LOG]","[",final_date,"]: ","Time running: ", time_running, file=open(log_file_name, "a"))
print ("[LOG]","[",final_date,"]: ", "Total files in directory", countertotal, file=open(log_file_name, "a"))
print ("[LOG]","[",final_date,"]: ", counterc, "Files that are not emails", file=open(log_file_name, "a")) 
print ("[LOG]","[",final_date,"]: ", counter, "Mail files successfully indexed", file=open(log_file_name, "a"))
print ("[LOG]","[",final_date,"]: ", counterb, "Mail files NOT indexed", file=open(log_file_name, "a"))
print ("[LOG]","[",final_date,"]: ", counterd, "Mail files converted from ISO-8891/LATIN-1 to UTF-8", file=open(log_file_name, "a"))
print ("[END]","[",final_date,"]: ", "------END of script------", file=open(log_file_name, "a"))
print ("-----------------------------------------------------------", file=open(log_file_name, "a"))
