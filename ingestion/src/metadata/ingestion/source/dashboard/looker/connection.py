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
Source connection handler
"""
import os
from typing import Optional

from looker_sdk import init40
from looker_sdk.sdk.api40.methods import Looker40SDK

from metadata.generated.schema.entity.automations.workflow import (
    Workflow as AutomationWorkflow,
)
from metadata.generated.schema.entity.services.connections.dashboard.lookerConnection import (
    LookerConnection,
)
from metadata.ingestion.connections.test_connections import test_connection_steps
from metadata.ingestion.ometa.ometa_api import OpenMetadata


def get_connection(connection: LookerConnection) -> Looker40SDK:
    """
    Create connection
    """
    if not os.environ.get("LOOKERSDK_CLIENT_ID"):
        os.environ["LOOKERSDK_CLIENT_ID"] = connection.clientId
    if not os.environ.get("LOOKERSDK_CLIENT_SECRET"):
        os.environ[
            "LOOKERSDK_CLIENT_SECRET"
        ] = connection.clientSecret.get_secret_value()
    if not os.environ.get("LOOKERSDK_BASE_URL"):
        os.environ["LOOKERSDK_BASE_URL"] = connection.hostPort

    return init40()


def test_connection(
    metadata: OpenMetadata,
    client: Looker40SDK,
    service_connection: LookerConnection,
    automation_workflow: Optional[AutomationWorkflow] = None,
) -> None:
    """
    Test connection. This can be executed either as part
    of a metadata workflow or during an Automation Workflow
    """

    test_fn = {"CheckAccess": client.me}

    test_connection_steps(
        metadata=metadata,
        test_fn=test_fn,
        service_fqn=service_connection.type.value,
        automation_workflow=automation_workflow,
    )
