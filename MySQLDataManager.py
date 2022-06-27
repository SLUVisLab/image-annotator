from sqlalchemy.ext.automap import automap_base
from skimage import io

from DataManager import DataManager


class MySQLDataManager(DataManager):

    """
    Responsible for:
        - getting image urls (next or custom) from database
        - getting category associated with a url from database
        - writing to database
    """

    def __init__(self, db):
        self.db = db
        # bbox table object
        Base = automap_base()
        Base.prepare(db.engine, reflect=True)
        self.Bbox = Base.classes.bbox
        self.max_id = self._get_max_id()
        

    def _get_max_id(self):
        # return the last id in the table
        result = self.db.session.query(self.Bbox).order_by(self.Bbox.id.desc()).first()
        self.db.session.close()
        return result.id


    def get_instance(self, index):
        # return Bbox object at given index
        result = self.db.session.query(self.Bbox).filter(self.Bbox.id == index).first()
        self.db.session.close()
        return result

    
    def get_next_empty(self, index):
        # return first image after given index with a nan bbox value
        result = self.db.session.query(self.Bbox).filter(self.Bbox.id >= index,
                                                         self.Bbox.bbox == 'nan').first()
        self.db.session.close()
        return result.id


    def write_bbox(self, index, bbox):
        # write given bbox value to bbox column at given index
        result = self.db.session.query(self.Bbox).filter(self.Bbox.id == index).first()
        if bbox == 'not found':
            result.bbox = bbox
            self.db.session.commit()
            self.db.session.close()
        else:
            bbox = bbox.strip('[]').split(',')
            bbox = [int(x) for x in bbox]
            # check for negative bbox values
            if not any([x < 0 for x in bbox]):
                result.bbox = str(bbox)
                self.db.session.commit()
                self.db.session.close()

