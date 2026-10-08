class PathManager:

    def __init__(self):

        self.paths = {
            "A": {
                "bandwidth": 50,
                "used": 0,
                "delay": 10,
                "status": "available"
            },
            "B": {
                "bandwidth": 60,
                "used": 0,
                "delay": 15,
                "status": "available"
            }
        }

        # request_id -> allocation information
        self.leases = {}

    def show_paths(self):

        print("\nCurrent Network Resources")
        print("-" * 60)

        for name, path in self.paths.items():

            available = (
                path["bandwidth"] - path["used"]
            )

            utilization = (
                path["used"] / path["bandwidth"]
            ) * 100

            print(
                f"Path {name}: "
                f"Capacity={path['bandwidth']} Mbps | "
                f"Used={path['used']} Mbps | "
                f"Available={available} Mbps | "
                f"Utilization={utilization:.2f}% | "
                f"Delay={path['delay']} ms"
            )

    def allocate(
        self,
        request_id,
        required_bandwidth,
        selected_path=None
    ):

        # Prevent duplicate request allocation
        if request_id in self.leases:

            print(
                f"\nRequest {request_id} already allocated."
            )

            return self.leases[request_id]["path"]

        # If no path is provided, find one
        if selected_path is None:

            candidates = []

            for name, path in self.paths.items():

                available = (
                    path["bandwidth"] - path["used"]
                )

                if (
                    path["status"] == "available"
                    and available >= required_bandwidth
                ):
                    candidates.append(name)

            if not candidates:

                print(
                    f"\nRequest {request_id}: "
                    f"{required_bandwidth} Mbps → REJECTED"
                )

                return None

            # Choose path with maximum available bandwidth
            selected_path = max(
                candidates,
                key=lambda name:
                self.paths[name]["bandwidth"]
                - self.paths[name]["used"]
            )

        # Validate path
        if selected_path not in self.paths:

            print(
                f"\nRequest {request_id}: "
                f"Invalid Path"
            )

            return None

        path = self.paths[selected_path]

        available = (
            path["bandwidth"] - path["used"]
        )

        if path["status"] != "available":

            print(
                f"\nRequest {request_id}: "
                f"Path {selected_path} unavailable"
            )

            return None

        if available < required_bandwidth:

            print(
                f"\nRequest {request_id}: "
                f"Path {selected_path} does not "
                f"have enough bandwidth"
            )

            return None

        # Allocate
        path["used"] += required_bandwidth

        # Save lease
        self.leases[request_id] = {
            "path": selected_path,
            "bandwidth": required_bandwidth
        }

        return selected_path

    def release(self, request_id):

        if request_id not in self.leases:

            print(
                f"\nRequest {request_id}: "
                f"No active lease"
            )

            return False

        lease = self.leases[request_id]

        path_name = lease["path"]
        bandwidth = lease["bandwidth"]

        self.paths[path_name]["used"] -= bandwidth

        if self.paths[path_name]["used"] < 0:
            self.paths[path_name]["used"] = 0

        del self.leases[request_id]

        print(
            f"\nRequest {request_id} RELEASED"
        )

        print(
            f"Returned {bandwidth} Mbps "
            f"to Path {path_name}"
        )

        return True

    def show_leases(self):

        print("\nActive Bandwidth Leases")
        print("-" * 60)

        if not self.leases:

            print("No active leases")
            return

        for request_id, lease in self.leases.items():

            print(
                f"{request_id}: "
                f"Path {lease['path']} | "
                f"Bandwidth={lease['bandwidth']} Mbps"
            )

    def get_congestion_status(self, path_name):

        path = self.paths[path_name]

        utilization = (
            path["used"] /
            path["bandwidth"]
        ) * 100

        if utilization < 60:
            status = "LOW"

        elif utilization < 80:
            status = "MEDIUM"

        else:
            status = "HIGH"

        return utilization, status

    def choose_least_utilized_path(self):

        best_path = None
        lowest_utilization = float("inf")

        for name, path in self.paths.items():

            if path["status"] != "available":
                continue

            utilization = (
                path["used"] /
                path["bandwidth"]
            ) * 100

            if utilization < lowest_utilization:

                lowest_utilization = utilization
                best_path = name

        return best_path, lowest_utilization

    def release_request(self, request_id):
        """
        Release a bandwidth lease using the request ID.
        """

        if request_id not in self.leases:
            print(
                f"\nRequest {request_id}: "
                f"No active lease found"
            )
            return False

        lease = self.leases[request_id]

        path_name = lease["path"]
        bandwidth = lease["bandwidth"]

        if path_name not in self.paths:
            print(
                f"\nRequest {request_id}: "
                f"Invalid path {path_name}"
            )
            return False

        self.paths[path_name]["used"] -= bandwidth

        if self.paths[path_name]["used"] < 0:
            self.paths[path_name]["used"] = 0

        del self.leases[request_id]

        print(
            f"\nRequest {request_id} RELEASED"
        )

        print(
            f"Returned {bandwidth} Mbps "
            f"to Path {path_name}"
        )

        return True
if __name__ == "__main__":

    manager = PathManager()

    manager.show_paths()

    manager.allocate("R1", 25, "A")
    manager.allocate("R2", 10, "B")

    manager.show_paths()

    manager.show_leases()

    manager.release("R1")

    manager.show_paths()
    manager.show_leases()
