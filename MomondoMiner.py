import requests, json, time, sys

class MomondoMiner:
    def __init__(self, origin, destination, departure, arrival):
        self.base_url = "http://www.momondo.com/"
        self.flight_search_url = "https://www.momondo.com/api/3.0/FlightSearch/"
        self.origin = origin
        self.destination = destination
        self.departure = departure
        self.arrival = arrival

        self.airlines = []
        self.airports = []
        self.flights = []
        self.legs = []
        self.offers = []
        self.segments = []
        self.ticket_classes = []

        self.flight_search_params = {
            "AdultCount": 1,
            "ChildAges": [

            ],
            "TicketClass": "ECO",
            "Segments": [
                {
                    "Origin": self.origin,
                    "Destination": self.destination,
                    "Depart": "{}T08:00:00.000Z".format(self.departure),
                    "Departure": self.departure
                },
                {
                    "Origin": self.destination,
                    "Destination": self.origin,
                    "Depart": "{}T08:00:00.000Z".format(self.arrival),
                    "Departure": self.arrival
                }
            ],
            "Culture": "en-US",
            "Mix": "Segments",
            "Market": "US",
            "DirectOnly": False,
            "IncludeNearby": False
        }

    def log(self, statement):
        sys.stdout.write(statement)
        sys.stdout.flush()

    def initiate_session(self):
        self.session = requests.Session()
        self.log("Sending base request to {}... ".format(self.base_url))
        r = self.session.get(self.base_url, headers={'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36'})
        self.log(str(r.status_code) + " " + r.reason)
        if r.status_code != 200:
            return False
        else:
            return True

    def get_search_id(self):
        self.log("\nSending flight search request to {}... ".format(self.flight_search_url))
        r = self.session.post(self.flight_search_url, json=self.flight_search_params, headers={'Content-Type' : 'application/json; charset=utf-8'})
        self.log(str(r.status_code) + " " + r.reason)
        if r.status_code != 200:
            return False

        try:
            self.search_id = json.loads(r.text)["SearchId"]
        except:
            return False

        self.log(" SearchID: {}\n".format(self.search_id))

        return True

    def mine(self):
        while True:
            self.log("Querying search...")
            r = self.session.get(self.flight_search_url + self.search_id + '/0/true')
            self.log(str(r.status_code) + " " + r.reason)
            if r.status_code != 200:
                return False

            flight_search_response = json.loads(r.text)

            if flight_search_response["Airlines"] != None:
                self.airlines.extend(flight_search_response["Airlines"])

            if flight_search_response["Airports"] != None:
                self.airports.extend(flight_search_response["Airports"])

            if flight_search_response["Flights"] != None:
                self.flights.extend(flight_search_response["Flights"])

            if flight_search_response["Legs"] != None:
                self.legs.extend(flight_search_response["Legs"])

            if flight_search_response["Offers"] != None:
                self.offers.extend(flight_search_response["Offers"])

            if flight_search_response["Segments"] != None:
                self.segments.extend(flight_search_response["Segments"])

            if flight_search_response["TicketClasses"] != None:
                self.ticket_classes.extend(flight_search_response["TicketClasses"])

            self.log(" Done: {}\n".format(flight_search_response["Done"]))

            if flight_search_response["Done"] == True:
                print "Finished query."
                break

            time.sleep(5)

        self.summary = json.loads(r.text)["Summary"]

        return True

    def process_offer(self, offer_index):
        offer = self.offers[offer_index]

        payload = {
            "origin" : self.origin,
            "destination" : self.destination,
            "departure" : self.departure,
            "arrival" : self.arrival,
            "adult_price" : offer["AdultPrice"],
            "total_price" : offer["TotalPrice"],
            "currency_type" : offer["Currency"],
            "offer_url" : offer["Deeplink"],
            "journey_segments" : []
        }

        flight = self.flights[offer["FlightIndex"]]
        segment_indices = flight["SegmentIndexes"]

        for i in xrange(0, len(segment_indices)):
            current_segment = self.segments[segment_indices[i]]
            leg_indices = current_segment["LegIndexes"]

            payload_segment = {
                "segment_duration" : current_segment["Duration"],
                "segment_stops" : current_segment["Stops"],
                "segment_legs" : []
            }

            for j in xrange(0, len(leg_indices)):
                current_leg = self.legs[leg_indices[j]]

                payload_leg = {
                    "leg_arrival" : current_leg["Arrival"],
                    "leg_departure" : current_leg["Departure"],
                    "leg_duration" : current_leg["Duration"],
                    "flight_number" : current_leg["FlightNumber"],
                    "airline_name" : self.airlines[current_leg["AirlineIndex"]]["Name"]
                }

                payload_segment["segment_legs"].append(payload_leg)
            payload["journey_segments"].append(payload_segment)

        return payload

    def get_cheapest_offer(self):
        return self.process_offer(self.summary["CheapestOfferIndex"])

    def get_fastest_offer(self):
        return self.process_offer(self.summary["FastestOfferIndex"])

    def get_best_offer(self):
        return self.process_offer(self.summary["BestOfferIndex"])
