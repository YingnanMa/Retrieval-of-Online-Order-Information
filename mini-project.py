import sqlite3, time, getpass, re, sys
#from prettytable import PrettyTable

connection = None
cursor = None

def main():
    # The main function contral the function
    global connection, cursor

    #if len(sys.argv) < 2:
    #    path = input("Didn't find database from the shell. Please input the database: ")
    #else:
    #    path = str(sys.argv[1])
    #print(path)
    path="./database1.db"
    connect(path)
    login()
    connection.commit()
    connection.close()
    return

def login():
    # login pages, customer,
    while True:
        user_type = input("Welcome!\nEnter C to login as Customer.\nEnter A to login as Agent.\nEnter exit to exit.\nWaiting: ")
        print(user_type)
        if user_type == "exit":
            return
        elif user_type == 'C' or user_type == 'A':
            idn = input("Please enter you id: ")
            paw = getpass.getpass()
            check_password(user_type, idn, paw)
        else:
            print("Sorry, wrong commond.")
            time.sleep(1)
            login()

def check_password(type, idn, paw):
    # check check_password is right or not
    global connection, cursor, basket
    if re.match("^[A-Za-z0-9]*$",idn) and re.match("^[A-Za-z0-9]*$",paw):
        if type == 'C':
            cursor.execute('select pwd from customers where cid = ?;', (idn,))
            pid = cursor.fetchone()
            if pid == None:
                new_customers(idn, paw)
                login()
                return
            elif pid[0] == paw:
                customer_main(idn)
                return
            else:
                print("Your password or id is wrong! Return to the login page.")
                time.sleep(1)
                login()
                return
        elif type == 'A':
            cursor.execute('select pwd from agents where aid = ?;', (idn,))
            pid = cursor.fetchone()
            if pid == None:
                print("Your password or id is wrong! Return to the login page.")
                return
            elif pid[0] == paw:
                agent_main(idn)
                return
            else:
                print("Your password or id is wrong! Return to the login page.")
                time.sleep(1)
                login()
                return
    else:
        print("Your password or id is wrong! Return to the login page.")
        time.sleep(1)
        login()
    return

def new_customers(cid, pwd):
    # add new customers
    if input("Do your want to create a new account? Y/N  ") == 'Y':
        name = input("Please enter your name: ")
        address = input("Please enter your address: ")
        insert = '''
                     insert into customers(cid, name, address, pwd) values
                             (?, ?, ?, ?)
                '''
        cursor.execute(insert, (cid, name, address, pwd))
        print("Created successd! Please login again.")
        time.sleep(1)
    return

def customer_main(cid):
    # customer's main page
    global basket
    basket = []
    while True:
        order = input("Welcome. If you want search item please enter S.\nIf you want to list your order please enter L.\nIf you want to logout please enter logout.\n")
        if order == 'logout':
            basket = []
            return
        elif order == 'L':
            list_order(cid)
        elif order == 'S':
            search_for_products(cid)
        else:
            print("Sorry, wrong commond.")

def agent_main(aid):
    # agent's main page
    while True:
        order = input("Welcome. If you want to set up delivery, enter D.\nIf you want to update delivery, enter U.\nIf you want to add to stock, enter A.\nIf you want to logout enter logout.")
        if order == 'D':
            set_up_delivery()
        elif order == 'U':
            update_a_delivery()
        elif order == 'A':
            add_to_stock()
        elif order == 'logout':
            return
        else:
            print('Sorry, wrong commond.')


def search_for_products(cid):
    # search for products
    global connection, cursor
    key = input("Please enter what you instereted in (different key word spearted by ';'): ")
    keyword = []
    k = -1
    for i in range(0, len(key)):
        if key[i] == ';':
            keyword.append(key[k+1:i])
            k = i
    keyword.append(key[k+1:])
    item = []
    for i in range(0, len(keyword)):
        cursor.execute('select pid from products where name like ?;', ('%' + keyword[i] + '%',))
        a = cursor.fetchall()
        for k in range(0, len(a)):
            item.append([a[k][0], 1])

    # sort by order
    largest_num = 0
    unsort_list = []
    sort_list = [[]]
    for i in range(0, len(item)):
        unsort_list.append(item[i][0])
    for i in range(0, len(unsort_list)):
        n = unsort_list.count(unsort_list[i])
        while n > len(sort_list):
            sort_list.append([])
        if sort_list[n - 1].count(unsort_list[i]) == 0:
            sort_list[n -1].append(unsort_list[i])

    # sort by name
    list_name = [[]]
    while len(list_name) < len(sort_list):
        list_name.append([])
    for i in range(0, len(sort_list)):
        for j in range(0, len(sort_list[i])):
            find_name = '''
                            select name
                            from products
                            where pid = ?;
                        '''
            cursor.execute(find_name, (sort_list[i][j],))
            list_name[i].append(cursor.fetchone()[0])
        list_name[i].sort()
        list_name[i].reverse()
    list_name.reverse()
    # show
    list_show = []
    for i in range(0, len(list_name)):
        for j in range(0, len(list_name[i])):
            list_show.append(list_name[i][j])
    show = tuple(list_show)
    search_show(cid, 0, show)
    return

def search_show(cid, pos, show):
    # show the search result
    global connection, cursor

    pid_q = '''select pid from products where name == ?;'''
    num_store_q = '''select count(distinct sid) from carries where pid = ?;'''
    num_stock_q = '''select count(distinct sid) from carries where pid = ? and qty > 0;'''
    mini_price_q = '''select min(uprice) from carries where pid = ?;'''
    mini_stock_q = '''select min(uprice) from carries where pid = ? and qty > 0;'''
    back = False
    while not back:
        pid = []
        table = PrettyTable(["Product id", "Name", "Number of store carry", "Number of store have", "Minimum price", "Minimum price in stock", "Orders in 7 days"])
        for i in range(pos, pos+5):
            if i < len(show):
                cursor.execute(pid_q, (show[i],))
                pid.append(cursor.fetchone()[0])
                cursor.execute(num_store_q, (pid[i%5],))
                num_store = cursor.fetchone()[0]
                cursor.execute(num_stock_q, (pid[i%5],))
                num_stock = cursor.fetchone()[0]
                cursor.execute(mini_price_q, (pid[i%5],))
                mini_price = cursor.fetchone()[0]
                cursor.execute(mini_stock_q, (pid[i%5],))
                mini_stock = cursor.fetchone()[0]
                counts = count_orders(pid[i%5])
                table.add_row([pid[i%5], show[pos + i%5], num_store, num_stock, mini_price, mini_stock, counts])
        print(table)
        if pos <= len(show) - 5:
            print("Show next page enter next.")
        if pos >= 5:
            print("Show previous page enter pre.")
        com = input("Go back enter back. To show product detail enter the Product id. \n")
        if com == "next" and pos <= len(show) - 5:
            pos += 5
        elif com == "pre" and pos >= 5:
            pos -= 5
        elif com == "back":
            back = True
        elif com in pid:
            product_detail(cid, com)
        else:
            print("Wrong commond!")
    return

def product_detail(cid, pid):
    # show the product detail
    global connection, cursor

    table = PrettyTable(["Store id", "Price", "In stock", "Orders history"])
    find_name = '''
                            select name
                            from products
                            where pid = ?;
                        '''
    cursor.execute(find_name, (pid,))
    name = cursor.fetchone()[0]
    cate_q = ''' select c.name from categories c, products p where c.cat = p.cat and pid = ?;'''
    cursor.execute(cate_q, (pid,))
    cate_name = cursor.fetchone()[0]
    print("Product Id: " + pid + "  Name: " + name + "  Category: " + cate_name)

    # get sid

    store_q = '''select uprice, qty from carries where pid = ?;'''
    cursor.execute(store_q, (pid,))
    fetch = cursor.fetchall()
    price = [[],[]]
    for i in range(0, len(fetch)):
        if fetch[i][1] > 0:
            price[0].append(fetch[i][0])
        else:
            price[1].append(fetch[i][0])
    price[0].sort()
    price[1].sort()
    sid_in = '''select sid from carries where uprice = ? and pid = ? and qty > 0;'''
    sid_no = '''select sid from carries where uprice = ? and pid = ? and qty == 0;'''
    sid = []
    news_prices = [[],[]]
    # sort the detail
    for i in range(0,2):
        for j in price[i]:
            if j not in news_prices[i]:
                news_prices[i].append(j)
    for i in range(0, len(news_prices[0])):
        cursor.execute(sid_in, (news_prices[0][i],pid,))
        tem = cursor.fetchall()
        for j in range(0, len(tem)):
            sid.append(tem[j][0])
    for i in range(0, len(news_prices[1])):
        cursor.execute(sid_no, (news_prices[1][i], pid,))
        tem = cursor.fetchall()
        for j in range(0, len(tem)):
            sid.append(tem[j][0])

    # print
    price_q = '''select uprice from carries where sid = ? and pid = ?;'''
    qty_q = '''select qty from carries where sid = ? and pid =?;'''

    for i in range(0, len(sid)):
        cursor.execute(price_q, (sid[i],pid,))
        price = cursor.fetchone()[0]
        cursor.execute(qty_q, (sid[i],pid,))
        pty = cursor.fetchone()[0]
        num = count_orders_store(sid[i], pid)
        table.add_row([sid[i], price, pty, num])

    print(table)
    back = False

    while not back:
        cmd = input("To go back, enter back.\nTo add item to the backet, enter add.  ")
        if cmd == "add":
            while True:
                sid_select = input("Which store you would like select: ")
                if re.match("^[0-9]*$", sid_select):
                    if int(sid_select) in sid:
                        cursor.execute(price_q, (sid_select,pid,))
                        price = cursor.fetchone()[0]
                        add_basket(cid, sid_select, price, pid)
                        return
                    else:
                        print("Wrong sid!")
                else:
                    print("Wrong sid!")
        elif cmd == "back":
            back = True
        else:
            print("Wrong commond!")
    return



def count_orders_store(sid, pid):
    # count the qty
    global connection, cursor
    #cursor.execute('''select ol.qty, ol.oid from olines ol, orders o where ol.pid = ? and date(o.odate, '+7 day') >= date('now') and o.oid = ol.oid''', (pid,))
    cursor.execute('select ol.qty from olines ol, orders o where ol.pid = ? and ol.sid = ? and ol.oid = o.oid and date(o.odate, '+7 day') >= date('now');', (pid,sid,))
    orders = cursor.fetchall()
    num = 0
    for i in range(0, len(orders)):
        num += orders[i][0]
    return num

def add_basket(cid, sid, price, pid):
    # add one pid and sid into the store
    global basket
    back = False
    qty = 1
    while not back:
        cmd = input("Adding success!\nTo continue shopping, enter back.\nTo place order enter order.\nTo update the qty enter qty.  ")
        if cmd == "back":
            basket.append([sid,pid,qty,cid,price])
            return
        elif cmd == "order":
            basket.append([sid,pid,qty,cid,price])
            place_orders(basket)
            basket =[]
            back = True
        elif cmd == "qty":
            qty = input("Pleae update the qty: ")
            while qty < str(1) or not re.match("^[0-9]*$",qty):
                print("Illegal qty.")
                qty = input("Pleae update the qty: ")
        else:
            print("Wrong commond!")
    return

def place_orders(basket):
    global connection,cursor

    cursor.execute('SELECT max(oid) FROM orders;')
    temp = cursor.fetchone()[0]
    if temp == None:
        new_num = 1
    else:
        new_num = temp + 1
    address=input('What is your address? ')
    #create a list for checking how many items can be ordered successfully
    can_order=[]
    #get basket information
    #basket[sid,pid,qty,cid,uprice]
    basket_num = len(basket)
    for i in range (0,basket_num):
        basket_sid=basket[i][0]
        basket_pid=basket[i][1]
        basket_qty=basket[i][2]

        #get qty in store
        cursor.execute('SELECT qty FROM carries WHERE sid=? AND pid=? ;',(basket_sid, basket_pid))
        store_qty=cursor.fetchone()

        #get product name
        cursor.execute('SELECT name FROM products WHERE pid=?;',(basket_pid,))
        pname=cursor.fetchone()
        #check qty of basket
        check=True
        choose = 'C'
        while check:
            if int(basket_qty)<= store_qty[0]:
                check=False
            elif int(basket_qty) > store_qty[0]:
                check=True
                print('The store quantity for '+pname[0]+ ' is '+ str(store_qty[0])+'  but there are '+str(basket_qty)+' in the basket')
                #users choose to change the quantity or delete the item
                choose=input('Input C to change the quantity or input D to delate the product')

                check_input=True
                while check_input:
                    if choose=='C':
                        new_qty=input('Input your new quantity ')
                        if re.match("^[0-9]*$",new_qty):
                            check_input=False
                            if int(new_qty) <= store_qty[0]:
                                check = False
                            new_qty = int(new_qty)
                        else:
                            print('Wrong quantity.')
                        basket[i][2]=new_qty
                    elif choose=='D':
                        check=False
                        check_input = False
                        can_order.append(basket)
                    else:
                        print('Wrong input')
                        choose = input('Input C to change the quantity or input D to delate the product')
                        check_input= True
        if choose != 'D':
            can_order.append(basket[i])
            #get current date for odate
            current_date=time.strftime("%d/%m/%Y")

           #get address


            #create a new oid number

            #place order for the item in new basket
            if len(can_order)>0:
                #orders=[oid,cid,odate,address]
                #olines=[oid,sid,pid,qty,uprice]
                #carries=[sid,pid,qty,uprice]
                #basket[sid,pid,qty,cid,uprice]
                order_oid=new_num
                order_cid=basket[0][3]
                order_odate=current_date
                order_address=address
                order_sid=can_order[i][0]
                order_pid=can_order[i][1]
                order_qty=can_order[i][2]
                order_uprice_q = 'select uprice from carries where sid = ? and pid =?'
                cursor.execute(order_uprice_q, (order_sid, order_pid))
                order_uprice = cursor.fetchone()[0]
                cursor.execute('select max(oid) from orders')
                if cursor.fetchone()[0] < order_oid:
                    cursor.execute('INSERT INTO orders VALUES(?,?,?,?);',(order_oid,order_cid,order_odate,order_address))
                cursor.execute('INSERT INTO olines VALUES(?,?,?,?,?);',(order_oid,int(order_sid),order_pid,order_qty,order_uprice))
                cursor.execute('UPDATE carries SET qty=qty-? WHERE sid=? AND pid=?;',(order_qty,order_sid,order_pid))

            connection.commit()
    basket = []
    connection.commit()
    return


def count_orders(pid):
    # count the qty
    global connection, cursor
    cursor.execute('''select ol.qty, ol.oid from olines ol, orders o where ol.pid = ? and date(o.odate, '+7 day') >= date('now') and o.oid = ol.oid''', (pid,))
    orders = cursor.fetchall()
    num = 0
    for i in range(0, len(orders)):
        num += orders[i][0]
        #######
    return num

def list_order(cid):
    global connection, cursor

    order_cid = cid
    cursor.execute(
        'SELECT DISTINCT orders.oid , orders.odate, count(DISTINCT olines.pid), SUM(olines.qty*olines.uprice) FROM orders, olines WHERE orders.oid=olines.oid and cid=? GROUP BY orders.oid ,orders.odate ORDER BY orders.odate DESC ;',
        (order_cid,))
    order_List = cursor.fetchall()
    order_number = len(order_List)

    # get oid list for print details
    Oid_list = []
    for item in order_List:
        Oid_list.append(item[0])

    # check if the users wants to see orders
    check_needorder = True
    while check_needorder:
        answer_1 = input("Do you want to see the orders ? input Y for yes and N for no:")
        if answer_1 == 'Y':
            check_needorder = False
            # print order list
            print_list(order_number, order_List)
        elif answer_1 == 'N':
            check_needorder = False
        else:
            print('incorrect input')
            check_needorder = True

    # check if the users want to see details of orders
    check_detail = True
    while check_detail:
        answer_2 = input("Do you want to see more details ? input Y for yes and N for no:")
        if answer_2 == 'Y':
            check_detail = True
            # print detail
            print_detail(Oid_list)
        elif answer_2 == 'N':
            check_detail = False
        else:
            print('incorrect input')
            check_detail = True

    connection.commit()
    return


def print_list(order_num, order_list):
    # check the number of orders larger than 5 or not and then print the list
    if order_num <= 5:
        # print the order list
        for i in range(0, order_num):
            print(str(i + 1) + ' | ' + 'oid:' + str(order_list[i][0]) + ' | ' + 'odate: ' + str(
                order_list[i][1]) + ' | ' + 'product_num: ' + str(order_list[i][2]) + ' | ' + 'total_price: ' + str(
                order_list[i][3]))
        print('All of your orders have been printed.')

    elif order_num > 5:
        # print the first 5 orders before the "need more" input
        for k in range(0, 5):
            print(str(k + 1) + ' | ' + 'oid:' + str(order_list[k][0]) + ' | ' + 'odate: ' + str(
                order_list[k][1]) + ' | ' + 'product_num: ' + str(order_list[k][2]) + ' | ' + 'total_price: ' + str(
                order_list[k][3]))
        order_left = order_num - 5
        check_yn = True
        start_index = 0

        # check if the users need to get more orders
        while check_yn:
            answer = input("Do you want to get more orders? input Y to see more or input N to skip this step:")
            if answer == 'Y':
                check_yn = True

                if order_left > 5:

                    start_index += 5
                    for j in range(start_index, 5 + start_index):
                        print(str(j + 1) + ' | ' + 'oid:' + str(order_list[j][0]) + ' | ' + 'odate: ' + str(
                            order_list[j][1]) + ' | ' + 'product_num: ' + str(
                            order_list[j][2]) + ' | ' + 'total_price: ' + str(order_list[j][3]))
                    order_left -= 5
                else:
                    start_index += 5
                    for m in range(start_index, order_num):
                        print(str(m + 1) + ' | ' + 'oid:' + str(order_list[m][0]) + ' | ' + 'odate: ' + str(
                            order_list[m][1]) + ' | ' + 'product_num: ' + str(
                            order_list[m][2]) + ' | ' + 'total_price: ' + str(order_list[m][3]))
                    print('All of your orders have been printed.')
                    check_yn = False

            elif answer == 'N':
                check_yn = False

            else:
                print('incorrect input')
                check_yn = True

    connection.commit()
    return


def print_detail(oid_list):

    check_oid = True
    while check_oid:
        answer_3_str = input("input your oid:")
        answer_3 = int(answer_3_str)
        if answer_3 in oid_list:
            check_oid = False
            detail_list = []
            # olines=[oid,sid,pid,qty,uprice]
            cursor.execute(
                'SELECT o2.sid, o2.pid, o2.qty, o2.uprice FROM olines o2 WHERE o2.oid = ?;', (answer_3,))
            a = cursor.fetchall()
            print(a)
            cursor.execute('select trackingno, pickUpTime, dropOffTime from deliveries where oid = ?', (answer_3,))
            b = cursor.fetchall()
            if b == []:
                detail_list.append('None')
                detail_list.append('None')
                detail_list.append('None')
            else:
                for item in b[0]:
                    detail_list.append(item)
            cursor.execute('select address from orders where oid = ?', (answer_3,))
            detail_list.append(cursor.fetchone()[0])

            for i in range(0, len(a)):
                # print delivery information
                print("oid: " + answer_3_str + ' | ' + "trackingNo: " + str(
                    detail_list[0]) + ' | ' + "pickuptime: " + detail_list[1] + ' | ' + "dropofftime: " +
                      str(detail_list[2]) + ' | ' + "address: " + str(detail_list[3]))

                # print product information
                l_sid = a[i][0]
                cursor.execute('select name from stores where sid = ?;', (l_sid,))
                l_sname = cursor.fetchone()[0]
                l_pid = a[i][1]
                cursor.execute('select name from products where pid =?;', (l_pid,))
                l_pname = cursor.fetchone()[0]
                l_qty = a[i][2]
                cursor.execute('select name from products where pid =?;', (l_pid,))
                l_unit = cursor.fetchone()[0]
                l_uprice = a[i][3]

                # print("sid        "+"store name  "+"pid           "+"product name "+"qty  "+"unit  "+"uprice")

                print("sid: " + str(l_sid) + ' | ' + "sname: " + l_sname + ' | ' + "pid: " + str(
                    l_pid) + ' | ' + "pname: " + l_pname + ' | ' + "qty: " + str(
                    l_qty) + ' | ' + "unit: " + l_unit + ' | ' + "uprice: " + str(l_uprice))
        else:
            check_oid = True

def set_up_delivery():
    global connection, cursor

    # deliveries(trackingno, oid, pickUpTime, dropOffTime)
    # creat a trackingno to deliveries
    # add oid to the delivery
    # add pickUpTime(if no set it to null)
    # set dropOffTime to null
    print('...set_up_delivery...')
    cursor.execute("select MAX(trackingno) from deliveries;")
    maxnumber= cursor.fetchone()[0]
    if maxnumber == None:
        new_trackingno = 1
    else:
        new_trackingno = int(maxnumber) + 1
    check=True
    while check:
        a = input("Do you want to add one delivery order?(y/n)")
        if a == "y":
            check=True

            chek = True
            while chek:
                cursor.execute("select oid from orders")
                tmp = cursor.fetchall()
                oid_list = []
                for i in range(0, len(tmp)):
                    oid_list.append(tmp[i][0])
                for i in range(0, len(oid_list)):
                    oid_list[i] = str(oid_list[i])
                print(oid_list)
                oidno = input('Please input the order id: ')
                if oidno in oid_list:
                    new_pickup = input("'Please input the pick up time: like 'yyyy-mm-dd'")
                    #check the input date is right
                    while len(new_pickup) != 10 or not re.match("^[0-9-]*$", new_pickup):
                        new_pickup = input('Please input the pick up time (yyyy-mm-dd): ')
                    year = new_pickup[:4]
                    mounth = int(new_pickup[5:7])
                    day = int(new_pickup[8:])
                    jump_off = True
                    while jump_off:
                        if int(year) >= 2000 and new_pickup[4] == '-' and new_pickup[7] == '-':
                            if int(mounth) == 1 or int(mounth) == 3 or int(mounth) == 5 or int(mounth) == 7 or int(mounth) == 8 or int(mounth) == 10 or int(mounth) == 12:
                                if int(day) >= 1 and int(day) <=31:
                                    dropofftime='null'
                                    cursor.execute('insert into deliveries values(?,?,?,?);', (new_trackingno, oidno, new_pickup,dropofftime,))
                                    connection.commit()
                                    jump_off = False
                                    chek = False
                                else:
                                    print('Invalid input, the day should between 01 to 31.')
                                    jump_off = False
                                    chek = True
                            elif   int(mounth) == 4 or int(mounth) == 6 or int(mounth) == 9 or int(mounth) == 11:
                                if int(day) >= 1 and int(day) <= 30:
                                    dropofftime='null'
                                    cursor.execute('insert into deliveries values(?,?,?,?);', (new_trackingno, oidno, new_pickup,dropofftime,))
                                    connection.commit()
                                    jump_off = False
                                    chek = False
                                else:
                                    print('Invalid input, the day should between 01 to 30. ')
                                    jump_off = False
                                    chek = True
                            elif int(mounth) == 2:
                                if int(day) >= 1 and int(day) <= 29:
                                    dropofftime='null'
                                    cursor.execute('insert into deliveries values(?,?,?,?);', (new_trackingno, oidno, new_pickup,dropofftime,))
                                    connection.commit()
                                    jump_off = False
                                    chek = False
                                else:
                                    print('Invalid input, the day should between 01 to 29. ')
                                    jump_off = False
                                    chek = True
                            elif int(mounth)>12 or int(mounth)<1:
                                print('The mounth should between 01 and 12')
                                jump_off = False
                                chek = True
                        else:
                            print('Invalid in put or the year should be >= 2000')
                            chek = True
                            jump_off = False
                else:
                    print('The order id is invalid')
                    jump_off = False
                    chek =True
        elif a=='n':
            check=False
        elif (a != 'y') or (a!='n'):
            print("invalid input, please input 'y' or 'n'.")
            check=True
    print('...set_up_delivery...END...')
    return

def update_a_delivery():
    global connection, cursor
    # select trackingno to see oid, pickUpTime, dropOffTime
    print('...update_a_delivery...')
    check2 = True
    while check2:
        cursor.execute('select distinct(trackingno) from deliveries')
        tmp = cursor.fetchall()
        trackingnumber_list = []
        for i in range(0,len(tmp)):
            trackingnumber_list.append(str(tmp[i][0]))
        print(trackingnumber_list)
        trackingnumber = input("Please input a tracking number(trackingno):")
        if trackingnumber in trackingnumber_list:
            cursor.execute('select oid, pickUpTime, dropOffTime from deliveries where trackingno=? ;',(trackingnumber,))
            tep = cursor.fetchall()
            print('  oid      Pickuptime    Dropofftime')
            print (tep)
            check2 =False
        else:
            print('Invalid trackingnumber, please input correct trackingnumber.')
            print(trackingnumber_list)
            check2 =True


    # update pickUpTime
    picup = True
    while picup:
        a = input('do you want change the pick up time?(y/n): ')
        if a == 'y':
            orderid = input('input order id: ')
            cursor.execute("select oid from deliveries where trackingno = ?", (trackingnumber,))
            twp = cursor.fetchall()
            orderid_list = []
            for i in range(0,len(twp)):
                orderid_list.append(str(twp[i][0]))
            if orderid in orderid_list:
                new_pickup = input("'Please input the pick up time: like 'yyyy-mm-dd': ")
                #check update
                while len(new_pickup) != 10 or not re.match("^[0-9-]*$", new_pickup):
                    new_pickup = input('Please input the pick up time (yyyy-mm-dd): ')
                year = new_pickup[:4]
                mounth = int(new_pickup[5:7])
                day = int(new_pickup[8:])
                jump_off = True
                while jump_off:
                    if int(year) >= 2000 and new_pickup[4] == '-' and new_pickup[7] == '-':
                        if int(mounth) == 1 or int(mounth) == 3 or int(mounth) == 5 or int(mounth) == 7 or int(mounth) == 8 or int(mounth) == 10 or int(mounth) == 12:
                            if int(day) >= 1 and int(day) <=31:
                                cursor.execute('update deliveries set pickUpTime = ? where trackingno = ? and oid = ?;', (new_pickup, trackingnumber,orderid,))
                                connection.commit()
                                jump_off = False
                                picup = False
                            else:
                                print('Invalid input, the day should between 01 to 31.')
                                jump_off = False
                                picup = True
                        elif   int(mounth) == 4 or int(mounth) == 6 or int(mounth) == 9 or int(mounth) == 11:
                            if int(day) >= 1 and int(day) <= 30:
                                cursor.execute('update deliveries set pickUpTime = ? where trackingno = ? and oid = ?;', (new_pickup, trackingnumber,orderid,))
                                connection.commit()
                                jump_off = False
                                picup = False
                            else:
                                print('Invalid input, the day should between 01 to 30. ')
                                jump_off = False
                                picup = True
                        elif int(mounth) == 2:
                            if int(day) >= 1 and int(day) <= 29:
                                cursor.execute('update deliveries set pickUpTime = ? where trackingno = ? and oid = ?;', (new_pickup, trackingnumber,orderid,))
                                connection.commit()
                                jump_off = False
                                picup = False
                            else:
                                print('Invalid input, the day should between 01 to 29. ')
                                jump_off = False
                                picup = True
                        elif int(mounth)>12 or int(mounth)<1:
                            print('The mounth should between 01 and 12')
                            jump_off = False
                            picup = True
                    else:
                        print('Invalid input or the year should >= 2000')
                        picup = True
                        jump_off = False
            else:
                print("The order id not in the list")
                picup = True
        elif a == 'n':
            picup=False
        elif (a != 'y') or (a!='no'):
            print("invalid input, please input 'y' or 'n'.")
            picup=True

    #update dropOffTime
    dropof = True
    while dropof:
        dropoff = input('do you want change the drop off time?(y/n):')
        if dropoff == 'y':
            off_orderid = input('input order id: ')
            cursor.execute("select oid from deliveries where trackingno = ?", (trackingnumber,))
            tep = cursor.fetchall()
            off_orderid_list = []
            for i in range(0,len(tep)):
                off_orderid_list.append(str(tep[i][0]))
            if off_orderid in off_orderid_list:
                new_dropoff = input("'Please input the pick up time: like 'yyyy-mm-dd'")
                while len(new_dropoff) != 10 or not re.match("^[0-9-]*$", new_dropoff):
                    new_dropoff = input('Please input the pick up time (yyyy-mm-dd): ')
                year = new_dropoff[:4]
                mounth = int(new_dropoff[5:7])
                day = int(new_dropoff[8:])
                jump_offf = True
                while jump_offf:
                    if int(year) >= 2000 and new_dropoff[4] == '-' and new_dropoff[7] == '-':
                        if int(mounth) == 1 or int(mounth) == 3 or int(mounth) == 5 or int(mounth) == 7 or int(mounth) == 8 or int(mounth) == 10 or int(mounth) == 12:
                            if int(day) >= 1 and int(day) <=31:
                                cursor.execute('update deliveries set dropOffTime = ? where trackingno = ? and oid=? ;', (new_dropoff, trackingnumber,off_orderid,))
                                connection.commit()
                                jump_offf = False
                                dropof = False
                            else:
                                print('Invalid input, the day should between 01 to 31.')
                                jump_offf = False
                                dropof = True
                        elif   int(mounth) == 4 or int(mounth) == 6 or int(mounth) == 9 or int(mounth) == 11:
                            if int(day) >= 1 and int(day) <= 30:
                                cursor.execute('update deliveries set dropOffTime = ? where trackingno = ? and oid=? ;', (new_dropoff, trackingnumber,off_orderid,))
                                connection.commit()
                                jump_offf = False
                                dropof = False
                            else:
                                print('Invalid input, the day should between 01 to 30. ')
                                jump_offf = False
                                dropof = True
                        elif int(mounth) == 2:
                            if int(day) >= 1 and int(day) <= 29:
                                cursor.execute('update deliveries set dropOffTime = ? where trackingno = ? and oid=? ;', (new_dropoff, trackingnumber,off_orderid,))
                                connection.commit()
                                jump_offf = False
                                dropof = False
                            else:
                                print('Invalid input, the day should between 01 to 29. ')
                                jump_offf = False
                                dropof = True
                        elif int(mounth)>12 or int(mounth)<1:
                            print('The mounth should between 01 and 12')
                            jump_offf = False
                            dropof = True
                    else:
                        print('Invalid input or the year should >= 2000')
                        dropof = True
                        jump_offf = False
            else:
                print("Invalid input order id")
                dropof = True
        elif dropoff == 'n':
            dropof = False
        elif (dropoff != 'y') or (dropoff != 'n'):
            print("invalid input, please input 'y' or 'n'.")
            dropof = True

    # delete oid from deliveries
    Delete = True
    while Delete:
        d_oid = input('do you want delete oid from deliveries?(y/n)')
        if d_oid == 'y':
            check32 = True
            while check32:
                cursor.execute('select distinct(trackingno) from deliveries')
                tmp = cursor.fetchall()
                trackingnumber_list1 = []
                for i in range(0,len(tmp)):
                    trackingnumber_list1.append(str(tmp[i][0]))
                print(trackingnumber_list1)
                trackingnumber2 = input("Please input a tracking number(trackingno):")
                if trackingnumber2 in trackingnumber_list1:
                    ##
                    check52 = True
                    while check52:
                        oid2 = input("please input the oid number you want to delete: ")
                        cursor.execute('select oid from deliveries  where trackingno = ?', (trackingnumber2,))
                        tmp1 = cursor.fetchall()
                        oid1 = []
                        for i in range(0,len(tmp1)):
                            oid1.append(str(tmp1[i][0]))
                        if oid2 in oid1:
                            cursor.execute('delete from deliveries where trackingno = ? and oid =? ;', (trackingnumber2, oid2,))
                            connection.commit()
                            check52 =False
                            check32=False
                        else:
                            print('Invalid trackingnumber, please input correct trackingnumber.')
                            print(oid1)
                            check52 =True
                else:
                    print('Invalid trackingnumber, please input correct trackingnumber.')
                    check32 =True
            Delete = False
        elif d_oid == 'n':
            Delete = False
        elif (d_oid != 'y') or (d_oid != 'n'):
            print("invalid input, please input 'y' or 'n'.")
            Delete = True
    print('...update_a_delivery...END...')
    return

def add_to_stock():
    global connection, cursor

    # add quantity to carries(sid, pid, qty, uprice) by giving sid and pid.
    # ask if agent want to change the unitprice(uprice).

    print("...add_to_stock...")

    #check pid in the querry
    check_pid = True
    while check_pid:
        cursor.execute("select pid from products")
        tmp = cursor.fetchall()
        pid_list = []
        for i in range(0,len(tmp)):
            pid_list.append(tmp[i][0])
        for i in range(0, len(pid_list)):
            pid_list[i] = str(pid_list[i])
        print(pid_list)
        pid = input("please input the product id like 'xxxxxx',the product id are above:")
        if pid in pid_list:
            check_sid = True
            while check_sid:

                cursor.execute('select s.sid from stores s, carries c where c.sid = s.sid and c.pid =?;', (pid,))
                tap = cursor.fetchall()
                sid_list=[]
                for i in range(0,len(tap)):
                    sid_list.append(str(tap[i][0]))

                print(sid_list)
                ssid = input('please input the store id:')
                if ssid in sid_list:
                    quantity = input('please input the number of products:')
                    rematch = re.match("^[0-9-]*$", quantity)
                    if not rematch:
                        rematch = False
                        check_pid = True
                        print('Invalid input')
                    while rematch:
                        print('updating data...')
                        cursor.execute('select qty from carries where pid = ? and sid = ?', (pid,ssid,))
                        new_quantityy = cursor.fetchone()
                        if new_quantityy == None :
                            print("there is no such pair")
                            check_sid = True
                            rematch = False
                        else:
                            new_quantityy = new_quantityy[0]
                            print("update ")
                            new_quantity = int(new_quantityy) + int(quantity)
                            cursor.execute('update carries set qty = ? where pid =? and sid =?;', (new_quantity, pid, ssid,))
                            connection.commit()
                            rematch = False
                            check_pid = False
                            check_sid = False

                else:
                    print('Invalid input, please input correct store id.')
                    check_sid = True
        else:
            print('Invalid input, please input correct product id.')
            check_pid = True

    #ask agent to change the unit price
    checking_unit_price = True
    while checking_unit_price:
        question = input('Do you want to change the unit price?(y/n)')
        if question == 'y':
            float_number = str(input ('please input the price:'))
            check_unit_price = re.compile(r'^[-+]?[0-9]+\.[0-9]+$')
            result = check_unit_price.match(float_number)
            if result:
                cursor.execute('update carries set uprice = ? where pid =? and sid =?;',(float_number,pid,ssid,))
                connection.commit()
                checking_unit_price = False
            else:
                print('Invalid input, please input the folat number and this is input format: 999.99')
                checking_unit_price = True
        elif question == 'n':
            checking_unit_price = False
        elif (question != 'y') or (question != 'n'):
            print("Invalid input, please input 'y' or 'n'. ")
            checking_unit_price = True
    print("...add_to_stock...END...")

    return

def define_tables():
    # creat table for the database
    global connection, cursor
    create_table = []
    create_table.append('''drop table if exists deliveries;''')
    create_table.append('''drop table if exists olines;''')
    create_table.append('''drop table if exists orders;''')
    create_table.append('''drop table if exists customers;''')
    create_table.append('''drop table if exists carries;''')
    create_table.append('''drop table if exists products;''')
    create_table.append('''drop table if exists categories;''')
    create_table.append('''drop table if exists stores;''')
    create_table.append('''drop table if exists agents;''')

    create_table.append('''
    create table agents (
      aid text,
      name text,
      pwd text,
      primary key (aid));
    ''')

    create_table.append('''
    create table stores (
      sid int,
      name text,
      phone text,
      address        text,
      primary key (sid));
    ''')

    create_table.append('''
    create table categories (
      cat char(3),
      name text,
      primary key (cat));
    ''')

    create_table.append('''
    create table products (
      pid char(6),
      name text,
      unit text,
      cat char(3),
      primary key (pid),
      foreign key (cat) references categories);
    ''')

    create_table.append('''
    create table carries (
      sid int,
      pid char(6),
      qty int,
      uprice real,
      primary key (sid,pid),
      foreign key (sid) references stores,
      foreign key (pid) references products);
    ''')

    create_table.append('''
    create table customers (
      cid text,
      name text,
      address text,
      pwd text,
      primary key (cid));
    ''')

    create_table.append('''
    create table orders (
      oid int,
      cid text,
      odate date,
      address text,
      primary key (oid),
      foreign key (cid) references customers);
    ''')

    create_table.append('''
    create table olines (
      oid int,
      sid int,
      pid char(6),
      qty int,
      uprice real,
      primary key (oid,sid,pid),
      foreign key (oid) references orders,
      foreign key (sid) references stores,
      foreign key (pid) references products);
    ''')

    create_table.append('''
    create table deliveries (
      trackingNo int,
      oid int,
      pickUpTime date,
      dropOffTime date,
      primary key (trackingNo,oid),
      foreign key (oid) references orders);
    ''')

    for item in create_table:
            cursor.execute(item)
    connection.commit()

    return

def insert_data():
    # insert data to the database
    global connection, cursor

    insert_customer = '''
                          Insert into customers(cid, name, address, pwd) VALUES
                                  ('admin', 'Tom', '6452 24 ave', '123456'),
                                  ('jack233', 'Jack', '10233 83 ave', 'jack332233'),
                                  ('987654', 'Lily', '1792 97 street','lily987654'),
                                  ('a', 'Aline', 'Winterhold', 'theelder');
                      '''

    insert_deliveries = '''
                           insert into deliveries(trackingno, oid, pickUpTime, dropOffTime) VALUES
                                   (123100, 100, '2017-02-20', '2017-06-20'),
                                   (123101, 101, '2017-04-20', '2017-04-29'),
                                   (123102, 102, '2017-05-30', '2017-08-01'),
                                   (123103,103,'2017-02-19','2017-09-08'),
                                   (123104,104,'2017-02-11','2017-09-08'),
                                   (123105,105,'2017-02-12','2017-09-02'),
                                   (123106,106,'2017-02-19','2017-09-08'),
                                   (123107,107,'2017-02-20','2017-09-06'),
                                   (123108,108,'2017-02-19','2017-09-11'),
                                   (123109,109,'2017-02-26','2017-09-01'),
                                   (123110,110,'2017-02-12','2017-09-12'),
                                   (123111,111,'2017-02-12','2017-09-04'),
                                   (123112,112,'2017-02-19','2017-09-11'),
                                   (100001,113,'2017-02-11','2017-09-14'),
                                   (100001,114,'2017-02-13','2017-09-15'),
                                   (100001,115,'2017-02-17','2017-09-19'),
                                   (100001,116,'2017-02-11','2017-09-13'),
                                   (100001,117,'2017-02-11','2017-09-14'),
                                   (100001,118,'2017-02-16','2017-09-18'),
                                   (100001,119,'2017-02-17','2017-09-21'),
                                   (100001,120,'2017-02-14','2017-09-15'),
                                   (100001,121,'2017-02-15','2017-09-19'),
                                   (100001,122,'2017-02-18','2017-09-19'),
                                   (100001,123,'2017-02-11','2017-09-16'),
                                   (100001,124,'2017-02-15','2017-09-19'),
                                   (100001,125,'2017-02-11','2017-09-14'),
                                   (987654,126,'2017-09-11','2017-10-14'),
                                   (987654,127,'2017-09-17','2017-10-19');
                        '''

    insert_agent = '''
                       insert into agents(aid, name, pwd) VALUES
                               ('Alibaba', 'Yun Ma', 'mywcnym'),
                               ('JD', 'QD Liu', '123456');
                   '''
    insert_products = '''
                          insert into products(pid, name, unit, cat) VALUES
                                ('163292', 'Mario Kart 8 Deluxe - NS', '1', 'gam'),
                                ('150949', 'Splatoon 2 - NS', '1', 'gam'),
                                ('163211', 'The Legend of Zelda: BOW - NS', '1', 'gam'),
                                ('163205', 'Super Mario Odyssey - NS', '1', 'gam'),
                                ('692019', 'Assassins Creed Orignins - Xbox', '1', 'gam'),
                                ('736823', 'Forza Horizon 3 - Xbox', '1', 'gam'),
                                ('726913', 'NHL 18 - Xbox', '1', 'gam'),
                                ('729383', 'Call of Duty WW2 - Xbox', '1', 'gam'),
                                ('076457', 'Horizon Zero Dawn - PS4', '1', 'gam'),
                                ('645858', 'Assassins Creed Orignins - PS4', '1', 'gam'),
                                ('167654', 'FIFA 18 - NS', '1', 'gam'),
                                ('009345', 'The Last of Us Remastered - PS4', '1', 'gam'),
                                ('031232', 'NHL 18 - PS4', '1', 'gam'),
                                ('032344', 'Call of Duty WW2 - PS4', '1', 'gam'),
                                ('021214', 'FIFA 18 - PS4', '1', 'gam');
                      '''

    insert_carries = '''
                         insert into carries(sid, pid, qty, uprice) VALUES
                                (100001, '163292', 8, 79.99),
                                (100001, '150949', 2, 79.98),
                                (100001, '163211', 3, 68.88),
                                (100001, '163205', 8, 92.96),
                                (100001, '692019', 1, 83.79),
                                (100001, '736823', 5, 79.99),
                                (100001, '726913', 6, 79.98),
                                (100001, '729383', 9, 79.99),
                                (100001, '076457', 3, 78.92),
                                (100001, '167654', 4, 69.99),
                                (100001, '009345', 6, 86.82),
                                (100001, '031232', 0, 45.89),
                                (100001, '032344', 1, 72.81),
                                (100001, '021214', 4, 79.99),
                                (100002, '163292', 2, 72.82),
                                (100002, '150949', 8, 79.99),
                                (100002, '163211', 8, 79.99),
                                (100002, '163205', 3, 72.99),
                                (100002, '692019', 1, 79.99),
                                (100002, '736823', 0, 71.99),
                                (100002, '726913', 7, 71.99),
                                (100002, '729383', 6, 69.89),
                                (100002, '076457', 3, 79.89),
                                (100002, '167654', 4, 79.89),
                                (100002, '009345', 2, 79.99),
                                (100002, '031232', 9, 62.99),
                                (100002, '032344', 7, 79.99),
                                (100002, '021214', 4, 75.99),
                                (100003, '163292', 4, 79.99),
                                (100003, '150949', 3, 72.02),
                                (100003, '163211', 1, 73.79),
                                (100003, '163205', 2, 79.98),
                                (100003, '692019', 7, 79.89),
                                (100003, '736823', 9, 79.99),
                                (100003, '726913', 6, 72.34),
                                (100003, '729383', 4, 74.33),
                                (100003, '076457', 3, 79.99),
                                (100003, '167654', 4, 69.99),
                                (100003, '009345', 2, 68.99),
                                (100003, '031232', 2, 79.99),
                                (100003, '032344', 5, 79.99),
                                (100003, '021214', 0, 30.99),
                                (100006, '163292', 4, 79.99),
                                (100006, '150949', 3, 79.99),
                                (100006, '163211', 0, 79.98),
                                (100006, '692019', 2, 79.99),
                                (100006, '736823', 1, 79.99),
                                (100006, '726913', 4, 69.98),
                                (100006, '729383', 2, 59.99),
                                (100006, '076457', 4, 79.99),
                                (100006, '031232', 1, 79.99),
                                (100006, '032344', 2, 79.99),
                                (100006, '021214', 3, 79.99),
                                (100007, '163292', 4, 79.99),
                                (100007, '163211', 1, 79.99),
                                (100007, '163205', 3, 79.99),
                                (100007, '692019', 0, 69.99),
                                (100007, '736823', 2, 79.99),
                                (100007, '726913', 6, 74.98),
                                (100007, '076457', 1, 79.99),
                                (100007, '167654', 2, 79.99),
                                (100007, '021214', 5, 79.99),
                                (100008, '163292', 2, 62.02),
                                (100008, '150949', 3, 63.41),
                                (100008, '163211', 1, 79.99),
                                (100008, '163205', 4, 62.89),
                                (100008, '692019', 1, 79.99),
                                (100008, '736823', 2, 79.99),
                                (100008, '726913', 3, 79.99),
                                (100008, '729383', 6, 79.99),
                                (100008, '076457', 7, 79.99),
                                (100008, '167654', 3, 72.31),
                                (100008, '009345', 3, 79.99),
                                (100008, '031232', 1, 79.99),
                                (100008, '032344', 0, 74.65),
                                (100008, '021214', 6, 79.99),
                                (100009, '163292', 2, 79.99),
                                (100009, '150949', 3, 79.99),
                                (100009, '163211', 1, 79.99),
                                (100009, '163205', 4, 25.96),
                                (100009, '692019', 1, 34.45),
                                (100009, '736823', 2, 79.99),
                                (100009, '726913', 3, 67.89),
                                (100009, '729383', 6, 79.99),
                                (100009, '076457', 7, 79.99),
                                (100009, '167654', 3, 79.99),
                                (100009, '009345', 3, 96.8),
                                (100009, '031232', 1, 79.99),
                                (100009, '032344', 0, 79.99),
                                (100009, '021214', 6, 79.99),
                                (100010, '163292', 8, 79.99),
                                (100010, '150949', 2, 78.89),
                                (100010, '163211', 3, 37.0),
                                (100010, '163205', 8, 79.99),
                                (100010, '692019', 1, 66.2),
                                (100010, '009345', 6, 79.99),
                                (100010, '031232', 0, 72.98),
                                (100020, '163292', 12, 72.98),
                                (100020, '150949', 20, 79.99),
                                (100020, '163211', 12, 71.86),
                                (100020, '163205', 30, 68.79),
                                (100020, '692019', 12, 79.99),
                                (100020, '736823', 11, 79.99),
                                (100020, '726913', 9, 55.6),
                                (100020, '729383', 8, 79.99),
                                (100020, '076457', 21, 79.99),
                                (100020, '167654', 7, 34.99),
                                (100020, '009345', 31, 79.99),
                                (100020, '031232', 9, 34.99),
                                (100020, '032344', 18, 79.99),
                                (100020, '021214', 17, 79.99),
                                (100011, '163292', 9, 32.79),
                                (100011, '150949', 2, 79.99),
                                (100011, '163211', 1, 29.99),
                                (100011, '163205', 0, 29.99),
                                (100011, '692019', 2, 79.99),
                                (100011, '167654', 7, 79.99),
                                (100011, '009345', 3, 79.99),
                                (100011, '031232', 9, 79.99),
                                (100012, '150949', 2, 79.89),
                                (100012, '163211', 2, 69.98),
                                (100012, '163205', 3, 79.99),
                                (100012, '692019', 2, 79.99),
                                (100012, '009345', 3, 32.79),
                                (100012, '031232', 9, 79.99),
                                (100012, '032344', 8, 79.99),
                                (100012, '021214', 7, 79.99);
                    '''

    insert_stores = '''
                         insert into stores(sid, name, phone, address) VALUES
                                (100001, 'EB Games - WEM', 'a','a'),
                                (100003, 'Eb Games - Kw', 'a', 'a'),
                                (100002, 'EB Games - SG', 'a', 'a'),
                                (100006, 'Walmart - South', 'a', 'a'),
                                (100007, 'Walmart - Nouth', 'a', 'a'),
                                (100008, 'Walmart - East', 'a', 'a'),
                                (100009, 'Walmart - Center', 'a', 'a'),
                                (100010, 'Toysrus - Jasper', 'a', 'a'),
                                (100011, 'Toysrus - Jack', 'a', 'a'),
                                (100012, 'Toysrus - Nouth', 'a', 'a'),
                                (100020, 'Amazon.ca', 'a', 'a');
                    '''

    insert_category = '''
                            insert into categories(cat, name) VALUES
                                    ('gam', 'Game');
                      '''

    insert_olines  = '''
                        insert into olines(oid, sid, pid, qty, uprice) VALUES
                              (100,100001, '163292', 3, 79.99),
                              (100,100002, '163205', 1, 72.99),
                              (100,100001, '163211', 1, 68.88),
                              (101,100002, '729383', 2, 69.89),
                              (101,100001, '692019', 1, 83.79),
                              (102,100001, '736823', 3, 79.99),
                              (102,100001, '726913', 4, 79.98),
                              (103,100001, '729383', 7, 79.99),
                              (104,100002, '163211', 4, 79.99),
                              (104,100002, '163205', 2, 72.99),
                              (105,100003, '163292', 1, 79.99),
                              (106,100003, '163292', 2, 79.99),
                              (107,100007, '163211', 1, 79.99),
                              (107,100001, '729383', 2, 79.99),
                              (107,100002, '150949', 4, 79.99),
                              (108,100008, '729383', 2, 79.99),
                              (109,100009, '163205', 4, 25.96),
                              (110,100007, '163205', 3, 79.99),
                              (110,100008, '736823', 1, 79.99),
                              (111,100010, '163292', 2, 79.99),
                              (112,100020, '150949', 10, 79.99),
                              (113,100006, '150949', 2, 79.99),
                              (114,100009, '163211', 1, 79.99),
                              (114,100007, '076457', 1, 79.99),
                              (115,100010, '163205', 2, 79.99),
                              (116,100012, '021214', 7, 79.99),
                              (117,100012, '031232', 2, 79.99),
                              (117,100011, '150949', 1, 79.99),
                              (118,100012, '163211', 1, 69.98),
                              (119,100006, '163292', 1, 79.99),
                              (119,100012, '031232', 2, 79.99),
                              (120,100006, '726913', 4, 69.98),
                              (121,100009, '150949', 1, 79.99),
                              (122,100012, '009345', 3, 32.79),
                              (122,100001, '729383', 1, 79.99),
                              (122,100001, '009345', 4, 86.82),
                              (123,100008, '076457', 3, 79.99),
                              (124,100009, '150949', 1, 79.99),
                              (125,100003, '167654', 3, 69.99),
                              (125,100001, '009345', 1, 86.82),
                              (126,100001, '163292', 4, 79.99),
                              (127,100001, '163292', 3, 79.99),
                              (128,100001, '150949', 2, 79.98);

                    '''
    insert_orders ='''
                      insert into orders(oid, cid, odate, address) VALUES
                            (100,'admin',"2017-10-01",'100 ave'),
                            (101,'admin',"2017-10-02",'101 ave'),
                            (102,'admin',"2017-10-03",'100 ave'),
                            (103,'admin',"2017-10-04",'101 ave'),
                            (104,'admin',"2017-10-01",'100 ave'),
                            (105,'admin',"2017-10-02",'101 ave'),
                            (106,'admin',"2017-10-03",'100 ave'),
                            (107,'admin',"2017-10-04",'101 ave'),
                            (108,'admin',"2017-10-01",'100 ave'),
                            (109,'admin',"2017-10-02",'101 ave'),
                            (110,'admin',"2017-10-03",'100 ave'),
                            (111,'admin',"2017-10-04",'101 ave'),
                            (112,'admin',"2017-10-01",'100 ave'),
                            (113,'a',"2017-10-01",'1001 ave'),
                            (114,'a',"2017-10-02",'1011 ave'),
                            (115,'a',"2017-10-03",'1001 ave'),
                            (116,'a',"2017-10-04",'1011 ave'),
                            (117,'a',"2017-10-01",'1001 ave'),
                            (118,'a',"2017-10-02",'1011 ave'),
                            (119,'a',"2017-10-03",'1001 ave'),
                            (120,'a',"2017-10-04",'1011 ave'),
                            (121,'a',"2017-10-01",'1001 ave'),
                            (122,'a',"2017-10-02",'1011 ave'),
                            (123,'a',"2017-10-03",'1001 ave'),
                            (124,'a',"2017-10-04",'1011 ave'),
                            (125,'a',"2017-10-01",'1001 ave'),
                            (126,'a',"2017-11-04",'1001 ave'),
                            (127,'a',"2017-10-30",'1001 ave'),
                            (128,'a',"2017-10-29",'1001 ave');
                   '''


    cursor.execute(insert_customer)
    cursor.execute(insert_deliveries)
    cursor.execute(insert_agent)
    cursor.execute(insert_products)
    cursor.execute(insert_carries)
    cursor.execute(insert_stores)
    cursor.execute(insert_category)
    cursor.execute(insert_orders)
    cursor.execute(insert_olines)
    connection.commit()
    return

def connect(path):
    global connection, cursor

    connection = sqlite3.connect(path)
    cursor = connection.cursor()
    cursor.execute(' PRAGMA forteign_keys=ON; ')
    connection.commit()
    return

if __name__ == "__main__":
    main()
