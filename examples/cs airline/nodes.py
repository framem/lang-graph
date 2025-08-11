from state import CustomerState

def Triage(state: CustomerState):
    print("triage")
    return state

def AskForFlightNumber(state: CustomerState):
    flight_number = "A-123"
    print("buy number: " + str(flight_number))
    state['flight_number'] = flight_number
    return state

def GetFlightDetails(state: CustomerState):
    print("flight details")
    return state