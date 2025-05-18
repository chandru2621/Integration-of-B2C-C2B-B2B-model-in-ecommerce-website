from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Email, Length, NumberRange

class BulkRequestForm(FlaskForm):
    organization_name = StringField('Organization Name', 
        validators=[DataRequired(), Length(min=2, max=100)])
    
    organization_address = StringField('Organization Address',
        validators=[DataRequired(), Length(min=5, max=200)])
    
    contact_email = StringField('Contact Email',
        validators=[DataRequired(), Email()])
    
    contact_phone = StringField('Contact Phone',
        validators=[Length(max=20)])
    
    product_category = SelectField('Product Category',
        choices=[
            ('electronics', 'Electronics'),
            ('furniture', 'Furniture'),
            ('clothing', 'Clothing'),
            ('office_supplies', 'Office Supplies'),
            ('packaging', 'Packaging Materials'),
            ('other', 'Other')
        ],
        validators=[DataRequired()])
    
    quantity = IntegerField('Quantity',
        validators=[DataRequired(), NumberRange(min=1)])
    
    requirements = TextAreaField('Specific Requirements',
        validators=[Length(max=500)]) 