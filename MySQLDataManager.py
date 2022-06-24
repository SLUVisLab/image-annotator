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
        self.current_id = 0
        self.current_img = None
        

    def _get_max_id(self):
        # return the last id in the table
        result = self.db.session.query(self.Bbox).order_by(self.Bbox.id.desc()).first()
        self.db.session.close()
        return result.id


    def next_blank_img(self):
        # return the first instance with id greater than current id and nan bbox value
        result = self.db.session.query(self.Bbox).filter(self.Bbox.bbox == 'nan',
                                                         self.Bbox.id >= self.current_id).first()
        self.current_id = result.id
        self.current_img = result.image_path
        self.db.session.close()
        return self.current_img


    def next_img(self):
        # dont allow an id greater than max_id
        if (self.current_id + 1) <= self.max_id:
            result = self.db.session.query(self.Bbox).filter(self.Bbox.id == (self.current_id + 1)).first()
            self.current_id = result.id
            self.current_img = result.image_path
            self.db.session.close()
        return self.current_img


    def previous_img(self):
        # dont allow an id less than one
        if (self.current_id - 1) >= 1:
            result = self.db.session.query(self.Bbox).filter(self.Bbox.id == (self.current_id - 1)).first()
            self.current_id = result.id
            self.current_img = result.image_path
            self.db.session.close()
        return self.current_img


    def custom_img(self, i):
        # make sure id is in range [1, max_id] inclusive
        if i >= 1 and i <= self.max_id:
            result = self.db.session.query(self.Bbox).filter(self.Bbox.id == i).first()
            self.current_id = result.id
            self.current_img = result.image_path
            self.db.session.close()
        return self.current_img
    

    def category(self, url):
        # return object category associated with given url
        result = self.db.session.query(self.Bbox).filter(self.Bbox.image_path == url).first()
        self.db.session.close()
        return result.object_category_name


    def bbox(self, url):
        # return bbox value associated with given url
        result = self.db.session.query(self.Bbox).filter(self.Bbox.image_path == url).first()
        self.db.session.close()
        return result.bbox


    def write_bbox(self, bbox):
        # write given bbox value to bbox column at current id
        result = self.db.session.query(self.Bbox).filter(self.Bbox.id == self.current_id).first()
        result.bbox = bbox
        self.db.session.commit()
        self.db.session.close()

