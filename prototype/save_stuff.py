import pickle

option = "load"
# option = "write"

path = "../data/parameters/para1.txt"
mylist = ["hi", 12, {"key": 420}, ['a','b']]

if option == "write":
    file = open(path,'wb')
    pickle.dump(mylist,file)
    file.close()

if option == "load":
    file = open(path,'rb')
    mylist2 = pickle.load(file)
    print(mylist==mylist2)



# print(self.CurMov.parameters)

coolparams = [[10, 10, 10, 10], [True, 10, 1], [True, 50, 25, 25], [False, 1, 10, 0], [True, 21, 89],
              [False, 10, 10, 10, 10, 4, 10], [False, 50]]

for clazz, newparams in zip(SliderClass.all_sliders, coolparams):
    print(clazz._params_image)
    clazz.settr(newparams)
    print(clazz._params_image)
