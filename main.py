from PyQt5 import QtWidgets, uic, QtCore
from PyQt5.QtWidgets import QFileDialog, QDialog
import queue
import threading
from PyQt5.QtGui import QIcon
import sys
from instabot_py import InstaBot
from checker import InstaChecker
import license
import time, random
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import datetime
#from instabot import *

class Ui(QtWidgets.QMainWindow):
    proxyqueue = queue.Queue()
    cooldownqueue = queue.Queue()
    bad_queue = queue.Queue()
    taken_names = queue.Queue()
    good_names = []
    notifemail = ""
    running = False
    names = []
    count = 0
    proxiescount = 0
    thread_count = 0
    mainproxy = "Default"
    proxies = []
    threads = []
    claiming_flag = False
   
    checked_count = 1
    error_count = 0
    filter_flag = False
    filter2_count = 0
    sandbox_flag = False
    filter_count = 0
    prev_count = 1
    claim_name = ""
    name_count = 0
    
    if (license.licence_check() != 1):
        print("check failed")
        sys.exit(0)

    def __init__(self):
        super(Ui, self).__init__() # Call the inherited classes __init__ method
        uic.loadUi('gui.ui', self) # Load the .ui file

      
        self.login_status = False
        
        #Buttons
        self.login_Btn = self.findChild(QtWidgets.QPushButton, 'loginButton')
        self.login_Btn.clicked.connect(self.loginButtonPressed) # Remember to pass the definition/method, not the return value!

        self.start_Btn = self.findChild(QtWidgets.QPushButton, 'claimButton')
        self.start_Btn.clicked.connect(self.MainLoop)

        self.stop_Btn = self.findChild(QtWidgets.QPushButton, 'stopButton')
        self.stop_Btn.clicked.connect(self.StopLoop)
        
        self.import_userlist_Btn = self.findChild(QtWidgets.QPushButton, 'usernameButton')
        self.import_userlist_Btn.clicked.connect(self.importUserList)

        self.proxy_main_Btn = self.findChild(QtWidgets.QPushButton, 'mainProxyButton')
        self.proxy_main_Btn.clicked.connect(self.mainProxy)

        self.proxy_Btn = self.findChild(QtWidgets.QPushButton, 'proxyButton')
        self.proxy_Btn.clicked.connect(self.proxyLoad)

        self.filter_Btn = self.findChild(QtWidgets.QPushButton, 'filterButton')
        self.filter_Btn.clicked.connect(self.filter)

        self.sandbox_Btn = self.findChild(QtWidgets.QPushButton, 'sandbox_Btn')
        self.sandbox_Btn.clicked.connect(self.sandbox)

        self.notif_Btn = self.findChild(QtWidgets.QPushButton, 'notifButton')
        self.notif_Btn.clicked.connect(self.updateEmail)

        self.speed_Box = self.findChild(QtWidgets.QComboBox, 'comboBox')
        self.speed_Box.currentIndexChanged.connect(self.updateSpeed)
        

        self.check_LineEdit = self.findChild(QtWidgets.QLineEdit, 'lineEdit_checking')
        self.username_LineEdit = self.findChild(QtWidgets.QLineEdit, 'lineEdit_username')
        self.password_LineEdit = self.findChild(QtWidgets.QLineEdit, 'lineEdit_password')
        self.email_LineEdit = self.findChild(QtWidgets.QLineEdit, 'lineEdit_email')
        self.listSize_LineEdit = self.findChild(QtWidgets.QLineEdit, 'lineEdit_listSize')

        
        self.proxyMain_LineEdit = self.findChild(QtWidgets.QLineEdit, 'lineEdit_proxyMain')
        self.proxy_LineEdit = self.findChild(QtWidgets.QLineEdit, 'lineEdit_proxyNo')
        self.checkedNo_LineEdit = self.findChild(QtWidgets.QLineEdit, 'lineEdit_checkedNo')
        self.errorNo_LineEdit = self.findChild(QtWidgets.QLineEdit, 'lineEdit_errorcount')
        self.day_LineEdit = self.findChild(QtWidgets.QLineEdit, 'lineEdit_day')
        self.hour_LineEdit = self.findChild(QtWidgets.QLineEdit, 'lineEdit_hour')
        self.second_LineEdit = self.findChild(QtWidgets.QLineEdit, 'lineEdit_second')
        self.threadpool_LineEdit = self.findChild(QtWidgets.QLineEdit, 'lineEdit_threadpool')
        self.cooldown_LineEdit = self.findChild(QtWidgets.QLineEdit, 'lineEdit_cooldown')
        self.notif_LineEdit = self.findChild(QtWidgets.QLineEdit, 'lineEdit_notif')
        self.senderE_LineEdit = self.findChild(QtWidgets.QLineEdit, 'lineEdit_senderE')
        self.senderP_LineEdit = self.findChild(QtWidgets.QLineEdit, 'lineEdit_SenderP')



        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(4) #30

        self.consoleUpdate = QtCore.QTimer()
        self.consoleUpdate.timeout.connect(self.ConsoleUpdate)
        self.consoleUpdate.start(16) #30

        self.claimtimer = QtCore.QTimer()
        self.claimtimer.timeout.connect(self.claimcheck)
        self.claimtimer.start(1) #30

        self.timer2 = QtCore.QTimer()
        self.timer2.timeout.connect(self.cooldown)
        self.timer2.start(20000)

        self.console = self.findChild(QtWidgets.QTextEdit, 'textEdit_console')
        
        self.show() # Show the GUI
        

    def updateEmail(self):
        self.notifemail=self.notif_LineEdit.text()
        self.console.append("Sending test email to: " + str(self.notifemail))
        self.sendEmail("\n\n*This email is to check notifications work*\n\n ","NOTIFICATION EMAIL CHECK")
        

    def updateSpeed(self):
       
        if (self.speed_Box.currentIndex() == 0): #200 /s
            self.thread_count= 100
            self.timer.setInterval(4)
        else: #100 /s
            self.thread_count= 50
            self.timer.setInterval(8)

        self.console.append("Speed updated... " + str(self.speed_Box.currentText()))
        

    def filter(self):
        if (self.proxyqueue.empty() == True or not self.names):
            self.console.append("IMPORT PROXIES AND USERNAMES FIRST") #Create object threads
        else:
            if (self.speed_Box.currentIndex() == 0): #200 /s
                self.thread_count= 50
                self.timer.setInterval(8)
            else: #100 /s
                self.thread_count= 20
                self.timer.setInterval(8)

            self.good_names = []
            self.filter_flag = True
            self.sandbox_flag = True
            self.console.append("FILTERING LIST")
            self.loginButtonPressed()
            self.claiming_flag = True
            self.running = True


    def sandbox(self):
        if self.sandbox_flag == False:
            self.sandbox_flag = True
        else:
            self.sandbox_flag = False
        
        self.console.append("Sandbox - " + str(self.sandbox_flag))


    def proxyLoad(self):
        self.proxies = []
        dlg = QFileDialog()
        dlg.setFileMode(QFileDialog.ExistingFile)
        dlg.setNameFilters(["Text files (*.txt)"])
        
        
        self.console.append("Reading proxies list file...")
      
        if dlg.exec_():
            filenames = dlg.selectedFiles()
            f = open(filenames[0], 'r')

            Lines = f.readlines() 
            self.proxiescount = 0
            # Strips the newline character 
            self.proxies.clear()

            for line in Lines: 
                self.proxies.append(line.strip()) 
                self.proxyqueue.put(line.strip())
                self.proxiescount += 1
        else:
            self.console.append("Invalid file selected...")
                
        self.proxy_LineEdit.setText(str(self.proxiescount))
        self.console.append("File read - " + str(self.proxiescount) + " proxies loaded")
      

    def mainProxy(self):
        self.mainproxy = self.proxyMain_LineEdit.text()
        self.console.append("Main proxy loaded... " + self.mainproxy)
       

    def importUserList(self):
        self.names = []
        dlg = QFileDialog()
        dlg.setFileMode(QFileDialog.ExistingFile)
        dlg.setNameFilters(["Text files (*.txt)"])
        
            
        self.console.append("Reading username list file...")
      
        if dlg.exec_():
            filenames = dlg.selectedFiles()
            f = open(filenames[0], 'r')

            Lines = f.readlines() 
            self.count = 0
            # Strips the newline character 
            for line in Lines: 
                self.names.append(line.strip()) 
                self.count += 1
        else:
            self.console.append("Invalid file selected...")
                
        self.listSize_LineEdit.setText(str(self.count))
        self.console.append("File read - " + str(self.count) + " words loaded")
        

    def sendEmail(self,Cname,subjects):
        if (self.notifemail != ""):
            print("Sending Email Notification")
            try:
                sender_email = self.senderE_LineEdit.text()
                receiver_email = self.notifemail
                password = self.senderP_LineEdit.text()

                message = MIMEMultipart("alternative")
                message["Subject"] = subjects
                message["From"] = "IGClaimer 2020"
                message["To"] = receiver_email

                now = datetime.datetime.now()

                # Create the plain-text and HTML version of your message
                text = ("The following username has been claimed " + Cname + "\n" + now.strftime("%Y-%m-%d %H:%M:%S")) 
                

                # Turn these into plain/html MIMEText objects
                part1 = MIMEText(text, "plain")


                # Add HTML/plain-text parts to MIMEMultipart message
                # The email client will try to render the last part first
                message.attach(part1)


                # Create secure connection with server and send email
                context = ssl.create_default_context()
                with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
                    server.login(sender_email, password)
                    server.sendmail(
                        sender_email, receiver_email, message.as_string()
                    )
            except:
                print("Failed to send email - GOOGLE SECURITY\nLOGIN to your GMAIL account using chrome to fix\n\nCheck *Less secure apps* is ENABLED too @ \nhttps://myaccount.google.com/lesssecureapps?pli=1")

    def loginButtonPressed(self):
        try:
            if(self.login_status == False):
                global bot

                if (self.proxyqueue.empty() == True):
                    self.console.append("IMPORT PROXIES FIRST") #Create object threads

                else:
                    #LOGIN BIT
                    if ( self.sandbox_flag == False):
                        bot = InstaBot(login=self.username_LineEdit.text().strip(),  password=self.password_LineEdit.text().strip(), console=self.console, apps = app, email_a = self.email_LineEdit.text().strip())
                        bot.login()

                    self.console.append("Creating threads") #Create object threads
                    self.checker = InstaChecker(proxy=str(self.proxies[random.randint(0,len(self.proxies)-1)]),console=self.console,apps = app)
                    
                self.updateSpeed()
                self.login_status = True
              
            else:
                self.console.append("Already Logged In") #Create object threads
        except:
            self.console.append("Login Failed") #Create object threads
        

    def StopLoop(self):
        #global bot
        self.console.append("****BOT STOPPING****")
      
        #bot.logout()
        self.running = False
    
        self.login_status = False

    def FilterThreadFunc(self,name,Tproxy):
        response = self.checker.filter(check_name=name,Tproxy = Tproxy)

        if response == 0:
            self.good_names.append(name)
            self.filter_count += 1
            self.proxyqueue.put(Tproxy)
        
        elif response == 1:
            self.taken_names.put(name)
            self.proxyqueue.put(Tproxy)
            
        
        else:
            self.bad_queue.put(name)
            self.cooldownqueue.put(Tproxy)
            
    def claimcheck(self):
        global bot

        if(self.claiming_flag == True and self.sandbox_flag == False):
            if(self.login_status == True):
                bot.claim(self.claim_name)
                
            else:
                self.loginButtonPressed()
                bot.claim(self.claim_name)

            self.running = False
            self.login_status = False
            self.sendEmail(self.claim_name,"Username Claimed")
            while(1):
                
                time.sleep(1)
        

    def ThreadFunction(self,name_check,Threadproxy):
        
        
        response = self.checker.check(check_name=name_check,Tproxy = Threadproxy)
     


        if response == 0: #Taken
            self.checked_count += 1
            self.proxyqueue.put(Threadproxy)
        elif response == 1: #CLAIMABLE
            self.claim_name = name_check   
            self.claiming_flag = True
            print ("CLAIMING: " + name_check)
            
        elif response == 2: #PROXY ERROR
            self.error_count += 1
            self.cooldownqueue.put(Threadproxy)
            
        elif response == 3: #INSTA ERROR
            self.error_count += 1
            self.cooldownqueue.put(Threadproxy)
            
        elif response == 4: #REQUEST TIMEOUT
            
            self.cooldownqueue.put(Threadproxy)
            
        
        

    def Threadcookie(self):
        
        self.console.append("COOKIES UPDATE")
        

        while(self.checker.Retrieve_Cookie() != 0):
            self.checker.Update_Proxy(str(self.proxies[random.randint(0,len(self.proxies)-1)]))
        

        self.console.append("SUCCESS: X-CSRFToken Request")
        
        
    def MainLoop(self):
        
        time.sleep(1)
        self.running = True
        self.claiming_flag = False


        if (self.login_status == False):
            self.console.append("LOGIN FIRST")
            
        else:
            self.console.append("****STARTING BOT****")
            

    def cooldown(self):
        try:
            per_second = (self.checked_count - self.prev_count) / 20
            per_hour = per_second*3600
            per_day = per_hour * 24

            self.day_LineEdit.setText(str(per_day))
            self.hour_LineEdit.setText(str(per_hour))
            self.second_LineEdit.setText(str(per_second))
            self.prev_count = self.checked_count
        except:
            print("DIV 0 ERROR")

        for x in range (3):
            if (self.cooldownqueue.empty() != True):
                self.proxyqueue.put(self.cooldownqueue.get())

    def ConsoleUpdate(self):
        self.console.verticalScrollBar().setValue(self.console.verticalScrollBar().maximum())
        if(self.console.verticalScrollBar().value() > 0):
            self.console.clear()
        
        self.threadpool_LineEdit.setText(str(threading.active_count()))
        app.processEvents()


    def update(self):
        
       
        if(self.running == True and self.login_status == True):
        
            
    
            
            try:
                if threading.active_count() <= int(self.thread_count) and self.claiming_flag == False and self.proxyqueue.empty() != True:
                    

                    Threadproxy = self.proxyqueue.get()
                   
                    self.checkedNo_LineEdit.setText(str(self.checked_count))
                    self.errorNo_LineEdit.setText(str(self.error_count))
                    self.cooldown_LineEdit.setText(str(self.cooldownqueue.qsize()))

                    
                    name_check = self.names[self.name_count]
                    self.check_LineEdit.setText(str(name_check))
                    


                    #thread = threading.Thread(target=self.ThreadFunction, args=(name_check,))
                    
                    thread = threading.Thread(target=self.ThreadFunction, args=(name_check,Threadproxy,))
                    thread.start()

                    self.name_count += 1
                    if (self.name_count >= (len(self.names) - 1)):
                        self.name_count = 0
            except:
                self.console.append("THREAD START ERROR")

        

            try:
                if self.filter_flag == True:
                    print("Starting filter")
                    for name in self.names:
                        while(threading.active_count() > int(self.thread_count) or self.proxyqueue.empty() == True):
                            pass
                        Threadproxy = self.proxyqueue.get()

                        Fthread = threading.Thread(target=self.FilterThreadFunc, args=(name,Threadproxy,))
                        Fthread.start()
                        self.filter2_count += 1
                        self.console.append("checking - " + str(name) + " " + str(self.filter2_count))
                        self.ConsoleUpdate()

                    while self.bad_queue.empty() != True:
                        name_recheck = self.bad_queue.get()
                        while(threading.active_count() > int(self.thread_count) or self.proxyqueue.empty() == True):
                            pass
                        Threadproxy = self.proxyqueue.get()

                        Fthread = threading.Thread(target=self.FilterThreadFunc, args=(name_recheck ,Threadproxy,))
                        Fthread.start()
                        self.filter2_count += 1
                        self.console.append("checking - " + str(name_recheck ) + " " + str(self.filter2_count))
                        self.ConsoleUpdate()
                        

                    
                    for x in range (10):
                        self.console.append("Waiting")
                        self.ConsoleUpdate()
                        time.sleep(1)

                    self.console.append("Saving " + str(len(self.good_names)))
                    self.ConsoleUpdate()
                    filtered_names = self.good_names
                    with open('filtered_names.txt', 'w') as f:
                        for item in filtered_names:
                            f.write("%s\n" % item)
                    
                    
                    with open('taken_names.txt', 'w') as f:
                        while (self.taken_names.empty() != True):
                            item = self.taken_names.get()
                            f.write("%s\n" % item)
                    
                    self.console.append("Filter complete, saved to filtered_names.txt...")
                    
                    self.filter_flag = False
                    self.sandbox_flag = False
                    self.claiming_flag = False
                    self.running = False
                    self.good_names = []

                    self.updateSpeed()

                
                    

            except:
                self.console.append("FILTER ERROR")
                self.filter_flag = False
                self.sandbox_flag = False
                self.claiming_flag = False
                self.running = False
                self.good_names = []

                self.updateSpeed()

            

            if self.checked_count % 100000 == 0:
                self.Threadcookie()

            
            

        

           

           
sys._excepthook = sys.excepthook 
def exception_hook(exctype, value, traceback):
    print(exctype, value, traceback)
    sys._excepthook(exctype, value, traceback) 
    sys.exit(1) 
sys.excepthook = exception_hook 

app = QtWidgets.QApplication(sys.argv) # Create an instance of QtWidgets.QApplication

app.setWindowIcon(QIcon("/Claimer2020/icon.png"))
        
window = Ui() # Create an instance of our class
app.exec_() # Start the application
