from sqlalchemy.ext.automap import automap_base
from sqlalchemy import or_

class MySQLDataManager:

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
        self.close_session()
        return result.id


    def get_instance(self, session_id, current_index, next_index=None, bbox=None):

        current_img = self.db.session.query(self.Bbox).filter(self.Bbox.id == current_index).first()
        # mark current image as open
        current_img.status = 'open'
        current_img.session_id = 'nan'
        # write bbox if given
        if bbox is not None:
            current_img.bbox = bbox

        next_img = None
        # get the next image
        if next_index is not None:
            if next_index >= 1 and next_index <= self.max_id:
                # go to image regardless of nan bbox, still must be open
                if next_index < current_index:
                    next_img = self.db.session.query(self.Bbox).filter(self.Bbox.id <= next_index) \
                                                               .filter(self.Bbox.status == 'open') \
                                                               .order_by(self.Bbox.id.desc()).first()
                else:
                    next_img = self.db.session.query(self.Bbox).filter(self.Bbox.id >= next_index) \
                                                                .filter(self.Bbox.status == 'open').first()
        else:
            # go to next image with nan bbox and is open
            next_img = self.db.session.query(self.Bbox).filter(self.Bbox.id >= current_index) \
                                                       .filter(self.Bbox.bbox == 'nan') \
                                                       .filter(or_(self.Bbox.status == 'open',
                                                                   self.Bbox.session_id == session_id)).first()

        # if next_img is not a NoneType
        if next_img is not None:
            next_img.status = 'pending'
            next_img.session_id = session_id
            self.db.session.commit()
            # return the next image
            return next_img
        
        return current_img

    
    def close_session(self):
        self.db.session.close()

