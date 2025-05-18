from app import create_app, db
from models.product import Product
from models.user import User

def add_sample_products():
    app = create_app()
    with app.app_context():
        # Check if we already have a seller
        seller = User.query.filter_by(role='seller').first()
        if not seller:
            seller = User(
                username='seller',
                email='seller@example.com',
                role='seller'
            )
            seller.set_password('seller123')
            db.session.add(seller)
            db.session.commit()
            print(f"Created seller with ID: {seller.id}")

        # Add sample products
        products = [
            {
                'name': 'Organic Cotton Tote Bag',
                'description': 'Handmade tote bag made from 100% organic cotton',
                'price': 24.99,
                'stock': 50,
                'category': 'Reusable Fashion',
                'subcategory': 'Bags',
                'brand': 'EcoStyle',
                'sustainability_score': 5,
                'materials': 'Organic cotton',
                'certifications': 'GOTS certified',
                'image_url': 'https://example.com/tote-bag.jpg',
                'seller_id': seller.id
            },
            {
                'name': 'Bamboo Toothbrush',
                'description': 'Eco-friendly toothbrush made from sustainable bamboo',
                'price': 4.99,
                'stock': 100,
                'category': 'Refillable Personal Care',
                'subcategory': 'Oral Care',
                'brand': 'GreenLife',
                'sustainability_score': 5,
                'materials': 'Bamboo, BPA-free bristles',
                'certifications': 'FSC certified',
                'image_url': 'https://example.com/toothbrush.jpg',
                'seller_id': seller.id
            },
            {
                'name': 'Stainless Steel Water Bottle',
                'description': 'Reusable water bottle made from food-grade stainless steel',
                'price': 19.99,
                'stock': 75,
                'category': 'Reusable Kitchenware',
                'subcategory': 'Drinkware',
                'brand': 'EcoBottle',
                'sustainability_score': 5,
                'materials': 'Stainless steel',
                'certifications': 'FDA approved',
                'image_url': 'https://example.com/water-bottle.jpg',
                'seller_id': seller.id
            },
            {
                'name': 'Solar-Powered Phone Charger',
                'description': 'Portable solar charger for mobile devices',
                'price': 49.99,
                'stock': 30,
                'category': 'Recycled Electronics',
                'subcategory': 'Chargers',
                'brand': 'SunPower',
                'sustainability_score': 4,
                'materials': 'Recycled plastic, solar panels',
                'certifications': 'RoHS compliant',
                'image_url': 'https://example.com/charger.jpg',
                'seller_id': seller.id
            },
            {
                'name': 'Beeswax Food Wraps',
                'description': 'Reusable food wraps made from organic cotton and beeswax',
                'price': 14.99,
                'stock': 60,
                'category': 'Eco-friendly Home Items',
                'subcategory': 'Food Storage',
                'brand': 'BeeGreen',
                'sustainability_score': 5,
                'materials': 'Organic cotton, beeswax, jojoba oil',
                'certifications': 'Organic certified',
                'image_url': 'https://example.com/food-wraps.jpg',
                'seller_id': seller.id
            }
        ]

        # Add products to database
        for product_data in products:
            if not Product.query.filter_by(name=product_data['name']).first():
                product = Product(**product_data)
                db.session.add(product)
                print(f"Added product: {product_data['name']}")

        db.session.commit()
        
        # Verify products in database
        all_products = Product.query.all()
        print("\nProducts in database:")
        for product in all_products:
            print(f"- {product.name} (ID: {product.id}, Category: {product.category})")

if __name__ == '__main__':
    add_sample_products() 