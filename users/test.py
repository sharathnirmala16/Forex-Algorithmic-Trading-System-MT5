str1 = '0.005, 20, 0.005'
str2 = '4,20, 1'



li = [float(ele) if '.' in ele else int(ele) for ele in str1.split(',')]
print(li)