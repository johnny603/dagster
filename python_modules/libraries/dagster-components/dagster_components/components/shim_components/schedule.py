from dagster_components.components.shim_components.base import ShimComponent, ShimScaffolder
from dagster_components.scaffold import scaffold_with


class ScheduleScaffolder(ShimScaffolder):
    def get_text(self, filename: str) -> str:
        return f"""# import dagster as dg
# 
#
# @dg.schedule(cron_schedule=..., target=...)
# def {filename}(context: dg.ScheduleEvaluationContext): ...

"""


@scaffold_with(ScheduleScaffolder)
class RawScheduleComponent(ShimComponent):
    """Schedule component."""
