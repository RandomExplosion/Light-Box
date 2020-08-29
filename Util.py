import sys      #For console printing
"""
    This file exists to prevent circular imports of the below function(s) and/or Class(es)
"""
#print to console and flush output stream
def printfl(string):
    """Print to console and flush output stream so text is visible"""
    print(string)       #Print
    sys.stdout.flush()  #Flush