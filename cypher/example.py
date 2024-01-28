class MyObject(object):
    def __init__(self, length: int = 1):
        super().__init__()
        self.length = length

    def __len__(self):
        return self.length


foo = MyObject(4)
print(len(foo))
