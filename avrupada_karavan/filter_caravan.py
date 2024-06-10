import pandas as pd

# Load the Excel file
file_path = '/Users/kasimtugrulvural/Documents/avrupadakaravan/vehicle_data.xlsx'
df = pd.read_excel(file_path)

# Filter out rows with 'No title'
df = df[df['Title'] != 'No title']
df = df[df['Title'] != 'Başlık yok ']
df = df[df['Title'] != 'Başlık yok']

# Replace 'mo-160' with 'mo-1024' in image links
df['Main Image'] = df['Main Image'].str.replace('mo-160', 'mo-1024')
df['Images'] = df['Images'].str.replace('mo-160', 'mo-1024')

# Save the cleaned data to a new Excel file
cleaned_file_path = '/Users/kasimtugrulvural/Documents/avrupadakaravan/vehicle_datda.xlsx'
df.to_excel(cleaned_file_path, index=False)

# Display the cleaned data
print(df.head())
