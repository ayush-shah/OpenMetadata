#  Copyright 2021 Collate
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#  http://www.apache.org/licenses/LICENSE-2.0
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

"""
Median Metric definition
"""
# pylint: disable=duplicate-code

from typing import List, cast

from sqlalchemy import column

from metadata.profiler.metrics.core import StaticMetric, _label
from metadata.profiler.orm.functions.median import MedianFn
from metadata.profiler.orm.registry import is_quantifiable
from metadata.utils.logger import profiler_logger

logger = profiler_logger()


class Median(StaticMetric):
    """
    Median Metric

    Given a column, return the Median value.

    - For a quantifiable value, return the usual Median
    """

    @classmethod
    def name(cls):
        return "median"

    @classmethod
    def is_window_metric(cls):
        return True

    @property
    def metric_type(self):
        return float

    @_label
    def fn(self):
        """sqlalchemy function"""
        if is_quantifiable(self.col.type):
            return MedianFn(column(self.col.name), self.col.table.name, 0.5)

        logger.debug(
            f"Don't know how to process type {self.col.type} when computing Median"
        )
        return None

    def df_fn(self, dfs=None):
        """Dataframe function"""
        from pandas import (  # pylint: disable=import-outside-toplevel
            DataFrame,
            concat,
            isnull,
        )

        dfs = cast(List[DataFrame], dfs)

        if is_quantifiable(self.col.type):
            # we can't compute the median unless we have
            # the entire set. Median of Medians could be used
            # though it would required set to be sorted before hand
            try:
                df = concat(dfs)
            except MemoryError:
                logger.error(
                    f"Unable to compute Median for {self.col.name} due to memory constraints."
                    f"We recommend using a smaller sample size or partitionning."
                )
                return None
            median = df[self.col.name].median()
            return None if isnull(median) else median
        logger.debug(
            f"Don't know how to process type {self.col.type} when computing Median"
        )
        return None
