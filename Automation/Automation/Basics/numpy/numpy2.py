# Find Maximum

# Find Minimum

# Find Sum

# Find Average


import numpy as np

marks = np.array([85, 92, 78, 95, 88])
#find the maximum
print(np.max(marks))
#find the minimum
print(np.min(marks))
#find the sum
print(np.sum(marks))
#find the average
print(np.mean(marks))
#find the position of the maximum number in the list
print(np.argmax(marks))
#find the position of the minimum number in the list
print(np.argmin(marks))

'''
🧠 The easiest way to remember.
Function	    Meaning
max()	        Maximum value
argmax()	    Index of maximum value
min()	        Minimum value
argmin()	    Index of minimum value
'''