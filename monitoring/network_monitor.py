import time


class NetworkMonitor:

    def __init__(self):

        self.paths = {
            "Path A": [
                "s1-eth2",
                "s2-eth1",
                "s2-eth2",
                "s4-eth1"
            ],
            "Path B": [
                "s1-eth3",
                "s3-eth1",
                "s3-eth2",
                "s4-eth2"
            ]
        }

        self.capacities = {
            "Path A": 50,
            "Path B": 60
        }

    # -------------------------------------------------
    # CONVERT BYTES/SECOND TO Mbps
    # -------------------------------------------------

    def bytes_to_mbps(self, bytes_per_second):

        return (
            bytes_per_second * 8
        ) / 1_000_000

    # -------------------------------------------------
    # READ INTERFACE STATISTICS
    # -------------------------------------------------

    def get_stats(self, interface):

        rx_path = (
            f"/sys/class/net/{interface}/statistics/rx_bytes"
        )

        tx_path = (
            f"/sys/class/net/{interface}/statistics/tx_bytes"
        )

        try:

            with open(rx_path, "r") as file:
                rx_bytes = int(file.read())

            with open(tx_path, "r") as file:
                tx_bytes = int(file.read())

            return rx_bytes, tx_bytes

        except FileNotFoundError:

            return None, None

    # -------------------------------------------------
    # STATUS
    # -------------------------------------------------

    def get_status(self, utilization):

        if utilization < 60:
            return "LOW"

        elif utilization < 80:
            return "MEDIUM"

        else:
            return "HIGH"

    # -------------------------------------------------
    # GET ONE LIVE MEASUREMENT
    # -------------------------------------------------

    def get_live_utilization(self, interval=1):

        previous = {}

        # Take first snapshot
        for interfaces in self.paths.values():

            for interface in interfaces:

                previous[interface] = (
                    self.get_stats(interface)
                )

        # Wait for measurement interval
        time.sleep(interval)

        utilization = {}

        # Take second snapshot
        for path_name, interfaces in self.paths.items():

            rx_rates = []
            tx_rates = []

            for interface in interfaces:

                current = self.get_stats(interface)

                if current[0] is None:
                    continue

                previous_rx, previous_tx = (
                    previous[interface]
                )

                rx_rate = (
                    current[0] - previous_rx
                )

                tx_rate = (
                    current[1] - previous_tx
                )

                rx_mbps = self.bytes_to_mbps(
                    rx_rate
                )

                tx_mbps = self.bytes_to_mbps(
                    tx_rate
                )

                rx_rates.append(rx_mbps)
                tx_rates.append(tx_mbps)

            # No data available
            if not rx_rates:

                continue

            # Average traffic across path interfaces
            path_rx_mbps = (
                sum(rx_rates) / len(rx_rates)
            )

            path_tx_mbps = (
                sum(tx_rates) / len(tx_rates)
            )

            capacity = self.capacities[path_name]

            # Utilization based on RX traffic
            path_utilization = (
                path_rx_mbps / capacity
            ) * 100

            # Convert Path A / Path B
            short_name = path_name[-1]

            utilization[short_name] = {
                "rx_mbps": path_rx_mbps,
                "tx_mbps": path_tx_mbps,
                "capacity": capacity,
                "utilization": path_utilization,
                "status": self.get_status(
                    path_utilization
                )
            }

        return utilization

    # -------------------------------------------------
    # PRINT ONE LIVE MEASUREMENT
    # -------------------------------------------------

    def show_live_utilization(self, interval=1):

        data = self.get_live_utilization(interval)

        print("\nLive Network Utilization")
        print("=" * 60)

        for path_name in ["A", "B"]:

            if path_name not in data:

                print(
                    f"Path {path_name}: "
                    f"No interface data"
                )

                continue

            path = data[path_name]

            print(
                f"Path {path_name}: "
                f"Traffic={path['rx_mbps']:.2f} Mbps | "
                f"Capacity={path['capacity']} Mbps | "
                f"Utilization="
                f"{path['utilization']:.2f}% | "
                f"Status={path['status']}"
            )

        return data

    # -------------------------------------------------
    # CONTINUOUS MONITOR
    # -------------------------------------------------

    def monitor(self, interval=1):

        print("\nNetwork Path Monitor")
        print("=" * 60)

        try:

            while True:

                data = self.get_live_utilization(
                    interval
                )

                for path_name in ["A", "B"]:

                    print(
                        f"\nPath {path_name}"
                    )

                    print("-" * 60)

                    if path_name not in data:

                        print(
                            "No interface data available"
                        )

                        continue

                    path = data[path_name]

                    print(
                        f"TRAFFIC: "
                        f"RX={path['rx_mbps']:.2f} Mbps | "
                        f"TX={path['tx_mbps']:.2f} Mbps"
                    )

                    print(
                        f"CAPACITY: "
                        f"{path['capacity']} Mbps"
                    )

                    print(
                        f"UTILIZATION: "
                        f"{path['utilization']:.2f}% | "
                        f"Status={path['status']}"
                    )

        except KeyboardInterrupt:

            print(
                "\nMonitoring stopped."
            )


if __name__ == "__main__":

    monitor = NetworkMonitor()

    monitor.monitor()
