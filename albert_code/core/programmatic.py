from __future__ import annotations

import asyncio

from albert_code import __version__
from albert_code.core.agent_loop import AgentLoop
from albert_code.core.agents.models import BuiltinAgentName
from albert_code.core.config import VibeConfig
from albert_code.core.logger import logger
from albert_code.core.output_formatters import create_formatter
from albert_code.core.types import (
    AssistantEvent,
    ClientMetadata,
    EntrypointMetadata,
    LLMMessage,
    OutputFormat,
    Role,
)
from albert_code.core.utils import ConversationLimitException

_DEFAULT_CLIENT_METADATA = ClientMetadata(name="vibe_programmatic", version=__version__)


def run_programmatic(
    config: VibeConfig,
    prompt: str,
    max_turns: int | None = None,
    max_price: float | None = None,
    output_format: OutputFormat = OutputFormat.TEXT,
    previous_messages: list[LLMMessage] | None = None,
    agent_name: str = BuiltinAgentName.AUTO_APPROVE,
    client_metadata: ClientMetadata = _DEFAULT_CLIENT_METADATA,
) -> str | None:
    formatter = create_formatter(output_format)

    agent_loop = AgentLoop(
        config,
        agent_name=agent_name,
        message_observer=formatter.on_message_added,
        max_turns=max_turns,
        max_price=max_price,
        enable_streaming=False,
        entrypoint_metadata=EntrypointMetadata(
            agent_entrypoint="programmatic",
            agent_version=__version__,
            client_name=client_metadata.name,
            client_version=client_metadata.version,
        ),
    )
    logger.info("USER: %s", prompt)

    async def _async_run() -> str | None:
        try:
            if previous_messages:
                non_system_messages = [
                    msg for msg in previous_messages if not (msg.role == Role.system)
                ]
                agent_loop.messages.extend(non_system_messages)
                logger.info(
                    "Loaded %d messages from previous session", len(non_system_messages)
                )

            agent_loop.emit_new_session_telemetry()

            async for event in agent_loop.act(prompt):
                formatter.on_event(event)
                if isinstance(event, AssistantEvent) and event.stopped_by_middleware:
                    raise ConversationLimitException(event.content)

            return formatter.finalize()
        finally:
            await agent_loop.telemetry_client.aclose()

    return asyncio.run(_async_run())
