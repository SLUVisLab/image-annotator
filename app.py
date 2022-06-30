from flask import Flask, render_template, request, session
from apscheduler.schedulers.background import BackgroundScheduler
from flask_sqlalchemy import SQLAlchemy
import yaml
import uuid

from MySQLDataManager import MySQLDataManager


app = Flask(__name__)

with open("../conf/app.yml", "r") as stream:
   conf = yaml.safe_load(stream)

app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+mysqldb://{ conf['mysql']['username'] }:{ conf['mysql']['password'] }@localhost/{ conf['mysql']['database'] }"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_POOL_SIZE'] = 20
app.config['SECRET_KEY'] = conf['app']['secret_key']

db = SQLAlchemy(app)
dataManager = MySQLDataManager(db)


# reset image status and sessions in db every 24 hours
sched = BackgroundScheduler(daemon=True)
sched.add_job(dataManager.reset_sessions, 'interval', hours=24)
sched.start()


@app.route("/", methods=["GET", "POST"])
def index():

    if "image_id" not in session:
        session["image_id"] = 1

    if "session_id" not in session:
        session["session_id"] = uuid.uuid4()
        
    params = {
        "session_id": session["session_id"],
        "current_index": session["image_id"],
        "next_index": None,
        "bbox": None
    }

    if request.method == "POST":
        # id which form was submitted
        form_name = request.form.get("form_name")

        # custom index
        if form_name == "custom_index_form":
            custom_index = int(request.form['custom_index'])
            params["next_index"] = custom_index

        # next
        elif form_name == "next_form":
            params["next_index"] = session["image_id"] + 1

        # previous
        elif form_name == "previous_form":
            params["next_index"] = session["image_id"] - 1

        # submit bbox
        elif form_name == "submit_bbox_form":
            bbox = request.form['bbox_value']
            # check for empty submission
            if bbox != '[]':
                params["bbox"] = bbox

        # not found
        elif form_name == "diff_category_form":
            selected = request.form.get('category')
            if selected == 'no':
                params["bbox"] = 'not found'
            else:
                dataManager.change_category(session["image_id"], selected)
                params["next_index"] = session["image_id"]

    result = dataManager.get_instance(**params)
    session["image_id"] = result.id
    existing_bbox = result.bbox
    existing_bbox = "[]" if existing_bbox == "nan" else existing_bbox

    data = {'image_url': result.image_path, 
            'category': result.object_category_name, 
            'index': session["image_id"], 
            'max_index': str(dataManager.max_id),
            'categories': dataManager.categories,
            'bbox': existing_bbox}

    dataManager.close_session()

    return render_template("index.html", data=data)


if __name__ == "__main__": 
    app.run(host='0.0.0.0')

# prevent negative bbox values