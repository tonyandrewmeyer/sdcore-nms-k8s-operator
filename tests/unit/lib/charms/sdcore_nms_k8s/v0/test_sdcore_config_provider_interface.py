# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

from unittest.mock import patch

import pytest
import scenario

from tests.unit.lib.charms.sdcore_nms_k8s.v0.dummy_sdcore_config_provider_charm.src.dummy_provider_charm import (  # noqa: E501
    DummySdcoreConfigProviderCharm,
)


class TestSdcoreConfigProvider:
    @pytest.fixture(autouse=True)
    def context(self):
        self.ctx = scenario.Context(
            charm_type=DummySdcoreConfigProviderCharm,
            meta={
                "name": "sdcore-config-provider",
                "provides": {
                    "sdcore_config": {
                        "interface": "sdcore_config",
                    }
                },
            },
            actions={
                "set-webui-url": {
                    "description": "Set the URL of the web UI",
                    "params": {
                        "relation-id": {
                            "description": "The relation ID of the relation to get the URL from",
                            "type": "string",
                        },
                        "url": {
                            "description": "The URL of the web UI",
                            "type": "string",
                        },
                    },
                },
                "set-webui-url-in-all-relations": {
                    "description": "Set the URL of the web UI in all relations",
                    "params": {
                        "url": {
                            "description": "The URL of the web UI",
                            "type": "string",
                        },
                    },
                },
            },
        )

    @pytest.fixture(autouse=True)
    def setUp(self, request):
        yield
        request.addfinalizer(self.tearDown)

    @staticmethod
    def tearDown() -> None:
        patch.stopall()

    def test_given_unit_is_leader_when_set_webui_url_then_data_is_in_application_databag(  # noqa: E501
        self,
    ):
        sdcore_config_relation = scenario.Relation(
            endpoint="sdcore_config",
        )
        state_in = scenario.State(
            leader=True,
            relations=[sdcore_config_relation],
        )
        action = scenario.Action(
            name="set-webui-url",
            params={
                "relation-id": str(sdcore_config_relation.relation_id),
                "url": "whatever-url.com",
            },
        )

        action_output = self.ctx.run_action(action, state_in)

        assert action_output.state.relations[0].local_app_data["webui_url"] == "whatever-url.com"

    def test_given_unit_is_not_leader_when_set_webui_url_then_data_is_not_in_application_databag(  # noqa: E501
        self,
    ):
        sdcore_config_relation = scenario.Relation(
            endpoint="sdcore_config",
        )
        state_in = scenario.State(
            leader=False,
            relations=[sdcore_config_relation],
        )
        action = scenario.Action(
            name="set-webui-url",
            params={
                "relation-id": str(sdcore_config_relation.relation_id),
                "url": "whatever-url.com",
            },
        )

        with pytest.raises(Exception) as e:
            self.ctx.run_action(action, state_in)

        assert "Unit must be leader to set application relation data" in str(e.value)

    def test_given_provided_webui_url_is_not_valid_when_set_webui_url_then_error_is_raised(  # noqa: E501
        self,
    ):
        sdcore_config_relation = scenario.Relation(
            endpoint="sdcore_config",
        )
        state_in = scenario.State(
            leader=True,
            relations=[sdcore_config_relation],
        )
        action = scenario.Action(
            name="set-webui-url",
            params={"relation-id": str(sdcore_config_relation.relation_id), "url": ""},
        )

        with pytest.raises(Exception) as e:
            self.ctx.run_action(action, state_in)

        assert "Invalid url" in str(e.value)

    def test_given_unit_is_leader_and_sdcore_config_relation_is_not_created_when_set_webui_information_then_runtime_error_is_raised(  # noqa: E501
        self,
    ):
        state_in = scenario.State(leader=True)
        action = scenario.Action(
            name="set-webui-url",
            params={"relation-id": "0", "url": "whatever-url.com"},
        )

        with pytest.raises(Exception) as e:
            self.ctx.run_action(action, state_in)

        assert "Relation sdcore_config not created yet." in str(e.value)

    def test_given_unit_is_leader_when_multiple_sdcore_config_relation_joined_then_data_in_application_databag(  # noqa: E501
        self,
    ):
        sdcore_config_relation_1 = scenario.Relation(
            endpoint="sdcore_config",
        )
        sdcore_config_relation_2 = scenario.Relation(
            endpoint="sdcore_config",
        )
        state_in = scenario.State(
            leader=True,
            relations=[sdcore_config_relation_1, sdcore_config_relation_2],
        )
        action_1 = scenario.Action(
            name="set-webui-url",
            params={
                "relation-id": str(sdcore_config_relation_1.relation_id),
                "url": "whatever-url-1.com",
            },
        )
        action_2 = scenario.Action(
            name="set-webui-url",
            params={
                "relation-id": str(sdcore_config_relation_2.relation_id),
                "url": "whatever-url-2.com",
            },
        )

        action_output_1 = self.ctx.run_action(action_1, state_in)
        action_output_2 = self.ctx.run_action(action_2, action_output_1.state)

        assert (
            action_output_1.state.relations[0].local_app_data["webui_url"] == "whatever-url-1.com"
        )
        assert (
            action_output_2.state.relations[1].local_app_data["webui_url"] == "whatever-url-2.com"
        )

    def test_given_unit_is_leader_and_multiple_sdcore_config_relations_when_set_webui_information_in_all_relations_then_all_relations_are_updated(  # noqa: E501
        self,
    ):
        sdcore_config_relation_1 = scenario.Relation(
            endpoint="sdcore_config",
        )
        sdcore_config_relation_2 = scenario.Relation(
            endpoint="sdcore_config",
        )
        state_in = scenario.State(
            leader=True,
            relations=[sdcore_config_relation_1, sdcore_config_relation_2],
        )
        action = scenario.Action(
            name="set-webui-url-in-all-relations",
            params={"url": "whatever-url.com"},
        )

        action_output = self.ctx.run_action(action, state_in)

        assert action_output.state.relations[0].local_app_data["webui_url"] == "whatever-url.com"
        assert action_output.state.relations[1].local_app_data["webui_url"] == "whatever-url.com"
