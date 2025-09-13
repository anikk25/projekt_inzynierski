from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from math import ceil

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///conditioners.db'
db = SQLAlchemy(app)

last_conditioner_type: None | str = None
page: int = 1
what_to_sort: None | str = None
sort_order: None | str = None
website_state: dict = {
    "can_click_previous": False,
    "can_click_next": True
}

class ConditionersDatabase(db.Model):
    url = db.Column(db.String(2048), primary_key=True, nullable=False)
    name = db.Column(db.String, nullable=False)
    price = db.Column(db.Float, nullable=False)
    ingredients = db.Column(db.String, nullable=False)
    pred_type = db.Column(db.String(3), nullable=False)

    def __repr__(self):
        return '<Conditioner %r>' % self.url


@app.route("/", methods=['GET'])
def index():
    global last_conditioner_type, page, website_state, sort_order
    page_size = 25

    # Zmiana wyszukiwanego typu odżywki
    if 'conditioner_type' in request.args.keys():
        last_conditioner_type = request.args['conditioner_type']
        website_state['last_conditioner_type'] = last_conditioner_type

    # Zmiana strony
    if last_conditioner_type and last_conditioner_type != "ALL":
        total_conditioners = ConditionersDatabase.query.where(ConditionersDatabase.pred_type == last_conditioner_type).count()
    else:
        total_conditioners = ConditionersDatabase.query.count()

    website_state['total_pages'] = ceil(total_conditioners/page_size)
    
    if 'page' in request.args.keys():
        if request.args['page'] == 'next':
            page += 1
        elif request.args['page'] == 'previous':
            page -= 1
        elif request.args['page'] == 'first':
            page = 1
        elif request.args['page'] == 'last':
            page = website_state['total_pages']
    else:
        page = 1

    website_state['current_page'] = page

    website_state['can_click_previous'] = False if page == 1 else True
    website_state['can_click_next'] = True if page*page_size < total_conditioners else False

    
    # Sortowanie danych po cenie
    if 'sort_order' in request.args.keys():
        if request.args['sort_order'] == 'ASC':
            sort_order = "ASC"
        elif request.args['sort_order'] == 'DESC':
            sort_order = "DESC"
        else:
            sort_order = None
        website_state['sort_order'] = sort_order

    # Filtrowanie danych
    if last_conditioner_type and last_conditioner_type != "ALL":
        if sort_order == "ASC":
            conditioners = ConditionersDatabase.query.where(ConditionersDatabase.pred_type == last_conditioner_type).order_by(ConditionersDatabase.price.asc()).limit(page_size).offset((page-1)*page_size).all()
        elif sort_order == "DESC":
            conditioners = ConditionersDatabase.query.where(ConditionersDatabase.pred_type == last_conditioner_type).order_by(ConditionersDatabase.price.desc()).limit(page_size).offset((page-1)*page_size).all()
        else:
            conditioners = ConditionersDatabase.query.where(ConditionersDatabase.pred_type == last_conditioner_type).order_by(ConditionersDatabase.name).limit(page_size).offset((page-1)*page_size).all()
    else:
        if sort_order == "ASC":
            conditioners = ConditionersDatabase.query.order_by(ConditionersDatabase.price.asc()).limit(page_size).offset((page-1)*page_size).all()
        elif sort_order == "DESC":
            conditioners = ConditionersDatabase.query.order_by(ConditionersDatabase.price.desc()).limit(page_size).offset((page-1)*page_size).all()
        else:
            conditioners = ConditionersDatabase.query.order_by(ConditionersDatabase.name).limit(page_size).offset((page-1)*page_size).all()

    return render_template('index.html', conditioners=conditioners, website_state=website_state)


if __name__ == "__main__":
    app.run(debug=True)