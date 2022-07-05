import sqlalchemy
import yaml
from PIL import Image
import requests
from io import BytesIO
import torch
from torchvision.utils import draw_bounding_boxes
import numpy as np



with open("../conf/app.yml", "r") as stream:
   conf = yaml.safe_load(stream)


engine = sqlalchemy.create_engine(f"mysql+mysqldb://{conf['mysql']['username']}:{conf['mysql']['password']}@localhost/{conf['mysql']['database']}")

img_num = 1

with engine.connect() as connection:
    result = connection.execute(f"Select * from bbox where id = {img_num};").first()

url = result[1]
bbox = result[3]

bbox = bbox.replace("[", "").replace("]", "").split(",")
bbox = [int(x) for x in bbox]
bbox = [bbox[0], bbox[2], bbox[1], bbox[3]]

response = requests.get(result[1])
im = Image.open(BytesIO(response.content)).convert("RGB")
im = im.rotate(270, expand=True)

bbox = torch.tensor(bbox, dtype=torch.int)
bbox = bbox.unsqueeze(0)

# convert img to pass through draw bounding box
img_conv = torch.tensor(np.array(im), dtype=torch.uint8)
img_conv = torch.permute(img_conv, (2, 0, 1))

# draw bounding box and fill color
img_conv = draw_bounding_boxes(img_conv, bbox, width=3, colors = "white")
img_conv = Image.fromarray(img_conv.permute(1, 2, 0).byte().numpy())

img_conv.show()

