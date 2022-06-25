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

    if request.method == "POST":
        # id which form was submitted
        form_name = request.form.get("form_name")

        # custom index: 
        # change url to url at given index
        if form_name == "custom_index_form":
            index = int(request.form['custom_index'])
            # make sure custom index is in range [1, max_id] inclusive
            if index >= 1 and index <= dataManager.max_id:
                session["image_id"] = index

        # next:
        # for moving on after visiting previous image index with no new bbox value
        elif form_name == "next_form":
            session["image_id"] += 1

        # previous:
        # move to image at index - 1
        elif form_name == "previous_form":
            session["image_id"] -= 1

        # submit bbox:
        # extract bbox list
        # write to csv at index of current image
        elif form_name == "submit_bbox_form":
            bbox = request.form['bbox_value']
            # check for empty submission
            if bbox != '[]' and bbox != 'not found':
                bbox = bbox.strip('[]').split(',')
                bbox = [int(x) for x in bbox]
                dataManager.write_bbox(session["image_id"], str(bbox))
                session["image_id"] += 1

        # not found:
        # write not found to csv at index of current image
        elif form_name == "not_found_form":
            dataManager.write_bbox(session["image_id"], 'not found')
            session["image_id"] += 1

    # loading page
    elif request.method == "GET":
        if not "image_id" in session:
            session["image_id"] = 1

    bbox_instance = dataManager.get_instance(session["image_id"])
    existing_bbox = bbox_instance.bbox
    existing_bbox = "[]" if existing_bbox == "nan" else existing_bbox

    data = {'image_url': bbox_instance.image_path, 
            'category': bbox_instance.object_category_name, 
            'index': session["image_id"], 
            'max_index': str(dataManager.max_id),
            'bbox': existing_bbox}

    return render_template("index.html", data=data)


if __name__ == "__main__": 
    app.run(host='0.0.0.0')
