import nest_asyncio
from flask import Flask, request, send_file
from flask_restx import Api, Resource, fields, Namespace
import pdfkit
import os

# Apply the nest_asyncio patch
nest_asyncio.apply()

# Configure pdfkit with the path to wkhtmltopdf
path_wkhtmltopdf = '/usr/local/bin/wkhtmltopdf'  # Update this path based on your installation
config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)

app = Flask(__name__)
api = Api(app, version='1.0', title='PDF Generator API',
          description='An API to convert code snippets to PDF files')

ns = Namespace('pdf', description='PDF operations')
api.add_namespace(ns)

# Define the expected input model for the API
code_model = api.model('Code', {
    'code': fields.String(required=True, description='The code to convert to PDF')
})

# Define the response model for error messages
message_model = api.model('Message', {
    'message': fields.String(description='Response message')
})

@ns.route('/generate-pdf')
class PDFGenerator(Resource):
    @ns.expect(code_model)
    @ns.response(200, 'Success')
    @ns.response(400, 'Validation Error', model=message_model)
    def post(self):
        data = request.get_json()
        if 'code' not in data:
            return {"message": "No code provided"}, 400

        code = data['code']

        # Convert code to HTML
        html_content = f"""
        <html>
        <head>
            <style>
                body {{
                    font-family: monospace;
                    white-space: pre;
                }}
            </style>
        </head>
        <body>
            <pre>{code}</pre>
        </body>
        </html>
        """

        # Generate PDF from HTML
        pdf_file_path = 'output.pdf'
        pdfkit.from_string(html_content, pdf_file_path, configuration=config)

        # Send the PDF file as response
        return send_file(pdf_file_path, as_attachment=True, download_name='output.pdf')

# Run the Flask app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8281, debug=True)