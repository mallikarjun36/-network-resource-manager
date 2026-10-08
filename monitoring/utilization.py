class UtilizationCalculator:
    def __init__(self):
        self.capacities = {
            "Path A": 50,
            "Path B": 30
        }

    def calculate(self, path_name, traffic_mbps):
        capacity = self.capacities[path_name]

        utilization = (traffic_mbps / capacity) * 100

        if utilization < 60:
            status = "LOW"
        elif utilization < 80:
            status = "MEDIUM"
        else:
            status = "HIGH"

        return utilization, status


if __name__ == "__main__":
    calculator = UtilizationCalculator()

    test_data = {
        "Path A": 20,
        "Path B": 25
    }

    print("\nPath Utilization")
    print("-" * 40)

    for path, traffic in test_data.items():
        utilization, status = calculator.calculate(
            path,
            traffic
        )

        print(
            f"{path}: "
            f"{traffic} Mbps / "
            f"{calculator.capacities[path]} Mbps "
            f"= {utilization:.2f}% "
            f"({status})"
        )
