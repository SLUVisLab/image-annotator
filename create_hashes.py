from PIL import Image
import hashlib
import yaml
import sqlalchemy
import requests
from io import BytesIO
import multiprocessing

with open("../conf/app.yml", "r") as stream:
   conf = yaml.safe_load(stream)


engine = sqlalchemy.create_engine(f"mysql+mysqldb://{conf['mysql']['username']}:{conf['mysql']['password']}@localhost/{conf['mysql']['database']}")
connection = engine.connect()


def generate_hash(ids):
    all_rows = connection.execute(f"Select * from bbox where id in {ids};")
    for row in all_rows:
        print(f"ID: {row[0]}")
        url_response = requests.get(row[1])
        im = Image.open(BytesIO(url_response.content))
        hash = hashlib.md5(im.tobytes())
        connection.execute(f"Update bbox set md5_hash = '{hash.hexdigest()}' where id = {row[0]};")
    print('Complete')


if __name__ == '__main__':
    count_non_null = connection.execute(f"Select count(*) from bbox where md5_hash is NULL;").first()[0]
    first_null = connection.execute(f"Select id from bbox where md5_hash is NULL;").first()[0]
    num_workers = 5
    rows_per_worker = int(count_non_null / num_workers)
    jobs = []
    for w in range(num_workers):
        section = connection.execute(f"Select id from bbox where md5_hash is NULL and id >= {first_null + rows_per_worker * w} and id <= {first_null + rows_per_worker * (w + 1)};")
        section = [s[0] for s in section]
        p = multiprocessing.Process(target=generate_hash, args=(tuple(section),))
        jobs.append(p)
        p.start()
    connection.close()
