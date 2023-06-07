from faker import Faker
fake= Faker()
for i in range(10):
    print(fake.name())
    print(fake.address())
    print(fake.email())
    print(fake.text())