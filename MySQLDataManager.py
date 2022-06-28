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


    def _get_instance(self, index):
        # return Bbox object at given index
        result = self.db.session.query(self.Bbox).filter(self.Bbox.id == index).first()
        result.status = 'pending'
        self.db.session.commit()
        return result


    def _mark_open(self, index):
        # return Bbox object at given index
        result = self.db.session.query(self.Bbox).filter(self.Bbox.id == index).first()
        result.status = 'open'
        self.db.session.commit()
        self.db.session.close()


    def get_next(self, current_index):
        self._mark_open(current_index)
        if current_index < self.max_id:
            current_index += 1
        return self._get_instance(current_index)


    def get_previous(self, current_index):
        self._mark_open(current_index)
        if current_index > 1:
            current_index -= 1
        return self._get_instance(current_index)


    def get_custom(self, current_index, custom_index):
        self._mark_open(current_index)
        if custom_index >= 1 and custom_index <= self.max_id:
            current_index = custom_index
        return self._get_instance(current_index)


    def get_next_empty(self, current_index):
        self._mark_open(current_index)
        # return first image after given index with a nan bbox value
        result = self.db.session.query(self.Bbox).filter(self.Bbox.id >= current_index) \
                                                 .filter(self.Bbox.bbox == 'nan') \
                                                 .filter(self.Bbox.status == 'open').first()
        self.db.session.close()
        return self._get_instance(result.id)


    def write_bbox(self, index, bbox):
        # write given bbox value to bbox column at given index
        result = self.db.session.query(self.Bbox).filter(self.Bbox.id == index).first()
        if bbox == 'not found':
            result.bbox = bbox
            result.status = 'open'
            self.db.session.commit()
            self.db.session.close()
        else:
            bbox = bbox.strip('[]').split(',')
            bbox = [int(x) for x in bbox]
            # check for negative bbox values
            if not any([x < 0 for x in bbox]):
                result.bbox = str(bbox)
                result.status = 'open'
                self.db.session.commit()
                self.db.session.close()

