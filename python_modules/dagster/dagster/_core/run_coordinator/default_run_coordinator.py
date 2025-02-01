from dagster._core.run_coordinator.synchronous_launch_run_coordinator import (
    SynchronousLaunchRunCoordinator,
)

# for backwards compatibility, we need to keep the old DefaultRunCoordinator
DefaultRunCoordinator = SynchronousLaunchRunCoordinator
