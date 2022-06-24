from DataManager import DataManager

class CSVDataManager(DataManager):

    """
    Responsible for:
        - getting image urls (next or custom) from csv
        - getting category associated with a url from csv
        - writing to csv
    """

    def __init__(self, df):
        self.df = df
        self.max_index = self.df.shape[0] - 1
        self.current_index = 0
        self.current_img = None


    def next_img(self):
        # return the first url after current_index with a nan bbox value
        cropped_df = self.df.iloc[self.current_index:]
        for i, row in cropped_df.iterrows():
            if row['bbox'] == 'nan':
                self.current_index = i
                self.current_img = row['image_path']
                return self.current_img


    def previous_img(self):
        # prevent negative index values
        if self.current_index == 0:
            print("Image index cannot be less than zero")
            return self.current_img
        self.current_index -= 1
        self.current_img = self.df['image_path'].iloc[self.current_index]
        return self.current_img


    def custom_img(self, i):
        # return url at given index
        # check for index out of bounds
        try:
            self.current_img = self.df['image_path'].iloc[i]
            self.current_index = i
        except IndexError:
            print("Image index out of range")
        return self.current_img
    

    def category(self, url):
        # find category associated with given url
        row = self.df.loc[self.df["image_path"] == url]
        return row['object_category_name'].iloc[0]


    def bbox(self, url):
        # find bbox associated with given url if any
        row = self.df.loc[self.df["image_path"] == url]
        return row['bbox'].iloc[0]


    def write_bbox(self, bbox):
        # write bbox values to row at current index
        self.df.at[self.current_index, 'bbox'] = bbox
        self.df.to_csv('bbox.csv', index=False)
