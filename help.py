dict_ = {'squad': 111, 'possession': 100}
# squad = '111' and possesion = '100'
g = ' '.join(['squad',  '111', 'possesion', '100'])
# print(g)

# f = ' AND '.join([str(x) + '=' + str(y) for x, y in dict_.items()])


f = " AND ".join(f"{k} = '{v}'" for k, v in dict_.items())

print(f)


data = {'squad': '222', 'date': '2021-08-14'}
size = 2

x = "INSERT INTO {} ({}) VALUES ({})".format('fbref', ','.join(data.keys()), ','.join(data.values()))
# sql = 'INSERT INTO {} ({}) VALUES ({});'.format('fbref', " ".join(f"{k}, '{v}'" for k, v in data.items()))
# print(x)
# # print(sql)
#
# list_ = []
# for k, v in data.items():
#     string = str(k), str(v)
#     list_.append(string)
# print(" ".join(f"{k}" for k in data.keys()))
# print(" ".join(f"{v}" for v in data.items()))
