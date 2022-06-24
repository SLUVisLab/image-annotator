from sqlalchemy.ext.automap import automap_base

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

    """
    def next_blank_img(self, index):
        # return the first instance with id greater than current id and nan bbox value
        result = self.db.session.query(self.Bbox).filter(self.Bbox.bbox == 'nan',
                                                         self.Bbox.id >= self.current_id).first()
        self.current_id = result.id
        self.current_img = result.image_path
        self.db.session.close()
        return self.current_img
    """


    def get_url(self, index):
        # dont allow an id greater than max_id
        if index >= 1 and index <= self.max_id:
            result = self.db.session.query(self.Bbox).filter(self.Bbox.id == index).first()
            self.db.session.close()
            return result.image_path

    def get_bbox_instance(self, index):
        # dont allow an id greater than max_id
        if index >= 1 and index <= self.max_id:
            result = self.db.session.query(self.Bbox).filter(self.Bbox.id == index).first()
            self.db.session.close()
            return result


    def write_bbox(self, index, bbox):
        # write given bbox value to bbox column at current id
        result = self.db.session.query(self.Bbox).filter(self.Bbox.id == index).first()
        result.bbox = bbox
        self.db.session.commit()
        self.db.session.close()

