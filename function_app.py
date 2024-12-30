import azure.functions as func
import logging
import pdfkit
import os
import subprocess

os.environ['LD_LIBRARY_PATH'] = os.path.join(os.getcwd(), 'local_libs') + ':' + os.environ.get('LD_LIBRARY_PATH', '')


app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.route(route="HelloWorld", methods=['GET'])
def hello(req: func.HttpRequest) -> func.HttpResponse:
    """Basic Hello World endpoint"""
    try:
        return func.HttpResponse("Hello World", status_code=200)
    except Exception as e:
        logging.error(f"Error in HelloWorld endpoint: {str(e)}")
        return func.HttpResponse("Failed", status_code=500)

@app.route(route="PDFconverter", methods=['GET'])
def converter(req: func.HttpRequest) -> func.HttpResponse:
    """Endpoint to convert HTML to PDF"""
    logging.info("PDF conversion trigger function started")

    # Set HTML file path and wkhtmltopdf binary path
    html_file_path = os.path.join(os.getcwd(), "text.html")  # Ensure 'text.html' exists in the deployment folder
    path_to_wkhtmltopdf = os.path.join(os.getcwd(), 'wkhtmltopdf')  # Adjust path as per deployment

    logging.info(f"HTML file path: {html_file_path}")
    logging.info(f"wkhtmltopdf path: {path_to_wkhtmltopdf}")
    logging.info(f"LD_LIBRARY_PATH: {os.environ['LD_LIBRARY_PATH']}")
    logging.info(subprocess.check_output(['ldd', 'wkhtmltopdf']).decode())
    logging.info(f"LD_LIBRARY_PATH: {os.environ['LD_LIBRARY_PATH']}")


    try:
        # Check if the HTML file exists
        if not os.path.isfile(html_file_path):
            logging.error("HTML file not found")
            return func.HttpResponse("HTML file not found", status_code=404)

        # Configure pdfkit
        config = pdfkit.configuration(wkhtmltopdf=path_to_wkhtmltopdf)

        # Convert HTML to PDF
        pdf = pdfkit.from_file(html_file_path, False, configuration=config)

        # Return the PDF in the HTTP response
        return func.HttpResponse(
            pdf,
            status_code=200,
            mimetype='application/pdf',
            headers={
                "Content-Disposition": "inline; filename=Azure_output.pdf"
            }
        )
    except FileNotFoundError as e:
        logging.error(f"File not found error: {str(e)}")
        return func.HttpResponse(
            f"Failed to generate PDF: File not found - {str(e)}",
            status_code=500
        )
    except Exception as e:
        logging.error(f"Failed to generate PDF: {str(e)}")
        return func.HttpResponse(
            f"Failed to generate PDF: {str(e)}",
            status_code=500
        )

@app.route(route="http_trigger", auth_level=func.AuthLevel.ANONYMOUS)
def http_trigger(req: func.HttpRequest) -> func.HttpResponse:
    """Sample HTTP trigger for personalized response"""
    logging.info("Python HTTP trigger function processed a request.")

    name = req.params.get('name')
    if not name:
        try:
            req_body = req.get_json()
            name = req_body.get('name')
        except ValueError:
            pass

    if name:
        return func.HttpResponse(f"Hello, {name}. This HTTP triggered function executed successfully.")
    else:
        return func.HttpResponse(
            "This HTTP triggered function executed successfully. "
            "Pass a name in the query string or in the request body for a personalized response.",
            status_code=200
        )


