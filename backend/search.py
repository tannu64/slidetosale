from sqlalchemy.orm import Session
import models


def search_products(db: Session, keyword: str, variant_query: str = None):
    results = []
    keyword = keyword.strip().lower()

    products = (
        db.query(models.Product)
        .filter(models.Product.title.ilike(f'%{keyword}%'))
        .all()
    )

    for product in products:
        variants = product.variants
        if variant_query:
            vq = variant_query.strip().lower()
            variants = [v for v in variants if vq in (v.title or '').lower()]

        for v in variants:
            results.append({
                'product': product.title,
                'variant': v.title,
                'price': v.price,
                'stock': v.stock,
                'in_stock': v.stock > 0,
            })

    return results
