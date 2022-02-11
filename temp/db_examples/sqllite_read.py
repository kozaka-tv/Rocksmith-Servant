import sqlite3

conn = sqlite3.connect('example.db')

c = conn.cursor()

t = ('RHAT',)
c.execute('SELECT * FROM stocks WHERE symbol=?', t)



print(c.fetchone())
