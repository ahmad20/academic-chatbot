import os
import hashlib
import pandas as pd

class Data:
    def __init__(self, df_path="./data.csv"):
        """
        Initializes the Data class.

        Parameters:
        - df_path (str): The path to the CSV file.
        """
        self.df_path = df_path

    def _load_dataframe(self):
        """
        Load the CSV file into a pandas DataFrame.

        Returns:
        - pd.DataFrame: The loaded DataFrame.
        """
        if os.path.exists(self.df_path):
            return pd.read_csv(self.df_path)
        else:
            return pd.DataFrame(columns=["hash_id", "source"])

    def _save_dataframe(self, df):
        """
        Save the DataFrame to the CSV file.

        Parameters:
        - df (pd.DataFrame): The DataFrame to be saved.
        """
        df.to_csv(self.df_path, index=False)

    def set_data(self, source):
        """
        Set data by calculating hash_id and updating the CSV file.

        Parameters:
        - source (str): The source data to be processed.
        """
        self.source = source
        self.hash_id = hashlib.md5(str(source).encode()).hexdigest()

        df = self._load_dataframe()

        # Check if hash_id exists
        if self.hash_id in df["hash_id"].values:
            raise Exception("This document has already been processed")

        new_data = pd.DataFrame([[self.hash_id, self.source]], columns=["hash_id", "source"])
        df = pd.concat([df, new_data], ignore_index=True)

        self._save_dataframe(df)
