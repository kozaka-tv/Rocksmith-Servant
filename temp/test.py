class MyClass:
    static_elem = 123

    def __init__(self):
        self.object_elem = 456

c1 = MyClass()
c2 = MyClass()

# Initial values of both elements
print(c1.static_elem, c1.object_elem)
# 123 456
print(c2.static_elem, c2.object_elem)
# 123 456

print("Nothing new so far ...")
print("Let's try changing the static element")
MyClass.static_elem = 999

print(c1.static_elem, c1.object_elem)
# 999 456
print(c2.static_elem, c2.object_elem)
# 999 456

print("Now, let's try changing the object element")
c1.object_elem = 888

print(c1.static_elem, c1.object_elem)
# 999 888
print(c2.static_elem, c2.object_elem)
# 999 456