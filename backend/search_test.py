from database import SessionLocal
from search import search_products

db = SessionLocal()

print('Search: hoodie')
for r in search_products(db, 'hoodie'):
    print('  ', r['product'], '/', r['variant'], '| stock:', r['stock'], '| in_stock:', r['in_stock'])

print()
print('Search: hoodie + M')
for r in search_products(db, 'hoodie', 'M'):
    print('  ', r['product'], '/', r['variant'], '| stock:', r['stock'], '| in_stock:', r['in_stock'])

db.close()
