from app import create_app
from extensions import db
from models.product import Product
from models.user import User

def add_sample_products():
    app = create_app()
    with app.app_context():
        # Get admin user
        admin = User.query.filter_by(role='admin').first()
        if not admin:
            print("No admin user found. Please create an admin user first.")
            return

        # Sample bulk sustainable products for organizations
        bulk_products = [
            {
                'name': 'Bulk Recycled Paper (5000 sheets)',
                'description': 'High-quality recycled paper, perfect for office use. 5000 sheets per box, 20% post-consumer waste content.',
                'price': 49.99,
                'category': 'Office Supplies',
                'stock': 100,
                'sustainability_score': 85,
                'materials': 'Recycled paper',
                'certifications': 'FSC Certified, Green Seal',
                'bulk_discount': '15% off for orders over 5 boxes'
            },
            {
                'name': 'Eco-Friendly Cleaning Kit (50 sets)',
                'description': 'Complete cleaning kit with biodegradable products. Includes all-purpose cleaner, glass cleaner, and floor cleaner. 50 sets per case.',
                'price': 299.99,
                'category': 'Cleaning Supplies',
                'stock': 50,
                'sustainability_score': 90,
                'materials': 'Plant-based ingredients, recycled packaging',
                'certifications': 'EPA Safer Choice, Green Seal',
                'bulk_discount': '20% off for orders over 3 cases'
            },
            {
                'name': 'Bulk Bamboo Cutlery Set (1000 sets)',
                'description': 'Sustainable bamboo cutlery sets for events and offices. Each set includes fork, knife, and spoon. 1000 sets per box.',
                'price': 399.99,
                'category': 'Food Service',
                'stock': 30,
                'sustainability_score': 95,
                'materials': 'Bamboo',
                'certifications': 'BPA Free, Compostable',
                'bulk_discount': '25% off for orders over 5 boxes'
            },
            {
                'name': 'Reusable Water Bottles (500 units)',
                'description': 'Stainless steel water bottles with company logo option. 500 units per case, various colors available.',
                'price': 2499.99,
                'category': 'Promotional Items',
                'stock': 20,
                'sustainability_score': 88,
                'materials': 'Stainless steel, BPA-free plastic',
                'certifications': 'FDA Approved, BPA Free',
                'bulk_discount': '30% off for orders over 1000 units'
            },
            {
                'name': 'Organic Cotton Tote Bags (1000 units)',
                'description': 'Customizable organic cotton tote bags for events and promotions. 1000 units per order, various sizes available.',
                'price': 1999.99,
                'category': 'Promotional Items',
                'stock': 15,
                'sustainability_score': 92,
                'materials': 'Organic cotton',
                'certifications': 'GOTS Certified, Fair Trade',
                'bulk_discount': '20% off for orders over 2000 units'
            },
            {
                'name': 'Solar-Powered LED Lights (100 units)',
                'description': 'Outdoor solar-powered LED lights for office buildings. 100 units per set, includes installation guide.',
                'price': 1499.99,
                'category': 'Energy Solutions',
                'stock': 25,
                'sustainability_score': 96,
                'materials': 'Recycled aluminum, solar panels',
                'certifications': 'Energy Star, RoHS Compliant',
                'bulk_discount': '25% off for orders over 200 units'
            },
            {
                'name': 'Bulk Compostable Food Containers (5000 units)',
                'description': 'Eco-friendly food containers for corporate events and cafeterias. 5000 units per pallet, various sizes available.',
                'price': 899.99,
                'category': 'Food Service',
                'stock': 40,
                'sustainability_score': 94,
                'materials': 'PLA (Plant-based plastic)',
                'certifications': 'Compostable, FDA Approved',
                'bulk_discount': '15% off for orders over 10000 units'
            },
            {
                'name': 'Recycled Office Furniture Set (10 sets)',
                'description': 'Complete office furniture set made from recycled materials. Includes desk, chair, and storage unit. 10 sets per order.',
                'price': 4999.99,
                'category': 'Office Furniture',
                'stock': 10,
                'sustainability_score': 89,
                'materials': 'Recycled wood, recycled metal',
                'certifications': 'FSC Certified, GREENGUARD',
                'bulk_discount': '20% off for orders over 20 sets'
            }
        ]

        # Add products to database
        for product_data in bulk_products:
            # Check if product already exists
            existing_product = Product.query.filter_by(name=product_data['name']).first()
            if not existing_product:
                product = Product(
                    name=product_data['name'],
                    description=product_data['description'],
                    price=product_data['price'],
                    category=product_data['category'],
                    stock=product_data['stock'],
                    admin_id=admin.id,
                    sustainability_score=product_data['sustainability_score'],
                    materials=product_data['materials'],
                    certifications=product_data['certifications'],
                    bulk_discount=product_data['bulk_discount']
                )
                db.session.add(product)
                print(f"Added product: {product_data['name']}")
            else:
                print(f"Product already exists: {product_data['name']}")

        db.session.commit()
        print("\nAll products have been added successfully!")

if __name__ == '__main__':
    add_sample_products() 