FLASK_APP=app.py FLASK_ENV=development flask run --host=0.0.0.0

# https://tewarid.github.io/2019/06/04/extract-all-tabular-data-from-multipart-mime-documents.html

use python `email` library to load the .mhtml files, and then extract the text/html part, and load it with beautifulsoup (for parsing)
