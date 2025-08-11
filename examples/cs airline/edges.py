from typing import Literal

from state import CustomerState


def checking_required_data(state: CustomerState) -> Literal["got_flight_number", "try_again"]:
    # Check if flight number exists and is not empty
    if state.get("flight_number") and state.get("flight_number").strip():
        print(f"Got flight number: {state.get('flight_number')}")
        return "got_flight_number"
    else:
        print("Flight number not provided or empty, try again")
        return "try_again"