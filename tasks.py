from robocorp.tasks import task
from RPA.HTTP import HTTP
from RPA.Excel.Files import Files
from RPA.Tables import Tables
from robocorp import browser
from RPA.PDF import PDF
from RPA.Archive import Archive
import shutil
import os
@task
def order_robots_from_RobotSpareBin():
    """
        Orders robots from RobotSpareBin Industries Inc.
        Saves the order HTML receipt as a PDF file.
        Saves the screenshot of the ordered robot.
        Embeds the screenshot of the robot to the PDF receipt.
        Creates ZIP archive of the receipts and the images.
    """
    if os.path.exists("output/orders"):
        shutil.rmtree("output/orders")
    os.makedirs("output/orders", exist_ok=True)
    page = get_order_page()
    
    orders = get_orders()
    for order in orders:
        trial = 1
        while not proceed_order(page, order) and trial < 3:
            trial += 1

    zip_orders()

def zip_orders():
    archive = Archive()
    archive.archive_folder_with_zip("output/orders", "output/orders.zip")   
def get_order_page():
    browser.goto("https://robotsparebinindustries.com/#/robot-order")
    page = browser.page()
    
    #page.wait_for_selector("button:text('OK')", timeout=3000)
    close_annoying_modal(page)
    return page
    
def proceed_order(page, order):
    if fill_the_form(page, order):
        if export_as_pdf(page, order):
            print('order ' + order['Order number'] + ' saved')
            page.click("#order-another")
            close_annoying_modal(page)
            return True
        else:
            return False
    else:
        return False

def get_orders():
    """Downloads excel file from the given URL"""
    http = HTTP()
    http.download(url="https://robotsparebinindustries.com/orders.csv", overwrite=True)
    tables = Tables()
    return tables.read_table_from_csv(path="orders.csv", header=True)
    

def close_annoying_modal(page):
    try:
        print('check for modal')
        ok = page.wait_for_selector("button:text('OK')", timeout=5000)
        print('modal found')
        page.click("button:text('OK')")
        
    except:
        print('no modal')
    


def fill_the_form(page, order):
    page.select_option("#head", order["Head"])
    page.set_checked("#id-body-" + order["Body"], True)
    #page.fill("input:type('number')", order["Legs"])
    locator = page.get_by_placeholder("Enter the part number for the legs").fill(order["Legs"])
    #locator
    page.fill("#address", order["Address"])
    validation = validate_order(page)
    trial = 1
    while not validation and trial < 5:
        trial += 1
        validation = validate_order(page)

    return validation

def validate_order(page):
    page.click("#order")
    try:
        error = page.wait_for_selector(".alert-danger", timeout=3000)
        return False
    except Exception as e:
        return True

def export_as_pdf(page, order):
    """save order and robot screenshot to a pdf file"""
    robot_preview_path = "output/robot_preview_screenshot.png"
    receipt_path = "output/receipt.pdf"

    order_path = "output/orders/receipt-order-" + str(order["Order number"]) + ".pdf"

    # retrieve objects
    receipt_check = page.wait_for_selector("#receipt", timeout=5000)
    receipt = page.locator("#receipt").inner_html()

    robot_preview_check = page.wait_for_selector("#robot-preview-image", timeout=5000)
    robot_preview = page.locator("#robot-preview-image")
    robot_preview.screenshot(path=robot_preview_path)
    #robot_preview_screenshot = browser.screenshot(robot_preview)

    pdf = PDF()
    #pdf_path = "output/receipt-order-" + str(order["Order number"]) + ".pdf"
    pdf.html_to_pdf(receipt, receipt_path)    
    #pdf.html_to_pdf(robot_preview, robot_preview_pdf_path)  
    print('try to robot_preview ')
    pdf.add_watermark_image_to_pdf(image_path=robot_preview_path, source_path=receipt_path, output_path=order_path)
    print('robot_preview added')
    return True    
    """try:
        receipt_check = page.wait_for_selector("#receipt", timeout=5000)
        receipt = page.locator("#receipt").inner_html()
        print('robot locator check')
        receipt_check = page.wait_for_selector("#robot-preview-image", timeout=5000)
        robot_preview = page.locator("#robot-preview-image")
        print('robot locator ok')
        robot_preview_screenshot = browser.screenshot(robot_preview)
        print('robot preview ok')
        pdf = PDF()
        pdf_path = "output/receipt-order-" + str(order["Order number"]) + ".pdf"
        pdf.html_to_pdf(receipt, pdf_path)    
        print('try to add png')
        pdf.add_files_to_pdf(files=robot_preview_screenshot, target_document=pdf_path)
        print('png added')
        return True
    except:
        return False"""