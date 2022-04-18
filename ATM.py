import pandas as pd
import numpy as np
import cx_Oracle as cx
import sys
from datetime import datetime,date
import time
from tabulate import tabulate
from pygame import mixer

connection = cx.connect('hr/atharv')
cursor = connection.cursor()

def log_in():
    print('Log In'.center(100))
    i = 2
    while i >= 0:
        account_no = int(input('Enter account number: '))
        pin = input('Enter PIN: ')
        try:
            account_no_query = 'select account_no from customer where account_no = :account_no'
            cursor.execute(account_no_query,[account_no])
            db_acc_no = cursor.fetchall()
            global db_acc_no_
            db_acc_no_ = db_acc_no[0][0]
            db_acc_no = db_acc_no[0][0]
            pin_query = 'select pin from customer where account_no = :account_no'
            cursor.execute(pin_query,[account_no])
            db_pin = cursor.fetchall()
            global db_pin_
            db_pin_ = db_pin[0][0]
            db_pin = db_pin[0][0]
        except:
            print('Account number not found'.center(100))
        
        if account_no == db_acc_no :
            login_time_query = 'select round(sysdate-last_login,5) from customer where account_no = :db_acc_no'
            cursor.execute(login_time_query,[db_acc_no])
            login_time = cursor.fetchall()
            login_time = login_time[0][0]
            print('login time',login_time)
            if pin != db_pin and i == 0:
                print('Invalid PIN'.center(100))
                print('Your account is blocked for next 24 hours'.center(100))
                sys.exit()
            elif pin != db_pin:
                print('Invalid PIN'.center(100))
            else:
                print('Log in successfully'.center(100))
                name_query = 'select initcap(first_name) from customer where account_no = :db_acc_no'
                cursor.execute(name_query,[db_acc_no])
                name = cursor.fetchall()
                name = name[0][0]
                print(f'Welcome {name}'.center(100))
                login_datetime_update = 'update customer set last_login = sysdate where account_no=:db_acc_no'
                cursor.execute(login_datetime_update,[db_acc_no])
                connection.commit()
                break
        i-=1

        
def create_acc():
    print('Create Account'.center(100))
    while True:
        first_name=input('Enter first_name: ').upper()
        if len(first_name) == 0:
            print('First name is cumpulsory'.center(100))
            continue
        else:
            break
    while True:
        last_name = input('Enter last name: ').upper()
        if len(last_name) == 0:
            print('Last name is cumpulsory'.center(100))
            continue
        else:
            break
    while True:
        city = input('Enter your city: ').upper()
        if len(city) == 0:
            print('City is cumpulsory'.center(100))
            continue
        else:
            break
    while True:
        acc_type_list = ['SAVING', 'CURRENT', 'SALARY']
        acc_type = input('Choose account type: Saving, Current, Salary: ').upper()
        if acc_type not in acc_type_list:
            print('Account Type should match with Saving or Current or Salary'.center(100))
            continue
        else:
            break
    while True:
        adhar_no = input('Enter Adhar Number: ')
        if len(adhar_no) != 12:
            print('Length of Adhar number must be 12'.center(100))
            continue
        else:
            adhar_no = int(adhar_no)
            break
    while True:
        balance = int(input('Deposite money to create your account(Greater Than Rs.10000): '))
        if balance <= 10000:
            print('Balance should be greater than 10000'.center(100))
            continue
        else:
            break
    while True:
        pin = input('Create PIN (4 Digits): ')
        if len(pin) != 4:
            print('Length of pin must be 4'.center(100))
            continue
        else:
            pin = int(pin)
            break
    dob = input('Enter Date of Birth (DD-MON-YYYY): ').upper()
    while True:
        mob_no = input('Enter mobile number: ')
        if len(mob_no) != 10:
            print('Length of Mobile Number must be 10'.center(100))
            continue
        else:
            break
    while True:
        gender_list = ['M','F']
        gender = input('Select gender(M, F): ').upper()
        if gender not in gender_list:
            print('Gender should match with M or F'.center(100))
            continue
        else:
            break
    opening_date = datetime.today()
    last_login = datetime.today()
    cursor.execute('select account_no_sq.nextval from dual')
    acc_no = cursor.fetchall()
    acc_no = acc_no[0][0]
    create_query = '''insert into customer values 
                (:acc_no,:first_name,:last_name,:acc_type,:adhar_no,:city,:pin,:balance,:dob,:gender,:opening_date,:mob_no,:last_login)'''
    cursor.execute(create_query,[acc_no,first_name,last_name,acc_type,adhar_no,city,pin,balance,dob,gender,opening_date,mob_no,last_login])
    connection.commit()
    print('Account created successfully\nLog in to proceed'.center(100))
    acc_info_query = '''select account_no,first_name,last_name,gender,mob_no
                from customer
                where account_no = :acc_no'''
    cursor.execute(acc_info_query,[acc_no])
    acc_info = cursor.fetchall()
    account_no_df = []
    first_name_df = []
    last_name_df = []
    gender_df = []
    mob_no_df = []
    account_no_df.append(acc_info[0][0])
    first_name_df.append(acc_info[0][1])
    last_name_df.append(acc_info[0][2])
    gender_df.append(acc_info[0][3])
    mob_no_df.append(acc_info[0][4])

    acc_info_df = pd.DataFrame({'Account Number': account_no_df,'First name': first_name_df,'Last Name':last_name_df,'Gender':gender_df,
                      'Mobile Number':mob_no_df})
    print('Account Information preview:'.center(100))
    print('\n',acc_info_df.to_string(index=False))
    connection.commit()
    full_login()
        
def credit():
    print('Cash Deposite'.center(100))
    add_money = int(input('Enter amount: '))
    credit_transaction = '''update customer
                             set balance = balance + :add_money
                             where account_no = :db_acc_no_'''
    cursor.execute(credit_transaction,[add_money,db_acc_no_])
    add_money_str = str(add_money)
    add_money_ = '+'+add_money_str
    timestamp = time.strftime('%I:%M:%S %p',time.localtime())
    update_credit_query = '''insert into credit values
                            (:db_acc_no_,:add_money_,sysdate,:timestamp)'''
    cursor.execute(update_credit_query,[db_acc_no_,add_money_,timestamp])
    connection.commit()
    print(f'Your account is credited by {add_money}'.center(100))


def debit():
    print('Cash Withdrawal'.center(100))
    remove_money = int(input('Enter amount: '))
    balance_query = 'select balance from customer where account_no = :db_acc_no_'
    cursor.execute(balance_query,[db_acc_no_])
    balance = cursor.fetchall()
    balance = balance[0][0]
    transaction_count_query = 'select count(transaction_date) from debit where account_no = :db_acc_no_'
    cursor.execute(transaction_count_query,[db_acc_no_])
    transaction_count = cursor.fetchall()
    transaction_count = transaction_count[0][0]
    transaction_date_query = "select to_char((max(transaction_date)),'yyyy-mm-dd') from debit where account_no=:db_acc_no_ "
    cursor.execute(transaction_date_query,[db_acc_no_])
    transaction_date = cursor.fetchall()
    transaction_date = transaction_date[0][0]
    if transaction_count >= 5 and transaction_date == str(date.today()):
        print('You have reached daily transaction limit'.center(100))
    else:
        if balance - remove_money < 10000:
            print('Minimun balance is violated'.center(100))
        else:
            debit_transaction = '''update customer
                                     set balance = balance - :remove_money
                                     where account_no = :db_acc_no_'''
            cursor.execute(debit_transaction,[remove_money,db_acc_no_])
            remove_money_str = str(remove_money)
            remove_money_ = '-'+remove_money_str
            timestamp = time.strftime('%I:%M:%S %p',time.localtime())
            update_debit_query = '''insert into debit values
                                    (:db_acc_no_,:remove_money_,sysdate,:timestamp)'''
            cursor.execute(update_debit_query,[db_acc_no_,remove_money_,timestamp])
            connection.commit()
            mixer.init()
            mixer.music.load('Cash_Withdraw_sound.wav')
            mixer.music.set_volume(0.5)
            mixer.music.play()
            time.sleep(12)
            print(f'Your account is debited by {remove_money}'.center(100))


def acc_info():
    print('Account Information'.center(100))
    acc_info_query = "select account_no,first_name,last_name,gender,account_type,city,adhar_no,upper(to_char(dob,'dd-mon-yyyy')),mob_no,upper(to_char(opening_date,'dd-mon-yyyy')),balance from customer where account_no = :db_acc_no_"
    cursor.execute(acc_info_query,[db_acc_no_])
    account_info = cursor.fetchall()
    account_no_df = []
    first_name_df = []
    last_name_df = []
    gender_df = []
    account_type_df = []
    city_df = []
    adhar_no_df = []
    dob_df = []
    mob_no_df = []
    opening_date_df = []
    balance_df = []

    account_no_df.append(account_info[0][0])
    first_name_df.append(account_info[0][1])
    last_name_df.append(account_info[0][2])
    gender_df.append(account_info[0][3])
    account_type_df.append(account_info[0][4])
    city_df.append(account_info[0][5])
    adhar_no_df.append(account_info[0][6])
    dob_df.append(account_info[0][7])
    mob_no_df.append(account_info[0][8])
    opening_date_df.append(account_info[0][9])
    balance_df.append(account_info[0][10])
    
    account_info_df = pd.DataFrame({
                      'Account Number':account_no_df,'First name':first_name_df,'Last Name':last_name_df,'Gender':gender_df,
                      'Account Type':account_type_df,'City':city_df,'Adhar Number':adhar_no_df,'DOB':dob_df,'Mobile':mob_no_df,
                      'Account Opening Date':opening_date_df,'Balance':balance_df})
    account_info_df = account_info_df.transpose()
    print(tabulate(account_info_df,showindex=True))
    

def pin_change():
    print('PIN Change'.center(100))
    while True:
        account_no = int(input('Enter account number: '))
        try:
            account_no_query = 'select account_no from customer where account_no = :account_no'
            cursor.execute(account_no_query,[account_no])
            db_acc_no = cursor.fetchall()
            global db_acc_no_
            db_acc_no_ = db_acc_no[0][0]
            db_acc_no = db_acc_no[0][0]
        
        except:
            print('Account number not found'.center(100))
        if account_no == db_acc_no :
            new_pin = int(input('Enter new PIN: '))
            pin_update_query = 'update customer set pin = :new_pin where account_no = :db_acc_no_'
            cursor.execute(pin_update_query,[new_pin,db_acc_no_])
            connection.commit()
            print('PIN updated successfully'.center(100))
            break


def forgot_pin():
    print('Forgot PIN'.center(100))
    while True:
        account_no = int(input('Enter account number: '))
        try:
            account_no_query = 'select account_no from customer where account_no = :account_no'
            cursor.execute(account_no_query,[account_no])
            db_acc_no = cursor.fetchall()
            global db_acc_no_
            db_acc_no_ = db_acc_no[0][0]
            db_acc_no = db_acc_no[0][0]
        
        except:
            print('Account number not found'.center(100))
        if account_no == db_acc_no :
            forgot_pin_query = 'select pin from customer where account_no = :db_acc_no_'
            cursor.execute(forgot_pin_query,[db_acc_no_])
            forgot_pin_recover = cursor.fetchall()
            forgot_pin_recover = forgot_pin_recover[0][0]
            print(f'Your PIN is {forgot_pin_recover}'.center(100))
            break
            
    
def statement():
    print('Account Statement'.center(100))
    print('You will get last five transactions'.center(100))
    statement_query = '''select amount,to_char(transaction_date,'dd-mm-yyyy'),time
                         from credit
                         where account_no = :db_acc_no_
                         union all
                         select amount,to_char(transaction_date,'dd-mm-yyyy'),time
                         from debit
                         where account_no = :db_acc_no_
                         order by 2 desc'''
    cursor.execute(statement_query,[db_acc_no_])
    statement = cursor.fetchmany(5)
    amount = []
    tran_date = []
    time = []
    for i in range(len(statement)):
        amount.append(statement[i][0])
        tran_date.append(statement[i][1])
        time.append(statement[i][2])
    statement_df = pd.DataFrame({'Amount':amount,'Transaction Date':tran_date,'Time':time})
    print('\n')
    print(tabulate(statement_df,showindex=False,headers=statement_df.columns))
    

def update():
    print('Update Account Details'.center(100))
    print('Only City and Mobile number is allowed'.center(100))
    select_update = input('Select City(C) or Mobile Number(M): ').upper()
    if select_update == 'C':
        city = input('Enter City: ').upper()
        update_city_query = 'update customer set city  = :city where account_no = :db_acc_no_'
        cursor.execute(update_city_query,[city,db_acc_no_])
        connection.commit()
        print('City is updated'.center(100))
    else:
        mobile_no =  input('Enter Mobile Number: ')
        update_mob_no_query = 'update customer set mob_no  = :mobile_no where account_no = :db_acc_no_'
        cursor.execute(update_mob_no_query,[mobile_no,db_acc_no_])
        connection.commit()
        print('Mobile Number is updated'.center(100))
        
     
def balance_check():
    balance_check_query = 'select balance from customer where account_no = :db_acc_no_'
    cursor.execute(balance_check_query,[db_acc_no_])
    balance = cursor.fetchall()
    global balance_
    balance_ = balance[0][0]
    print(f'Your balance is {balance_}'.center(100))


def full_login():
    log_in()
    cnt = 'y'
    while cnt == 'y':
        while True:
            print('\n')
            print('Services:'.center(100))
            print('\n')
            print('\t\t  Account Information (A)\t\tDeposite Money (C)')
            print('\t\t  Withdraw Money (W)\t\t\tPIN Change (P)')
            print('\t\t  Balance Check (B)\t\t\tUpdate Details (U)')
            print('\t\t  Statement (S)\t\t\t\tDelete Account (D)')
            services_list = ['A','C','W','P','B','U','S','D']
            services = input('Enter service: ').upper()
            if services in services_list:
                if services == 'A':
                    acc_info()
                elif services == 'C':
                    credit()
                elif services == 'W':
                    debit()
                elif services == 'P':
                    pin_change()
                elif services == 'B':
                    balance_check()
                elif services == 'U':
                    update()
                elif services == 'S':
                    statement()
                elif services == 'D':
                    delete_customer()
                cnt = input('Do want to continue: Yes/No[y/n]')
                if cnt == 'y':
                    continue
                else:
                    print('Thank You'.center(100))
                    print('Visit Again'.center(100))
                    break
            else:
                print('Enter valid key'.center(100))
                continue


def delete_customer():
    del_confirmation = input('Do want to delete account? Yes/No[y/n]: ')
    if del_confirmation == 'y':
        balance_check()
        print('Withdraw all money before account closing'.center(100))
        if balance_ == 0:
            del_insert_query = '''insert into del_customer
                                  (select account_no,first_name,last_name,account_type,adhar_no,city,pin,dob,gender,opening_date,
                                  mob_no
                                  from customer
                                  where account_no = :db_acc_no_)'''
            cursor.execute(del_insert_query,[db_acc_no_])
            del_query = 'delete from customer where account_no = :db_acc_no_'
            cursor.execute(del_query,[db_acc_no_])
            connection.commit()
            print('Your account is deleted'.center(100))
        else:
            balance_query_del = 'select balance from customer where account_no = :db_acc_no_'
            cursor.execute(balance_query_del,[db_acc_no_])
            balance_del = cursor.fetchall()
            balance_del = balance_del[0][0]
            debit_transaction = '''update customer
                                     set balance = 0
                                     where account_no = :db_acc_no_'''
            cursor.execute(debit_transaction,[db_acc_no_])
            remove_money_del = 0
            remove_money_del_str = str(remove_money_del)
            remove_money_del = '-'+remove_money_del_str
            timestamp = time.strftime('%I:%M:%S %p',time.localtime())
            update_debit_del_query = '''insert into debit values
                                    (:db_acc_no_,:remove_money_del,sysdate,:timestamp)'''
            cursor.execute(update_debit_del_query,[db_acc_no_,remove_money_del,timestamp])
            print(f'Your account is debited by {balance_}'.center(100))
            del_insert_query = '''insert into del_customer
                                  (select account_no,first_name,last_name,account_type,adhar_no,city,pin,dob,gender,opening_date,
                                  mob_no
                                  from customer
                                  where account_no = :db_acc_no_)'''
            cursor.execute(del_insert_query,[db_acc_no_])
            del_query = 'delete from customer where account_no = :db_acc_no_'
            cursor.execute(del_query,[db_acc_no_])
            connection.commit()
            print('Your account is deleted'.center(100))
            
            
    else:
        print('Thank You'.center(100))
    
##--------------------------------------------------- MAIN --------------------------------------------------------------


print('Welcome to MyBank'.center(100))
print('\n')
while True:
    print('Log In (L)'.center(100))
    print('Create New Account (N)'.center(100))
    print('Forgot PIN (F)'.center(100))
    print('Exit (X)'.center(100))
    print('\n')
    init_service_list = ['L','N','F','X']

    init_service = input('Enter Service: ').upper()
    if init_service in init_service_list:
        if init_service == 'L':
            full_login()          
        elif init_service == 'N':
            create_acc()
        elif init_service == 'F':
            forgot_pin()
            relogin = input('Do you want to log in: Yes/No[y/n]')
            if relogin == 'y':
                full_login()
            else:
                print('Thank You'.center(100))
                print('Visit Again'.center(100))
        elif init_service == 'X':
            sys.exit()
    else:
        continue





