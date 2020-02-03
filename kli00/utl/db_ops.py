import sqlite3
from datetime import datetime #for timestamp - that will be how story updates are sorted.

DB_FILE = "discobandit.db"

def accountExists(user):
    db = sqlite3.connect(DB_FILE) #open if file exists, otherwise create
    c = db.cursor()               #facilitate db ops

    #==========================================================

    c.execute(
    """
        SELECT * FROM accounts WHERE username = (?)
    """, (user,)
    )

    rowCount = 0
    for row in c:
        rowCount += 1

    #==========================================================

    db.close()  #close database

    if (rowCount == 1):
        return True

    return False

# function to takes in a username and password and creates a new user entry
def addAccount(user, pw):
    db = sqlite3.connect(DB_FILE) #open if file exists, otherwise create
    c = db.cursor()               #facilitate db ops

    #==========================================================

    c.execute("INSERT INTO accounts VALUES (?, ?)", (user, pw))

    #==========================================================

    db.commit() #save changes
    db.close()  #close database

# function that authenticates the username and password arguments to verify that the account exists
def authenticate(user, pw):
    db = sqlite3.connect(DB_FILE) #open if file exists, otherwise create
    c = db.cursor()               #facilitate db ops

    #==========================================================

    c.execute(
    """
        SELECT * FROM accounts WHERE username = (?)
    """, (user,)
    )

    rowCount = 0
    for row in c:
        db.close() #only one iteration should happen anyway so I can close it right now
        rowCount += 1
        if (rowCount != 1):
            return False

        return pw == row[1]

# function that returns a 2d array of stories, with each subarray containing the title, content, and author
def viewStories():
    db = sqlite3.connect(DB_FILE) #open if file exists, otherwise create
    c = db.cursor()               #facilitate db ops

    #==========================================================

    #Gets a list of titles; to be used in next loop
    titles = []
    c.execute("SELECT * FROM stories")
    for row in c:
        titles.append(row[0])

    latestUpdates = []
    for title in titles:
        c.execute(
        """
            SELECT * FROM storyUpdates
            WHERE title = (?)
            ORDER BY timestamp DESC
        """, (title,)
        )

        update = c.fetchone() #fetches the latest update of this specific story (possible because c is ordered by timestamp in descending order)
        arr = []
        arr.append(str(update[0])) #title
        arr.append(str(update[1])) #content
        arr.append(str(update[2])) #author
        latestUpdates.append(arr) #yes, that's a 2D list

    db.close()  #close database
    return latestUpdates #returns a 2D list

def fetchContributedToStories(user):
    db = sqlite3.connect(DB_FILE) #open if file exists, otherwise create
    c = db.cursor()               #facilitate db ops

    #==========================================================

    #Gets a list of titles, or stories contributed to; to be used in next loop
    titles = []
    c.execute(
    """
        SELECT * FROM storyUpdates
        WHERE user = (?)
        GROUP BY title
        ORDER BY title DESC
    """, (user,)
    )

    for row in c:
        titles.append(str(row[0])) #title

    stories = {}
    for title in titles:
        c.execute(
        """
            SELECT * FROM storyUpdates
            WHERE title = (?)
            ORDER BY timestamp ASC
        """, (title,)
        ) #We actually want the earlier updates to be in front, so c is ordered by timestamp but in ascending order this time.

        updates = [] #array of updates for a story
        for update in c:
            updates.append(str(update[1])) #content

        stories[title] = updates #key: title, value: updates array

    db.close()  #close database
    return stories #returns a dictionary

def storyExists(title):
    db = sqlite3.connect(DB_FILE) #open if file exists, otherwise create
    c = db.cursor()               #facilitate db ops

    #==========================================================

    c.execute(
    """
        SELECT * FROM stories WHERE title = (?)
    """, (title,)
    )

    rowCount = 0
    for row in c:
        rowCount += 1

    #==========================================================

    db.close()  #close database

    if (rowCount == 1):
        return True

    return False

def addStory(title, creator, update):
    db = sqlite3.connect(DB_FILE) #open if file exists, otherwise create
    c = db.cursor()               #facilitate db ops

    #==========================================================

    c.execute("INSERT INTO stories VALUES (?, ?)", (title, creator))

    #Counting the initial creation of a story as the first "update"
    c.execute("INSERT INTO storyUpdates VALUES(?, ?, ?, ?)", (title, update, creator, datetime.now())) #datetime.now --> timestamp

    #==========================================================

    db.commit() #save changes
    db.close()  #close database

def addStoryUpdate(title, addition, user):
    db = sqlite3.connect(DB_FILE) #open if file exists, otherwise create
    c = db.cursor()               #facilitate db ops

    #==========================================================

    c.execute("INSERT INTO storyUpdates VALUES (?, ?, ?, ?)", (title, addition, user, datetime.now()))

    #==========================================================

    db.commit() #save changes
    db.close()  #close database

#For the stories page and when editing a story
def fetchLatestUpdate(title):
    db = sqlite3.connect(DB_FILE) #open if file exists, otherwise create
    c = db.cursor()               #facilitate db ops

    #==========================================================

    c.execute(
    """
        SELECT * FROM storyUpdates
        WHERE title = (?)
        ORDER BY timestamp DESC
    """, (title,)
    )

    update = c.fetchone() #fetch the latest update in c
    db.close()  #close database
    return update

def searchStories(searchValue):
    stories = viewStories()
    # compare each title with search value and sort by edit distance
    levenshteinDistances = {}
    for el in stories:
        levenshteinDistances[levenshteinDist(str(searchValue), str(el[0]))] = el
        print(el[0] + ": " + str(levenshteinDist(str(searchValue), str(el[0]))))
    sortedStories = [value for (key, value) in sorted(levenshteinDistances.items())]
    #sortedBySearchTitles = [value for (key, value) in sorted(levenshteinDistances.items())]
    # print(sortedStories)
    # print(levenshteinDistances)
    # print(searchValue)
    return sortedStories
    
# dynamic programming implementation of edit distance
def levenshteinDist(str1, str2): 
    m = len(str1)
    n = len(str2)
    # 2d array (m by n matrix) to store subproblems 
    dp = [[0 for x in range(n+1)] for x in range(m+1)] 
  
    # Fill dp[][] in bottom up manner 
    for i in range(m+1): 
        for j in range(n+1): 
  
            # If first string is empty, insert all characters of second string 
            if i == 0: 
                dp[i][j] = j    # Minimum # of operations = j 
  
            # If second string is empty, remove all characters of second string 
            elif j == 0: 
                dp[i][j] = i    # Minimum # of operations = i 
  
            # If last characters are same, ignore last char and recurse for remaining string 
            elif str1[i-1] == str2[j-1]: 
                dp[i][j] = dp[i-1][j-1] 
  
            # If last character are different, consider all possibilities and find minimum 
            else: 
                dp[i][j] = 1 + min(dp[i][j-1],        # Insert 
                                   dp[i-1][j],        # Remove 
                                   dp[i-1][j-1])      # Replace 
  
    return dp[m][n] 