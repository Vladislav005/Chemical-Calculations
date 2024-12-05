import pandas as pd

if __name__ == '__main__':
    path = 'D:\Python projects\Chemistry\import_file.csv'
    df = pd.read_csv(path, skiprows=range(2))
    print(df.to_markdown())