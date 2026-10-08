from resource_manager.path_manager import PathManager
from monitoring.network_monitor import NetworkMonitor
from controller.controller import SDNController


class DecisionEngine:

    def __init__(self):

        self.manager = PathManager()
        self.monitor = NetworkMonitor()
        self.controller = SDNController()

        self.live_utilization = {
            "A": 0.0,
            "B": 0.0
        }

    # ==================================================
    # LIVE UTILIZATION
    # ==================================================

    def update_live_utilization(self):

        data = self.monitor.show_live_utilization(1)

        if not data:

            print(
                "\nUnable to obtain live network utilization."
            )

            return False

        self.live_utilization["A"] = (
            data["A"]["utilization"]
        )

        self.live_utilization["B"] = (
            data["B"]["utilization"]
        )

        return True

    # ==================================================
    # EFFECTIVE UTILIZATION
    # ==================================================

    def get_effective_utilization(self, path_name):

        live = self.live_utilization[path_name]

        path = self.manager.paths[path_name]

        leased = path["used"]

        capacity = path["bandwidth"]

        leased_percentage = (
            leased / capacity
        ) * 100

        return live + leased_percentage

    # ==================================================
    # PATH STATUS
    # ==================================================

    def show_path_status(self):

        print("\nPath Decision Status")
        print("=" * 60)

        for name, path in self.manager.paths.items():

            live = self.live_utilization[name]

            capacity = path["bandwidth"]

            leased = path["used"]

            effective = (
                self.get_effective_utilization(name)
            )

            available = capacity * (
                1 - effective / 100
            )

            if effective < 60:

                status = "LOW"

            elif effective < 80:

                status = "MEDIUM"

            else:

                status = "HIGH"

            print(
                f"Path {name}: "
                f"Capacity={capacity} Mbps | "
                f"Live Utilization={live:.2f}% | "
                f"Leased={leased} Mbps | "
                f"Effective Utilization={effective:.2f}% | "
                f"Estimated Available={available:.2f} Mbps | "
                f"Status={status}"
            )

    # ==================================================
    # SELECT PATH
    # ==================================================

    def decide_path(self, required_bandwidth):

        candidates = []

        for name, path in self.manager.paths.items():

            capacity = path["bandwidth"]

            effective = (
                self.get_effective_utilization(name)
            )

            available = capacity * (
                1 - effective / 100
            )

            if available >= required_bandwidth:

                candidates.append(
                    (
                        name,
                        effective,
                        available
                    )
                )

        if not candidates:

            print(
                f"\nRequest {required_bandwidth} Mbps "
                f"→ NO PATH AVAILABLE"
            )

            return None

        # Lowest effective utilization wins
        candidates.sort(
            key=lambda item: item[1]
        )

        selected = candidates[0]

        selected_path = selected[0]
        utilization = selected[1]
        available = selected[2]

        print(
            f"\nRequest {required_bandwidth} Mbps "
            f"→ Selected Path {selected_path}"
        )

        print(
            f"Effective utilization: "
            f"{utilization:.2f}%"
        )

        print(
            f"Estimated available bandwidth: "
            f"{available:.2f} Mbps"
        )

        return selected_path

    # ==================================================
    # ALLOCATE REQUEST
    # ==================================================

    def allocate_request(
        self,
        request_id,
        bandwidth
    ):

        print(
            "\nUpdating live network utilization..."
        )

        if not self.update_live_utilization():

            return None

        self.show_path_status()

        selected_path = self.decide_path(
            bandwidth
        )

        if selected_path is None:

            print(
                f"Request {request_id}: "
                f"REJECTED"
            )

            return None

        result = self.manager.allocate(
            request_id,
            bandwidth,
            selected_path
        )

        if result is None:

            return None

        print(
            f"SDN Controller: "
            f"Activating Path {selected_path}"
        )

        self.controller.select_path(
            selected_path
        )

        print(
            f"Network path switched to "
            f"Path {selected_path}"
        )

        self.show_path_status()

        return result

    # ==================================================
    # RELEASE REQUEST
    # ==================================================

    def release_request(
        self,
        request_id
    ):

        print(
            f"\nReleasing Request {request_id}"
        )

        result = self.manager.release_request(
            request_id
        )

        if result is None:

            print(
                f"Request {request_id}: "
                f"NOT FOUND"
            )

            return False

        path_name = result["path"]

        bandwidth = result["bandwidth"]

        print(
            f"Request {request_id}: "
            f"{bandwidth} Mbps released "
            f"from Path {path_name}"
        )

        self.show_path_status()

        return True

    # ==================================================
    # FIND MIGRATION TARGET
    # ==================================================

    def find_migration_path(
        self,
        current_path,
        bandwidth
    ):

        candidates = []

        for name, path in self.manager.paths.items():

            if name == current_path:
                continue

            if path["status"] != "available":
                continue

            effective = (
                self.get_effective_utilization(name)
            )

            capacity = path["bandwidth"]

            available = capacity * (
                1 - effective / 100
            )

            if available >= bandwidth:

                candidates.append(
                    (
                        name,
                        effective,
                        available
                    )
                )

        if not candidates:

            return None

        candidates.sort(
            key=lambda item: item[1]
        )

        return candidates[0][0]

    # ==================================================
    # MIGRATE ONE REQUEST
    # ==================================================

    def migrate_request(
        self,
        request_id
    ):

        # ----------------------------------------------
        # Find existing lease
        # ----------------------------------------------

        if request_id not in self.manager.leases:

            print(
                f"\nRequest {request_id}: "
                f"Lease not found"
            )

            return False

        lease = self.manager.leases[request_id]

        current_path = lease["path"]

        bandwidth = lease["bandwidth"]

        print(
            f"\nMigration check for {request_id}"
        )

        print(
            f"Current Path: {current_path}"
        )

        print(
            f"Bandwidth: {bandwidth} Mbps"
        )

        # ----------------------------------------------
        # Find destination
        # ----------------------------------------------

        target_path = self.find_migration_path(
            current_path,
            bandwidth
        )

        if target_path is None:

            print(
                "No suitable migration path available."
            )

            return False

        # ----------------------------------------------
        # Do not migrate unnecessarily
        # ----------------------------------------------

        if target_path == current_path:

            print(
                f"{request_id} already on "
                f"best path."
            )

            return False

        print(
            f"\nMigrating {request_id}: "
            f"{current_path} → {target_path}"
        )

        # ----------------------------------------------
        # Release old path
        # ----------------------------------------------

        self.manager.release_request(
            request_id
        )

        # ----------------------------------------------
        # Allocate destination
        # ----------------------------------------------

        result = self.manager.allocate(
            request_id,
            bandwidth,
            target_path
        )

        if result is None:

            print(
                "\nMigration failed."
            )

            return False

        # ----------------------------------------------
        # Reconfigure SDN path
        # ----------------------------------------------

        print(
            f"\nSDN Controller: "
            f"Activating Path {target_path}"
        )

        self.controller.select_path(
            target_path
        )

        print(
            f"Network path migrated to "
            f"Path {target_path}"
        )

        self.show_path_status()

        return True

    # ==================================================
    # AUTOMATIC MIGRATION CHECK
    # ==================================================

    # ==================================================
    # AUTOMATIC MIGRATION CHECK
    # ==================================================

    def check_and_migrate(self):

        print(
            "\nChecking for congested paths..."
        )

        if not self.update_live_utilization():
            return

        self.show_path_status()

        migrations = []

        # ----------------------------------------------
        # Find requests on HIGH paths
        # ----------------------------------------------

        for request_id, lease in list(
            self.manager.leases.items()
        ):

            current_path = lease["path"]

            effective = (
                self.get_effective_utilization(
                    current_path
                )
            )

            # Migrate only requests on HIGH paths
            if effective >= 80:

                migrations.append(
                    request_id
                )

        if not migrations:

            print(
                "\nNo migration required."
            )

            return

        # ----------------------------------------------
        # Perform migrations
        # ----------------------------------------------

        for request_id in migrations:

            # Request may already have been migrated
            if request_id not in self.manager.leases:
                continue

            print(
                f"\nCongestion detected for "
                f"Request {request_id}"
            )

            migrated = self.migrate_request(
                request_id
            )

            if migrated:

                print(
                    f"\nMigration completed for "
                    f"{request_id}"
                )

            else:

                print(
                    f"\nMigration not performed for "
                    f"{request_id}"
                )

        # ----------------------------------------------
        # Final state after migration
        # ----------------------------------------------

        print(
            "\nFinal Path Status After Migration"
        )

        self.show_path_status()

        print(
            "\nActive Bandwidth Leases"
        )

        self.manager.show_leases()

# ======================================================
# TEST
# ======================================================

if __name__ == "__main__":

    engine = DecisionEngine()

    # Initial status
    engine.update_live_utilization()
    engine.show_path_status()

    # Allocate R1
    engine.allocate_request(
        "R1",
        10
    )

    # Allocate R2
    engine.allocate_request(
        "R2",
        10
    )

    # Show leases
    engine.manager.show_leases()

    # Check for migration
    engine.check_and_migrate()
