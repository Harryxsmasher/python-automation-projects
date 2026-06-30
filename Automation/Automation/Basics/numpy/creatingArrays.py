
# Create an Array
import numpy as np

marks = np.array([85,97,85,42,58,96,65])

print(marks)



# Concept 2 - Array Attribute
# <class 'numpy.ndarray'>
# nd means Non-Dimensional Array
print(type(marks))

# means one line and one dimension
print(marks.ndim)

#meaning how many elements in the array
print(marks.shape)

#meaning exactly how many elements in the array
print(marks.size)

# int64
# Meaning every element in the array are integer
print(marks.dtype)

# Concept 3 - Indexing

print(marks[0])
print(marks[-1])

#Concept 4 - Slicing
print(marks[1:4])

