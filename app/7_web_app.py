from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from math import ceil

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///conditioners.db'
db = SQLAlchemy(app)

last_conditioner_type: None | str = None
page: int = 1
sort_order: None | str = None
website_state: dict = {
    "can_click_previous": False,
    "can_click_next": True
}
p: int = 0
e: int = 0
h: int = 0

type_recommendation_translate: dict = {
    "P": "Proteinowy",
    "E": "Emolientowy",
    "H": "Humektantowy"
}

class ConditionersDatabase(db.Model):
    url = db.Column(db.String(2048), primary_key=True, nullable=False)
    name = db.Column(db.String, nullable=False)
    price = db.Column(db.Float, nullable=False)
    ingredients = db.Column(db.String, nullable=False)
    pred_type = db.Column(db.String(3), nullable=False)


    def __repr__(self):
        return '<Conditioner %r>' % self.url


@app.route("/", methods=['GET','POST'])
def index():
    global last_conditioner_type, page, website_state, sort_order, \
        p, e, h
    page_size = 25
    p = 0
    e = 0
    h = 0

    # Recommendation of the hair conditioner's type

    # Calculating points for recommended conditioner types based
    # on selected hair conditions
    if request.form.getlist('hair_condition'): 
        # If any hair condition option is selected
        for condition in request.form.getlist('hair_condition'):
            if condition == "Nadmierne obciążenie":
                p+=1
                e-=1
                h+=1
            if condition == "Strączkowanie":
                p+=1
                e-=1
                h+=1
            if condition == "Matowość":
                e+=1
                h-=1
            if condition == "Suchość":
                p-=1
                e+=1
            if condition == "Łamanie się włosów":
                e+=1
                h-=1
            if condition == "Elektryzowanie":
                e+=1
            if condition == "Puch":
                p+=1
                e+=1
                h-=1
            if condition == "Rozprostowanie skrętu":
                p+=1
                e-=1
                h-=1
            if condition == "Szybkie przetłuszczanie":
                p+=1
                e-=1
                h+=1
    
        # Assigning the recommended type of hair conditioner
        # based on points
        if p > e and p > h:
            last_conditioner_type = 'P'
        if e > p and e > h:
            last_conditioner_type = 'E'
        if h > p and h > e:
            last_conditioner_type = 'H'
        if p == e and p > h:
            last_conditioner_type = 'PE'
        if p == h and p > e:
            last_conditioner_type = 'PH'
        if e == h and e > p:
            last_conditioner_type = 'EH'
        if p == e and e == h:
            last_conditioner_type = 'PEH'
        website_state['type_recommendation'] = \
            type_recommendation_translate[last_conditioner_type] \
                if last_conditioner_type in type_recommendation_translate.keys() \
                    else last_conditioner_type
        website_state['last_conditioner_type'] = last_conditioner_type
        website_state['last_selected_hair_conditions'] = \
            request.form.getlist('hair_condition')
    elif not request.form.getlist('hair_condition') and not 'page' \
        in request.args.keys() and not 'sort_order' in request.args.keys():
        website_state['type_recommendation'] = None
        website_state['last_selected_hair_conditions'] = []
        if not 'conditioner_type' in request.args.keys():
            website_state['last_conditioner_type'] = None
            last_conditioner_type = None


    # Changing the searched hair conditioner type
    if 'conditioner_type' in request.args.keys():
        last_conditioner_type = request.args['conditioner_type']
        website_state['last_conditioner_type'] = last_conditioner_type

    # Changing the page
    if last_conditioner_type and last_conditioner_type != "ALL":
        total_conditioners = \
            ConditionersDatabase.query.where(\
                ConditionersDatabase.pred_type == \
                    last_conditioner_type).count()
    else:
        total_conditioners = ConditionersDatabase.query.count()

    website_state['total_pages'] = ceil(total_conditioners/page_size)
    
    if 'page' in request.args.keys():  
        # Recently, a user wanted to change the page
        if request.args['page'] == 'next':
            page += 1
        elif request.args['page'] == 'previous':
            page -= 1
        elif request.args['page'] == 'first':
            page = 1
        elif request.args['page'] == 'last':
            page = website_state['total_pages']
    else:  # The user performed an action other than changing the page
        page = 1


    website_state['current_page'] = page

    website_state['can_click_previous'] = False if page == 1 else True
    website_state['can_click_next'] = True if page*page_size < \
        total_conditioners else False

    
    # Sorting data by price
    if 'sort_order' in request.args.keys():
        if request.args['sort_order'] == 'ASC':
            sort_order = "ASC"
        elif request.args['sort_order'] == 'DESC':
            sort_order = "DESC"
        else:
            sort_order = None
        website_state['sort_order'] = sort_order

    # Data filtering
    if last_conditioner_type and last_conditioner_type != "ALL":
        if sort_order == "ASC":
            conditioners = \
                ConditionersDatabase.query.where(\
                ConditionersDatabase.pred_type == \
                    last_conditioner_type).order_by(\
                        ConditionersDatabase.price.asc()).limit(\
                            page_size).offset((page-1)*page_size).all()
        elif sort_order == "DESC":
            conditioners = \
                ConditionersDatabase.query.where(\
                    ConditionersDatabase.pred_type == \
                        last_conditioner_type).order_by(\
                            ConditionersDatabase.price.desc()).limit(\
                                page_size).offset((page-1)*page_size).all()
        else:
            conditioners = \
                ConditionersDatabase.query.where(\
                    ConditionersDatabase.pred_type == \
                        last_conditioner_type).order_by(\
                            ConditionersDatabase.name).limit(\
                                page_size).offset((page-1)*page_size).all()
    else:
        if sort_order == "ASC":
            conditioners = \
                ConditionersDatabase.query.order_by(\
                    ConditionersDatabase.price.asc()).limit(\
                        page_size).offset((page-1)*page_size).all()
        elif sort_order == "DESC":
            conditioners = \
                ConditionersDatabase.query.order_by(\
                    ConditionersDatabase.price.desc()).limit(\
                        page_size).offset((page-1)*page_size).all()
        else:
            conditioners = \
                ConditionersDatabase.query.order_by(\
                    ConditionersDatabase.name).limit(\
                        page_size).offset((page-1)*page_size).all()

    return render_template('index.html', conditioners=conditioners, \
                           website_state=website_state)


if __name__ == "__main__":
    app.run(debug=True)