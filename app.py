from flask import Flask, render_template, request, session
from flask_sqlalchemy import SQLAlchemy
import yaml

# from CSVDataManager import CSVDataManager
from MySQLDataManager import MySQLDataManager


app = Flask(__name__)

with open("../conf/app.yml", "r") as stream:
   conf = yaml.safe_load(stream)

mysql_user = conf['mysql']['username']
mysql_pass = conf['mysql']['password']
mysql_db = conf['mysql']['database']
app_secret_key = conf['app']['secret_key']

app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+mysqldb://{mysql_user}:{mysql_pass}@localhost/{mysql_db}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_POOL_SIZE'] = 20
app.config['SECRET_KEY'] = app_secret_key

db = SQLAlchemy(app)
dataManager = MySQLDataManager(db)


@app.route("/", methods=["GET", "POST"])
def index():

    if "image_id" not in session:
        session["image_id"] = 1
    result = None

    if request.method == "POST":
        # id which form was submitted
        form_name = request.form.get("form_name")

        params = {"current_index": session["image_id"]}

        # custom index
        if form_name == "custom_index_form":
            custom_index = int(request.form['custom_index'])
            params["custom_index"] = custom_index

        # submit bbox
        elif form_name == "submit_bbox_form":
            bbox = request.form['bbox_value']
            # check for empty submission
            if bbox != '[]':
                dataManager.write_bbox(session["image_id"], bbox)

        # not found
        elif form_name == "not_found_form":
            dataManager.write_bbox(session["image_id"], 'not found')

        funcs = {
            "next_form": dataManager.get_next,
            "previous_form": dataManager.get_previous,
            "next_empty_form": dataManager.get_next_empty,
            "custom_index_form": dataManager.get_custom,
            "submit_bbox_form": dataManager.get_next_empty,
            "not_found_form": dataManager.get_next_empty,
        }

        result = funcs[form_name](**params)

    # loading page
    elif request.method == "GET":
        result = dataManager.get_next_empty(session["image_id"])

    # mark image as "pending", time out pending once a night
    # not have a bbox, and not pending to show to user
    # move buttons
    # say another object is in the image
    session["image_id"] = result.id
    existing_bbox = result.bbox
    existing_bbox = "[]" if existing_bbox == "nan" else existing_bbox

    data = {'image_url': result.image_path, 
            'category': result.object_category_name, 
            'index': session["image_id"], 
            'max_index': str(dataManager.max_id),
            'bbox': existing_bbox}

    return render_template("index.html", data=data)


if __name__ == "__main__": 
    app.run(host='0.0.0.0')
