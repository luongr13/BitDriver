import csv


# Read dQBCustomerInfo.csv and put data
# into a dictionary to access QBCustomerName_Actual
#
# [0] = Short Name
# [3] = QB Customer Name Actual
#
def readCustomerInfo(dictionary, filename):
    """
    :type dictionary: Dictionary[str]
    :type filename: str
    """
    with open(filename, mode='r', encoding='cp1252') as infile:
        csv_file = csv.reader(infile)
        for line in csv_file:
            # key = shortname
            # value = actual_name
            dictionary[line[0]] = line[3]   


# Read the spreadsheet containing
# pulls to consolidate any pulls and returns
# and store into a dictionary.
#
# ie. Pulling a qty of 3 and returning 1 is equivalent
# to just pulling a qty of 2.
#
def readSpreadsheet(spreadsheet_db, filename):
    """
    :type dictionary: Dictionary[str]
    :type filename: str
    """
    with open(filename, mode='r', newline='') as csvfile:
        qty_map = {}
        reader = csv.reader(csvfile)
        for row in reader:
            row[1] = formatDate(row[1])
            row[2] = row[2].split('-')[0]
            key = row[2]
            value = row

            if key in spreadsheet_db:
                qty = int(spreadsheet_db[key][6]) + int(row[6])
                row[6] = str(qty)

            spreadsheet_db[key] = row

            if int(spreadsheet_db[key][6]) == 0:
                del spreadsheet_db[key]


# Write consolidated pulls to a separate
# csv file.
#
def writeCSV(dictionary, filename):
    """
    :type dictionary: Dictionary[str]
    :type filename: str
    """
    with open(filename, mode='w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        for key in dictionary:
            writer.writerow(dictionary[key])


# Get a list for Bits fields in
# the following format:
#
# [0] = Parent Company
# [1] = Facility Name
# [2] = Date
# [3] = Ticket Number
# [4] = Requestor
# [5] = Approver
# [6] = Quantity
def getBitsData(pull_lst, customer_info):
    """
    :type pull_lst: List[str]
    :type customer_info: Dictionary[str]
    :rtype: List[str]
    """
    short_name = pull_lst[3]
    actual_name = customer_info[short_name]
    i = actual_name.rfind(":")
    
    if i != -1:
        parent = actual_name[0:i]
        facility = actual_name[i+1:].replace(',', '')
    else:
        parent = actual_name
        facility = parent

    date = pull_lst[1]
    ticket = pull_lst[2]
    requestor = getRequestor(pull_lst[4])
    approver = getApprover(pull_lst[4])
    qty = pull_lst[6]

    return [parent, facility, date, ticket, requestor, approver, qty]


# Date field requires a specific format where
# month needs prepended '0' if month can be
# represented with a single digit
#
def formatDate(date):
    """
    :type dictionary: Dictionary[str]
    :type filename: str
    """
    date = date.split('/')
    if (len(date[0]) < 2):
        date[0] = '0' + date[0]
    if (len(date[1]) < 2):
        date[1] = '0' + date[1]
        
    return "/".join(date)


# Get the Approver for the pull request
#
def getApprover(string):
    """
    :rtype: str
    """
    return string.split(":")[0].strip()


# Get the requestor for the pull request
#
def getRequestor(string):
    """
    :rtype: str
    """
    lst = string.split(":")
    requestor = ""
    if len(lst) > 1:
        requestor = lst[1]
        
    return requestor


if __name__ == "__main__":
    customer_db = {}
    spreadsheet_db = {}
    
    readCustomerInfo(customer_db, 'CustomerInfo.csv')
    readSpreadsheet(spreadsheet_db, 'Spreadsheet.csv')

    lst1 = getBitsData(spreadsheet_db['1102315'], customer_db)
    lst2 = getBitsData(spreadsheet_db['1092510'], customer_db)
    print(lst1)
    print(lst2)
