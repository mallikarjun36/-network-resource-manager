import subprocess


class SDNController:

    def __init__(self):
        self.current_path = None

    def add_flow(self, switch, flow):
        cmd = [
            "sudo",
            "ovs-ofctl",
            "add-flow",
            switch,
            flow
        ]

        subprocess.run(cmd, check=True)

    def delete_path_flows(self):
        """
        Remove only IP forwarding flows installed by this controller.
        The default NORMAL flow is preserved.
        """

        print("\nRemoving existing path flows...")

        for switch in ["s1", "s2", "s3", "s4"]:

            cmd = [
                "sudo",
                "ovs-ofctl",
                "del-flows",
                switch,
                "ip"
            ]

            subprocess.run(
                cmd,
                check=False
            )

    def setup_path_a(self):

        print("\nSetting Path A...")
        print("h1 -> s1 -> s2 -> s4 -> h2")

        # -------------------------------------------------
        # Forward direction
        # h1 -> s1 -> s2 -> s4 -> h2
        # -------------------------------------------------

        # s1: h1 -> s2
        self.add_flow(
            "s1",
            "priority=100,ip,"
            "nw_src=10.0.0.1,"
            "nw_dst=10.0.0.2,"
            "actions=output:2"
        )

        # s2: s1 -> s4
        self.add_flow(
            "s2",
            "priority=100,ip,"
            "nw_src=10.0.0.1,"
            "nw_dst=10.0.0.2,"
            "actions=output:2"
        )

        # s4: s2 -> h2
        self.add_flow(
            "s4",
            "priority=100,ip,"
            "nw_src=10.0.0.1,"
            "nw_dst=10.0.0.2,"
            "actions=output:3"
        )

        # -------------------------------------------------
        # Reverse direction
        # h2 -> s4 -> s2 -> s1 -> h1
        # -------------------------------------------------

        # s4: h2 -> s2
        self.add_flow(
            "s4",
            "priority=100,ip,"
            "nw_src=10.0.0.2,"
            "nw_dst=10.0.0.1,"
            "actions=output:1"
        )

        # s2: s4 -> s1
        self.add_flow(
            "s2",
            "priority=100,ip,"
            "nw_src=10.0.0.2,"
            "nw_dst=10.0.0.1,"
            "actions=output:1"
        )

        # s1: s2 -> h1
        self.add_flow(
            "s1",
            "priority=100,ip,"
            "nw_src=10.0.0.2,"
            "nw_dst=10.0.0.1,"
            "actions=output:1"
        )

        self.current_path = "A"

        print("Path A configured.")

    def setup_path_b(self):

        print("\nSetting Path B...")
        print("h1 -> s1 -> s3 -> s4 -> h2")

        # -------------------------------------------------
        # Forward direction
        # h1 -> s1 -> s3 -> s4 -> h2
        # -------------------------------------------------

        # s1: h1 -> s3
        self.add_flow(
            "s1",
            "priority=100,ip,"
            "nw_src=10.0.0.1,"
            "nw_dst=10.0.0.2,"
            "actions=output:3"
        )

        # s3: s1 -> s4
        self.add_flow(
            "s3",
            "priority=100,ip,"
            "nw_src=10.0.0.1,"
            "nw_dst=10.0.0.2,"
            "actions=output:2"
        )

        # s4: s3 -> h2
        self.add_flow(
            "s4",
            "priority=100,ip,"
            "nw_src=10.0.0.1,"
            "nw_dst=10.0.0.2,"
            "actions=output:3"
        )

        # -------------------------------------------------
        # Reverse direction
        # h2 -> s4 -> s3 -> s1 -> h1
        # -------------------------------------------------

        # s4: h2 -> s3
        self.add_flow(
            "s4",
            "priority=100,ip,"
            "nw_src=10.0.0.2,"
            "nw_dst=10.0.0.1,"
            "actions=output:2"
        )

        # s3: s4 -> s1
        self.add_flow(
            "s3",
            "priority=100,ip,"
            "nw_src=10.0.0.2,"
            "nw_dst=10.0.0.1,"
            "actions=output:1"
        )

        # s1: s3 -> h1
        self.add_flow(
            "s1",
            "priority=100,ip,"
            "nw_src=10.0.0.2,"
            "nw_dst=10.0.0.1,"
            "actions=output:1"
        )

        self.current_path = "B"

        print("Path B configured.")

    def select_path(self, path):

        if path not in ["A", "B"]:
            print(f"Invalid path: {path}")
            return False

        if self.current_path == path:
            print(f"\nPath {path} is already active.")
            return True

        self.delete_path_flows()

        if path == "A":
            self.setup_path_a()
        else:
            self.setup_path_b()

        return True

    def show_status(self):

        print("\nController Status")
        print("=" * 50)

        if self.current_path:
            print(f"Active Path: {self.current_path}")
        else:
            print("Active Path: NONE")


if __name__ == "__main__":

    controller = SDNController()

    print("\nSDN Path Controller")
    print("=" * 50)

    # Start with Path A
    controller.setup_path_a()

    controller.show_status()
