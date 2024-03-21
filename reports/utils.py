import datetime
import decimal
import json
from django.urls import reverse
from django.utils.translation import gettext as _
from .models import ReportDefinition


def create_album_report_template():
    # use a predefined report definition so you don't have to start from scratch in this demo app,
    # for a real word app you would probably start with an empty report if nothing was saved previously

    report_definition = {"docElements": [
        {"elementType": "text", "id": 3, "containerId": "0_header", "x": 0, "y": 20, "width": 575, "height": 40,
         "content": "My Albums", "eval": False, "styleId": "", "bold": True, "italic": False, "underline": False,
         "horizontalAlignment": "center", "verticalAlignment": "middle", "textColor": "#741b47", "backgroundColor": "",
         "font": "helvetica", "fontSize": "24", "lineSpacing": 1, "borderColor": "#000000", "borderWidth": 1,
         "borderAll": False, "borderLeft": False, "borderTop": False, "borderRight": False, "borderBottom": False,
         "paddingLeft": 2, "paddingTop": 2, "paddingRight": 2, "paddingBottom": 2, "printIf": "",
         "removeEmptyElement": False, "alwaysPrintOnSamePage": True, "pattern": "", "cs_condition": "",
         "cs_styleId": "", "cs_bold": False, "cs_italic": False, "cs_underline": False,
         "cs_horizontalAlignment": "left", "cs_verticalAlignment": "top", "cs_textColor": "#000000",
         "cs_backgroundColor": "", "cs_font": "helvetica", "cs_fontSize": 12, "cs_lineSpacing": 1,
         "cs_borderColor": "#000000", "cs_borderWidth": "1", "cs_borderAll": False, "cs_borderLeft": False,
         "cs_borderTop": False, "cs_borderRight": False, "cs_borderBottom": False, "cs_paddingLeft": 2,
         "cs_paddingTop": 2, "cs_paddingRight": 2, "cs_paddingBottom": 2, "spreadsheet_hide": False,
         "spreadsheet_column": "", "spreadsheet_colspan": "", "spreadsheet_addEmptyRow": False},
        {"elementType": "text", "id": 5, "containerId": "0_content", "x": 0, "y": 10, "width": 575, "height": 20,
         "content": "List of all available albums:", "eval": False, "styleId": "", "bold": True, "italic": False,
         "underline": False, "horizontalAlignment": "left", "verticalAlignment": "middle", "textColor": "#000000",
         "backgroundColor": "", "font": "helvetica", "fontSize": 12, "lineSpacing": 1, "borderColor": "#000000",
         "borderWidth": 1, "borderAll": False, "borderLeft": False, "borderTop": False, "borderRight": False,
         "borderBottom": False, "paddingLeft": 2, "paddingTop": 2, "paddingRight": 2, "paddingBottom": 2,
         "printIf": "${year} == None", "removeEmptyElement": True, "alwaysPrintOnSamePage": True, "pattern": "",
         "cs_condition": "", "cs_styleId": "", "cs_bold": False, "cs_italic": False, "cs_underline": False,
         "cs_horizontalAlignment": "left", "cs_verticalAlignment": "top", "cs_textColor": "#000000",
         "cs_backgroundColor": "", "cs_font": "helvetica", "cs_fontSize": 12, "cs_lineSpacing": 1,
         "cs_borderColor": "#000000", "cs_borderWidth": "1", "cs_borderAll": False, "cs_borderLeft": False,
         "cs_borderTop": False, "cs_borderRight": False, "cs_borderBottom": False, "cs_paddingLeft": 2,
         "cs_paddingTop": 2, "cs_paddingRight": 2, "cs_paddingBottom": 2, "spreadsheet_hide": False,
         "spreadsheet_column": "", "spreadsheet_colspan": "", "spreadsheet_addEmptyRow": False},
        {"elementType": "text", "id": 11, "containerId": "0_content", "x": 0, "y": 30, "width": 575, "height": 20,
         "content": "List of all available albums for the year ${year}:", "eval": False, "styleId": "", "bold": True,
         "italic": False, "underline": False, "horizontalAlignment": "left", "verticalAlignment": "middle",
         "textColor": "#000000", "backgroundColor": "", "font": "helvetica", "fontSize": 12, "lineSpacing": 1,
         "borderColor": "#000000", "borderWidth": 1, "borderAll": False, "borderLeft": False, "borderTop": False,
         "borderRight": False, "borderBottom": False, "paddingLeft": 2, "paddingTop": 2, "paddingRight": 2,
         "paddingBottom": 2, "printIf": "${year} != None", "removeEmptyElement": True, "alwaysPrintOnSamePage": True,
         "pattern": "", "cs_condition": "", "cs_styleId": "", "cs_bold": False, "cs_italic": False,
         "cs_underline": False, "cs_horizontalAlignment": "left", "cs_verticalAlignment": "top",
         "cs_textColor": "#000000", "cs_backgroundColor": "", "cs_font": "helvetica", "cs_fontSize": 12,
         "cs_lineSpacing": 1, "cs_borderColor": "#000000", "cs_borderWidth": "1", "cs_borderAll": False,
         "cs_borderLeft": False, "cs_borderTop": False, "cs_borderRight": False, "cs_borderBottom": False,
         "cs_paddingLeft": 2, "cs_paddingTop": 2, "cs_paddingRight": 2, "cs_paddingBottom": 2,
         "spreadsheet_hide": False, "spreadsheet_column": "", "spreadsheet_colspan": "",
         "spreadsheet_addEmptyRow": False},
        {"elementType": "table", "id": 17, "containerId": "0_content", "x": 0, "y": 50, "dataSource": "${albums}",
         "columns": 4, "header": True, "contentRows": "1", "footer": False, "border": "grid", "borderColor": "#000000",
         "borderWidth": "1", "spreadsheet_hide": False, "spreadsheet_column": "", "spreadsheet_addEmptyRow": False,
         "headerData": {"elementType": "none", "id": 18, "height": 20, "backgroundColor": "#f3f3f3",
                        "repeatHeader": True, "columnData": [
                 {"elementType": "table_text", "id": 19, "width": 220, "height": 20, "content": "Name", "eval": False,
                  "styleId": "33", "bold": True, "italic": False, "underline": False, "horizontalAlignment": "center",
                  "verticalAlignment": "middle", "textColor": "#000000", "backgroundColor": "", "font": "helvetica",
                  "fontSize": 12, "lineSpacing": 1, "paddingLeft": 2, "paddingTop": 2, "paddingRight": 2,
                  "paddingBottom": 2, "removeEmptyElement": False, "alwaysPrintOnSamePage": True, "pattern": "",
                  "cs_condition": "", "cs_styleId": "", "cs_bold": False, "cs_italic": False, "cs_underline": False,
                  "cs_horizontalAlignment": "left", "cs_verticalAlignment": "top", "cs_textColor": "#000000",
                  "cs_backgroundColor": "", "cs_font": "helvetica", "cs_fontSize": 12, "cs_lineSpacing": 1,
                  "cs_paddingLeft": 2, "cs_paddingTop": 2, "cs_paddingRight": 2, "cs_paddingBottom": 2, "printIf": "",
                  "borderWidth": 1},
                 {"elementType": "table_text", "id": 20, "width": 215, "height": 20, "content": "Artist", "eval": False,
                  "styleId": "33", "bold": True, "italic": False, "underline": False, "horizontalAlignment": "center",
                  "verticalAlignment": "top", "textColor": "#000000", "backgroundColor": "", "font": "helvetica",
                  "fontSize": 12, "lineSpacing": 1, "paddingLeft": 2, "paddingTop": 2, "paddingRight": 2,
                  "paddingBottom": 2, "removeEmptyElement": False, "alwaysPrintOnSamePage": True, "pattern": "",
                  "cs_condition": "", "cs_styleId": "", "cs_bold": False, "cs_italic": False, "cs_underline": False,
                  "cs_horizontalAlignment": "left", "cs_verticalAlignment": "top", "cs_textColor": "#000000",
                  "cs_backgroundColor": "", "cs_font": "helvetica", "cs_fontSize": 12, "cs_lineSpacing": 1,
                  "cs_paddingLeft": 2, "cs_paddingTop": 2, "cs_paddingRight": 2, "cs_paddingBottom": 2, "printIf": "",
                  "borderWidth": 1},
                 {"elementType": "table_text", "id": 27, "width": 80, "height": 20, "content": "Year", "eval": False,
                  "styleId": "33", "bold": True, "italic": False, "underline": False, "horizontalAlignment": "center",
                  "verticalAlignment": "top", "textColor": "#000000", "backgroundColor": "", "font": "helvetica",
                  "fontSize": 12, "lineSpacing": 1, "paddingLeft": 2, "paddingTop": 2, "paddingRight": 2,
                  "paddingBottom": 2, "removeEmptyElement": False, "alwaysPrintOnSamePage": True, "pattern": "",
                  "cs_condition": "", "cs_styleId": "", "cs_bold": False, "cs_italic": False, "cs_underline": False,
                  "cs_horizontalAlignment": "left", "cs_verticalAlignment": "top", "cs_textColor": "#000000",
                  "cs_backgroundColor": "", "cs_font": "helvetica", "cs_fontSize": 12, "cs_lineSpacing": 1,
                  "cs_paddingLeft": 2, "cs_paddingTop": 2, "cs_paddingRight": 2, "cs_paddingBottom": 2, "printIf": "",
                  "borderWidth": 1},
                 {"elementType": "table_text", "id": 28, "width": 60, "height": 20, "content": "Best Of", "eval": False,
                  "styleId": "33", "bold": True, "italic": False, "underline": False, "horizontalAlignment": "center",
                  "verticalAlignment": "top", "textColor": "#000000", "backgroundColor": "", "font": "helvetica",
                  "fontSize": 12, "lineSpacing": 1, "paddingLeft": 2, "paddingTop": 2, "paddingRight": 2,
                  "paddingBottom": 2, "removeEmptyElement": False, "alwaysPrintOnSamePage": True, "pattern": "",
                  "cs_condition": "", "cs_styleId": "", "cs_bold": False, "cs_italic": False, "cs_underline": False,
                  "cs_horizontalAlignment": "left", "cs_verticalAlignment": "top", "cs_textColor": "#000000",
                  "cs_backgroundColor": "", "cs_font": "helvetica", "cs_fontSize": 12, "cs_lineSpacing": 1,
                  "cs_paddingLeft": 2, "cs_paddingTop": 2, "cs_paddingRight": 2, "cs_paddingBottom": 2, "printIf": "",
                  "borderWidth": 1}]}, "contentDataRows": [
            {"elementType": "none", "id": 21, "height": 20, "backgroundColor": "", "alternateBackgroundColor": "",
             "groupExpression": "", "printIf": "", "alwaysPrintOnSamePage": True, "columnData": [
                {"elementType": "table_text", "id": 22, "width": 220, "height": 20, "content": "${name}", "eval": False,
                 "styleId": "34", "bold": False, "italic": False, "underline": False, "horizontalAlignment": "left",
                 "verticalAlignment": "top", "textColor": "#000000", "backgroundColor": "", "font": "helvetica",
                 "fontSize": 12, "lineSpacing": 1, "paddingLeft": 2, "paddingTop": 2, "paddingRight": 2,
                 "paddingBottom": 2, "removeEmptyElement": False, "alwaysPrintOnSamePage": True, "pattern": "",
                 "cs_condition": "", "cs_styleId": "", "cs_bold": False, "cs_italic": False, "cs_underline": False,
                 "cs_horizontalAlignment": "left", "cs_verticalAlignment": "top", "cs_textColor": "#000000",
                 "cs_backgroundColor": "", "cs_font": "helvetica", "cs_fontSize": 12, "cs_lineSpacing": 1,
                 "cs_paddingLeft": 2, "cs_paddingTop": 2, "cs_paddingRight": 2, "cs_paddingBottom": 2,
                 "borderWidth": 1},
                {"elementType": "table_text", "id": 23, "width": 215, "height": 20, "content": "${artist}",
                 "eval": False, "styleId": "34", "bold": False, "italic": False, "underline": False,
                 "horizontalAlignment": "left", "verticalAlignment": "top", "textColor": "#000000",
                 "backgroundColor": "", "font": "helvetica", "fontSize": 12, "lineSpacing": 1, "paddingLeft": 2,
                 "paddingTop": 2, "paddingRight": 2, "paddingBottom": 2, "removeEmptyElement": False,
                 "alwaysPrintOnSamePage": True, "pattern": "", "cs_condition": "", "cs_styleId": "", "cs_bold": False,
                 "cs_italic": False, "cs_underline": False, "cs_horizontalAlignment": "left",
                 "cs_verticalAlignment": "top", "cs_textColor": "#000000", "cs_backgroundColor": "",
                 "cs_font": "helvetica", "cs_fontSize": 12, "cs_lineSpacing": 1, "cs_paddingLeft": 2,
                 "cs_paddingTop": 2, "cs_paddingRight": 2, "cs_paddingBottom": 2, "borderWidth": 1},
                {"elementType": "table_text", "id": 29, "width": 80, "height": 20, "content": "${year}", "eval": False,
                 "styleId": "34", "bold": False, "italic": False, "underline": False, "horizontalAlignment": "left",
                 "verticalAlignment": "top", "textColor": "#000000", "backgroundColor": "", "font": "helvetica",
                 "fontSize": 12, "lineSpacing": 1, "paddingLeft": 2, "paddingTop": 2, "paddingRight": 2,
                 "paddingBottom": 2, "removeEmptyElement": False, "alwaysPrintOnSamePage": True, "pattern": "",
                 "cs_condition": "", "cs_styleId": "", "cs_bold": False, "cs_italic": False, "cs_underline": False,
                 "cs_horizontalAlignment": "left", "cs_verticalAlignment": "top", "cs_textColor": "#000000",
                 "cs_backgroundColor": "", "cs_font": "helvetica", "cs_fontSize": 12, "cs_lineSpacing": 1,
                 "cs_paddingLeft": 2, "cs_paddingTop": 2, "cs_paddingRight": 2, "cs_paddingBottom": 2,
                 "borderWidth": 1}, {"elementType": "table_text", "id": 30, "width": 60, "height": 20,
                                     "content": "'Yes' if ${best_of_compilation} else ''", "eval": True,
                                     "styleId": "34", "bold": False, "italic": False, "underline": False,
                                     "horizontalAlignment": "left", "verticalAlignment": "top", "textColor": "#000000",
                                     "backgroundColor": "", "font": "helvetica", "fontSize": 12, "lineSpacing": 1,
                                     "paddingLeft": 2, "paddingTop": 2, "paddingRight": 2, "paddingBottom": 2,
                                     "removeEmptyElement": False, "alwaysPrintOnSamePage": True, "pattern": "",
                                     "cs_condition": "${best_of_compilation} ", "cs_styleId": "35", "cs_bold": False,
                                     "cs_italic": False, "cs_underline": False, "cs_horizontalAlignment": "left",
                                     "cs_verticalAlignment": "top", "cs_textColor": "#000000", "cs_backgroundColor": "",
                                     "cs_font": "helvetica", "cs_fontSize": 12, "cs_lineSpacing": 1,
                                     "cs_paddingLeft": 2, "cs_paddingTop": 2, "cs_paddingRight": 2,
                                     "cs_paddingBottom": 2, "borderWidth": 1}]}],
         "footerData": {"elementType": "none", "id": 24, "height": 20, "backgroundColor": "", "columnData": [
             {"elementType": "table_text", "id": 25, "width": 220, "height": 20, "content": "", "eval": False,
              "styleId": "", "bold": False, "italic": False, "underline": False, "horizontalAlignment": "left",
              "verticalAlignment": "top", "textColor": "#000000", "backgroundColor": "", "font": "helvetica",
              "fontSize": 12, "lineSpacing": 1, "paddingLeft": 2, "paddingTop": 2, "paddingRight": 2,
              "paddingBottom": 2, "removeEmptyElement": False, "alwaysPrintOnSamePage": True, "pattern": "",
              "cs_condition": "", "cs_styleId": "", "cs_bold": False, "cs_italic": False, "cs_underline": False,
              "cs_horizontalAlignment": "left", "cs_verticalAlignment": "top", "cs_textColor": "#000000",
              "cs_backgroundColor": "", "cs_font": "helvetica", "cs_fontSize": 12, "cs_lineSpacing": 1,
              "cs_paddingLeft": 2, "cs_paddingTop": 2, "cs_paddingRight": 2, "cs_paddingBottom": 2, "borderWidth": 1},
             {"elementType": "table_text", "id": 26, "width": 215, "height": 20, "content": "", "eval": False,
              "styleId": "", "bold": False, "italic": False, "underline": False, "horizontalAlignment": "left",
              "verticalAlignment": "top", "textColor": "#000000", "backgroundColor": "", "font": "helvetica",
              "fontSize": 12, "lineSpacing": 1, "paddingLeft": 2, "paddingTop": 2, "paddingRight": 2,
              "paddingBottom": 2, "removeEmptyElement": False, "alwaysPrintOnSamePage": True, "pattern": "",
              "cs_condition": "", "cs_styleId": "", "cs_bold": False, "cs_italic": False, "cs_underline": False,
              "cs_horizontalAlignment": "left", "cs_verticalAlignment": "top", "cs_textColor": "#000000",
              "cs_backgroundColor": "", "cs_font": "helvetica", "cs_fontSize": 12, "cs_lineSpacing": 1,
              "cs_paddingLeft": 2, "cs_paddingTop": 2, "cs_paddingRight": 2, "cs_paddingBottom": 2, "borderWidth": 1},
             {"elementType": "table_text", "id": 31, "width": 80, "height": 20, "content": "", "eval": False,
              "styleId": "", "bold": False, "italic": False, "underline": False, "horizontalAlignment": "left",
              "verticalAlignment": "top", "textColor": "#000000", "backgroundColor": "", "font": "helvetica",
              "fontSize": 12, "lineSpacing": 1, "paddingLeft": 2, "paddingTop": 2, "paddingRight": 2,
              "paddingBottom": 2, "removeEmptyElement": False, "alwaysPrintOnSamePage": True, "pattern": "",
              "cs_condition": "", "cs_styleId": "", "cs_bold": False, "cs_italic": False, "cs_underline": False,
              "cs_horizontalAlignment": "left", "cs_verticalAlignment": "top", "cs_textColor": "#000000",
              "cs_backgroundColor": "", "cs_font": "helvetica", "cs_fontSize": 12, "cs_lineSpacing": 1,
              "cs_paddingLeft": 2, "cs_paddingTop": 2, "cs_paddingRight": 2, "cs_paddingBottom": 2, "borderWidth": 1},
             {"elementType": "table_text", "id": 32, "width": 60, "height": 20, "content": "", "eval": False,
              "styleId": "", "bold": False, "italic": False, "underline": False, "horizontalAlignment": "left",
              "verticalAlignment": "top", "textColor": "#000000", "backgroundColor": "", "font": "helvetica",
              "fontSize": 12, "lineSpacing": 1, "paddingLeft": 2, "paddingTop": 2, "paddingRight": 2,
              "paddingBottom": 2, "removeEmptyElement": False, "alwaysPrintOnSamePage": True, "pattern": "",
              "cs_condition": "", "cs_styleId": "", "cs_bold": False, "cs_italic": False, "cs_underline": False,
              "cs_horizontalAlignment": "left", "cs_verticalAlignment": "top", "cs_textColor": "#000000",
              "cs_backgroundColor": "", "cs_font": "helvetica", "cs_fontSize": 12, "cs_lineSpacing": 1,
              "cs_paddingLeft": 2, "cs_paddingTop": 2, "cs_paddingRight": 2, "cs_paddingBottom": 2,
              "borderWidth": 1}]}},
        {"elementType": "text", "id": 7, "containerId": "0_footer", "x": 320, "y": 0, "width": 255, "height": 30,
         "content": "Page ${page_number} / ${page_count}", "eval": False, "styleId": "", "bold": False, "italic": False,
         "underline": False, "horizontalAlignment": "right", "verticalAlignment": "middle", "textColor": "#666666",
         "backgroundColor": "", "font": "helvetica", "fontSize": 12, "lineSpacing": 1, "borderColor": "#000000",
         "borderWidth": 1, "borderAll": False, "borderLeft": False, "borderTop": False, "borderRight": False,
         "borderBottom": False, "paddingLeft": 2, "paddingTop": 2, "paddingRight": 2, "paddingBottom": 2, "printIf": "",
         "removeEmptyElement": False, "alwaysPrintOnSamePage": True, "pattern": "", "cs_condition": "",
         "cs_styleId": "", "cs_bold": False, "cs_italic": False, "cs_underline": False,
         "cs_horizontalAlignment": "left", "cs_verticalAlignment": "top", "cs_textColor": "#000000",
         "cs_backgroundColor": "", "cs_font": "helvetica", "cs_fontSize": 12, "cs_lineSpacing": 1,
         "cs_borderColor": "#000000", "cs_borderWidth": "1", "cs_borderAll": False, "cs_borderLeft": False,
         "cs_borderTop": False, "cs_borderRight": False, "cs_borderBottom": False, "cs_paddingLeft": 2,
         "cs_paddingTop": 2, "cs_paddingRight": 2, "cs_paddingBottom": 2, "spreadsheet_hide": False,
         "spreadsheet_column": "", "spreadsheet_colspan": "", "spreadsheet_addEmptyRow": False},
        {"elementType": "text", "id": 8, "containerId": "0_footer", "x": 0, "y": 0, "width": 290, "height": 30,
         "content": "Created on ${current_date}", "eval": False, "styleId": "", "bold": False, "italic": False,
         "underline": False, "horizontalAlignment": "left", "verticalAlignment": "middle", "textColor": "#666666",
         "backgroundColor": "", "font": "helvetica", "fontSize": 12, "lineSpacing": 1, "borderColor": "#000000",
         "borderWidth": 1, "borderAll": False, "borderLeft": False, "borderTop": False, "borderRight": False,
         "borderBottom": False, "paddingLeft": 2, "paddingTop": 2, "paddingRight": 2, "paddingBottom": 2, "printIf": "",
         "removeEmptyElement": False, "alwaysPrintOnSamePage": True, "pattern": "", "cs_condition": "",
         "cs_styleId": "", "cs_bold": False, "cs_italic": False, "cs_underline": False,
         "cs_horizontalAlignment": "left", "cs_verticalAlignment": "top", "cs_textColor": "#000000",
         "cs_backgroundColor": "", "cs_font": "helvetica", "cs_fontSize": 12, "cs_lineSpacing": 1,
         "cs_borderColor": "#000000", "cs_borderWidth": "1", "cs_borderAll": False, "cs_borderLeft": False,
         "cs_borderTop": False, "cs_borderRight": False, "cs_borderBottom": False, "cs_paddingLeft": 2,
         "cs_paddingTop": 2, "cs_paddingRight": 2, "cs_paddingBottom": 2, "spreadsheet_hide": False,
         "spreadsheet_column": "", "spreadsheet_colspan": "", "spreadsheet_addEmptyRow": False}], "parameters": [
        {"id": 1, "name": "page_count", "type": "number", "arrayItemType": "string", "eval": False, "nullable": False,
         "pattern": "", "expression": "", "showOnlyNameType": True, "testData": ""},
        {"id": 2, "name": "page_number", "type": "number", "arrayItemType": "string", "eval": False, "nullable": False,
         "pattern": "", "expression": "", "showOnlyNameType": True, "testData": ""},
        {"id": 9, "name": "current_date", "type": "date", "arrayItemType": "string", "eval": False, "nullable": False,
         "pattern": "d. MMMM yyyy, H:mm", "expression": "", "showOnlyNameType": False, "testData": ""},
        {"id": 10, "name": "year", "type": "number", "arrayItemType": "string", "eval": False, "nullable": True,
         "pattern": "0", "expression": "", "showOnlyNameType": False, "testData": ""},
        {"id": 12, "name": "albums", "type": "array", "arrayItemType": "string", "eval": False, "nullable": False,
         "pattern": "", "expression": "", "showOnlyNameType": False,
         "testData": "[{\"name\":\"¿Dónde Jugarán las Niñas?\",\"artist\":\"Molotov\",\"year\":\"1997\",\"best_of_compilation\":\"\"},{\"name\":\"Big Ones\",\"artist\":\"Aerosmith\",\"year\":\"1995\",\"best_of_compilation\":\"1\"},{\"name\":\"The Greatest Hits\",\"artist\":\"INXS\",\"year\":\"1996\",\"best_of_compilation\":\"true\"},{\"name\":\"Coming Home\",\"artist\":\"Pain\",\"year\":\"2016\",\"best_of_compilation\":\"\"}]",
         "children": [
             {"id": 13, "name": "name", "type": "string", "arrayItemType": "string", "eval": False, "nullable": False,
              "pattern": "", "expression": "", "showOnlyNameType": False, "testData": ""},
             {"id": 14, "name": "artist", "type": "string", "arrayItemType": "string", "eval": False, "nullable": False,
              "pattern": "", "expression": "", "showOnlyNameType": False, "testData": ""},
             {"id": 15, "name": "year", "type": "number", "arrayItemType": "string", "eval": False, "nullable": True,
              "pattern": "", "expression": "", "showOnlyNameType": False, "testData": ""},
             {"id": 16, "name": "best_of_compilation", "type": "boolean", "arrayItemType": "string", "eval": False,
              "nullable": False, "pattern": "", "expression": "", "showOnlyNameType": False, "testData": ""}]}],
                         "styles": [
                             {"id": 33, "name": "Table Header", "bold": True, "italic": False, "underline": False,
                              "horizontalAlignment": "center", "verticalAlignment": "middle", "textColor": "#000000",
                              "backgroundColor": "", "font": "helvetica", "fontSize": "10", "lineSpacing": 1,
                              "borderColor": "#000000", "borderWidth": "1", "borderAll": False, "borderLeft": False,
                              "borderTop": False, "borderRight": False, "borderBottom": False, "paddingLeft": "2",
                              "paddingTop": "2", "paddingRight": "2", "paddingBottom": "2"},
                             {"id": 34, "name": "Table Content", "bold": False, "italic": False, "underline": False,
                              "horizontalAlignment": "left", "verticalAlignment": "middle", "textColor": "#000000",
                              "backgroundColor": "", "font": "helvetica", "fontSize": "9", "lineSpacing": 1,
                              "borderColor": "#000000", "borderWidth": "1", "borderAll": False, "borderLeft": False,
                              "borderTop": False, "borderRight": False, "borderBottom": False, "paddingLeft": "2",
                              "paddingTop": "2", "paddingRight": "2", "paddingBottom": "2"},
                             {"id": 35, "name": "Table Content Highlight", "bold": True, "italic": False,
                              "underline": False, "horizontalAlignment": "center", "verticalAlignment": "middle",
                              "textColor": "#3d85c6", "backgroundColor": "", "font": "helvetica", "fontSize": "9",
                              "lineSpacing": 1, "borderColor": "#000000", "borderWidth": "1", "borderAll": False,
                              "borderLeft": False, "borderTop": False, "borderRight": False, "borderBottom": False,
                              "paddingLeft": "2", "paddingTop": "2", "paddingRight": "2", "paddingBottom": "2"}],
                         "version": 2,
                         "documentProperties": {"pageFormat": "A4", "pageWidth": "", "pageHeight": "", "unit": "mm",
                                                "orientation": "portrait", "contentHeight": "", "marginLeft": "10",
                                                "marginTop": "10", "marginRight": "10", "marginBottom": "10",
                                                "header": True, "headerSize": "80", "headerDisplay": "always",
                                                "footer": True, "footerSize": "30", "footerDisplay": "always",
                                                "patternLocale": "en", "patternCurrencySymbol": "$"}}

    report_number = ReportDefinition.objects.all().count() + 1
    report_type = 'report_'+str(report_number)
    return ReportDefinition.objects.create(
        report_type=report_type, report_definition=json.dumps(report_definition),
        last_modified_at=datetime.datetime.now())


def get_menu_items(controller):
    """Returns application menu items with special class for active menu item."""
    return (
        {'url': reverse('albums:album_index'), 'label': _('menu.albums'),
         'id': 'menu_album', 'class': 'activeMenuItem' if controller == 'album' else ''},
        {'url': reverse('albums:report_edit'), 'label': _('menu.report'),
         'id': 'menu_report', 'class': 'activeMenuItem' if controller == 'report' else ''})


def json_default(obj):
    """Serializes decimal and date values, can be used for json encoder."""
    if isinstance(obj, decimal.Decimal):
        return float(obj)
    if isinstance(obj, datetime.date):
        return str(obj)
    raise TypeError
