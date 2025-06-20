
# Configuration for participants

import csv

# you can define it in external csv file in simple format, row by row (fields are comma separated):
# ip_address1,participant_name1
# ip_address2,participant_name2

# Please note, name of participants can't contain the '-'

participants_list="conf/participants.csv"

participants = dict()

with open(participants_list, newline='') as csvfile:
    reader = csv.DictReader(csvfile,['IP','NAME'])
    for row in reader:
        if row['IP'] is not None and row['NAME'] is not None:
            participants.update({row['IP']:row['NAME']})

# OR you can still define dict of participants here below

# here you define the same set of participants
# but order of declaration is important
# the only name of participant has a matter, other parameters are just for
# decoration purpose

participants.update( {
'10.100.100.10':'MME'
,'10.100.10.101':'SGW'
,'10.100.10.100':'PGWC'
,'1.1.1.3':'PGWC'
,'1.1.1.2':'PGWU'

    ,'1.1.1.1':'TAS'
    ,'2.2.2.2':'CSCF'
# for example, one logical DRA has two instances
    ,'3.3.3.3':'DRA'
    ,'4.4.4.4':'DRA'
# GT
    ,'79111111111':'MSS'
    ,'79222222222':'OCS'
    ,'79333333333':'HLR'
# TAS GT in addition to it's IP
    ,'79444444444':'TAS'

})

if __name__ == "__main__":
    print ("participants:")
    print ("\n".join(map(lambda item: f"{item[0]},{item[1]}", participants.items())))
