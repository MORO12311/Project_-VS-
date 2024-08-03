thistuple = tuple(("apple", "banana", "cherry")) # note the double round-brackets
thistuple = ("apple", "banana", "cherry") 
# print(thistuple[::])
str = ("I Love Python")
# print(str.split())
# print(str.index("H")) # error 
# print(str.find("H")) # not error --> -1 
x=""" Hello 'sadasas' "sadasd"
World
Omar
"""
# print(x.split())
# print(x.count("s"))
# print(x.startswith("h")) # Case sensitive


thisList=["apple","Orange ","banana"]
thisList[0:2]=["Omar"]
# print(thisList)


list=[10,-9,88,0,1,2]
# list.sort(reverse=False) #Rearrange list as normal
# list.sort(reverse=True) #Rearrange list as nonnormal
# print(list.pop())
# print(list)

set1={1,2,3,3}
# print(set1.union(list))

# list1=["omar","Ahmed",1,2,34,44]
# for l in list1:
#     print(f"Hello{l}")

list = [1,2,3,4,5]
list.pop(-len(list))
print(list) 