import json
from openpyxl import Workbook
from MomondoMiner import MomondoMiner

if __name__ == "__main__":
    m = MomondoMiner("SFO", "LAX", "2017-12-24", "2017-12-27")
    m.initiate_session()
    m.get_search_id()
    m.mine()
    data = m.get_best_offer()

    print json.dumps(data, indent=4, sort_keys=True)
    print "\nGenerating workbook file..."

    wb = Workbook()
    ws = wb.active
    ws.title = "MomondoMiner"

    ws['A1'] = "Airline"
    ws['B1'] = "Origin"
    ws['C1'] = "Destination"
    ws['D1'] = "Departure Date"
    ws['E1'] = "Return Date"
    ws['F1'] = "Total Price"
    ws['G1'] = "Currency"
    ws['H1'] = "Departure Duration"
    ws['I1'] = "Return Duration"
    ws['J1'] = "Departure Stops"
    ws['K1'] = "Return Stops"
    ws['L1'] = "URL"

    ws['A2'] = data["journey_segments"][0]["segment_legs"][0]["airline_name"]
    ws['B2'] = data["origin"]
    ws['C2'] = data["destination"]
    ws['D2'] = data["departure"]
    ws['E2'] = data["arrival"]
    ws['F2'] = data["total_price"]
    ws['G2'] = data["currency_type"]
    ws['H2'] = data["journey_segments"][0]["segment_duration"]
    ws['I2'] = data["journey_segments"][1]["segment_duration"]
    ws['J2'] = data["journey_segments"][0]["segment_stops"]
    ws['K2'] = data["journey_segments"][1]["segment_stops"]
    ws['L2'] = data["offer_url"]

    wb.save("MomondoMiner.xlsx")

    print "Done!"
