from fastapi import FastAPI
from pydantic import BaseModel
import  uvicorn

app = FastAPI()

# Define product availability at each center
WAREHOUSES = {
    "C1": {"A", "B", "C"},
    "C2": {"D", "E", "F"},
    "C3": {"G", "H", "I"},
}

# Define distances between centers and L1
DISTANCES = {
    "C1-L1": 3,
    "C2-L1": 2.5,
    "C3-L1": 2,
    "C1-C2": 4,
    "C1-C3": 3,
    "C2-C3": 2.5,
}

# Define vehicle running cost based on weight
VEHICLE_COST_BASE = 10  # Cost per unit distance for 0-5 kg
VEHICLE_COST_ADDITIONAL = 8  # Cost per unit distance for every additional 5 kg


def calculate_vehicle_cost(weight):
    if weight <= 5:
        return VEHICLE_COST_BASE
    additional_weight = max(0, weight - 5)
    additional_cost = ((additional_weight + 4) // 5) * VEHICLE_COST_ADDITIONAL  # Round up every extra 5 kg
    return VEHICLE_COST_BASE + additional_cost


# Define product weights
PRODUCT_WEIGHTS = {
    "A": 3, "B": 2, "C": 8,
    "D": 12, "E": 25, "F": 15,
    "G": 0.5, "H": 1, "I": 2,
}


class Order(BaseModel):
    A: int = 0
    B: int = 0
    C: int = 0
    D: int = 0
    E: int = 0
    F: int = 0
    G: int = 0
    H: int = 0
    I: int = 0


@app.post("/calculate_cost")
def calculate_cost(order: Order):
    order_dict = order.dict()
    required_items = {item: qty for item, qty in order_dict.items() if qty > 0}

    # Identify the warehouses needed
    used_centers = {center for center, products in WAREHOUSES.items() if any(p in products for p in required_items)}

    # Calculate total weight of the order
    total_weight = sum(PRODUCT_WEIGHTS[item] * qty for item, qty in required_items.items())

    # Determine the applicable vehicle running cost
    vehicle_cost_per_unit = calculate_vehicle_cost(total_weight)

    # If only one center is used, cost is straightforward
    if len(used_centers) == 1:
        start_center = list(used_centers)[0]
        total_cost = DISTANCES[f"{start_center}-L1"] * vehicle_cost_per_unit
        return {"minimum_cost": total_cost}

    # Otherwise, find the optimal route
    best_cost = float('inf')
    for start in used_centers:
        cost = DISTANCES[f"{start}-L1"] * vehicle_cost_per_unit
        other_centers = used_centers - {start}
        for other in other_centers:
            cost += DISTANCES.get(f"{start}-{other}", DISTANCES.get(f"{other}-{start}", 0)) * vehicle_cost_per_unit
        best_cost = min(best_cost, cost)

    return {"minimum_cost": best_cost}


if __name__ == "__main__":
    uvicorn.run(app,port=8000, host='0.0.0.0')
