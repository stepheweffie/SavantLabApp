from flask_admin.contrib.sqla import ModelView
from models import Product
from forms import ProductForm
from flask import request
from models import db
from flask_admin import expose


class RuleView(ModelView):
    form_create_rules = ('name', 'description', 'price')

    @expose('/', methods=['GET', 'POST'])
    def admin_index(self):
        form = ProductForm()
        if request.method == 'GET':
            return self.render('admin/store.html', form=form)
        if form.validate_on_submit():
            product = Product(name=form.name.data, description=form.description.data, price=form.price.data)
            db.session.add(product)
            db.session.commit()
            form.name.data = ''
            form.description.data = ''
            form.price.data = ''
        return self.render('admin/store.html', form=form)

