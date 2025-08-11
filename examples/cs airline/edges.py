from typing import Literal

from state import CustomerState


def checking_required_data(state: CustomerState) -> Literal["got_flight_number", "try_again"]:
    if state.get("flight_number") == "win":
        print("Got flight number, continue")
        return "got_flight_number"
    else:
        print("Flight number not provided, try again")
        return "try_again"