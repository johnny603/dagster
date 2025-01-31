from dataclasses import dataclass, replace
from datetime import datetime
from typing import Generic, Optional, Union

import dagster._check as check
from dagster._check.functions import CheckError
from dagster._core.definitions.asset_key import T_EntityKey
from dagster._core.definitions.events import AssetKeyPartitionKey
from dagster._core.definitions.partition import (
    AllPartitionsSubset,
    PartitionsDefinition,
    PartitionsSubset,
)
from dagster._core.definitions.time_window_partitions import (
    TimeWindowPartitionsDefinition,
    TimeWindowPartitionsSubset,
)
from dagster._core.instance import DynamicPartitionsStore
from dagster._serdes.serdes import DataclassSerializer, whitelist_for_serdes

EntitySubsetValue = Union[bool, PartitionsSubset]


class EntitySubsetSerializer(DataclassSerializer):
    """Ensures that the inner PartitionsSubset is converted to a serializable form if necessary."""

    def get_storage_name(self) -> str:
        # backcompat
        return "AssetSubset"

    def before_pack(self, value: "SerializableEntitySubset") -> "SerializableEntitySubset":
        if value.is_partitioned:
            return replace(value, value=value.subset_value.to_serializable_subset())
        return value


@whitelist_for_serdes(
    serializer=EntitySubsetSerializer,
    storage_field_names={"key": "asset_key"},
    old_storage_names={"AssetSubset"},
)
@dataclass(frozen=True)
class SerializableEntitySubset(Generic[T_EntityKey]):
    """Represents a serializable subset of a given EntityKey."""

    key: T_EntityKey
    value: EntitySubsetValue

    @property
    def is_partitioned(self) -> bool:
        return not isinstance(self.value, bool)

    @property
    def bool_value(self) -> bool:
        return check.inst(self.value, bool)

    @property
    def subset_value(self) -> PartitionsSubset:
        return check.inst(self.value, PartitionsSubset)

    @property
    def size(self) -> int:
        if not self.is_partitioned:
            return int(self.bool_value)
        else:
            return len(self.subset_value)

    @property
    def is_empty(self) -> bool:
        if self.is_partitioned:
            return self.subset_value.is_empty
        else:
            return not self.bool_value

    def with_asset_graph_partitions_def(
        self,
        partitions_def: Optional[PartitionsDefinition],
        current_time: Optional[datetime],
        dynamic_partitions_store: Optional[DynamicPartitionsStore],
    ) -> "SerializableEntitySubset":
        """Used to transform a persisted SerializableEntitySubset (e.g. generated from backfill data)
        into an up-to-date one based on the latest partitions information in the asset graph. Raises
        an exception if the partitions in the asset graph are now totally incompatible (say, a
        partitioned asset is now unpartitioned, or the subset references keys that no longer exist)
        but adjusts the SerializableEntitySubset to reflect the latest version of the
        PartitionsDefinition if it differs but is still valid (for example, the range of the
        partitions have been extended and the subset is still valid.
        """
        if self.is_partitioned:
            check.invariant(
                partitions_def is not None,
                f"{self.key.to_user_string()} was partitioned when originally stored, but is no longer partitioned.",
            )
            if isinstance(self.value, AllPartitionsSubset):
                check.invariant(
                    self.value.partitions_def == partitions_def,
                    f"Partitions definition for {self.key.to_user_string()} is no longer compatible with an AllPartitionsSubset",
                )
                return self
            elif isinstance(self.value, TimeWindowPartitionsSubset):
                current_partitions_def = self.value.partitions_def
                if (
                    not isinstance(partitions_def, TimeWindowPartitionsDefinition)
                    or current_partitions_def.timezone != partitions_def.timezone
                    or current_partitions_def.fmt != partitions_def.fmt
                    or current_partitions_def.cron_schedule != partitions_def.cron_schedule
                ):
                    raise CheckError(
                        f"Stored partitions definition for {self.key.to_user_string()} is no longer compatible with the latest partitions definition",
                    )
                missing_subset = self.value - partitions_def.subset_with_all_partitions()
                if not missing_subset.is_empty:
                    raise CheckError(
                        f"Stored partitions definition for {self.key.to_user_string()} includes partitions {missing_subset} that are no longer present",
                    )

                return SerializableEntitySubset(
                    self.key, self.value.with_partitions_def(partitions_def)
                )
            else:
                return self
        else:
            check.invariant(
                partitions_def is None,
                f"{self.key.to_user_string()} was un-partitioned when originally stored, but is now partitioned.",
            )
            return self

    def is_compatible_with_partitions_def(
        self, partitions_def: Optional[PartitionsDefinition]
    ) -> bool:
        if self.is_partitioned:
            # for some PartitionSubset types, we have access to the underlying partitions
            # definitions, so we can ensure those are identical
            if isinstance(self.value, (TimeWindowPartitionsSubset, AllPartitionsSubset)):
                return self.value.partitions_def == partitions_def
            else:
                return partitions_def is not None
        else:
            return partitions_def is None

    def __contains__(self, item: AssetKeyPartitionKey) -> bool:
        if not self.is_partitioned:
            return item.asset_key == self.key and item.partition_key is None and self.bool_value
        else:
            return item.asset_key == self.key and item.partition_key in self.subset_value

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}<{self.key}>({self.value})"
