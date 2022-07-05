from PIL import Image
import hashlib
import yaml
import sqlalchemy
import requests
from io import BytesIO


with open("../conf/app.yml", "r") as stream:
   conf = yaml.safe_load(stream)


engine = sqlalchemy.create_engine(f"mysql+mysqldb://{conf['mysql']['username']}:{conf['mysql']['password']}@localhost/{conf['mysql']['database']}")


with engine.connect() as connection:
    all_rows = connection.execute(f"Select * from bbox;")
    for row in all_rows:
        print(f"ID: {row[0]}")
        url_response = requests.get(row[1])
        im = Image.open(BytesIO(url_response.content))
        hash = hashlib.md5(im.tobytes())
        connection.execute(f'Update bbox set md5_hash = {hash} where id = {row[0]};')
    print('Complete')