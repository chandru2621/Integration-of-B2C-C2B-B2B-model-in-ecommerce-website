from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, FloatField, IntegerField, SelectField
from wtforms.validators import DataRequired, Optional, NumberRange, URL
from models.product import Product

class ProductSearchForm(FlaskForm):
    search = StringField('Search', validators=[Optional()])
    category = SelectField('Category', validators=[Optional()], choices=[
        ('', 'All Categories'),
        ('electronics', 'Electronics'),
        ('clothing', 'Clothing'),
        ('books', 'Books'),
        ('home', 'Home & Garden'),
        ('sports', 'Sports & Outdoors'),
        ('beauty', 'Beauty & Personal Care'),
        ('toys', 'Toys & Games'),
        ('automotive', 'Automotive'),
        ('other', 'Other')
    ])
    min_price = FloatField('Min Price', validators=[Optional(), NumberRange(min=0)])
    max_price = FloatField('Max Price', validators=[Optional(), NumberRange(min=0)])
    sort_by = SelectField('Sort By', validators=[Optional()], choices=[
        ('newest', 'Newest'),
        ('price_low', 'Price: Low to High'),
        ('price_high', 'Price: High to Low'),
        ('rating', 'Highest Rated')
    ])

class ProductForm(FlaskForm):
    name = StringField('Product Name', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    price = FloatField('Price', validators=[DataRequired(), NumberRange(min=0)])
    stock = IntegerField('Stock', validators=[DataRequired(), NumberRange(min=0)])
    category = SelectField('Category', choices=[(cat, cat) for cat in Product.CATEGORIES], validators=[DataRequired()])
    subcategory = StringField('Subcategory', validators=[Optional()])
    brand = StringField('Brand', validators=[Optional()])
    image_url = StringField('Image URL', validators=[Optional()])
    sustainability_score = IntegerField('Sustainability Score (1-5)', 
                                      validators=[DataRequired(), NumberRange(min=1, max=5)])
    materials = StringField('Materials Used', validators=[Optional()])
    certifications = StringField('Sustainability Certifications', validators=[Optional()]) 