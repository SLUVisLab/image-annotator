from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy

# from CSVDataManager import CSVDataManager
from MySQLDataManager import MySQLDataManager


app = Flask(__name__)

mysql_user = None
mysql_pass = None
mysql_db = None
app_secret_key = None

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
            url = dataManager.custom_img(index)

        # submit bbox:
        # extract bbox list
        # write to csv at index of current image
        elif form_name == "submit_bbox_form":
            bbox = request.form['submit_bbox_button']
            # check for empty submission
            if bbox == 'Submit':
                url = dataManager.current_img
            else:
                bbox = bbox.strip('submit bbox = []').split(',')
                bbox = [int(x) for x in bbox]
                dataManager.write_bbox(str(bbox))
                url = dataManager.next_blank_img()

        # not found:
        # write not found to csv at index of current image
        elif form_name == "not_found_form":
            dataManager.write_bbox('not found')
            url = dataManager.next_img()

        # next:
        # for moving on after visiting previous image index with no new bbox value
        elif form_name == "next_form":
            url = dataManager.next_img()

        # previous:
        # move to image at index - 1
        elif form_name == "previous_form":
            url = dataManager.previous_img()
    
    # loading page
    elif request.method == "GET":
        url = dataManager.next_img()
    
    cat = dataManager.category(url)
    existing_bbox = dataManager.bbox(url)
    existing_bbox = "[]" if existing_bbox == "nan" else existing_bbox

    data = {'image_url': url, 
            'category': cat, 
            'index': str(dataManager.current_id), 
            'max_index': str(dataManager.max_id),
            'bbox': existing_bbox}

    return render_template("index.html", data=data)


if __name__ == "__main__": 
    app.run()