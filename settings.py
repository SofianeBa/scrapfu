from dotenv import load_dotenv
import os


load_dotenv()
try:
    connect_str = os.getenv('AZ_Connection_String')
except os.error: 
    print('Error! Please check if the environment variable has been set.')
try:
    kvName = os.getenv('KV_NAME')
except OSError:
    print('Error: Please check if the KV_NAME environment variable is present')