from io import BytesIO
from openpyxl import Workbook
from openpyxl.styles import Font


class ExcelExporter:

    @staticmethod
    def sales_report(sales):

        wb = Workbook()
        ws = wb.active
        ws.title = "Sales Report"

        ws.append(["MINIFY GADGETS"])
        ws.append(["Sales Report"])
        ws.append([])

        headers = [
            "Invoice",
            "Customer",
            "Date",
            "Total",
            "Profit"
        ]

        ws.append(headers)

        for cell in ws[4]:
            cell.font = Font(bold=True)

        for sale in sales:

            ws.append([
                sale.invoice_number,
                sale.customer_name,
                sale.sale_date.strftime("%d/%m/%Y"),
                float(sale.total_amount),
                float(sale.profit)
            ])

        output = BytesIO()
        wb.save(output)
        output.seek(0)

        return output
    
        # ==========================================================
    # PURCHASE REPORT
    # ==========================================================

    @staticmethod
    def purchase_report(purchases):

        wb = Workbook()
        ws = wb.active
        ws.title = "Purchase Report"

        ws.append(["MINIFY GADGETS"])
        ws.append(["Purchase Report"])
        ws.append([])

        headers = [
            "Purchase No",
            "Supplier",
            "Date",
            "Status",
            "Total"
        ]

        ws.append(headers)

        for cell in ws[4]:
            cell.font = Font(bold=True)

        for purchase in purchases:

            ws.append([
                purchase.purchase_number,
                purchase.supplier.name if purchase.supplier else "",
                purchase.purchase_date.strftime("%d/%m/%Y"),
                purchase.status,
                float(purchase.total_amount)
            ])

        output = BytesIO()
        wb.save(output)
        output.seek(0)

        return output
    
        # ==========================================================
    # INVENTORY REPORT
    # ==========================================================

    @staticmethod
    def inventory_report(variants):

        wb = Workbook()
        ws = wb.active
        ws.title = "Inventory Report"

        ws.append(["MINIFY GADGETS"])
        ws.append(["Inventory Report"])
        ws.append([])

        ws.append([
            "Product",
            "SKU",
            "Colour",
            "Storage",
            "Buying Price",
            "Selling Price",
            "Stock"
        ])

        for cell in ws[4]:
            cell.font = Font(bold=True)

        for item in variants:
            ws.append([
                item.product.name,
                item.sku,
                item.colour,
                item.storage,
                float(item.buying_price),
                float(item.selling_price),
                item.quantity
            ])

        output = BytesIO()
        wb.save(output)
        output.seek(0)

        return output
    
        # ==========================================================
    # PROFIT REPORT
    # ==========================================================

    @staticmethod
    def profit_report(sales):

        wb = Workbook()
        ws = wb.active
        ws.title = "Profit Report"

        ws.append(["MINIFY GADGETS"])
        ws.append(["Profit Report"])
        ws.append([])

        ws.append([
            "Invoice",
            "Customer",
            "Date",
            "Sales",
            "Profit"
        ])

        for cell in ws[4]:
            cell.font = Font(bold=True)

        for sale in sales:
            ws.append([
                sale.invoice_number,
                sale.customer_name,
                sale.sale_date.strftime("%d/%m/%Y"),
                float(sale.total_amount),
                float(sale.profit)
            ])

        output = BytesIO()
        wb.save(output)
        output.seek(0)

        return output
    
        # ==========================================================
    # IMEI REPORT
    # ==========================================================

    @staticmethod
    def imei_report(imeis):

        wb = Workbook()
        ws = wb.active
        ws.title = "IMEI Report"

        ws.append(["MINIFY GADGETS"])
        ws.append(["IMEI Report"])
        ws.append([])

        ws.append([
            "IMEI",
            "Product",
            "SKU",
            "Storage",
            "Colour",
            "Status"
        ])

        for cell in ws[4]:
            cell.font = Font(bold=True)

        for item in imeis:

            variant = item.product_variant

            ws.append([
                item.imei,
                variant.product.name if variant else "",
                variant.sku if variant else "",
                variant.storage if variant else "",
                variant.colour if variant else "",
                item.status
            ])

        output = BytesIO()
        wb.save(output)
        output.seek(0)

        return output
    
        # ==========================================================
    # LOW STOCK REPORT
    # ==========================================================

    @staticmethod
    def low_stock_report(products):

        wb = Workbook()
        ws = wb.active
        ws.title = "Low Stock Report"

        ws.append(["MINIFY GADGETS"])
        ws.append(["Low Stock Report"])
        ws.append([])

        ws.append([
            "Product",
            "SKU",
            "Colour",
            "Storage",
            "Current Stock",
            "Minimum Stock"
        ])

        for cell in ws[4]:
            cell.font = Font(bold=True)

        for item in products:
            ws.append([
                item.product.name,
                item.sku,
                item.colour,
                item.storage,
                item.quantity,
                item.minimum_stock
            ])

        output = BytesIO()
        wb.save(output)
        output.seek(0)

        return output